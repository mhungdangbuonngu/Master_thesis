# Hướng dẫn chạy code: dự đoán hiệp đồng thuốc 3 lớp + giải thích 3 cấp

Code hiện thực đề xuất trong `danh_gia_kha_thi_thesis.md`. Toàn bộ chỉ dùng **torch + numpy + pandas + scikit-learn**, không cần PyG, RDKit hay Captum. GCN và Integrated Gradients được viết tay, mỗi phần chỉ vài chục dòng.

## 1. Cấu trúc thư mục

```
src/
  data/
    make_synthetic.py   sinh dữ liệu bán tổng hợp có gene "cài sẵn" (ground truth cho explainer)
    prepare.py          4 file CSV thô -> 1 file .pt (gene, thuốc, cell, bộ ba, nhãn 3 lớp)
    dataset.py          đọc .pt + chia train/val/test (random / leave-combo-out / leave-cell-out)
  model/
    gnn.py              SynergyGNN: GCN trên mạng PPI, đối xứng theo (A, B)
  training/
    train.py            train + early stopping theo QWK, lưu model.pt và metrics.json
    baselines.py        majority, cell-only, MLP kiểu DeepSynergy (dùng cho Gate 2)
  eval/
    metrics.py          QWK, macro-F1, F1 từng lớp, polar error, confusion matrix
    attribution.py      IG 3 cấp: logit / contrast / interaction
    explain_benchmark.py  kill test (Gate 3): explainer có tìm đúng gene cài sẵn không
  testing/
    test_all.py         5 kiểm tra nhanh (đối xứng, không rò rỉ split, completeness của IG, ...)
data/                   dữ liệu (tự sinh khi chạy)
runs/                   kết quả train (tự sinh khi chạy)
```

## 2. Cài đặt từ đầu

```bash
# Python >= 3.10
pip install torch numpy pandas scikit-learn
# GPU: cài torch theo lệnh trên https://pytorch.org (chọn đúng bản CUDA). Không có GPU vẫn chạy được trên CPU, chỉ chậm hơn.
```

**Mọi lệnh đều chạy từ thư mục gốc `C:\HUST\THESIS`** bằng `python -m ...`, để các import `src.xxx` hoạt động.

## 3. Chạy toàn bộ trên dữ liệu bán tổng hợp (khoảng 2 phút với GPU)

```bash
python -m src.testing.test_all                    # 1. kiểm tra code: phải ra 5 dòng PASS
python -m src.data.make_synthetic                 # 2. sinh data/raw_synth/*.csv + ground_truth.json
python -m src.data.prepare                        # 3. -> data/synth.pt, in phân bố nhãn theo ngưỡng 5/10/20
python -m src.training.train                      # 4. train GNN -> runs/synth_combo_f0/
python -m src.training.baselines                  # 5. baseline trên cùng split
python -m src.eval.explain_benchmark              # 6. kill test cho 3 cấp attribution
```

Các tham số đều có giá trị mặc định. Tham số hay đổi:
- `train.py`:
  - `--split random|combo|cell`
  - `--fold 0..4`
  - `--seed`
  - `--epochs`
  - `--out runs/<tên>`
- `prepare.py`:
  - `--score synergy_loewe|synergy_bliss|synergy_hsa|synergy_zip`
  - `--thr 10`
  - `--max_genes 1000`

## 4. Flow training: dữ liệu đi qua những bước nào

```
CSV thô ──prepare.py──> synth.pt ──dataset.make_split──> train / val / test
                                                         │
                     SynergyGNN(A, B, expr_c) ◄──────────┘
                         │
   node gene g: [expr_c(g), tA(g)+tB(g), tA(g)·tB(g)]     (tA = 1 nếu g là target của thuốc A)
                         │  2 lớp GCN trên mạng PPI: h ← ReLU(Â · h · W)
                         │  chiếu mỗi gene xuống 4 chiều, rồi flatten (giữ danh tính từng gene)
                         │  ghép [eA + eB, eA · eB]  (embedding thuốc)
                         ▼
                   MLP → 3 logit (ant, add, syn)
                         │
   loss = CrossEntropy có trọng số lớp (1 / tần suất, vì additive chiếm khoảng 70%)
   AdamW, batch 256; mỗi epoch đo QWK trên val; giữ model tốt nhất; dừng sau 10 epoch không cải thiện
                         ▼
   test → metrics.json (QWK, macro-F1, F1 từng lớp, polar error, confusion, macro-AUROC)
```

**Các quyết định thiết kế (đều có lý do trong file khả thi):**

1. **Nhãn 3 lớp.** Synergy score > 10 là syn, < −10 là ant, còn lại là add (`prepare.to_labels`). Lệnh `prepare.py` in phân bố nhãn cho mọi cột `synergy_*` × ngưỡng 5/10/20, đây chính là đầu vào của Gate 1.
2. **Đối xứng A↔B.** Đặc trưng node dùng tổng và tích target, embedding thuốc cũng dùng tổng và tích. Vì vậy model đối xứng ngay từ thiết kế, không cần augmentation. `test_symmetry` kiểm tra điều này.
3. **Flatten thay vì pooling.** Pooling trung bình sẽ xóa danh tính gene, khi đó attribution lên gene không còn ý nghĩa.
4. **Split mặc định là leave-combination-out.** Cặp thuốc ở test chưa từng xuất hiện trong train (`test_split_no_leak`). Split random chỉ dùng để so với số liệu đã công bố.
5. **Metric chính là QWK.** Polar error (nhầm syn↔ant) được báo riêng vì đây là lỗi nguy hiểm nhất.

## 5. Ba cấp giải thích (`eval/attribution.py`)

Mọi cấp đều dùng Integrated Gradients theo biểu hiện gene, với baseline = 0 (expr đã z-score nên 0 = mức trung bình). Ba cấp chỉ khác nhau ở **đại lượng được giải thích**:

| Cấp | Đại lượng | Trả lời câu hỏi |
|---|---|---|
| (i) `logit` | z_syn | "gene nào đẩy logit syn lên". Đây là cách literature đang làm |
| (ii) `contrast` | Δ = z_syn − z_add | "vì sao là syn **thay vì** add" |
| (iii) `interaction` | Δ(A,B) − E_r Δ(A,r) − E_r Δ(r,B) + E_{r,r'} Δ(r,r') | "phần nào là **tương tác** của cặp, sau khi trừ hiệu ứng riêng của từng thuốc" |

Cấp (iii) là ANOVA bậc 2 theo trục thuốc, với r là thuốc tham chiếu (mặc định là mọi thuốc). Nếu thuốc A "hiệp đồng với mọi đối tác", phần đó bị trừ đi. `test_interaction_kills_main_effects` chứng minh: với model thuần cộng tính, attribution cấp (iii) bằng 0, còn cấp (ii) thì không.

**Thay đổi so với đề xuất ban đầu:** file khả thi đề nghị học một "null-drug embedding ∅" kèm head đơn trị liệu. Code dùng trung bình theo thuốc tham chiếu thay cho cách đó vì **không cần dữ liệu đơn trị liệu và không cần train thêm gì**. Nếu sau này có dữ liệu monotherapy của DrugComb, có thể thêm ∅ như một thuốc giả có target rỗng.

## 6. Kill test (`eval/explain_benchmark.py`)

Dữ liệu bán tổng hợp cài sẵn 3 nhóm gene:
- **Z (G0–G2)**: hiệp đồng, chỉ khi A ∈ S_A và B ∈ S_B.
- **W (G3–G5)**: đối kháng, khi A ∈ S_A và B ∈ S_C.
- **M (G6–G8)**: hiệu ứng chính. Thuốc ∈ S_M đẩy score lên ở **mọi** cặp, nên đây **không** phải tương tác.

Bộ ba được chấm phải mang cả tương tác thật lẫn hiệu ứng chính. Hai chỉ số:
- `recall@3`: tỷ lệ gene Z hoặc W lọt top-3. Càng cao càng tốt.
- `main@3`: tỷ lệ gene M lọt top-3. Càng **thấp** càng tốt, vì explainer khi đó không nhầm hiệu ứng chính là cơ chế hiệp đồng.

**Kết quả lần chạy thử** (seed 0, split combo fold 0, 300 cell):

| | recall@3 ↑ | main@3 ↓ |
|---|---|---|
| syn / logit | 0.152 | 0.398 |
| syn / contrast | 0.195 | 0.320 |
| syn / interaction | **0.203** | **0.147** |
| ant / logit | 0.057 | 0.428 |
| ant / contrast | **0.095** | 0.331 |
| ant / interaction | 0.068 | **0.089** |

Hiệu năng phân lớp trên test (leave-combo-out):

| Model | QWK | macro-F1 |
|---|---|---|
| majority | 0.000 | 0.274 |
| cell-only | 0.504 | 0.568 |
| MLP kiểu DeepSynergy | **0.815** | **0.852** |
| GNN | 0.765 | 0.808 |

**Đọc kết quả cho trung thực:**
1. **Cấp interaction giảm mạnh việc nhầm hiệu ứng chính** (main@3 từ 0.40 xuống 0.15 với syn, từ 0.43 xuống 0.09 với ant). Đây là hướng mà giả thuyết thesis dự đoán. Tuy vậy đây mới là **1 seed, 1 fold**. Trước khi viết vào luận văn cần chạy 5 seed × 5 fold và báo mean ± std.
2. **recall@3 của mọi cấp đều thấp (≤ 0.2).** Model dự đoán tốt nhưng không dựa chủ yếu vào gene Z. Đây là minh họa trực tiếp cho luận điểm "faithful ≠ mechanistic".
3. **Với 40 cell (gần với O'Neil có 39 cell), recall@3 bằng 0 ở mọi cấp.** Khi đó model chỉ cần nhớ danh tính từng cell, nên không có lý do học gene Z. Vì vậy mặc định là 300 cell. **Đây là rủi ro lớn cho dữ liệu thật** và nên được đưa vào phần hạn chế, hoặc giải quyết bằng cách gộp thêm cell line từ các nguồn khác của DrugComb.
4. Trên dữ liệu này, MLP không có đồ thị **thắng** GNN. Điều này hợp lý vì mạng PPI tổng hợp là ngẫu nhiên và không chứa tín hiệu. Trên dữ liệu thật vẫn phải so như vậy (Gate 2). Nếu GNN thua MLP, cần nói thẳng điều đó trong luận văn.

## 7. Chạy với dữ liệu thật (O'Neil / DrugComb)

Tạo thư mục `data/raw_oneil/` gồm 4 file với đúng tên cột sau:

| File | Cột | Nguồn |
|---|---|---|
| `combos.csv` | `drug_row, drug_col, cell_line_name, synergy_loewe` (thêm `synergy_bliss/hsa/zip` nếu có) | DrugComb summary table, lọc `study_name == "ONEIL"`. **Dùng điểm thô, không dùng bộ 13,243 mẫu của DeepDDS.** |
| `expression.csv` | hàng = tên cell line (trùng `cell_line_name`), cột = gene symbol | CCLE/DepMap `OmicsExpressionProteinCodingGenesTPMLogp1.csv`. Đổi tên cột về gene symbol và map ID cell line về tên. |
| `targets.csv` | `drug, gene` | DrugBank hoặc DrugComb drug annotation |
| `ppi.csv` | `gene1, gene2` | STRING, lọc combined_score ≥ 700 và đổi protein ID sang gene symbol |

Sau đó chạy:

```bash
python -m src.data.prepare --raw data/raw_oneil --out data/oneil.pt --score synergy_loewe --thr 10
python -m src.training.baselines --data data/oneil.pt --split combo --fold 0 --out runs/oneil_baselines_f0.json
python -m src.training.train --data data/oneil.pt --split combo --fold 0 --out runs/oneil_combo_f0
```

Lặp lại với `--fold 0..4`, `--split cell` và các seed khác nhau để có mean ± std. Lệnh `explain_benchmark.py` chỉ dùng được với dữ liệu bán tổng hợp, vì chỉ dữ liệu đó có ground truth. Với dữ liệu thật, gọi `src.eval.attribution.attribute(...)` để lấy điểm gene rồi phân tích tiếp (top gene, enrichment).

## 8. Những gì chưa làm, và khi nào nên thêm

- **CORAL / ordinal loss:** hiện dùng cross-entropy có trọng số lớp. Chỉ thêm nếu polar error trên dữ liệu thật đáng kể.
- **Script chạy nhiều fold × seed:** hiện chạy bằng vòng lặp shell. Viết script riêng khi số lần chạy đủ nhiều để thấy phiền.
- **Fidelity±, Jaccard giữa các seed, KEGG enrichment:** thêm ở giai đoạn GĐ4, sau khi qua Gate 3.
- **Đặc trưng hóa học của thuốc (RDKit fingerprint):** hiện thuốc chỉ được biểu diễn bằng target và embedding. Thêm nếu cần dự đoán cho thuốc mới (leave-drug-out).
