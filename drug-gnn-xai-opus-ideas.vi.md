# Báo cáo đề xuất ý tưởng (ideation report): drug_synergy_xai

Mức tiên tiến nhất hiện nay của con người (human state of the art): Khung học sâu đồ thị (graph deep learning framework) có khả năng diễn giải (interpretable) để dự đoán hiệp đồng thuốc (drug synergy prediction) bằng cách tích hợp độ tương đồng chức năng và lâm sàng (functional and clinical similarities) (DSimSynergy), Lai và cộng sự, npj Digital Medicine 2026

6 ý tưởng hạt giống (seed ideas) (xếp hạng theo độ mới (novelty), thang 1-10) và 8 hạn chế (limitations). Chưa có dòng mã nào được viết hay chạy.

## Mục lục

- [S1 · độ mới 6 · PathKNN-Syn: dự đoán hiệp đồng tăng cường bằng truy xuất (retrieval-augmented) với nhân tế bào (cell kernel) được học, phân rã theo đường truyền tín hiệu (pathway-factorised), và giải thích ở mức mẫu điển hình (exemplar-level explanations)](#s1)
- [S2 · độ mới 6 · PathX-Comp: một tensor tương tác chéo (crosstalk tensor) trên các đường truyền KEGG, chấm điểm mức độ các đường truyền mà hai thuốc nhắm tới bổ sung cho nhau (complement) trong một dòng tế bào (cell line) cụ thể, được thêm vào DSimSynergy như một số hạng hiệp đồng có sẵn và diễn giải được](#s2)
- [S3 · độ mới 6 · DoseCurve-Syn: một toán tử phi cộng tính (non-additivity operator) được học trong không gian liều (dose space). Hiệp đồng được tính như sai phân hữu hạn bậc hai (second-order finite difference) của các mô-đun đáp ứng đường truyền (pathway response modules) có cổng theo tế bào (cell-gated), được điều khiển bởi các đích tác dụng (targets) của mỗi thuốc.](#s3)
- [S4 · độ mới 6 · FlipPath-Syn: huấn luyện với phản thực tế ghép cặp (matched-counterfactual training), bộ mã hóa tế bào (cell encoder) có cổng đường truyền dạng sparsemax, và giải thích phản thực tế bằng hoán đổi đường truyền tối thiểu (minimal pathway-swap counterfactual explanations)](#s4)
- [S5 · độ mới 5 · SLink-Syn: một số hạng ghép nối gây chết tổng hợp (synthetic-lethality coupling term) trên "dấu vết" đích tác dụng lan truyền qua mạng (network-propagated target footprints) đặc thù theo tế bào, cho phép quy kết theo cặp gen (gene-pair attributions) đối với hiệp đồng thuốc](#s5)
- [S0 · độ mới 4.5 · SymTri-Rank: đầu tương tác ba tuyến tính (trilinear interaction head) đối xứng, có điều kiện theo tế bào (cell-conditioned), huấn luyện bằng xếp hạng có tính đến độ lớn (magnitude-aware ranking), cùng quy kết phân rã theo tương tác (interaction-decomposed attributions) cho DSimSynergy](#s0)
- [Các hạn chế của mức tiên tiến nhất hiện nay](#limitations)

<a id="s1"></a>
## S1 · độ mới 6 · PathKNN-Syn: dự đoán hiệp đồng tăng cường bằng truy xuất (retrieval-augmented) với nhân tế bào (cell kernel) được học, phân rã theo đường truyền tín hiệu (pathway-factorised), và giải thích ở mức mẫu điển hình (exemplar-level explanations)

_Thêm vào DSimSynergy một nhánh truy xuất khả vi (differentiable retrieval branch). Với mỗi truy vấn (query), nhánh này tra cứu các bộ ba (triplets) huấn luyện đã gán nhãn: cùng cặp thuốc đó ở các dòng tế bào khác, và từng thuốc đi với các thuốc đối tác (partners) khác trong cùng dòng tế bào. Các dòng tế bào của cặp thuốc được gán trọng số bằng một nhân (kernel) được học, nhân này cộng các khoảng cách biểu hiện gen (expression distances) theo từng đường truyền KEGG với trọng số phụ thuộc vào cặp thuốc; các đối tác được gán trọng số bằng cơ chế chú ý (attention) được học (và cũng có thể tìm kiếm sự khác biệt (dissimilarity-seeking)) trên các biểu diễn nhúng thuốc (drug embeddings). Dự đoán đi kèm sẵn các quy kết (attributions) theo mẫu điển hình và theo đường truyền, có thể kiểm chứng bằng phép xóa (deletion)._

### Động lực (Motivation)

Trên phép chia ngẫu nhiên theo bộ ba (random triplet split), bằng chứng giàu thông tin nhất cho một bộ ba kiểm tra (a,b,c) là cách cùng cặp thuốc đó đã hành xử ở các dòng tế bào khác, và cách a và b đã hành xử với các đối tác khác trong c. DSimSynergy chỉ có thể dùng bằng chứng này một cách ngầm định, bằng cách ghi nhớ (memorising) nó vào trọng số MLP từ các đặc trưng ghép nối (concatenated features) (L2). Cách này đòi hỏi nhiều dữ liệu đối với lớp dương tính (positive class) chỉ chiếm 3% và không đưa ra lời giải thích dựa trên ca (case-based explanation). Bộ mã hóa tế bào của nó chỉ là một lớp kết nối đầy đủ (FC layer), bỏ qua cấu trúc đường truyền và bỏ qua các thuốc đang được kết hợp. Các giải thích KEGG của nó là tương quan SHAP–biểu hiện hậu nghiệm (post-hoc) lấy từ một mô hình khác (mô hình hồi quy (regression)) (L4, L5). GCN trên mạng tương đồng (similarity network) giả định tính đồng loại (homophily), một giả định được ủng hộ yếu (PCC 0.21–0.23) và mâu thuẫn với chính cơ chế "bổ sung đường truyền (pathway complementarity)" của các tác giả (L7). Bộ phân loại (classifier) cũng không bao giờ thấy độ lớn điểm Loewe (Loewe magnitudes) (L8). Một nhánh truy xuất giải quyết trực tiếp các vấn đề này. (i) Nó biến các nhãn dương thưa thớt thành một tiên nghiệm phi tham số (non-parametric prior), làm sắc nét phần đầu của bảng xếp hạng, đúng điều mà AUPR đánh giá cao. (ii) Nhân trên các dòng tế bào được phân rã theo các đường truyền KEGG với trọng số phụ thuộc cặp thuốc, nên câu hỏi "những đường truyền nào khiến dòng tế bào c' hành xử giống c đối với cặp này" là một phần của phép tính lan truyền tiến (forward computation), chứ không phải một tương quan hậu nghiệm. (iii) Nhân đối tác được học và có dấu (signed), nên có thể ưu tiên các đối tác bổ sung thay vì các đối tác tương đồng. (iv) Nó tổng hợp điểm Loewe liên tục của các láng giềng (neighbours) làm bằng chứng trong khi vẫn giữ nguyên các nhãn nhị phân. Mọi thành phần đều đối xứng theo (a,b), nên bằng chứng truy xuất và các quy kết của nó không phụ thuộc vào thứ tự thuốc (L3).

### Phương pháp (Method)

Ký hiệu: tập gấp huấn luyện (training fold) T chứa (a,b,c,y,s), với y∈{0,1} và s là điểm Loewe. Các bản sao đảo chiều (mirrored copies) của một bộ ba được coi là cùng một bộ ba. Chỉ tập gấp huấn luyện CV hiện tại mới được ghi vào bộ nhớ (memory). Các bộ ba kiểm định (validation) và kiểm tra giữ lại (held-out test) chỉ được dùng để truy vấn và không bao giờ được lưu.

1) Các góc nhìn biểu hiện theo đường truyền (pathway expression views). Với mỗi đường truyền KEGG p có ít nhất 5 gen L1000 (khoảng 250 đường truyền; bộ gen (gene sets) lấy từ MSigDB C2:KEGG), x_c^p là vectơ biểu hiện log2(TPM+1) đã chuẩn hóa z (z-scored) của các gen L1000 thuộc p trong dòng tế bào c. Tính trước một lần khoảng cách theo đường truyền d_p(c,c') = ||x_c^p − x_{c'}^p||² / |p| dưới dạng tensor 83×83×P.

2) Nhân đường truyền có điều kiện theo cặp (pair-conditioned pathway kernel) (bộ nhớ cùng cặp (same-pair memory)). Gọi e_a và e_b là các biểu diễn nhúng thuốc của DSimSynergy (ghép nối đầu ra BP-GCN, ATC-GCN và GAT, chiếu xuống 64 chiều). Tạo mã cặp bất biến theo thứ tự (order-invariant pair code) q_ab = [e_a+e_b, e_a⊙e_b]. Trọng số đường truyền là w_p(a,b) = softplus(u_p + v_pᵀ q_ab), với phạt L1 (L1 penalty) λ_w·Σ_p w_p và λ_w = 1e-4 để chỉ có ít đường truyền được kích hoạt. Khoảng cách là D_ab(c,c') = Σ_p w_p(a,b)·d_p(c,c'). Bộ nhớ là M_pair = {(a,b,c',y',s') ∈ T : c' ≠ c}. Trọng số chú ý là α_{c'} = softmax_{c'}(−D_ab(c,c')/τ), với τ học được và khởi tạo bằng 1.

3) Nhân đối tác có dấu (signed partner kernel) (bộ nhớ cùng tế bào (same-cell memory)). M_a = {(a,b',c,y',s') ∈ T : b' ≠ b}, và M_b được định nghĩa đối xứng. Trọng số chú ý là β_{b'} = softmax_{b'}(h(e_b,e_{b'}, cell c)), trong đó h = MLP([e_b⊙e_{b'}, |e_b−e_{b'}|, cell_emb_c]) → vô hướng (scalar). Vì đầu vào có |e_b−e_{b'}| và không có ràng buộc về dấu, mô hình có thể học cách truy xuất các đối tác bổ sung chứ không chỉ các đối tác tương đồng (tính dị loại (heterophily), L7). Khi đánh giá, dùng tất cả các đối tác. Khi huấn luyện, lấy mẫu tối đa K=64 đối tác cho mỗi cặp thuốc–tế bào.

4) Tóm tắt bằng chứng (evidence summaries). Với mỗi bộ nhớ m ∈ {pair, a, b}, tính tỷ lệ dương tính đã làm trơn (smoothed positive rate) π_m = (Σ attn·y' + α0·π̄)/(Σ attn·n_eff + α0)·… Trong thực hành, dùng số đếm có trọng số n_m = N_m·Σ attn (N_m là kích thước bộ nhớ), k_m = N_m·Σ attn·y', và π_m = (k_m + α0 π̄)/(n_m + α0), với α0 = 2 và π̄ là tiên nghiệm lớp (class prior). Đồng thời tính bằng chứng độ lớn (magnitude evidence) μ_m = Σ attn·clip(s',−50,100)/50 và độ hỗ trợ (support) σ_m = log1p(N_m). Logit bằng chứng: r_m = logit(π_m). Gộp đối xứng bộ nhớ a và b: r_drug = (r_a + r_b)/2, μ_drug = (μ_a + μ_b)/2.

5) Hợp nhất (fusion). z = z_param(a,b,c) + Σ_{m∈{pair,drug}} γ_m(σ_m)·r_m + δᵀ[μ_pair, μ_drug]. Ở đây z_param là logit của bộ phân loại DSimSynergy giữ nguyên, được làm bất biến theo thứ tự bằng cách lấy trung bình hai thứ tự, và γ_m(σ) = softplus(g0_m + g1_m·σ), để bằng chứng được tin cậy hơn khi độ hỗ trợ lớn hơn. Đầu ra là p = sigmoid(z). Hàm mất mát (loss) là CE có trọng số theo lớp (class-weighted CE) của bài báo (giữ nguyên), ngưỡng quyết định (decision threshold) là 0.5, và điểm lưu mô hình (checkpoint) được chọn theo F1 trên tập kiểm định, như trong giao thức (protocol).

6) Rò rỉ dữ liệu (leakage) và tính nhất quán giữa huấn luyện/kiểm tra. Trong khi huấn luyện, bộ ba truy vấn và bản đảo chiều của nó luôn bị loại khỏi chính bộ nhớ của chúng (bỏ-chính-mình (leave-self-out)). Ngoài ra, ngẫu nhiên 20% mỗi bộ nhớ bị che đi (dropout bộ nhớ (memory dropout)), để mô hình không quá tin vào bằng chứng dày đặc hơn mức mà một bộ ba giữ lại sẽ thấy. Bộ ba kiểm định và kiểm tra chỉ truy vấn bộ nhớ của tập gấp huấn luyện. Tập kiểm tra không bao giờ được dùng, dù làm bộ nhớ hay để tinh chỉnh (tuning).

7) Giải thích có sẵn, chính xác theo cấu trúc (exact by construction) đối với số hạng truy xuất. (a) Quy kết theo mẫu điển hình (exemplar attribution): đóng góp của mỗi bộ ba huấn luyện được truy xuất vào z, tính bằng ∂z/∂y' nhân với khối lượng chú ý (attention mass) của nó; được báo cáo dưới dạng 'cặp X đã hiệp đồng (Loewe 42) trong dòng tế bào Y, trọng số 0.31'. (b) Quy kết theo đường truyền (pathway attribution): đóng góp w_p(a,b)·d_p vào nhân, cho ra các đường truyền KEGG đặc thù theo cặp thuốc mà bộ phân loại thực sự sử dụng. (c) Quy kết theo đối tác (partner attribution): β trên b', cho thấy các thuốc đối tác bổ sung hoặc tương đồng, tức là giải thích ở mức láng giềng trên mạng tương đồng. SHAP trên gen và phân tích nguyên tử (atom analysis) của GAT vẫn được chạy trên cùng bộ phân loại, không phải trên một mô hình hồi quy riêng.

8) Giao thức kiểm tra tính trung thực (faithfulness protocol). Đường cong xóa (deletion curves): loại bỏ top-k mẫu điển hình (theo quy kết) khỏi bộ nhớ, hoặc đặt bằng 0 top-k trọng số đường truyền, rồi dự đoán lại. Báo cáo mức giảm của p và của AUPR trên tập kiểm tra so với việc xóa ngẫu nhiên cùng số mẫu điển hình hoặc đường truyền, k ∈ {1,3,5,10}. Chạy kiểm tra hợp lý với trọng số ngẫu nhiên hóa (randomised-weight sanity check).

Mặc định: số chiều nhúng 64, P≈250 đường truyền, K=64 đối tác lấy mẫu, dropout bộ nhớ 0.2, α0=2, τ khởi tạo 1, λ_w=1e-4, Adam lr 1e-4 (đầu truy xuất có thể dùng 1e-3), batch 512, 50 epoch trên tập con (subset).

### Các hạn chế được giải quyết

L2, L3, L4, L5, L7, L8

### Tuyên bố về độ mới (Novelty claim)

Các bộ dự đoán hiệp đồng đã công bố (DeepSynergy, DeepDDS, AttenSynergy, HyperGraphSynergy, JointSyn, DSimSynergy) hoàn toàn là mô hình tham số (parametric), còn các mô hình cơ sở (baselines) dựa trên mẫu điển hình hay kNN dùng độ tương đồng cố định. Ý tưởng này là một bộ phân loại hiệp đồng tăng cường bằng truy xuất, khả vi và an toàn trước rò rỉ, với hai thành phần mới: (1) một nhân dòng tế bào phân rã theo các đường truyền KEGG và có điều kiện theo cặp thuốc, nên giải thích theo đường truyền là một phần của cơ chế mô hình chứ không phải bản tóm tắt SHAP–ORA hậu nghiệm; (2) một nhân truy xuất đối tác có dấu, có điều kiện theo tế bào, có thể học tính bổ sung thay vì tính đồng loại theo độ tương đồng. Các giải thích của nó đồng thời dựa trên ca (các mẫu điển hình huấn luyện kèm giá trị Loewe), dựa trên đường truyền và dựa trên láng giềng, và có thể kiểm tra bằng phép xóa. Nó khác S0 — vốn thay đổi đầu hợp nhất tham số (parametric fusion head) và hàm mất mát; ở đây cơ chế là truy xuất bằng chứng phi tham số với các nhân sinh học được học, còn bộ phân loại, hàm mất mát và ngưỡng được giữ nguyên.

### Kế hoạch triển khai (Implementation plan)

1) data_utils: sau khi đã cố định phép chia tập kiểm tra và phép chia các tập gấp, xây dựng các cấu trúc chỉ mục (index structures) theo từng tập gấp chỉ từ tập gấp huấn luyện. Đó là dict pair_key(min(a,b),max(a,b)) → tensor (cell_idx, y, s), và dict (drug,cell) → tensor (partner_idx, y, s). Các hàng đảo chiều được khử trùng lặp (deduplicated) theo pair_key. Cung cấp một hàm gom lô (collate function) thu thập các tensor bộ nhớ đã đệm (padded) (cùng cặp ≤83 mục; đối tác giới hạn ở K=64 khi huấn luyện, đầy đủ khi đánh giá) kèm mặt nạ (masks), đồng thời loại bỏ chính truy vấn và áp dụng dropout bộ nhớ 20% trong khi huấn luyện.
2) pathway_prep.py: tải bộ gen KEGG (file GMT MSigDB C2 KEGG), lấy giao với 949 gen L1000, giữ các đường truyền có ≥5 gen, và tính trước tensor d_p [83,83,P] dưới dạng file .pt.
3) model.py: thêm mô-đun RetrievalHead nhận các biểu diễn nhúng thuốc (đầu ra GCN/GAT hiện có, chiếu tuyến tính xuống 64), biểu diễn nhúng tế bào, tensor d_p và lô bộ nhớ, rồi trả về r_pair, r_drug, các μ, các γ và các bản đồ chú ý (attention maps). Trong hàm forward, tính z_param cho cả hai thứ tự và lấy trung bình, rồi cộng các số hạng truy xuất như ở bước 5 của Phương pháp.
4) train.py: giữ nguyên hàm mất mát, lr, batch, cách lưu checkpoint và ngưỡng. Thêm số hạng L1 λ_w. Thêm các cờ (flags) --no_retrieval, --uniform_kernel (w_p hằng số, không có điều kiện) và --raw_expr_kernel (cosin trên toàn bộ 949 gen) cho các thí nghiệm loại bỏ (ablations).
5) explain.py: xuất quy kết theo mẫu điển hình, đường truyền và đối tác; đường cong trung thực xóa/chèn (deletion/insertion faithfulness curves) so với ngẫu nhiên; kiểm tra hợp lý với trọng số ngẫu nhiên hóa; và phân tích SHAP trên gen hiện có, chạy trên bộ phân loại.
Tính toán: thao tác thu thập bộ nhớ có độ phức tạp O(batch×(83+2K)), không đáng kể trên A100. Lượt chạy sàng lọc (screening run) dự kiến trên tập gấp 1 với 50 epoch: <1 giờ.

### Tác động dự kiến (Expected effect)

Với phép chia ngẫu nhiên theo bộ ba, bằng chứng "cùng cặp ở các tế bào khác" có tính dự đoán rất cao, vì nhãn hiệp đồng của một cặp tương quan mạnh giữa các dòng tế bào. Một nhân đường truyền được học sẽ chọn ra những dòng tế bào quan trọng, chủ yếu làm tăng điểm của các dương tính thật (true positives) ở đầu bảng xếp hạng. Tác động dự kiến trên toàn bộ bộ chuẩn (benchmark): AUPR từ 0.77 lên khoảng 0.80–0.83, F1 từ 0.74 lên khoảng 0.76–0.79 (logit bằng chứng được hiệu chuẩn tốt (well-calibrated) quanh tiên nghiệm, nên 0.5 trở thành điểm vận hành (operating point) tốt hơn), AUROC từ 0.96 lên khoảng 0.97, ACC ≈0.98 (không đổi hoặc tăng nhẹ). Phương sai giữa các tập gấp sẽ thấp hơn nhờ tính bất biến theo thứ tự. Thứ tự dự kiến của các thí nghiệm loại bỏ: không truy xuất < nhân đồng nhất < nhân biểu hiện thô < nhân đường truyền có điều kiện theo cặp thuốc. Tính trung thực: xóa top-5 mẫu điển hình hoặc đường truyền sẽ làm giảm p nhiều hơn đáng kể so với xóa ngẫu nhiên.

### Rủi ro (Risks)

(1) Phụ thuộc quá mức vào bộ nhớ: mô hình có thể dựa vào truy xuất mà bỏ qua đặc trưng thuốc/tế bào, gây hại cho các cặp có ít hỗ trợ từ bộ nhớ và cho khả năng khái quát hóa sang DrugOut/CellOut. Theo dõi AUPR phân tầng (stratified) theo độ hỗ trợ của bộ nhớ. Giảm thiểu: dropout bộ nhớ và γ phụ thuộc độ hỗ trợ; quay về z_param khi bộ nhớ rỗng. (2) Lệch giữa huấn luyện/kiểm tra (train/test mismatch): nếu bộ nhớ khi huấn luyện thực chất dày hơn bộ nhớ khi kiểm tra dù đã bỏ-chính-mình, quá trình huấn luyện sẽ cho thấy khớp quá tự tin (over-confident fits) và F1 kiểm định thấp hơn F1 huấn luyện. Giảm thiểu: chỉ tinh chỉnh tỷ lệ dropout bộ nhớ trên tập gấp kiểm định. (3) Trọng số đường truyền bị dàn trải (diffuse): trọng số đường truyền có thể vẫn phân tán, khiến giải thích không có nhiều thông tin dù AUPR tăng. Giảm thiểu: tăng λ_w, hoặc thay softplus bằng chuẩn hóa sparsemax. (4) Độ phủ bộ gen (gene-set coverage): mỗi đường truyền KEGG có ít gen L1000 có thể khiến một số d_p bị nhiễu. Giảm thiểu: dùng các đường truyền có ≥5 gen và tùy chọn thêm các bộ GO-BP rút gọn (GO-BP slim sets). (5) Lỗi rò rỉ (leakage bugs): việc xây dựng bộ nhớ chỉ được dùng các hàng của tập gấp huấn luyện. Khẳng định (assert) rằng không có tổ hợp pair_key+cell nào của tập kiểm tra hay kiểm định xuất hiện trong bộ nhớ; một sai sót sẽ lộ ra dưới dạng điểm kiểm định cao bất thường.

### Kiểm tra độ mới (Novelty check)

Tôi không tìm thấy bài báo nào đề xuất một nhánh truy xuất khả vi, an toàn trước rò rỉ cho một bộ phân loại hiệp đồng dựa trên GNN. Nhánh như vậy sẽ lấy từ hai bộ nhớ: cùng cặp ở các dòng tế bào khác, và từng thuốc với các đối tác khác trong cùng dòng tế bào. Nó sẽ dùng một nhân tế bào phân rã theo đường truyền có điều kiện theo cặp thuốc, một nhân đối tác có dấu (có khả năng biểu diễn tính bổ sung), hợp nhất bằng chứng có cổng theo độ hỗ trợ (support-gated evidence fusion), và các quy kết theo mẫu điển hình và đường truyền được kiểm tra bằng phép xóa.

Tuy nhiên, mỗi thành phần đều có tiền lệ rõ ràng:
- **Dùng các bộ ba hiệp đồng đã gán nhãn làm ngữ cảnh hoặc bộ nhớ:** SynerGPT thực hiện học trong ngữ cảnh (in-context learning) trên các ví dụ hiệp đồng đã biết, với cơ chế chọn ngữ cảnh và một mô hình cơ sở kNN trên biểu diễn nhúng của bộ ba.
- **Dự đoán tăng cường bằng truy xuất, dựa trên ca, với giải thích bằng mẫu điển hình:** điều này đã có cho bài toán liên quan chặt chẽ là tương tác thuốc–thuốc (DDI) (CBR-DDI), và dưới dạng các mô hình hiệp đồng LLM-RAG.
- **Trọng số nhân được học, sinh ra từ đường truyền, cho độ tương đồng diễn giải được:** PIMKL làm điều này.
- **Động lực cốt lõi:** nghiên cứu 'One-hot news' đã chỉ ra rằng các mô hình hiệp đồng chủ yếu khai thác sự đồng biến thiên của nhãn (label co-variation) giữa các dòng tế bào và các cặp thuốc, đây chính là điều mà nhánh truy xuất làm cho tường minh.

Do đó, đóng góp ở đây là một sự kết hợp và điều chỉnh không tầm thường, được thiết kế kỹ lưỡng, từ các ý tưởng đã biết (tăng cường bằng truy xuất, kNN hoặc chú ý trên các láng giềng đã gán nhãn, học đa nhân theo đường truyền (pathway multiple-kernel learning)) áp dụng cho bộ chuẩn này. Đây không phải là một cơ chế mới về bản chất. Các phần ít tiền lệ nhất là nhân đường truyền có điều kiện theo cặp thuốc, truy xuất đối tác có dấu, và giao thức kiểm tra trung thực dựa trên phép xóa cho giải thích bằng mẫu điển hình trong dự đoán hiệp đồng.

Một lưu ý về mức cải thiện dự kiến: vì các mô hình hiện có đã khai thác sự đồng biến thiên của nhãn, mức cải thiện AUPR trên phép chia ngẫu nhiên theo bộ ba có thể khiêm tốn.

Tôi chỉ thấy RADDI (DDI tăng cường bằng truy xuất) trong một bản tóm tắt kết quả tìm kiếm, không có đường dẫn, nên không đưa vào làm tài liệu tham khảo.

Các công trình trước gần nhất đã tìm thấy:

- SynerGPT: In-Context Learning for Personalized Drug Synergy Prediction and Drug Design (2023) https://arxiv.org/abs/2307.11694: Trùng lặp về mặt khái niệm cao: đây là tiền lệ gần nhất. Một transformer dự đoán hiệp đồng cho một bộ ba truy vấn bằng cách lấy điều kiện trên một tập các bộ ba hiệp đồng đã biết, đã gán nhãn trong cùng ngữ cảnh dòng tế bào, hoạt động giống như một bộ nhớ truy xuất được học, và nó tối ưu hóa việc chọn ví dụ ngữ cảnh nào. Nó cũng có một mô hình cơ sở kNN trên biểu diễn nhúng (drug1, drug2, cell). Nó không dùng nhân tế bào phân rã theo đường truyền có điều kiện theo cặp, nhân đối tác có dấu, phép hợp nhất với một GNN tham số, hay giải thích bằng mẫu điển hình được kiểm tra bằng phép xóa.
- One-hot news: drug synergy models shortcut molecular features (bioRxiv 2025 / Bioinformatics) (2025) https://www.biorxiv.org/content/10.1101/2025.04.18.649584.full.pdf: Ủng hộ động lực hơn là phương pháp. Nghiên cứu cho thấy các mô hình hiệp đồng đã công bố chủ yếu hoạt động như phép tra cứu theo định danh (identifier lookups), khai thác sự đồng biến thiên của nhãn giữa các thuốc và dòng tế bào. Đây chính là sự ghi nhớ ngầm mà PathKNN-Syn sẽ làm cho tường minh. Điều đó cũng có nghĩa là mức cải thiện AUPR từ truy xuất tường minh trên phép chia ngẫu nhiên theo bộ ba có thể nhỏ hơn kỳ vọng, vì các mô hình tham số đã nắm bắt được phần lớn tín hiệu này.

<a id="s2"></a>
## S2 · độ mới 6 · PathX-Comp: một tensor tương tác chéo (crosstalk tensor) trên các đường truyền KEGG, chấm điểm mức độ các đường truyền mà hai thuốc nhắm tới bổ sung cho nhau (complement) trong một dòng tế bào (cell line) cụ thể, được thêm vào DSimSynergy như một số hạng hiệp đồng có sẵn và diễn giải được

_Ánh xạ các đích tác dụng DrugBank của mỗi thuốc lên các đường truyền KEGG và đọc mức hoạt động đường truyền (pathway activity) của dòng tế bào từ dữ liệu biểu hiện L1000. Sau đó, một ma trận tương tác chéo giữa các cặp đường truyền, đối xứng, thưa (sparse) và chỉ giới hạn ở các đường truyền cách nhau trong phạm vi 2 bước nhảy (hops), sẽ chấm điểm mức độ bổ sung giữa các đường truyền của hai thuốc trong tế bào đó. Điểm này được cộng vào logit của DSimSynergy, nên mô hình cho ra các quy kết chính xác theo cặp đường truyền thay vì giải thích sau sự việc bằng SHAP và ORA._

### Động lực (Motivation)

Các hạn chế được giải quyết:
- **L7:** GCN của DSimSynergy làm trơn (smooths) đặc trưng về phía các thuốc tương đồng, nhưng độ tương đồng thuốc chỉ tương quan yếu với hiệp đồng (PCC khoảng 0.2).
- **L4 và L5:** chính lời giải thích của bài báo, "mạng bổ sung đường truyền (pathway complementarity network)", được tìm ra sau khi huấn luyện. SHAP được tính tương quan với biểu hiện, các gen có |PCC|>0.5 được đưa vào phân tích tăng cường quá mức (ORA) KEGG, rồi một mạng tương tác chéo đường truyền được xem xét thủ công. Không phần nào trong số này là cơ chế bên trong mô hình, và không phần nào được kiểm tra tính trung thực.
- **L2:** hiệp đồng chỉ được đưa vào thông qua ghép nối rồi đến MLP. Với khoảng 3% dương tính, MLP phải học ngầm định những cặp đích tác dụng và những ngữ cảnh tế bào nào tương tác với nhau, nên thứ hạng của các dương tính (AUPR) bị ảnh hưởng.

Ý tưởng là đưa trực tiếp giả thuyết do chính các tác giả đề xuất vào mô hình. Hai thuốc hiệp đồng khi chúng tác động lên các đường truyền khác nhau nhưng có kết nối và đang hoạt động trong dòng tế bào, và dư thừa (redundant) (thường đối kháng (antagonistic)) khi tác động lên cùng một đường truyền. Chúng tôi biểu diễn điều này bằng một dạng song tuyến tính (bilinear form) tường minh trên các đường truyền, được điều biến theo tế bào. Thiên kiến quy nạp (inductive bias) này mạnh và ít tham số, có lợi cho lớp dương tính hiếm. Dự đoán cũng phân rã chính xác thành các đóng góp theo cặp đường truyền, có thể kiểm tra bằng phép xóa.

### Phương pháp (Method)

**Đầu vào**, tất cả được tính trước, không dùng thông tin nhãn:
- Ma trận nhị phân thuốc–đích tác dụng T (D×G), từ dữ liệu DrugBank đã dùng cho mạng BP.
- Bộ gen đường truyền KEGG ở người (MSigDB c2.cp.kegg, legacy và medicus), giữ các đường truyền có ít nhất 1 đích tác dụng trong số 521 thuốc và ít nhất 3 trong số 949 gen L1000. Còn lại P ≈ 150–250 đường truyền.
- Ma trận thành viên (membership matrices): M (P×G) trên tất cả gen, và M_L (P×949) trên các gen L1000.
- Đồ thị đường truyền Â (P×P): đường truyền p và q được nối nếu hệ số Jaccard giữa các bộ gen lớn hơn 0.05 hoặc KEGG liệt kê một liên kết bản đồ–bản đồ (map-to-map link). Â được chuẩn hóa đối xứng (symmetric-normalised).
- Mặt nạ bước nhảy (hop masks): H0 = I, H1 = 1 bước, H2 = đúng 2 bước.

**1) Mức tác động của thuốc lên đường truyền (drug–pathway engagement).**
- Độ phủ thô (raw coverage): c_A = (M T_Aᵀ) / sqrt(|G_p|), sau đó lan truyền sang các đường truyền lân cận: c̃_A = (I + γÂ)c_A, với γ = 0.5.
- Mức tác động: e_A = softplus(w_e ⊙ c̃_A + V h_A), trong đó h_A là biểu diễn nhúng thuốc của DSimSynergy (BP-GCN ‖ ATC-GCN ‖ GAT), V là ma trận P×dim, và w_e là hệ số tỷ lệ theo từng đường truyền được học, khởi tạo bằng 1.
- Phạt L1 λ_V‖V‖₁ (λ_V = 1e-3) giữ cho mức tác động bám vào các đích tác dụng đã biết. V h_A chỉ có thể bổ sung mức tác động đường truyền mà đặc trưng của thuốc và các láng giềng tương đồng của nó ủng hộ.

**2) Mức hoạt động đường truyền của tế bào (cell pathway activity).**
- m_c = σ((W_m ⊙ M_L) x_c + b_m), trong đó x_c là biểu hiện L1000 log2(TPM+1) đã chuẩn hóa z.
- W_m là ma trận trọng số gen-trong-đường-truyền có thể học, bị che theo quan hệ thành viên, khởi tạo bằng 1/|G_p∩L1000|, nên ban đầu nó là điểm trung bình của đường truyền.

**3) Ma trận tương tác chéo có cấu trúc theo bước nhảy (hop-structured crosstalk matrix).**
- K = Σ_{k=0..2} H_k ⊙ (S_k + S_kᵀ)/2. Các S_k là ma trận P×P có thể học, chỉ có phần tử trên các cạnh cách k bước, nên số tham số xấp xỉ số cạnh (vài nghìn).
- Khởi tạo: đường chéo (k=0) bắt đầu ở −0.1, là tiên nghiệm dư thừa (redundancy prior); các phần tử k=1 và k=2 bắt đầu ở +0.05, là tiên nghiệm bổ sung (complementarity prior). Tất cả các dấu đều được tự do thay đổi.
- Phạt L1 λ_K‖K‖₁ (λ_K = 1e-4) giữ cho K thưa.

**4) Logit bổ sung (complementarity logit)**, đối xứng theo A và B theo cấu trúc:
- s(A,B,c) = Σ_{p,q} (e_A ⊙ m_c)_p K_pq (e_B ⊙ m_c)_q = ẽ_Aᵀ K ẽ_B.
- Áp dụng dropout đường truyền (pathway dropout) 0.1 lên ẽ khi huấn luyện.

**5) Logit cuối cùng:** z = z_DSim(A,B,c) + β·s(A,B,c), với β là vô hướng có thể học, khởi tạo bằng 1. z_DSim là đầu concat+MLP giữ nguyên (logit của lớp hiệp đồng).
- Hàm mất mát: cross-entropy có trọng số theo lớp của bài báo, cộng λ_K‖K‖₁ + λ_V‖V‖₁.
- Bộ tối ưu (optimiser) và phép chia giống bài báo: Adam lr 1e-4, batch 512, checkpoint chọn theo F1 kiểm định, cùng phép chia.

**6) Giải thích.** Các giải thích này là chính xác đối với nhánh bổ sung:
- Mỗi cặp đường truyền nhận một đóng góp φ_pq = β ẽ_A,p K_pq ẽ_B,q, và tổng của chúng bằng logit của nhánh.
- Quy kết ở mức đường truyền: φ_p = Σ_q (φ_pq + φ_qp)/2.
- Quy kết ở mức gen bên trong một đường truyền suy ra từ ánh xạ tuyến tính có mặt nạ, với gradient×đầu vào (gradient×input) chính xác trên W_m qua σ.
- Đầu ra toàn cục: K đã học, cho ra các cạnh tương tác chéo có dấu mà mô hình thực sự dùng, và các cặp được điều biến theo tế bào đứng sau các bộ ba hiệp đồng xếp hạng cao nhất.

**7) Giao thức kiểm tra tính trung thực** (trên bộ phân loại, tập kiểm tra giữ lại, chỉ để báo cáo):
- Đường cong xóa: che top-k cặp đường truyền theo |φ| (đặt ẽ_p = 0 hoặc K_pq = 0) và theo dõi mức giảm của xác suất dự đoán và của AUPR. So sánh với che ngẫu nhiên và với cùng số đường truyền được chọn bởi SHAP+ORA của mô hình cơ sở.
- Kiểm tra hợp lý với K ngẫu nhiên hóa.
- Tỷ phần của nhánh (branch share): Var(βs)/Var(z) trên các bộ ba kiểm tra.

**Các thí nghiệm loại bỏ nhằm cô lập cơ chế:**
- (a) Mô hình cơ sở.
- (b) Nhánh với K chỉ có đường chéo, tức là dư thừa mà không có tương tác chéo.
- (c) K dày (dense) và hạng thấp (low-rank) (r = 16), không có tiên nghiệm bước nhảy KEGG.
- (d) Không có m_c, tức là không có ngữ cảnh tế bào.
- (e) Nhãn bộ gen bị xáo trộn giữa các đường truyền.

**Siêu tham số (hyperparameters) mặc định:** γ = 0.5, λ_K = 1e-4, λ_V = 1e-3, dropout đường truyền 0.1, β₀ = 1, P ≈ 200.

### Các hạn chế được giải quyết

L7, L4, L2, L5, L3

### Tuyên bố về độ mới (Novelty claim)

Yếu tố mới là một ma trận tương tác chéo có dấu, được học trên các cặp đường truyền, giới hạn ở các đường truyền cách nhau trong vòng 2 bước trên đồ thị đường truyền KEGG và được điều biến bởi mức hoạt động đường truyền của tế bào. Nó biến "mạng bổ sung đường truyền" hậu nghiệm của DSimSynergy (và các giải thích kiểu ORA tương tự) thành một số hạng chấm điểm đối xứng bên trong mô hình mà các giải thích của nó là chính xác. Các công trình trước khác ở chỗ:
- Các mô hình hiệp đồng có thông tin đường truyền (pathway-informed) (ví dụ DeepTraSynergy, các biến thể TranSynergy dựa trên đường truyền, các mô hình tổ hợp (ensembles) EXPRESS/Janizek) dùng đường truyền làm đặc trưng đầu vào hoặc làm bản tóm tắt hậu nghiệm.
- Các đầu song tuyến tính và ba tuyến tính, kể cả ứng viên S0, tương tác trong một không gian ẩn (latent space) không có ý nghĩa sinh học.
- Truy xuất với nhân đường truyền (S1) so sánh các dòng tế bào với nhau. Nó không mô hình hóa việc đường truyền nào của thuốc A tương tác với đường truyền nào của thuốc B.

Ở đây, bản thân không gian tương tác là cơ sở (basis) KEGG, với tiên nghiệm về dư thừa (đường chéo) so với bổ sung (1–2 bước). Các cạnh được học có thể đọc trực tiếp như các giả thuyết cơ chế có thể kiểm chứng và được kiểm tra bằng các phép thử xóa.

### Kế hoạch triển khai (Implementation plan)

1. **Chuẩn bị dữ liệu (script mới, ví dụ Code/prep_pathways.py).**
   - Nạp các đích tác dụng DrugBank đã dùng để xây mạng BP, và file GMT KEGG từ MSigDB (bản sao cục bộ; đưa kèm vào kho mã (vendor) nếu không có internet).
   - Xây T, M, M_L (căn theo thứ tự 949 gen của ma trận biểu hiện tế bào), Â, và các mặt nạ bước nhảy H1, H2 (dưới dạng danh sách chỉ số cạnh thưa (sparse edge-index lists)).
   - Lưu tất cả dưới dạng .npz. Bước này không dùng nhãn hiệp đồng.
2. **Mô hình (file mô hình DSimSynergy).** Thêm một nn.Module `PathComp` gồm:
   - các bộ đệm đã đăng ký (registered buffers): c̃ (D×P, tính trước), mặt nạ M_L, và các danh sách cạnh;
   - tham số: w_e, V (Linear dim→P, không có bias), W_m (dưới dạng giá trị trên các phần tử có mặt nạ, tức là một Linear thưa), b_m, trọng số cạnh theo từng bước nhảy, β;
   - forward(hA, hB, x_c, idxA, idxB): dựng K dày bằng cách rải (scatter) trọng số cạnh vào ma trận P×P rồi đối xứng hóa, sau đó trả về `s = einsum('bp,pq,bq->b', eA*m, K, eB*m)`.
   - Trong forward chính, dùng lại các biểu diễn nhúng thuốc đã được BP-GCN, ATC-GCN và GAT tính, và cộng β·s vào logit của lớp hiệp đồng (với đầu ra CE 2 lớp, cộng +βs/2 vào lớp 1 và −βs/2 vào lớp 0).
3. **Script huấn luyện.**
   - Thêm các phạt L1 vào hàm mất mát. Giữ nguyên phép chia (random_state 0 và 42), trọng số lớp, lr 1e-4, batch 512 và cách lưu checkpoint dựa trên F1.
   - Ghi log β và tỷ phần của nhánh.
   - Lượt chạy sàng lọc: tập gấp 1, 50 epoch. Lượt chạy đầy đủ: 5 tập gấp, mỗi tập khoảng 200 epoch. Nhánh này thêm dưới 1 triệu tham số và phép einsum P×P không đáng kể so với GAT.
4. **Script giải thích (mới, Code/explain_pathcomp.py).**
   - Tính φ_pq cho từng bộ ba kiểm tra, xếp hạng |φ| toàn cục và danh sách cạnh của K, lưu dạng CSV để vẽ mạng.
   - Chạy đường cong xóa/chèn so với che ngẫu nhiên và so với các đường truyền SHAP+ORA của mô hình cơ sở, và kiểm tra K ngẫu nhiên hóa.
   - Giữ phân tích gen SHAP hiện có, giờ chạy trên chính bộ phân loại.
5. **Cờ cho thí nghiệm loại bỏ:** `--k_mode {hop,diag,lowrank}`, `--no_cell_mod`, `--shuffle_genesets`.

### Tác động dự kiến (Expected effect)

**Tập kiểm tra DrugCombDB giữ lại, trung bình trên 5 tập gấp:**
- AUPR: 0.77 → khoảng 0.79–0.81. Mức cải thiện sẽ lớn nhất ở các cặp hiệp đồng mà hai thuốc có độ tương đồng BP/ATC thấp, tức là những cặp dựa vào các đường truyền bổ sung. Chúng tôi sẽ báo cáo AUPR phân tầng theo ngũ phân vị (quintile) độ tương đồng.
- F1: 0.74 → khoảng 0.75–0.77.
- AUROC: 0.96 → khoảng 0.96–0.97.
- ACC: khoảng 0.98, không đổi.

**Sàng lọc trên tập gấp 1:** nhánh này phải vượt thí nghiệm loại bỏ (b) (chỉ đường chéo) và (e) (bộ gen xáo trộn) ít nhất 0.01 AUPR. Điều đó sẽ cho thấy mức cải thiện đến từ tiên nghiệm tương tác chéo, chứ không phải từ tham số tăng thêm.

**Khả năng giải thích:** loại bỏ 5% cặp đường truyền hàng đầu sẽ làm giảm xác suất dự đoán nhiều hơn hẳn so với loại bỏ ngẫu nhiên (mục tiêu: mức giảm ít nhất gấp 3 lần). Nó cũng phải vượt một tập đường truyền SHAP+ORA cùng kích thước của mô hình cơ sở. K đã học phải tìm lại được các trục bổ sung đã biết, như MAPK–PI3K-Akt và các láng giềng của cơ chế kháng EGFR-TKI (EGFR-TKI resistance).

### Rủi ro (Risks)

- **Nhánh bị bỏ qua.** Trên phép chia ngẫu nhiên, việc z_DSim ghi nhớ định danh thuốc chiếm ưu thế; điều này sẽ biểu hiện thành β→0, tỷ phần nhánh dưới 5% và AUPR không thay đổi. Giảm thiểu: khởi động (warm up) chỉ với nhánh trong 5 epoch, hoặc áp dụng dropout lên z_DSim trong các epoch đầu.
- **Độ phủ đích tác dụng thưa hoặc nhiễu** trong KEGG đối với một số thuốc (ví dụ các hóa trị liệu có đích là DNA). V h_A bù đắp một phần, nhưng giải thích cho các thuốc này sẽ dựa nhiều hơn vào V; chúng tôi báo cáo riêng tỷ phần này.
- **File GMT KEGG có thể không có sẵn khi ngoại tuyến.** Phương án dự phòng: các bộ GO-BP đã có trên đĩa, phân cụm thành khoảng 200 mô-đun.
- **K quá khớp (overfits)**, cho ra các cạnh không ổn định giữa các tập gấp. Chúng tôi kiểm tra bằng mức trùng lặp của thứ hạng cạnh giữa các tập gấp và điều chỉnh λ_K nếu cần.
- **Mức cải thiện nằm trong phương sai giữa các tập gấp.** Lượt chạy sàng lọc có thể trông tích cực hay tiêu cực do ngẫu nhiên, nên chúng tôi xác nhận bằng cả 5 tập gấp và các kiểm định ghép cặp (paired tests) so với các thí nghiệm loại bỏ.
- **Giải thích chỉ trung thực một phần.** Quy kết đường truyền chỉ chính xác cho nhánh. Nếu phần lớn logit đến từ z_DSim, giải thích chỉ bao quát một phần quyết định; chỉ số tỷ phần nhánh làm cho điều này hiển thị rõ.

### Kiểm tra độ mới (Novelty check)

Giả thuyết sinh học không mới. Các thuốc tác động lên các đường truyền khác nhau nhưng có kết nối thì hiệp đồng, còn tác động lên cùng một đường truyền thì dư thừa. Chen và cộng sự 2016 đã dùng quy tắc này trong một mạng tương tác đường truyền–đường truyền để dự đoán hiệp đồng, SynPathy tìm ra nó qua độ gần đường truyền (pathway proximity), và DIPx dùng điểm kích hoạt đường truyền (pathway activation scores) xây dựng từ tương tác đích tác dụng. Các mô hình sâu có thông tin đường truyền (TranSynergy, SynPathy, PathSynergy) dùng đường truyền làm đầu vào hoặc làm giải thích hậu nghiệm. Các đầu song tuyến tính (ví dụ mô hình chú ý hạng thấp cộng bộ dự đoán song tuyến tính) là tiêu chuẩn nhưng hoạt động trong không gian ẩn.

Tôi không tìm thấy bài báo nào đặt một ma trận tương tác chéo đường truyền×đường truyền được học, có dấu và thưa vào bên trong một GNN hiệp đồng. Phiên bản của ý tưởng này giới hạn ma trận ở các cạnh KEGG 0/1/2 bước với tiên nghiệm dư thừa hoặc bổ sung, gắn cổng bởi mức hoạt động đường truyền được học của dòng tế bào, thêm nó vào như một số hạng logit, và phân rã chính xác thành các đóng góp theo cặp đường truyền được kiểm tra bằng phép xóa. Các tìm kiếm về ma trận tương tác đường truyền–đường truyền có thể học, chú ý chéo (cross-attention) ở mức đường truyền giữa thuốc A và thuốc B, và tensor tương tác chéo đường truyền cho hiệp đồng đều không cho kết quả trùng khớp trực tiếp. Tổng hợp lại, đây là một sự điều chỉnh không tầm thường, biến một kinh nghiệm (heuristic) dược lý mạng (network pharmacology) đã biết thành một đầu song tuyến tính có cấu trúc và diễn giải được. Nó không phải là cơ chế mới về bản chất: các thành phần đều đã biết (dạng song tuyến tính, tham số có cấu trúc đồ thị có mặt nạ, điểm hoạt động đường truyền, kiểm tra trung thực bằng phép xóa), và đóng góp nằm ở sự kết hợp cùng cách đóng khung về tính trung thực. Do đó cho điểm 6.

Lưu ý: tôi không thể loại trừ các bản tiền ấn phẩm (preprints) rất gần đây trong 2025–2026 có chú ý theo cặp đường truyền, nhưng không có bài nào xuất hiện khi tìm với nhiều cách diễn đạt khác nhau.

Các công trình trước gần nhất đã tìm thấy:

- Synergy evaluation by a pathway–pathway interaction network: a new way to predict drug combination (2016) https://pubs.rsc.org/en/content/articlelanding/2016/mb/c5mb00599j: Tiền lệ gần nhất về mặt khái niệm. Nó chấm điểm các cặp thuốc bằng cách ánh xạ đích tác dụng của mỗi thuốc vào các đường truyền và dùng một mạng tương tác đường truyền–đường truyền, và nó khẳng định các quy tắc dư thừa và bổ sung là quan trọng (cùng đường truyền qua các đích khác nhau; ít đường truyền nhưng kết nối cao). Cách chấm điểm là cố định và dựa trên mạng: không có ma trận tương tác chéo có dấu được học, không có điều biến theo dòng tế bào và không có mô hình sâu. Vì vậy, giả thuyết cốt lõi của ý tưởng không mới.
- SynPathy: Predicting Drug Synergy through Drug-Associated Pathways Using Deep Learning (2022) https://aacrjournals.org/mcr/article/20/5/762/694641/SynPathy-Predicting-Drug-Synergy-through-Drug: Một mô hình sâu dùng điểm tăng cường (enrichment scores) từ đích tác dụng thuốc đến đường truyền và đặc trưng tế bào làm đầu vào. Phát hiện của nó rằng hiệp đồng tăng lên khi các đường truyền hàng đầu của hai thuốc gần nhau trên mạng PPI chính là giả thuyết bổ sung. Nhưng đường truyền chỉ là đặc trưng đầu vào và được diễn giải sau sự việc. Không có số hạng cặp đường truyền song tuyến tính tường minh được học.

<a id="s3"></a>
## S3 · độ mới 6 · DoseCurve-Syn: một toán tử phi cộng tính (non-additivity operator) được học trong không gian liều (dose space). Hiệp đồng được tính như sai phân hữu hạn bậc hai (second-order finite difference) của các mô-đun đáp ứng đường truyền (pathway response modules) có cổng theo tế bào (cell-gated), được điều khiển bởi các đích tác dụng (targets) của mỗi thuốc.

_Mỗi thuốc được ánh xạ thành một vectơ "liều ức chế đường truyền (pathway-inhibition dose)" không âm (đích tác dụng DrugBank → các đường truyền KEGG/GO, lan truyền qua 1–2 bước trên đồ thị đường truyền, cộng một phần dư (residual) thưa được học từ biểu diễn nhúng của DSimSynergy). Các liều này đi qua các mô-đun đáp ứng có cổng theo tế bào thuộc hai loại: mô-đun ngưỡng lồi (convex threshold modules) (mô-đun "đường vòng/AND (bypass/AND)", chỉ có thể tạo ra hiệp đồng) và mô-đun bão hòa lõm (concave saturating modules) (mô-đun "dư thừa (redundancy)", chỉ có thể tạo ra đối kháng). Sai phân hữu hạn hỗn hợp (mixed finite difference) của chúng F(uA+uB) − F(uA) − F(uB) + F(0) được cộng vào logit của DSimSynergy. Kết quả đối xứng theo cấu trúc và có thiên kiến quy nạp về tương tác kiểu Loewe. Các quy kết của nó là các phép phân rã chính xác theo mô-đun/đường truyền/đích tác dụng, được kiểm tra bằng các phép thử xóa._

### Động lực (Motivation)

Hiệp đồng (Loewe > 10) nghĩa là hiệu ứng kết hợp lệch khỏi tổng của hai hiệu ứng đơn chất (single-agent effects). DSimSynergy không bao giờ biểu diễn độ lệch đó. Nó ghép nối biểu diễn nhúng của từng thuốc với biểu diễn nhúng tế bào và yêu cầu một MLP tự phát hiện tương tác một cách ngầm định, điều này đòi hỏi nhiều dữ liệu khi chỉ ~3% bộ ba là dương tính (L2). Đầu ra của nó phụ thuộc vào thứ tự thuốc và chỉ được đối xứng hóa nhờ tăng cường dữ liệu (augmentation) (L3). Đích tác dụng của thuốc không bao giờ gặp biểu hiện gen của dòng tế bào đang được điều trị, và các giải thích đường truyền là tương quan SHAP–biểu hiện hậu nghiệm rồi đến ORA (L4). Các giải thích đó đến từ một mô hình khác (mô hình hồi quy) và không bao giờ được kiểm tra tính trung thực (L5). GCN cũng làm trơn các thuốc về phía các thuốc tương đồng, dù phát hiện cơ chế của chính các tác giả là hiệp đồng đến từ các đường truyền bổ sung cách nhau 1–2 bước (L7).
Các ứng viên hiện có xử lý tương tác bằng một dạng ba tuyến tính tổng quát (S0), các mẫu điển hình láng giềng gần nhất (S1), hoặc một ma trận tương tác chéo cặp đường truyền được học (S2). Không cái nào có cấu trúc định nghĩa của hiệp đồng: một hàm đáp ứng dùng chung, bão hòa, đặc thù theo tế bào, được đánh giá tại các liều đơn lẻ và tại liều kết hợp, với hiệp đồng được đọc ra như độ cong (curvature) (sai phân bậc hai hỗn hợp) của hàm đó. Trong một toán tử như vậy, một cặp thuốc cộng tính cho tương tác đúng bằng 0. Dấu của tương tác được xác định một cách cơ học: cần cả hai thuốc để vượt ngưỡng thì cho hiệp đồng, còn tác động vào một mô-đun đã bão hòa thì cho đối kháng. Đây là một tiên nghiệm mạnh, ít tham số cho lớp dương tính hiếm. Vì logit là một tổng tường minh của các số hạng mô-đun, các giải thích đến thẳng từ phép tính chứ không phải được tái dựng sau đó.

### Phương pháp (Method)

Ký hiệu. Gen G = L1000 (949) ∪ tất cả gen đích DrugBank của 521 thuốc. Đường truyền k=1..K: các bộ gen KEGG ở người (~186). Nếu không có KEGG, dùng các bộ GO-BP đã dùng cho mạng BP, lọc theo kích thước 15–300 và lấy top K=300 theo độ phủ đích tác dụng. Ma trận thành viên M ∈ {0,1}^{K×|G|}, chuẩn hóa theo hàng thành M̃. Đồ thị đường truyền A_P: độ chồng lấp Jaccard của các bộ gen, 10 láng giềng hàng đầu cho mỗi đường truyền, chuẩn hóa đối xứng.

1) Trạng thái đường truyền của tế bào. x_c là biểu hiện log2(TPM+1) đã chuẩn hóa z (gen đích bị thiếu được đặt bằng 0 và gán một bias theo từng gen được học). Mức hoạt động đường truyền a_c = M̃_{L1000} x_c ∈ R^K. Ngữ cảnh tế bào z_c = LeakyReLU(W_z[a_c ; h_c]), trong đó h_c là biểu diễn nhúng tế bào FCNN hiện có (d=64).

2) Vectơ liều thuốc (không âm, có cổng theo tế bào).
- Tiên nghiệm đích tác dụng: p⁰_A = M̃ t_A, với t_A ∈ {0,1}^{|G|} là các đích DrugBank.
- Lan truyền để mô hình hóa tính bổ sung ở khoảng cách xa: p_A = p⁰_A + α₁ A_P p⁰_A + α₂ A_P² p⁰_A, với α = softplus(được học), khởi tạo 0.5 và 0.25.
- Phần dư được học cho các hiệu ứng bị thiếu hoặc ngoài đích (off-target): r_A = ReLU(W_r e_A), trong đó e_A là biểu diễn nhúng thuốc ghép nối của DSimSynergy (BP-GCN ‖ ATC-GCN ‖ GAT). Phạt L1 λ_r = 1e-3 giữ cho nó thưa.
- Hiệu lực thuốc (drug potency): s_A = softplus(w_s·e_A + b_s).
- Cổng tính dễ tổn thương của tế bào (cell vulnerability gate): g_c = 2σ(W_g z_c) ∈ (0,2)^K, cho biết việc ức chế mỗi đường truyền quan trọng đến mức nào trong tế bào c, đọc từ biểu hiện của tế bào đó.
- Liều: u_A^c = s_A · g_c ⊙ (p_A + r_A) ∈ R^K_{≥0}.
- Kết hợp: cộng nồng độ (concentration addition) trong không gian đường truyền, u_{AB}^c = u_A^c + u_B^c. Phép này đối xứng theo cấu trúc.

3) Các mô-đun đáp ứng (m=1..M, M=64; mỗi loại một nửa). Đầu vào mô-đun y_m(u) = Σ_k W⁺_{mk} u_k, với W⁺ = softplus(Ŵ) và phạt L1 λ_W = 1e-4 để mỗi mô-đun dùng một tập đường truyền thưa.
- Mô-đun lồi "đường vòng/AND": h_m(y) = τ·softplus((y − θ_m)/τ), với τ=0.5 và θ_m có thể học (khởi tạo 1.0). Hiệu ứng của chúng chỉ trở nên lớn khi liều kết hợp vượt ngưỡng, tức là khi cần cả hai thuốc để chặn các con đường dư thừa.
- Mô-đun lõm "dư thừa/bão hòa": h_m(y) = κ_m(1 − exp(−y/κ_m)), với κ_m có thể học (khởi tạo 1.0).
- Tương tác của mô-đun m: Δ_m(A,B,c) = h_m(y_m(u_A+u_B)) − h_m(y_m(u_A)) − h_m(y_m(u_B)) + h_m(0). Vì đầu vào không âm, Δ_m ≥ 0 với mô-đun lồi và Δ_m ≤ 0 với mô-đun lõm. Dấu được cố định bởi loại mô-đun, nên không có dấu nào phải học.
- Trọng số mô-đun đặc thù theo tế bào: ω_{c,m} = softplus(V z_c + b_V)_m ≥ 0.

4) Logit. ℓ(A,B,c) = ½[f(A,B,c) + f(B,A,c)] + β · Σ_m ω_{c,m} Δ_m + b.
- f là đầu concat-MLP giữ nguyên của DSimSynergy. Lấy trung bình trên cả hai thứ tự thuốc làm nó đối xứng, và nó mang các hiệu ứng chính (main effects) của từng thuốc trong từng tế bào.
- β ≥ 0 có thể học, khởi tạo bằng 1.
- Dropout cơ chế (mechanism dropout): với xác suất 0.3 mỗi batch, số hạng f bị bỏ khỏi logit, tức là hàm mất mát được tính trên β·ΣωΔ + b + ½(đầu chỉ có hiệu ứng chính) với phần đặc thù theo cặp của f bị đặt bằng 0. Trong thực hành, f được thay bằng f_main(A,c) + f_main(B,c), một MLP nhỏ trên [e_d ; h_c]. Điều này buộc nhánh cơ chế phải mang thông tin đặc thù theo cặp thay vì bị bỏ qua.

5) Hàm mất mát. BCE có trọng số theo lớp, như trong bộ chuẩn, cộng λ_r‖r‖₁ + λ_W‖W⁺‖₁. Không thay đổi gì khác ở hàm mất mát, để mọi mức cải thiện đều có thể quy cho toán tử.
- Hiệu chuẩn tùy chọn (optional calibration), báo cáo như một hàng thí nghiệm loại bỏ riêng: một độ lệch logit vô hướng (scalar logit offset) được khớp chỉ trên tập gấp kiểm định, tối đa hóa F1 kiểm định.

6) Quy kết có sẵn (chính xác, tính cho chính bộ phân loại).
- Mức mô-đun: đóng góp logit của mô-đun m là β ω_{c,m} Δ_m. Tổng của chúng đúng bằng phần cơ chế của logit.
- Mức đường truyền và thuốc: với mỗi mô-đun, h là hàm một chiều theo y. Phép phân rã theo đường đi (path decomposition) chính xác dọc đường thẳng từ 0 đến y cho mỗi đường truyền một phần của Δ_m từ W⁺_{mk}(u_{A,k}+u_{B,k}), chia theo tỷ phần của thuốc A so với thuốc B. Phần của đường truyền sau đó được ánh xạ ngược về từng gen đích qua M̃ t_A và các số hạng bước nhảy. Kết quả có dạng "đích EGFR của thuốc A (đường truyền ErbB) và đích PIK3CA của thuốc B (PI3K-Akt) cùng đẩy mô-đun đường vòng 17 vượt ngưỡng trong tế bào c".
- Mức tế bào: ∂ω/∂x_c và g_c xác định các gen biểu hiện khiến mô-đun hoặc đường truyền trở nên quyết định trong tế bào đó. Khác với quy trình của bài báo, không cần bước tương quan cộng ORA.
- Mức cấu trúc con (substructure): giữ các quy kết SHAP hoặc GAT trên f, nên phân tích mức nguyên tử của bài báo vẫn dùng được.

7) Giao thức kiểm tra tính trung thực, báo cáo trên tập kiểm tra giữ lại.
- Đường cong xóa: đặt bằng 0 top-k mô-đun/đường truyền (k = 1, 3, 5, 10) và so với che ngẫu nhiên k phần tử, đo mức giảm của xác suất dự đoán và của AUPR.
- Phản thực tế loại bỏ đích (target knock-out counterfactuals): bỏ một đích duy nhất khỏi t_A.
- Kiểm tra hợp lý: ngẫu nhiên hóa lại W⁺ và V và xác nhận các quy kết thay đổi.
- Tính nhất quán theo thứ tự: quy kết cho (A,B) và (B,A) phải giống hệt nhau (ở đây là chính xác, theo cấu trúc).

Mặc định: Adam lr 1e-4 (theo bộ chuẩn), batch 512, K≈186 (KEGG) hoặc 300, M=64, τ=0.5, 2 bước nhảy, dropout cơ chế 0.3, λ_r=1e-3, λ_W=1e-4. Checkpoint chọn theo F1 kiểm định theo giao thức. Chi phí tính toán thêm khoảng 4 lần đánh giá một lớp K×M cho mỗi bộ ba, không đáng kể.

### Các hạn chế được giải quyết

L2, L3, L4, L5, L7, L1

### Tuyên bố về độ mới (Novelty claim)

Theo hiểu biết của chúng tôi, chưa có bộ dự đoán hiệp đồng sâu đã công bố nào xây dựng logit phân loại từ một sai phân hữu hạn bậc hai hỗn hợp, F(uA+uB) − F(uA) − F(uB) + F(0), của một hàm đáp ứng dùng chung, có điều kiện theo tế bào, trên một không gian liều-đường truyền dựa trên đích tác dụng thuốc. Trong toán tử này, loại độ cong của mỗi mô-đun (ngưỡng lồi so với bão hòa lõm) quyết định dấu của tương tác. Điều này biến hai ý tưởng thành một thiên kiến quy nạp khả vi, có thể huấn luyện: cấu trúc định nghĩa của hiệp đồng theo mô hình tham chiếu (reference-model synergy) (độ lệch khỏi tính cộng tính liều (dose additivity)), và chính giả thuyết "mạng bổ sung đường truyền" hậu nghiệm của bài báo (thông qua lan truyền 1–2 bước và các mô-đun đường vòng kiểu AND).

Ý tưởng này khác các ứng viên hiện có ở những điểm sau:
- S0: không có tensor tương tác ba tuyến tính tự do. Tương tác chỉ tồn tại thông qua độ cong của đáp ứng.
- S1: không có truy xuất.
- S2: không có tham số theo cặp đường truyền×đường truyền nào được học. Hiệu ứng cặp nảy sinh từ các phi tuyến mô-đun dùng chung, nên số tham số tăng theo K·M thay vì K².
- DeepSynergy, DeepDDS, JointSyn và HyperGraphSynergy đều dùng ghép nối hoặc hợp nhất bằng chú ý.
- Các mô hình cơ chế (mechanistic models) (ví dụ mô phỏng tín hiệu Boolean/ODE) không được huấn luyện đầu-cuối (end-to-end) trên dữ liệu hiệp đồng sàng lọc thông lượng cao (HTS), và không cung cấp quy kết cộng tính chính xác.

Các giải thích phân rã chính xác logit của bộ phân loại, bất biến theo thứ tự theo cấu trúc, và được kiểm tra bằng các phép thử xóa.

### Kế hoạch triển khai (Implementation plan)

1) Script chuẩn bị dữ liệu (mới, prep_pathway_dose.py). Nạp bảng đích tác dụng DrugBank và các bộ gen GO-BP đã dùng để xây mạng tương đồng BP (trong Code/Data hoặc script xây dựng độ tương đồng). Nạp các bộ gen KEGG: file GMT MSigDB c2.cp.kegg nếu có, nếu không thì dùng phương án dự phòng GO-BP. Xây dựng và lưu:
- tập gen G;
- M̃ (thưa);
- A_P (đồ thị Jaccard 10 láng giềng hàng đầu của đường truyền, đã chuẩn hóa);
- ma trận đích tác dụng T ∈ {0,1}^{521×|G|};
- biểu hiện tế bào cho G (từ ma trận DepMap 24Q4 trong kho mã; gen đích ngoài L1000 lấy từ ma trận đầy đủ các gen mã hóa protein nếu có, nếu không thì che đi).
Lưu tất cả dưới dạng file .pt.

2) Mô hình (mô-đun mới pathway_dose.py, lớp DoseCurveHead). Tham số: trọng số bước nhảy α, W_r, w_s/b_s, W_z, W_g, Ŵ (M×K), θ, κ, V, β. forward(eA, eB, idxA, idxB, x_c, h_c) trả về logit cơ chế và một dict chứa Δ_m, ω, uA, uB để quy kết. Cài đặt h(0) theo dạng giải tích. Dùng float32 và kẹp (clamp) θ, κ để luôn dương.

3) Sửa lớp mô hình DSimSynergy chính:
- đưa ra ngoài biểu diễn nhúng của từng thuốc e_d (đầu ra BP-GCN ‖ ATC-GCN ‖ GAT trước khi ghép nối);
- tính đầu hiện có trên cả hai thứ tự và lấy trung bình;
- thêm MLP f_main cho dropout cơ chế;
- cộng đầu ra của DoseCurveHead vào logit;
- thêm các số hạng L1 vào hàm mất mát trong vòng lặp huấn luyện.
Giữ CE có trọng số theo lớp (viết dưới dạng CE 2-logit [0, ℓ] để luồng mã hiện có không đổi).

4) Script huấn luyện: không thay đổi phép chia (phép chia kiểm tra random_state 0, StratifiedKFold random_state 42). Thêm cờ --mech {on,off} và tỷ lệ dropout cơ chế. Sàng lọc nhanh dùng tập gấp 1 với 50 epoch. Các thí nghiệm loại bỏ:
- (a) mô hình cơ sở;
- (b) chỉ mô hình cơ sở đã đối xứng hóa;
- (c) + DoseCurve không có bước nhảy;
- (d) đầy đủ;
- (e) các biến thể chỉ có mô-đun lồi và chỉ có mô-đun lõm;
- (f) + hiệu chuẩn độ lệch logit chỉ trên tập kiểm định.

5) Script giải thích (mới, explain_dosecurve.py):
- phân rã theo mô-đun, đường truyền, đích tác dụng và thuốc cho từng bộ ba;
- bảng tổng hợp mô-đun→đường truyền theo từng cặp thuốc (ví dụ Binimetinib–Brigatinib, để so sánh với bài báo);
- đường cong xóa/chèn so với che ngẫu nhiên;
- phản thực tế loại bỏ đích;
- kiểm tra hợp lý bằng ngẫu nhiên hóa trọng số;
- SHAP trên f, giữ lại cho phân tích gen và nguyên tử để liên tục với bài báo.

6) Bộ chuẩn đầy đủ: 5 tập gấp, mỗi tập khoảng 200–300 epoch. Vừa trong dưới 50 GB, vì mô hình nhỏ.

### Tác động dự kiến (Expected effect)

Tập kiểm tra nội bộ, trung bình trên 5 tập gấp:
- AUPR: từ 0.77 lên khoảng 0.79–0.81. Tiên nghiệm phi cộng tính chủ yếu giúp xếp hạng các dương tính hiếm mà hai thuốc riêng lẻ không có gì nổi bật nhưng tác động lên các đường truyền bổ sung trong tế bào đó.
- F1: từ 0.74 lên khoảng 0.76–0.78. Đầu đã đối xứng hóa làm giảm phương sai, và hiệu chuẩn độ lệch tùy chọn chỉ trên tập kiểm định thêm ~0.01–0.02 với quy tắc 0.5.
- AUROC: tăng khoảng +0.005 (0.96 → ~0.965).
- ACC: không đổi ở ~0.98, vì đã bão hòa.

Trong thí nghiệm loại bỏ, mô hình đầy đủ dự kiến vượt mô hình cơ sở đã đối xứng hóa ít nhất +0.015 AUPR, và việc bỏ bước nhảy hoặc một loại mô-đun dự kiến làm mất một phần mức cải thiện.

Khả năng giải thích: xóa top-3 mô-đun được quy kết dự kiến làm giảm xác suất hiệp đồng dự đoán trung bình của các dương tính thật nhiều hơn hẳn so với xóa ngẫu nhiên 3 mô-đun (mục tiêu: mức giảm lớn hơn ≥3 lần). Các quy kết bất biến chính xác theo thứ tự. Giải thích đường truyền giờ đến từ chính bộ phân loại, nên các phát hiện kiểu p53/PI3K-Akt/kháng EGFR-TKI của bài báo có thể được kiểm tra trực tiếp.

### Rủi ro (Risks)

1) Đầu cơ sở f hấp thụ toàn bộ tín hiệu và β co lại, khiến nhánh cơ chế chỉ mang tính trang trí. Dấu hiệu sẽ là tỷ phần phương sai logit từ ΣωΔ thấp và thí nghiệm loại bỏ (c/d) ≈ (b). Giảm thiểu: dropout cơ chế, và báo cáo tỷ phần phương sai.
2) Chú thích đích tác dụng DrugBank thưa hoặc sai (hoặc đích nằm ngoài ma trận biểu hiện) khiến p⁰ không mang thông tin. Khi đó phần dư được học r_A sẽ chiếm ưu thế, làm suy yếu khả năng diễn giải sinh học. Theo dõi ‖r‖/‖p‖.
3) Mô-đun ngưỡng có θ quá cao cho gradient bằng 0. Theo dõi các mô-đun chết (dead modules) (Δ≡0); khởi tạo lại θ từ các phân vị (quantiles) của y trên tập huấn luyện.
4) Các bộ ba đảo chiều (B,A,c) của các cặp kiểm tra có mặt trong tập huấn luyện do phép tăng cường dữ liệu của bài báo được giữ nguyên theo quy định. Đối xứng hóa loại bỏ nhiễu do thứ tự nhưng không khắc phục điều này, nên các con số tuyệt đối vẫn so sánh được với bài báo.
5) Chỉ có ~83 dòng tế bào, nên các cổng tế bào g_c và ω_c có thể quá khớp. Điều này sẽ biểu hiện thành khoảng cách huấn luyện–kiểm định lớn hơn. Giảm thiểu: suy giảm trọng số (weight decay) trên W_g và V.
6) Mức cải thiện có thể nhỏ (<0.01 AUPR) trên phép chia ngẫu nhiên, nơi việc ghi nhớ cặp thuốc đã hoạt động tốt. Khi đó lợi ích chính sẽ là các giải thích trung thực và có thể là hành vi tốt hơn trên PairOut/DrugOut.

### Kiểm tra độ mới (Novelty check)

Tiền lệ gần nhất là ComboNet (Jin và cộng sự 2020). Nó đã đánh giá một hàm đáp ứng dùng chung trên vectơ đích của từng thuốc và trên vectơ đích kết hợp, và đọc ra hiệp đồng từ độ lệch so với kỳ vọng cộng tính (Bliss), kèm giải thích ở mức đích tác dụng. Công thức đó lấy từ một đoạn trích kết quả tìm kiếm; không đọc được file PDF. TranSynergy bao quát việc hồ sơ đích tác dụng (target profiles) gặp biểu hiện tế bào, với giải thích đường truyền từ phân tích bộ gen SHAP hậu nghiệm. DeepSynBa và DDoS đưa cấu trúc Loewe hoặc liều–đáp ứng (dose-response) vào mô hình sâu. CPA cộng biểu diễn nhúng thuốc trong không gian ẩn. Các yếu tố mới không thấy trong bài báo nào: cộng nồng độ của các "liều" đường truyền được lan truyền 1–2 bước trên đồ thị đường truyền; sai phân bậc hai hỗn hợp chính xác F(uA+uB)-F(uA)-F(uB)+F(0), cho đúng bằng 0 với các cặp cộng tính; mô-đun ngưỡng lồi chỉ có thể cho hiệp đồng và mô-đun bão hòa lõm chỉ có thể cho đối kháng; trọng số mô-đun có cổng theo tế bào; và một phép phân rã chính xác, bất biến theo thứ tự của chính logit bộ phân loại, được kiểm tra bằng các phép thử xóa. Tổng hợp lại, đây là sự kết hợp và điều chỉnh không tầm thường của các ý tưởng đã biết, không phải một cơ chế hoàn toàn mới. Điểm 6.

Các công trình trước gần nhất đã tìm thấy:

- Discovering Synergistic Drug Combinations for COVID with Biological Bottleneck Models (ComboNet) (2020) https://arxiv.org/abs/2011.04651: Trùng cao ở cơ chế cốt lõi. Mô-đun thuốc→đích và mô-đun đích→bệnh được học đồng thời với hiệp đồng; một 'lớp Bliss (Bliss layer)' kết hợp các vectơ đích dự đoán, và hiệp đồng là độ lệch so với kỳ vọng tính từ dự đoán đơn thuốc (công thức lấy từ đoạn trích tìm kiếm, chưa đọc PDF). Có giải thích ở mức đích. Không có không gian liều-đường truyền, cổng theo tế bào, mô-đun lồi/lõm có dấu cố định, hay quy kết chính xác.
- TranSynergy: Mechanism-driven interpretable deep neural network for the synergistic prediction and pathway deconvolution of drug combinations (2021) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7906476/: Trùng trung bình. Hồ sơ đích tác dụng thuốc lan trên một mạng tương tác protein gặp biểu hiện dòng tế bào của cùng các gen; giải thích đường truyền đến từ phân tích bộ gen SHAP hậu nghiệm (SA-GSEA). Không có toán tử phi cộng tính.

<a id="s4"></a>
## S4 · độ mới 6 · FlipPath-Syn: huấn luyện với phản thực tế ghép cặp (matched-counterfactual training), bộ mã hóa tế bào (cell encoder) có cổng đường truyền dạng sparsemax, và giải thích phản thực tế bằng hoán đổi đường truyền tối thiểu (minimal pathway-swap counterfactual explanations)

_Huấn luyện DSimSynergy đối chiếu với các bộ ba huấn luyện phản thực tế ghép cặp: cùng cặp thuốc ở một dòng tế bào khác có nhãn ngược lại, hoặc cùng dòng tế bào và một thuốc chung với một đối tác có nhãn ngược lại. Mã hóa mỗi dòng tế bào qua các mô-đun đường truyền KEGG được gắn cổng bởi một sparsemax có điều kiện theo cặp thuốc, để các đường truyền có cổng bằng 0 được chứng minh là không có tác động. Giải thích mỗi dự đoán bằng tập đường truyền nhỏ nhất mà, khi được hoán đổi từ một dòng tế bào đối kháng ghép cặp, làm lật (flip) quyết định của bộ phân loại._

### Động lực (Motivation)

Trên phép chia ngẫu nhiên, phần lớn các cặp thuốc trong DrugCombDB được thử nghiệm trên nhiều dòng tế bào. Các dương tính khó (hard positives) là những cặp chỉ hiệp đồng ở một vài dòng tế bào trong số đó, tức là hiệp đồng đặc thù theo ngữ cảnh (context-specific synergy). Hàm CE có trọng số theo lớp đơn thuần trên các bộ ba độc lập cùng phân phối (i.i.d.) của DSimSynergy (L1) cho phép mô hình khớp tỷ lệ cơ sở ở mức cặp (pair-level base rates) thông qua biểu diễn nhúng thuốc mà không tận dụng đủ các đặc trưng tế bào. Bộ mã hóa tế bào FC của nó (L4) không có cấu trúc đường truyền và bỏ qua những thuốc đang được kết hợp. Các giải thích KEGG của nó đến từ tương quan SHAP–biểu hiện hậu nghiệm rồi ORA, tính trên một mô hình hồi quy riêng (L5), và tính trung thực của chúng chưa bao giờ được kiểm tra. FlipPath-Syn giải quyết điều này theo ba cách.
(i) Một hàm mất mát tương phản phản thực tế ghép cặp (matched-counterfactual contrastive loss) so sánh mỗi bộ ba với các bộ ba huấn luyện đã gán nhãn chỉ khác đúng một yếu tố, hoặc dòng tế bào hoặc một thuốc đối tác, và có nhãn ngược lại. Mô hình chỉ có thể giảm hàm mất mát này bằng cách học những khác biệt về tế bào hay đối tác nào làm lật hiệp đồng. Đó là thông tin xếp hạng mà AUPR đánh giá cao trong các cặp có từng thuốc đều phổ biến (L1, L2).
(ii) Một bộ mã hóa tế bào phân rã theo đường truyền, với cổng đường truyền phụ thuộc vào cặp thuốc (đối xứng theo A và B), cho một thiên kiến quy nạp có nhận biết đích tác dụng (target-aware), phù hợp khi chỉ có 83 dòng tế bào (L4, L3).
(iii) Cổng sparsemax bằng đúng 0 đối với các đường truyền không được chọn, nên việc hoán đổi gen của chúng giữa các dòng tế bào được chứng minh là không thể thay đổi logit. Các giải thích mang tính can thiệp (interventional) theo cấu trúc. Các "tập lật (flip sets)" phản thực tế được tính trên chính bộ phân loại và đi kèm sẵn một phép kiểm tra trung thực xóa/chèn (L5).

### Phương pháp (Method)

Xương sống (backbone): giữ các nhánh thuốc của DSimSynergy (BP-GCN, ATC-GCN, GAT+GMP trên MACCS và đồ thị phân tử), cho ra d_A và d_B trong R^D. Thay bộ mã hóa tế bào FC 949→d' và làm cho biểu diễn cặp đối xứng.

1) Các mô-đun đường truyền. Ánh xạ 949 gen L1000 vào các đường truyền KEGG và giữ các đường truyền có ≥5 gen thành viên (dự kiến P≈180–220). Thêm một mô-đun phụ, "chưa chú thích (unannotated)", cho các gen không thuộc đường truyền nào được giữ. Với mỗi đường truyền p, một MLP nhỏ riêng e_p: R^{|G_p|}→R^8 (Linear-LeakyReLU-Linear) biến x_c[G_p] thành một biểu diễn nhúng hoạt động đường truyền u_p(c). Tất cả mô-đun chạy song song như một phép nhân ma trận thưa theo khối (block-sparse matmul) với mặt nạ gen→đường truyền.

2) Cổng thưa có điều kiện theo cặp thuốc. Định nghĩa q_AB = MLP_q(d_A + d_B) ⊕ MLP_q(d_A ⊙ d_B), đối xứng theo A và B. Khi đó g(A,B) = sparsemax( (Q q_AB) / τ ) ∈ Δ^P, với Q ∈ R^{P×h} và τ = 0.5. Thêm một tiên nghiệm đích tác dụng: độ lệch logit là β·log(1 + n_targets_p(A) + n_targets_p(B)), trong đó n_targets_p đếm số đích DrugBank của thuốc nằm trong p hoặc trong các láng giềng KEGG 1 bước của nó, và β được học, khởi tạo 0.5. Ngữ cảnh tế bào là z_{c|AB} = Σ_p g_p(A,B)·W_p u_p(c) với W_p ∈ R^{d'×8}. Một đường truyền có g_p = 0 đóng góp đúng bằng 0, nên logit bất biến chính xác với các gen của đường truyền đó.

3) Đầu đối xứng. s(A,B,c) = ½[MLP(d_A ⊕ d_B ⊕ z) + MLP(d_B ⊕ d_A ⊕ z)], lấy trung bình logit. Giữ concat-MLP gốc, để mức cải thiện có thể quy cho bộ mã hóa và hàm mất mát thay vì đầu dự đoán.

4) Hàm mất mát. L = L_wCE + λ_cell·L_cell + λ_drug·L_drug + λ_ent·L_sparse.
• L_cell (ghép theo cặp (pair-matched)): với mỗi bộ ba huấn luyện i = (A,B,c,y), lấy mẫu j = (A,B,c',1−y) từ cùng tập gấp huấn luyện, nếu có. L_cell = softplus(m − (2y−1)(s_i − s_j)), với lề (margin) m = 1 và trọng số 1/√|matches_i| để tránh đặt trọng số quá cao cho các cặp được thử trên nhiều dòng tế bào.
• L_drug (ghép theo đối tác (partner-matched)): j = (A,B',c,1−y) hoặc (A',B,c,1−y), cùng dạng.
• L_sparse = mean_p g_p · 1[p không nằm trong tiên nghiệm đích], một lực đẩy nhỏ về phía các đường truyền liên quan đến đích tác dụng.
Mặc định: λ_cell = 0.5, λ_drug = 0.25, λ_ent = 0.01, Adam lr 1e-4, batch 512 mẫu neo (anchors) cộng tối đa 512 đối tác ghép cặp trong cùng một lượt forward, khoảng 50 epoch trên tập con. Việc chọn checkpoint vẫn dựa trên F1 kiểm định ở ngưỡng 0.5. Một độ lệch logit vô hướng b* chọn chỉ trên tập gấp kiểm định được báo cáo như một hàng thí nghiệm loại bỏ riêng; hàng chính dùng ngưỡng 0.5.

5) Giải thích đường truyền phản thực tế (trên bộ phân loại, lúc kiểm tra). Với một bộ ba được dự đoán là hiệp đồng (A,B,c), tham chiếu c' là dòng tế bào đối kháng ghép cặp trong dữ liệu huấn luyện có khoảng cách biểu diễn nhúng đường truyền gần nhất. Định nghĩa bản lai (hybrid) x(S) = x_c với gen của các đường truyền trong S được thay bằng x_{c'}. Chạy lựa chọn tiến tham lam (greedy forward selection) trên các đường truyền có g_p > 0, mỗi bước thêm đường truyền mà việc hoán đổi làm giảm logit nhiều nhất, cho đến khi dự đoán lật xuống <0.5. Kết quả là tập lật tối thiểu S*, một giải thích nhân quả theo đường truyền đặc thù theo cặp và theo tế bào. Mỗi đường truyền cũng nhận một đóng góp tương phản φ_p = s(x_c) − s(x({p})). Ở mức nguyên tử: gradient tích phân (integrated gradients) trên đặc trưng nút GAT (đường cơ sở bằng 0), cộng trên các nguyên tử, cho quy kết cấu trúc con của thuốc đối với cùng bộ phân loại.

6) Giao thức kiểm tra tính trung thực. (a) Đường cong xóa: mức giảm xác suất và AUPR kiểm tra khi top-k đường truyền theo φ được hoán đổi sang tế bào tham chiếu, so với các đường truyền có cổng ngẫu nhiên và với các đường truyền SHAP-ORA của mô hình cơ sở. (b) Kiểm tra hoán đổi rỗng (null-swap check): hoán đổi tất cả đường truyền có g_p = 0 phải làm logit thay đổi đúng bằng 0, được kiểm chứng bằng số. (c) Kiểm tra hợp lý với trọng số ngẫu nhiên hóa. (d) Phân bố kích thước tập lật.

### Các hạn chế được giải quyết

L1, L4, L5, L3, L2

### Tuyên bố về độ mới (Novelty claim)

Các mô hình hiệp đồng hiện có, bao gồm DSimSynergy, JointSyn, HyperGraphSynergy, DeepDDS và các ứng viên S0–S3, được huấn luyện trên các bộ ba i.i.d. hoặc trên xếp hạng toàn cục. Không cái nào dùng giám sát phản thực tế có kiểm soát (controlled counterfactual supervision), tức là các cặp huấn luyện chỉ khác đúng một yếu tố (dòng tế bào hoặc đối tác) và có nhãn ngược lại. S0 dùng xếp hạng toàn cục có trọng số theo độ lớn; FlipPath-Syn dùng các phép tương phản ghép cặp một yếu tố, nhãn ngược lại. S1 truy xuất mẫu điển hình làm đặc trưng đầu vào; ở đây các mẫu điển hình ghép cặp chỉ được dùng làm tín hiệu huấn luyện, và lúc kiểm tra thì làm tham chiếu phản thực tế để giải thích. S2 và S3 mô hình hóa tương tác chéo cặp đường truyền hoặc phi cộng tính liều ở phía thuốc. FlipPath-Syn thì đặt cấu trúc vào bộ mã hóa tế bào, dùng cổng sparsemax có điều kiện theo cặp thuốc, nên tính không liên quan của đường truyền là chính xác và mang tính can thiệp. Theo hiểu biết của chúng tôi, đây cũng là mô hình hiệp đồng đầu tiên mà lời giải thích là một phản thực tế hoán đổi đường truyền tối thiểu làm lật chính quyết định của bộ phân loại, với tính trung thực được đảm bảo một phần theo cấu trúc (hiệu ứng đúng bằng 0 của các đường truyền không có cổng) và được kiểm tra bằng đường cong xóa, thay vì tương quan SHAP-biểu hiện hậu nghiệm rồi ORA.

### Kế hoạch triển khai (Implementation plan)

1) data/pathways.py: nạp các bộ gen KEGG (file GMT msigdb c2.cp.kegg) và lấy giao với 949 gen L1000. Xây mặt nạ gen→đường truyền M (949×P+1), ma trận kề đường truyền KEGG 1 bước, và số đích tác dụng của từng thuốc theo từng đường truyền từ các file đích DrugBank hiện có. Lưu đệm tất cả dưới dạng .npy.
2) data/matching.py: sau khi đã dựng phép chia cố định và chỉ số tập gấp, và chỉ dùng chỉ số huấn luyện của tập gấp hiện tại, xây dict pair→{cell: label} và (cell, drug)→{partner: label}. Với mỗi chỉ số huấn luyện, tính trước các mảng chỉ số ghép cặp có nhãn ngược lại cho trường hợp ghép theo cặp và ghép theo đối tác. Không bộ ba kiểm định hay kiểm tra nào được đánh chỉ mục.
3) model.py: thêm PathwayCellEncoder (các MLP theo từng đường truyền dạng chéo khối (block-diagonal) qua một Linear có mặt nạ cộng một Linear theo nhóm (grouped Linear)), PairGate (cài đặt sparsemax khoảng 20 dòng, số hạng tiên nghiệm đích), và một lượt forward đối xứng lấy trung bình trên cả hai thứ tự thuốc. Giữ nguyên các mô-đun GCN, GAT và đầu dự đoán. Cung cấp forward(..., return_gate=True).
4) train.py: hàm gom lô lấy một đối tác ghép theo cặp và một đối tác ghép theo đối tác cho mỗi mẫu neo khi có, rồi nối chúng vào batch. Thêm L_cell, L_drug và L_sparse vào CE có trọng số theo lớp hiện có. Dùng cờ cấu hình cho các giá trị λ để các thí nghiệm loại bỏ (λ=0, bộ mã hóa FC thay cho bộ mã hóa đường truyền, cổng softmax dày thay cho sparsemax, không có tiên nghiệm đích) chỉ là một công tắc. Giữ cách lưu checkpoint theo F1 kiểm định. Tùy chọn khớp một bias b* chỉ trên tập kiểm định và báo cáo riêng.
5) explain.py: tập lật tối thiểu tham lam, đóng góp φ_p, IG trên nguyên tử (captum), đường cong xóa/chèn so với các mô hình cơ sở ngẫu nhiên và SHAP-ORA, khẳng định hoán đổi rỗng, kiểm tra hợp lý với trọng số ngẫu nhiên hóa. Đầu ra là các file CSV và hình cho ca Binimetinib–Brigatinib để liên tục với bài báo.
Tính toán: khoảng 1.3× thời gian mỗi epoch của mô hình cơ sở (batch gấp đôi, các MLP đường truyền nhỏ). Sàng lọc tập gấp 1 với 50 epoch mất chưa tới một giờ trên nửa GPU A100; lượt chạy đầy đủ là 5 tập gấp × khoảng 150 epoch.

### Tác động dự kiến (Expected effect)

Sàng lọc tập gấp 1: AUPR +0.03 đến +0.05 so với mô hình cơ sở tái lập ở cùng số epoch, chủ yếu từ L_cell, tức các phép tương phản ghép theo cặp làm sắc nét thứ hạng trong cùng một cặp giữa các dòng tế bào. F1 +0.02 đến +0.04 ở ngưỡng cố định 0.5, và +0.04 đến +0.06 với độ lệch được hiệu chuẩn trên tập kiểm định. AUROC +0.005 đến +0.01. ACC không đổi hoặc +0.002. Mục tiêu trên bộ chuẩn đầy đủ: AUPR ≈ 0.80–0.82 so với 0.77, F1 ≈ 0.76–0.78 so với 0.74, AUROC ≈ 0.965–0.97, ACC ≈ 0.98. Mức cải thiện lớn nhất sẽ xuất hiện ở tầng các bộ ba kiểm tra mà cặp thuốc có nhãn lẫn lộn giữa các dòng tế bào huấn luyện. Mẫu thí nghiệm loại bỏ dự kiến: bỏ L_cell gây sụt giảm lớn nhất; thay sparsemax bằng softmax cho độ chính xác tương tự nhưng mất đảm bảo hoán đổi rỗng và có đường cong xóa phẳng hơn; bộ mã hóa FC kém khoảng 0.01 AUPR. Giải thích: xóa top-3 đường truyền theo φ sẽ làm giảm xác suất dự đoán nhiều lần hơn so với các đường truyền có cổng ngẫu nhiên, và tập lật thường chứa 1–5 đường truyền.

### Rủi ro (Risks)

(1) Đối tác ghép cặp có thể khan hiếm với một số cặp; với chỉ khoảng 3% dương tính, nhiều dương tính có thể không có đối tác nhãn ngược lại trong cùng dòng tế bào. Khi đó hàm mất mát thoái hóa về CE thuần và mức cải thiện co lại. Thống kê độ phủ sẽ được ghi log và các dương tính không có đối tác ghép cặp sẽ được tăng trọng số. (2) Hàm mất mát tương phản có thể nhấn mạnh quá mức các cặp được thử trên nhiều dòng tế bào và làm hỏng hiệu chuẩn ở 0.5, biểu hiện thành F1 ở 0.5 kém hơn nhưng AUPR tốt hơn. Giảm thiểu: trọng số 1/√n, λ_cell thấp hơn, và độ lệch hiệu chuẩn được báo cáo. (3) Cổng sparsemax có thể sụp đổ (collapse) về một vài đường truyền, hoặc về mô-đun "chưa chú thích", khiến giải thích trở nên tầm thường và làm giảm AUPR. Theo dõi entropy của cổng và quay về τ = 1 hoặc entmax-1.5. (4) Bộ mã hóa phân rã theo đường truyền có nhiều tham số hơn một lớp FC và có thể quá khớp với 83 dòng tế bào, biểu hiện thành khoảng cách huấn luyện/kiểm định. Dùng dropout trên u_p và suy giảm trọng số. (5) Tập lật tham lam chỉ là xấp xỉ và phụ thuộc vào lựa chọn dòng tế bào tham chiếu, nên sẽ được báo cáo cùng thứ hạng φ và độ ổn định giữa 5 mô hình tập gấp.

### Kiểm tra độ mới (Novelty check)

Tôi đã tìm kiếm từng phần trong ba phần của FlipPath-Syn. Mỗi phần đều có tiền lệ rõ ràng, nhưng tôi không thấy bài báo nào kết hợp chúng, hoặc áp dụng tín hiệu huấn luyện phản thực tế ghép cặp cho dự đoán hiệp đồng.

(ii) Bộ mã hóa tế bào phân rã theo đường truyền có điều kiện theo thuốc có các tiền lệ gần. DRPreter dùng chú ý có điều kiện theo thuốc trên các đồ thị con (subgraphs) đường truyền KEGG, dù là cho đáp ứng đơn thuốc. MOViDA và dòng công trình DrugCell dùng các mạng "nhìn thấy được (visible)" mô-đun theo đường truyền, và MOViDA mở rộng điều này sang hiệp đồng. TranSynergy và chính DSimSynergy đã tạo ra giải thích hiệp đồng ở mức đường truyền. Điểm mới ở đây là cổng sparsemax có điều kiện đối xứng theo cặp thuốc, kèm tiên nghiệm đích DrugBank. Đó là một thay đổi khiêm tốn: sparsemax và entmax là những cách tiêu chuẩn để có độ thưa chính xác.

(iii) Giải thích phản thực tế làm lật dự đoán bằng một thay đổi tối thiểu đã được thiết lập vững chắc trong XAI; CF-GNNExplainer là một ví dụ. Kiểm tra tính trung thực bằng nhiễu loạn (perturbation) đã có cho các mô hình hiệp đồng ở mức motif (VINCENT). Tuy nhiên, tôi không tìm thấy mô hình hiệp đồng nào mà lời giải thích là tập đường truyền nhỏ nhất, được hoán đổi từ một dòng tế bào đối kháng ghép cặp, làm lật quyết định, cùng với đảm bảo rằng các đường truyền không có cổng có tác động đúng bằng 0.

(i) Đối với hàm mất mát tương phản phản thực tế ghép cặp, tôi không tìm thấy công trình nào trước đó. Nó ghép mỗi bộ ba huấn luyện với một bộ ba chỉ khác dòng tế bào, hoặc chỉ khác một thuốc đối tác, và có nhãn ngược lại. Có các ý tưởng liên quan: PDTSyn coi mỗi dòng tế bào là một miền (domain), MGAE-DC dùng các kênh đặc thù theo nhãn, và HetBiSyn dùng khai thác mẫu âm khó (hard-negative mining). Không cái nào dùng các cặp ghép một yếu tố, nhãn ngược lại. Tuy vậy, bản thân hàm mất mát là một hàm mất mát lề theo cặp (pairwise margin loss) áp dụng cho một lựa chọn cặp hợp lý. Nó gần với một thủ thuật huấn luyện có động lực tốt hơn là một cơ chế mới.

Tổng thể, đây là sự kết hợp không tầm thường và mạch lạc của các thành phần đã biết (bộ mã hóa mô-đun theo đường truyền, cổng thưa, hàm mất mát xếp hạng theo cặp, giải thích phản thực tế). Nó mới ở cách lắp ghép chúng cho bài toán này, nhưng không phần nào mới về cơ chế. Điều đó đặt nó ở mức 6.

Các công trình trước gần nhất đã tìm thấy:

- DRPreter: Interpretable Anticancer Drug Response Prediction Using Knowledge-Guided Graph Neural Networks and Transformer (2022) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9699175/: Đây là khớp gần nhất với thành phần (ii). DRPreter tách dòng tế bào thành các đồ thị con đường truyền KEGG và dùng một transformer thuốc–đường truyền để tìm các đường truyền quan trọng với mỗi thuốc. Đó là một bộ mã hóa tế bào phân rã theo đường truyền có điều kiện theo thuốc, với diễn giải theo từng đường truyền. Khác biệt: nó dự đoán đáp ứng đơn thuốc chứ không phải hiệp đồng cặp, nó dùng chú ý dày thay vì sparsemax (nên không có đảm bảo đúng bằng 0), và không có huấn luyện phản thực tế hay giải thích bằng tập lật.
- TranSynergy: Mechanism-driven interpretable deep neural network for the synergistic prediction and pathway deconvolution of drug combinations (2021) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7906476/: TranSynergy dự đoán hiệp đồng với diễn giải ở mức đường truyền. Nó giải thích đường truyền hậu nghiệm, dùng SHAP rồi phân tích tăng cường bộ gen (gene set enrichment) (SA-GSEA), cùng kiểu giải thích mà đề xuất này phê phán ở DSimSynergy. Bộ mã hóa tế bào của nó không có cấu trúc đường truyền, và nó không dùng huấn luyện tương phản ghép cặp.

<a id="s5"></a>
## S5 · độ mới 5 · SLink-Syn: một số hạng ghép nối gây chết tổng hợp (synthetic-lethality coupling term) trên "dấu vết" đích tác dụng lan truyền qua mạng (network-propagated target footprints) đặc thù theo tế bào, cho phép quy kết theo cặp gen (gene-pair attributions) đối với hiệp đồng thuốc

_Lan truyền các đích DrugBank của mỗi thuốc trên một đồ thị tương tác protein–protein (PPI) mà trọng số cạnh phụ thuộc vào biểu hiện của dòng tế bào, cho ra một "dấu vết (footprint)" gen theo từng tế bào. Một ma trận ghép nối gen×gen đối xứng, hạng thấp, được dẫn hướng bởi tiên nghiệm gây chết tổng hợp và gen cùng họ (paralog), và gắn cổng bởi mức phụ thuộc gen (gene dependencies) DepMap của tế bào, chấm điểm mức độ hai dấu vết bổ sung cho nhau. Một phạt dư thừa (redundancy penalty) đẩy xuống các cặp tác động lên cùng các gen thiết yếu (essential genes). Số hạng thu được được cộng vào logit DSimSynergy đã lấy trung bình theo thứ tự, nên mỗi dự đoán đi kèm giải thích chính xác theo cặp gen đích, kiểm tra được bằng phép xóa._

### Động lực (Motivation)

L4: DSimSynergy mã hóa dòng tế bào độc lập với các thuốc, bằng một lớp kết nối đầy đủ trên 949 gen. Đích tác dụng của thuốc không bao giờ được nối với biểu hiện hay tính thiết yếu (essentiality) của chính nó trong tế bào đó. Vì vậy mô hình không thể biểu diễn con đường cơ chế được xác lập nhất dẫn đến hiệp đồng đặc thù theo ngữ cảnh: hai thuốc tác động lên các nút bổ sung của một hệ thống có cơ chế đệm (buffered) (gây chết tổng hợp hoặc được bù trừ bởi gen cùng họ) mà tế bào thực sự phụ thuộc vào. L7: việc làm trơn của GCN trên độ tương đồng BP/ATC giả định rằng các thuốc tương đồng thì hiệp đồng (PCC chỉ 0.21–0.23), trong khi lời giải thích của chính các tác giả là tính bổ sung. Số hạng ghép nối của chúng tôi thưởng tường minh cho tính bổ sung và phạt sự dư thừa (các đích thiết yếu chồng lấp), nên theo cấu trúc nó có nhận biết tính dị loại. L2: ghép nối cộng MLP không có số hạng cặp tường minh. Của chúng tôi là một tương tác cặp song tuyến tính trong không gian gen, có điều kiện theo tế bào. L5: giải thích hiện là SHAP hậu nghiệm trên một mô hình hồi quy riêng. Số hạng của chúng tôi phân rã chính xác thành đóng góp từ các cặp gen (i,j) bên trong chính bộ phân loại, nên có thể chạy kiểm tra trung thực bằng phép xóa. L3: phép ghép nối đối xứng, và logit xương sống được lấy trung bình trên cả hai thứ tự thuốc, nên dự đoán và quy kết đều bất biến theo thứ tự. Vì sao điều này sẽ giúp AUPR trên lớp dương tính hiếm: những dương tính mà DSimSynergy bỏ sót là các ca đặc thù theo ngữ cảnh, nơi cùng một cặp chỉ hiệp đồng ở vài dòng tế bào. Cổng phụ thuộc đặc thù theo tế bào và lan truyền có trọng số theo biểu hiện chính là những đặc trưng thay đổi giữa các dòng tế bào với một cặp cố định.

### Phương pháp (Method)

Tập gen: G = các gen mốc L1000 (L1000 landmark genes) (949) ∪ các đích DrugBank của 521 thuốc, khoảng 1.5–2.5 nghìn gen. Đồ thị: các liên kết vật lý/chức năng STRING v12 với điểm tổng hợp (combined score) ≥ 700, giới hạn trong G và có thêm vòng tự thân (self-loops); ma trận kề A.
Đầu vào tế bào: x_c = biểu hiện log2(TPM+1) trên G (DepMap 24Q4, cùng nguồn bài báo đã dùng). d_c = hiệu ứng gen DepMap CRISPR Chronos (Chronos gene effect) trên G, điền khuyết (imputed) bằng trung vị theo gen khi thiếu.
Cổng tính thiết yếu: e_c = σ(−(d_c − θ)/τ), với mặc định θ = −0.5 và τ = 0.2, và θ có thể học.

1) Lan truyền có điều kiện theo tế bào (PageRank cá nhân hóa (personalised PageRank) kiểu APPNP)
Cổng cạnh: w_ij^c = A_ij · σ(a1·x_ic + a2·x_jc + a3·x_ic·x_jc + b), với 4 tham số vô hướng dùng chung cho mọi cạnh. Ŵ^c = D^{-1/2} W^c D^{-1/2}.
Hạt giống (seed): s_A = softmax trên các đích T_A của các logit được học theo từng (thuốc, đích), khởi tạo đồng nhất; tác dụng DrugBank (chất ức chế (inhibitor)/chất chủ vận (agonist)) được dùng làm đặc trưng dấu.
Dấu vết: p_A^c = Σ_{k=0}^{K} α(1−α)^k (Ŵ^c)^k s_A, với K = 6 và α = 0.3. Đại lượng này được tính một lần mỗi batch cho từng tế bào duy nhất (83 tế bào) dưới dạng tích ma trận thưa, rồi đánh chỉ mục theo thuốc.

2) Ghép nối gây chết tổng hợp (đối xứng, hạng thấp)
q_A = g_c ⊙ p_A^c, trong đó g_c = e_c ⊙ softplus(w_g·x_c + b_g) là cổng theo từng gen cho biểu hiện và mức phụ thuộc.
M = ½(U Λ Vᵀ + V Λ Uᵀ), với U, V ∈ R^{|G|×R}, R = 32, và Λ là ma trận chéo.
z_SL = q_Aᵀ M q_B. Đại lượng này đối xứng theo A và B và không bao giờ phải dựng ma trận |G|² đầy đủ: z_SL = ½[(Uᵀq_A)ᵀΛ(Vᵀq_B) + (Vᵀq_A)ᵀΛ(Uᵀq_B)].

3) Số hạng dư thừa (chống hiệp đồng (anti-synergy))
z_red = −softplus(β) · (p_A ⊙ e_c)ᵀ(p_B ⊙ e_c) / (‖p_A ⊙ e_c‖ ‖p_B ⊙ e_c‖ + ε).
Tác động lên cùng các gen thiết yếu dự báo tính cộng tính hoặc đối kháng.

4) Logit cuối cùng
ℓ = ½[f_DSim(A,B,c) + f_DSim(B,A,c)] + γ · (z_SL + z_red), với γ có thể học và khởi tạo 0.1.
Xương sống DSimSynergy giữ nguyên (GCN BP/ATC, GAT phân tử, MLP tế bào).

5) Các bộ điều chuẩn tiên nghiệm và độ thưa (prior and sparsity regularisers)
- Tiên nghiệm SL: L_prior = −mean_{(i,j)∈P} M_ij + mean_{(i,j)∼random} softplus(M_ij), trong đó P = các cặp SL ở người trong SynLethDB ∪ các cặp gen cùng họ Ensembl nằm trong G.
- Độ thưa: L_sp = ‖U‖_1 + ‖V‖_1.
- Hàm mất mát tổng: L = CE có trọng số theo lớp (như trong bài báo) + λ_p L_prior + λ_s L_sp, với λ_p = 0.05 và λ_s = 1e-5.

6) Huấn luyện và đánh giá
Cùng phép chia, Adam lr 1e-4 (mô-đun ghép nối cũng dùng lr 1e-4), batch 512, khoảng 50 epoch trên tập con sàng lọc. Checkpoint chọn theo F1 kiểm định, như trong giao thức. Dự đoán kiểm tra dùng ngưỡng 0.5 và được lấy trung bình trên các mô hình tập gấp.

7) Giải thích (chính xác, bên trong bộ phân loại)
- z_SL = Σ_{i,j} q_Ai M_ij q_Bj. Các cặp gen (i,j) hàng đầu theo |q_Ai M_ij q_Bj + q_Aj M_ji q_Bi| cho ra các cặp đích–đích hoặc đích–gen hạ nguồn (downstream gene) điều khiển mỗi dự đoán trong tế bào đó.
- Quy kết theo đường đi: phân rã p_A thành các đóng góp theo từng bước nhảy dọc đồ thị PPI.
- Tóm tắt ở mức đường truyền đến từ việc tổng hợp điểm cặp trên các bộ gen KEGG. Phép tổng hợp này chính xác, không phải ORA.
- Tính trung thực: (a) đường cong xóa đặt bằng 0 top-k gen trong g_c, so với các gen ngẫu nhiên có cùng bậc (matched degree), báo cáo Δprob và ΔAUPR; (b) kiểm tra hợp lý với U và V ngẫu nhiên hóa.
- Giữ SHAP trên biểu hiện và quy kết GAT/nguyên tử để các phân tích của bài báo vẫn sử dụng được.

### Các hạn chế được giải quyết

L4, L7, L2, L5, L3

### Tuyên bố về độ mới (Novelty claim)

S2 chấm điểm tương tác chéo giữa các cặp đường truyền KEGG, S3 mô hình hóa phi cộng tính trong không gian liều, S1 truy xuất mẫu điển hình huấn luyện, S4 huấn luyện trên các bộ ba phản thực tế, và S0 thêm một đầu nhúng ba tuyến tính tổng quát. Ý tưởng này khác tất cả chúng. Nó đặt tương tác trong không gian gen, dưới dạng một ghép nối gây chết tổng hợp được học giữa các dấu vết đích lan truyền qua mạng. Nó dùng ba thành phần đặc thù theo tế bào mà không ứng viên nào và không GNN hiệp đồng đã công bố nào chúng tôi biết (DeepDDS, JointSyn, HyperGraphSynergy, DSimSynergy) kết hợp lại: (i) một toán tử lan truyền PPI có trọng số cạnh phụ thuộc vào biểu hiện của tế bào; (ii) gắn cổng theo mức phụ thuộc CRISPR (tính thiết yếu); (iii) một ghép nối song tuyến tính được neo vào tiên nghiệm SL và gen cùng họ, đi kèm một phạt dư thừa tường minh, để tách tính bổ sung khỏi sự chồng lấp. "Phơi nhiễm bổ sung (complementary exposure)" theo độ gần mạng (network proximity) (Cheng và cộng sự 2019) là tĩnh, không phụ thuộc tế bào và không được học. Ở đây nó trở thành một mô-đun khả vi, đặc thù theo tế bào, có giám sát, với giải thích là các cặp gen và có thể kiểm tra bằng phép xóa.

### Kế hoạch triển khai (Implementation plan)

1) Script chuẩn bị dữ liệu (file mới prep_slink.py):
- Xây tập gen G từ danh sách L1000 cộng các đích DrugBank của các thuốc trong Code/Data/TRAIN.
- Tải các cạnh STRING (≥700), ma trận DepMap 24Q4 CRISPRGeneEffect (cùng phiên bản với dữ liệu biểu hiện), và các danh sách SynLethDB và gen cùng họ.
- Lưu: A dưới dạng tensor COO thưa; x_c và d_c cho 83 dòng tế bào; danh sách chỉ số đích theo từng thuốc; chỉ số cặp tiên nghiệm P.
2) Mô hình (mô-đun mới slink.py): lớp SLinkHead(nn.Module) chứa cổng cạnh, các logit hạt giống theo từng đích, U, V, Λ, cổng g_c, β và γ. forward(drugA_idx, drugB_idx, cell_idx):
- Chạy lan truyền cho các tế bào duy nhất (torch.sparse.mm, K = 6).
- Thu thập dấu vết cho A và B và trả về z_SL, z_red và các vectơ q được lưu đệm để quy kết.
- Bộ nhớ nhỏ: với mỗi tế bào trong tối đa 83 tế bào, |G| × số thuốc dùng trong batch, khoảng 2k × 521 số thực, xấp xỉ 4 MB mỗi tế bào, xử lý theo từng khúc (chunks).
3) Sửa file mô hình DSimSynergy (lớp có hàm forward ghép nối ba đặc trưng thuốc với đặc trưng tế bào):
- Tính f(A,B,c) và f(B,A,c) và lấy trung bình logit.
- Cộng γ(z_SL + z_red) vào logit của lớp hiệp đồng. Với đầu ra CE 2 lớp, cộng nó vào logit[:,1] − logit[:,0] bằng cách cộng vào logit[:,1].
4) Sửa vòng lặp huấn luyện: thêm L_prior và L_sp vào hàm mất mát. Phép chia, trọng số lớp, cách lưu checkpoint theo F1 và ngưỡng 0.5 giữ nguyên.
5) explain_slink.py mới:
- Quy kết cặp gen hàng đầu cho từng bộ ba, tổng hợp trên KEGG.
- Đường cong xóa và chèn trên tập kiểm tra so với các gen ngẫu nhiên có cùng bậc.
- Kiểm tra hợp lý với trọng số ngẫu nhiên hóa.
6) Cờ thí nghiệm loại bỏ:
- --no_sl (chỉ xương sống + lấy trung bình theo thứ tự);
- --no_prop (K = 0, chỉ đích);
- --no_dep (e_c = 1);
- --shuffle_dep (vectơ phụ thuộc bị hoán vị giữa các tế bào);
- --no_prior (λ_p = 0);
- --no_red.
Mỗi cờ chạy trên tập con sàng lọc (tập gấp 1, 50 epoch). Lượt chạy đầy đủ 5 tập gấp được thực hiện cho cấu hình tốt nhất.

### Tác động dự kiến (Expected effect)

Đây là các tác động mong đợi, không phải kết quả đã đo.
- Kiểm tra nội bộ, tập con sàng lọc: AUPR tăng khoảng 0.02–0.04 so với DSimSynergy chạy lại cùng ngân sách. F1 tăng khoảng 0.02–0.03, vì sẽ có ít dương tính giả (false positives) hơn ở những cặp hiệp đồng trong các dòng tế bào khác nhưng không phải dòng này, và độ nhạy (recall) cao hơn với các dương tính đặc thù theo ngữ cảnh.
- AUROC tăng khoảng 0.005. ACC gần như không đổi ở khoảng 0.98.
- Mục tiêu trên bộ chuẩn đầy đủ: AUPR ≥ 0.79 và F1 ≥ 0.75, so với 0.77 và 0.74 của bài báo.
- Lấy trung bình theo thứ tự cũng sẽ giảm phương sai F1 giữa các tập gấp.
- Thí nghiệm loại bỏ: phần lớn mức cải thiện sẽ biến mất với --no_sl và --shuffle_dep, điều này sẽ xác nhận rằng ghép nối đặc thù theo tế bào là nguyên nhân.
- Giải thích: xóa top-k gen được quy kết sẽ gây sụt giảm xác suất hiệp đồng lớn hơn nhiều so với xóa ngẫu nhiên có cùng bậc. Một tỷ lệ đáng kể các cặp hàng đầu sẽ là các cặp SL hoặc gen cùng họ đã biết, hoặc thành viên của cùng một đường truyền, ví dụ các nút MAPK và PI3K đối với các tổ hợp có Binimetinib.

### Rủi ro (Risks)

(1) Trên phép chia ngẫu nhiên, sự ghi nhớ của xương sống có thể chiếm ưu thế, nên số hạng ghép nối đóng góp ít và γ co về 0. Điều này sẽ biểu hiện thành chênh lệch nhỏ giữa mô hình đầy đủ và --no_sl; giảm thiểu bằng cách báo cáo phân tách kiểu PairOut/CellOut trên tập kiểm định. (2) Dữ liệu DepMap CRISPR có thể thiếu cho một số trong 83 dòng tế bào; điền khuyết bằng trung vị làm yếu cổng. Khi đó --shuffle_dep sẽ không cho thấy mất mát nào. (3) Các gen trung tâm (hub genes) trong STRING có thể chi phối dấu vết và khiến giải thích trở nên chung chung (TP53, EGFR ở khắp nơi). Giảm thiểu: lan truyền chuẩn hóa theo bậc và so sánh với các gen ngẫu nhiên có cùng bậc trong các phép thử xóa. (4) Các danh sách tiên nghiệm SL thưa và thiên lệch về gen ung thư, nên tiên nghiệm có thể làm quy kết quá khớp với các cặp đã biết. Kiểm tra bằng --no_prior và kiểm tra hợp lý với trọng số ngẫu nhiên hóa. (5) Việc thêm một nguồn dữ liệu bên ngoài (hiệu ứng CRISPR) có thể bị chất vấn. Đây là đặc trưng ở mức tế bào từ cùng phiên bản DepMap, không chứa nhãn hiệp đồng và không đụng đến các tập kiểm tra bên ngoài. Thí nghiệm loại bỏ --no_dep đo hiệu ứng khi không có nó. (6) Tham số thêm (U và V: khoảng 2k × 32 × 2) có thể quá khớp với lớp dương tính khoảng 3%. Phạt L1 và hạng thấp hạn chế điều này; quá khớp sẽ biểu hiện thành khoảng cách giữa AUPR kiểm định và kiểm tra.

### Kiểm tra độ mới (Novelty check)

Các thành phần chính đều đã được công bố. TranSynergy (2021) kết hợp hồ sơ đích tác dụng thuốc lan truyền qua mạng PPI với mức phụ thuộc gen và biểu hiện của tế bào, và giải thích dự đoán bằng SHAP trên gen và đường truyền. Đó là phần cốt lõi của ý tưởng 'dấu vết đích đặc thù theo tế bào + tính thiết yếu + giải thích mức gen' cho bài toán này, và phần độ mới của đề xuất đã bỏ sót nó. SynCell (2025) đã xây một mạng con PPI cho mỗi dòng tế bào từ biểu hiện. Cheng và cộng sự (2019) đã đặt ra nguyên lý bổ sung so với chồng lấp trên tương tác đồ (interactome). Việc ánh xạ đối tác SL của các đích thuốc để khám phá tổ hợp có từ năm 2018. Điều tôi không tìm thấy tiền lệ là dạng cụ thể: một ghép nối gen×gen song tuyến tính, đối xứng, hạng thấp, được học giữa hai dấu vết, được điều chuẩn về phía các cặp SynLethDB và gen cùng họ; một phạt dư thừa riêng trên các gen thiết yếu chung; các cạnh lan truyền gắn cổng theo biểu hiện của tế bào; và các quy kết cặp gen chính xác bên trong mô hình kèm phép thử xóa. Đó là một sự điều chỉnh và kết hợp không tầm thường chứ không phải một cơ chế mới, nên 5 phù hợp hơn 3–4 hay 7. Lưu ý: tôi không đọc được Li và cộng sự 2018 ('Network propagation predicts drug synergy in cancers', Cancer Research), bài này có thể trùng lặp nhiều hơn. Một nghiên cứu trên nấm men (yeast) cho thấy hiệp đồng dự đoán từ hồ sơ hóa học-di truyền (chemical-genetic profiles) cộng mạng tương tác di truyền (genetic-interaction network) không đứng vững, điều này đặt dấu hỏi cho giả thuyết ghép nối SL. TranSynergy nên được trích dẫn và lý tưởng là dùng làm mô hình cơ sở.

Các công trình trước gần nhất đã tìm thấy:

- TranSynergy: Mechanism-driven interpretable deep neural network for the synergistic prediction and pathway deconvolution of drug combinations (2021) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7906476/: Trùng cao. Mỗi thuốc được biểu diễn bằng các đích DrugBank lan truyền trên mạng PPI; dòng tế bào bằng mức phụ thuộc gen và/hoặc biểu hiện trên cùng các gen đó; một transformer kết hợp chúng, và một phương pháp bộ gen dựa trên SHAP cho quy kết gen và đường truyền. Điều này đã bao quát phần cốt lõi của 'dấu vết đích lan truyền + tính thiết yếu của tế bào + giải thích mức gen'. Nó thiếu ghép nối SL song tuyến tính đối xứng được học, tiên nghiệm SL/gen cùng họ, phạt dư thừa, trọng số cạnh có điều kiện theo tế bào và quy kết cặp gen chính xác bên trong mô hình.
- SynCell: Contextualized Drug Synergy Prediction (2025) https://arxiv.org/html/2511.17695v3: Trùng trung bình. Xây một mạng con PPI cho mỗi dòng tế bào từ các protein biểu hiện cao của tế bào đó bên trong một đồ thị tri thức (knowledge graph) thuốc–protein–tế bào để dự đoán hiệp đồng; tuyên bố khả năng khái quát hóa và diễn giải tốt hơn. Đã đi trước thành phần lan truyền có điều kiện theo tế bào (mạng con cứng thay vì trọng số cạnh được học gắn cổng theo biểu hiện). Không có ghép nối SL hay gắn cổng theo mức phụ thuộc.

<a id="s0"></a>
## S0 · độ mới 4.5 · SymTri-Rank: đầu tương tác ba tuyến tính (trilinear interaction head) đối xứng, có điều kiện theo tế bào (cell-conditioned), huấn luyện bằng xếp hạng có tính đến độ lớn (magnitude-aware ranking), cùng quy kết phân rã theo tương tác (interaction-decomposed attributions) cho DSimSynergy

_Thay đầu concat+MLP phụ thuộc thứ tự của DSimSynergy bằng một đầu tương tác thuốc×thuốc×tế bào hạng thấp, bất biến hoán vị (permutation-invariant), có cổng theo tế bào, cùng một bộ đọc ra nguyên tử (atom readout) có điều kiện theo đối tác/tế bào. Huấn luyện bằng CE có trọng số theo lớp cộng một hàm mất mát xếp hạng theo cặp (pairwise ranking loss) có trọng số theo độ lớn Loewe và một hàm mất mát hồi quy Loewe, và hiệu chuẩn độ lệch logit chỉ trên tập gấp kiểm định. Mục tiêu là AUPR/F1 cao hơn, với các giải thích chính xác, nhất quán theo thứ tự và đã được kiểm tra tính trung thực._

### Động lực (Motivation)

AUROC của DSimSynergy là 0.96 nhưng AUPR chỉ 0.77 và F1 0.74. Khoảng cách đó đúng như kỳ vọng ở một mô hình xếp hạng tốt tổng thể nhưng sắp xếp kém các dương tính hiếm ở đầu bảng, và được đánh giá ở ngưỡng 0.5 mà ý nghĩa của nó đã bị dịch chuyển do trọng số lớp. Năm hạn chế gây ra điều này và được khắc phục cùng lúc:
(L2) Hiệp đồng là một tương tác thuốc×thuốc×tế bào phi cộng tính, nhưng mô hình cơ sở chỉ ghép nối đặc trưng và để MLP tự phát hiện các số hạng nhân từ khoảng 3% dương tính. Cách này đòi hỏi nhiều dữ liệu, và bản thân tương tác không bao giờ được bộc lộ.
(L3) Ghép nối khiến f(A,B,c) ≠ f(B,A,c). Tính đối xứng chỉ được khuyến khích qua tăng cường dữ liệu, nên dự đoán và quy kết SHAP phụ thuộc vào thứ tự đầu vào. Các bản đảo chiều của bộ ba kiểm tra cũng có thể lọt vào tập huấn luyện nếu tăng cường dữ liệu diễn ra trước khi chia.
(L1, L8) BCE có trọng số theo lớp theo từng điểm (pointwise) không tối ưu phần đầu bảng xếp hạng cũng không dùng độ lớn Loewe. Điểm 11 và điểm 80 nhận cùng một nhãn, dù độ lớn là tín hiệu sắp thứ tự mạnh giữa các dương tính.
(L6, L5) Chú ý GAT với gộp cực đại toàn cục (global max-pooled) được tính theo từng thuốc, bỏ qua thuốc đối tác và dòng tế bào. Các quy kết đến từ một mô hình hồi quy riêng, và tính trung thực của chúng chưa bao giờ được đo.

### Phương pháp (Method)

Ký hiệu: thuốc a, thuốc b, tế bào c, nhãn y∈{0,1}, điểm Loewe s (có sẵn cho mọi bộ ba đã gán nhãn). Dữ liệu, phép chia và nhãn giữ nguyên.

1) Bộ mã hóa thuốc (drug encoder). Giữ BP-GCN, ATC-GCN và GAT phân tử. Thay gộp cực đại toàn cục bằng một bộ đọc ra chú ý có cổng, có điều kiện theo ngữ cảnh (context-conditioned gated attention readout). Với thuốc a có trạng thái nguyên tử h_i (đầu ra GAT, số chiều F), vectơ gộp của đối tác m_b (gộp trung bình các nguyên tử của b, chỉ dùng làm truy vấn, nên không có đệ quy) và vectơ tế bào h_c:
- q = W_q[m_b ; h_c]
- α_i = softmax_i( w^T tanh(W_k h_i + q) )
- g_a = Σ_i α_i h_i
Các α_i là trọng số lồi (convex weights) chính xác, phụ thuộc vào đối tác và tế bào.
Vectơ thuốc: z_a = LayerNorm(W_d[e_a^BP ; e_a^ATC ; g_a]) ∈ R^256. Cùng một bộ trọng số dùng chung cho cả hai thuốc.

2) Bộ mã hóa tế bào. Giữ MLP 949 gen: h_c = LeakyReLU(W_1 x_c) ∈ R^256, với dropout 0.2.

3) FiLM có điều kiện theo tế bào:
- γ_c = 1 + tanh(W_γ h_c)
- β_c = W_β h_c
- u_a = γ_c ⊙ z_a + β_c (tương tự với u_b)

4) Đầu tương tác đối xứng. Logit là ℓ = ℓ_add + ℓ_int + b0, trong đó:
- ℓ_add = MLP_add([u_a + u_b ; h_c]). Đây là số hạng cộng tính / ngữ cảnh đơn chất.
- ℓ_int = MLP_pair([u_a ⊙ u_b ; |u_a − u_b|]) + Σ_{r=1..R} (P u_a)_r (P u_b)_r (Q h_c)_r. Phần thứ hai là số hạng ba tuyến tính hạng thấp (phân rã CP) thuốc×thuốc×tế bào với R = 64 và P dùng chung, nên đối xứng theo a và b.
Mọi thành phần đều bất biến khi hoán đổi a và b. Tăng cường dữ liệu đảo thứ tự trở nên không cần thiết và được loại bỏ, đồng thời loại bỏ mọi nguy cơ rò rỉ qua bản đảo chiều. Các MLP có 2 lớp với kích thước ẩn 256, LeakyReLU và dropout 0.3.

5) Các đầu phụ trợ (auxiliary heads), dùng chung bộ mã hóa:
- Đầu hồi quy: ŝ = MLP_reg(cùng đặc trưng với logit). Hàm mất mát L_reg = Huber_δ=1( ŝ − clip(s, −50, 100)/20 ).
- Hàm mất mát xếp hạng theo cặp có tính đến độ lớn trong mỗi batch. P = các dương tính, N = các âm tính. N_h = top-k (k = 8·|P|, giới hạn bởi |N|) âm tính có logit cao nhất, tức là khai thác mẫu âm khó.
  L_rank = (1/|P||N_h|) Σ_{i∈P, j∈N_h} w_i · softplus( −(ℓ_i − ℓ_j)/τ )
  trong đó w_i = 1 + log(1 + (s_i − 10)/10) và τ = 0.5.
  Nếu một batch không có dương tính nào, L_rank = 0. Các batch được lấy bởi một bộ lấy mẫu (sampler) đảm bảo ít nhất 16 dương tính mỗi batch 512, trong khi giữ tỷ lệ lớp tự nhiên cho phần còn lại.
- Hàm mất mát tổng: L = L_wCE + λ_rank·L_rank + λ_reg·L_reg, với λ_rank = 0.5 và λ_reg = 0.2. L_wCE dùng trọng số lớp của mô hình cơ sở.

6) Hiệu chuẩn chỉ trên tập kiểm định (L1). Sau khi huấn luyện mỗi tập gấp, khớp một nhiệt độ (temperature) vô hướng T và độ lệch δ trên tập kiểm định của tập gấp đó: độ lệch tối đa hóa F1 kiểm định tại p = σ((ℓ+δ)/T) ≥ 0.5, và T tối thiểu hóa NLL kiểm định. Gộp cả hai vào bias của mô hình, để ACC và F1 báo cáo vẫn dùng ngưỡng 0.5 trên xác suất đầu ra của mô hình. Tập kiểm tra không bao giờ bị đụng đến. Việc chọn checkpoint vẫn dùng F1 kiểm định như trong giao thức, tính sau khi khớp lại δ ở mỗi epoch được đánh giá. Để minh bạch, F1@0.5 chưa hiệu chuẩn cũng được báo cáo.

7) Giải thích chính bộ phân loại được đánh giá (L5):
(a) Phân rã chính xác ℓ = ℓ_add + ℓ_int. Báo cáo tỷ lệ logit của mỗi dương tính đến từ số hạng tương tác.
(b) Gradient tích phân (Integrated Gradients) (50 bước, đường cơ sở = biểu hiện trung bình của tập huấn luyện) của ℓ_int theo 949 gen, cho quy kết gen đặc thù theo cặp. Tổng hợp chúng lên các bộ gen KEGG/GO-BP bằng tổng |IG| với một phân phối rỗng hoán vị (permutation null), thay vì qua tương quan + ORA.
(c) Quy kết nguyên tử = α_i × IG trên đặc trưng nguyên tử. Vì bộ đọc ra có điều kiện, các nguyên tử được làm nổi bật của thuốc a thay đổi theo đối tác b.
(d) Tính trung thực: đường cong xóa trên tập kiểm tra (chỉ để phân tích, không dùng để chọn). Che top-k gen (thay bằng trung bình của chúng) hoặc top-k nguyên tử (đặt nút bằng 0) với k ∈ {5, 10, 20, 50}. Đo mức giảm xác suất dự đoán và AUPR so với che ngẫu nhiên cùng k, và chạy kiểm tra hợp lý với trọng số ngẫu nhiên hóa. So sánh với chú ý GMP+GAT và SHAP trên mô hình cơ sở.
(e) Tính nhất quán theo thứ tự: quy kết dưới (a,b) và (b,a) giống hệt nhau theo cấu trúc. Với mô hình cơ sở, báo cáo tương quan Spearman giữa chúng.

Mặc định: Adam lr 1e-4 (các đầu dùng 3e-4), batch 512, suy giảm trọng số 1e-5, 50 epoch trên bộ chuẩn tập con, 150 epoch mỗi tập gấp trên bộ chuẩn đầy đủ, dừng sớm (early stopping) với độ kiên nhẫn (patience) 30 theo F1 kiểm định.

### Các hạn chế được giải quyết

L1, L2, L3, L8, L6, L5

### Tuyên bố về độ mới (Novelty claim)

So với DSimSynergy, yếu tố mới chính là một đầu ba tuyến tính thuốc×thuốc×tế bào hạng thấp, có cổng theo tế bào, được chứng minh là bất biến theo thứ tự. Nó nằm trên GCN tương đồng chức năng/lâm sàng và GAT phân tử, và tách chính xác mỗi logit thành một phần cộng tính và một phần tương tác có thể quy kết riêng. Yếu tố mới thứ hai là một bộ đọc ra nguyên tử có điều kiện theo ngữ cảnh, cho quy kết cấu trúc con đặc thù theo tổ hợp thay vì chú ý GAT theo từng thuốc. Thứ ba là huấn luyện với một hàm mất mát xếp hạng theo cặp có trọng số theo độ lớn Loewe và khai thác mẫu âm khó, cùng với CE và một hồi quy Loewe phụ trợ. Các mô hình hiệp đồng trước (DeepDDS, AttenSyn, JointSyn, HyperGraphSynergy) chỉ dùng các thành phần này riêng lẻ hoặc hoàn toàn không: hợp nhất song tuyến tính hoặc chú ý không có đối xứng chính xác, BCE thuần, và mô hình phân loại và hồi quy tách biệt. Không mô hình nào báo cáo tính trung thực qua đường cong xóa trên chính bộ phân loại được đánh giá.

### Kế hoạch triển khai (Implementation plan)

1) Bộ nạp dữ liệu (data loader) (script dataset trong Code/): bỏ tăng cường dữ liệu đảo thứ tự, hoặc chỉ giữ nó trên phần huấn luyện sau khi chia; với mô hình đối xứng thì nó đằng nào cũng thừa. Mang theo điểm Loewe s như một tensor thứ ba bên cạnh y. Cài đặt PositiveAwareBatchSampler đảm bảo ít nhất 16 dương tính mỗi batch 512.
2) models.py:
- Thay gộp cực đại toàn cục trong mô-đun GAT bằng ContextReadout(h_atoms, batch_idx, query) trả về g và α.
- Thêm DrugProj (concat→Linear→LayerNorm), FiLM(h_c) và SymTriHead(u_a, u_b, h_c) trả về (ℓ_add, ℓ_int, ŝ).
- forward() tính m_a và m_b (gộp trung bình) trước, sau đó tính bộ đọc ra của mỗi thuốc với truy vấn [m_partner ; h_c].
3) train.py: cài đặt loss = wCE + 0.5·rank_loss(logits, y, s) + 0.2·huber(ŝ, s'), trong đó rank_loss khai thác mẫu âm khó trong batch. Sau mỗi lượt kiểm định, khớp độ lệch δ bằng tìm kiếm lưới (grid search) trên các phân vị logit để tối đa hóa F1 kiểm định, rồi chọn checkpoint theo F1 đó. Sau khi huấn luyện, khớp T trên tập kiểm định bằng LBFGS và lưu T và δ vào checkpoint.
4) eval.py: áp dụng σ((ℓ+δ)/T), tính AUPR, AUROC, F1@0.5 và ACC@0.5 trên tập kiểm tra giữ lại, và lấy trung bình trên các mô hình của các tập gấp. Đồng thời ghi log F1@0.5 chưa hiệu chuẩn.
5) explain.py: dùng Captum IntegratedGradients trên ℓ_int theo biểu hiện tế bào và đặc trưng nguyên tử; tổng hợp lên các bộ gen KEGG từ các tài nguyên phân tích tăng cường hiện có; cài đặt đường cong xóa/chèn và kiểm tra trọng số ngẫu nhiên hóa; kiểm tra tính nhất quán theo thứ tự.
6) Thí nghiệm loại bỏ trên bộ chuẩn tập con (tập gấp 1, 50 epoch): mô hình cơ sở; +chỉ đầu đối xứng; +số hạng ba tuyến tính; +hàm mất mát xếp hạng; +hàm mất mát hồi quy; +hiệu chuẩn; +bộ đọc ra theo ngữ cảnh. Cách này quy mức cải thiện cho từng thành phần.

### Tác động dự kiến (Expected effect)

Đây là các tác động dự kiến trên tập kiểm tra nội bộ DrugCombDB; chưa cái nào được chạy.
- AUPR: từ 0.77 lên khoảng 0.80–0.83. Đóng góp chính sẽ là số hạng tương tác tường minh và hàm mất mát xếp hạng có trọng số theo độ lớn, cả hai đều đưa các hiệp đồng mạnh lên đầu bảng.
- F1: từ 0.74 lên khoảng 0.77–0.80, chủ yếu nhờ đặt ngưỡng đã hiệu chuẩn trên tập kiểm định, với phương sai giữa các tập gấp thấp hơn vì tính đối xứng loại bỏ nhiễu thứ tự.
- AUROC: từ 0.96 lên khoảng 0.96–0.97.
- ACC: khoảng 0.98, không đổi hoặc tăng nhẹ.
- Giải thích: đường cong xóa sẽ cho thấy mức giảm xác suất và AUPR lớn hơn đáng kể với các gen có IG cao nhất và các nguyên tử được quy kết cao nhất so với che ngẫu nhiên. Độ nhất quán theo thứ tự sẽ là 1.0, so với Spearman thấp hơn hẳn 1 ở mô hình cơ sở.

### Rủi ro (Risks)

- Hàm mất mát xếp hạng làm điểm số quá sắc. Hiệu chuẩn sẽ cho thấy điều này qua AUROC hoặc ACC giảm, hoặc độ lệch chọn trên tập kiểm định trở nên cực đoan. Giảm thiểu: hạ λ_rank xuống 0.2.
- Số hạng ba tuyến tính quá khớp với định danh thuốc khi chỉ có 83 dòng tế bào. Điều này sẽ biểu hiện thành khoảng cách huấn luyện–kiểm định tăng. Giảm thiểu: dropout trên P và Q, và giảm R xuống 32.
- Độ lệch chọn trên tập kiểm định có thể không chuyển được sang tập kiểm tra khi tập kiểm định có ít dương tính. Điều này sẽ biểu hiện thành F1 đã hiệu chuẩn không tốt hơn F1 chưa hiệu chuẩn. Cả hai đều được báo cáo.
- Bỏ tăng cường dữ liệu có thể làm giảm số mẫu hiệu dụng cho GAT. Nếu vậy, giữ tăng cường chỉ trên tập huấn luyện, vốn vô hại với mô hình đối xứng.
- Hồi quy Loewe có thể cạnh tranh với phân loại (chuyển giao âm (negative transfer)). Điều này sẽ biểu hiện thành AUPR thấp hơn khi thêm hàm mất mát hồi quy trong thí nghiệm loại bỏ; khi đó đặt λ_reg bằng 0.
- Chú ý nguyên tử có điều kiện theo ngữ cảnh có thể trở nên dàn trải và khó diễn giải hơn. Đường cong xóa sẽ cho thấy liệu nó có trung thực hay không.
- Phản bác có thể có về giao thức: độ lệch hiệu chuẩn được gộp vào mô hình, nhưng nó chỉ được khớp trên dữ liệu kiểm định. Các con số ngưỡng 0.5 chưa hiệu chuẩn cũng được báo cáo để minh bạch.

### Kiểm tra độ mới (Novelty check)

Tôi chấm ý tưởng này 4.5 trên 10. Nó kết hợp tốt các thành phần đã biết, nhưng thiết kế trung tâm của nó đã được công bố, chủ yếu trong RECOVER.

**Đã được công bố**
- **Đầu đối xứng, có điều kiện theo tế bào.** RECOVER (2022) có một mô-đun kết hợp bất biến hoán vị (tổng hợp đối xứng cộng một tensor song tuyến tính với các lát (slices) đối xứng), có điều kiện theo dòng tế bào qua FiLM. Về cơ bản đó là "đầu đối xứng + FiLM theo tế bào".
- **Số hạng tương tác thuốc×thuốc×tế bào hạng thấp.** DTF (2019) và comboFM (2020) đã mô hình hóa hiệp đồng như các tương tác phân rã tensor (tensor factorization) hạng thấp thuốc × thuốc × dòng tế bào.
- **Đối xứng chính xác thay cho tăng cường dữ liệu.** Bài báo GNN hiệp đồng diễn giải được (2021) đã đạt bất biến thứ tự chính xác bằng một bộ giải mã phân rã đối xứng (symmetric factorization decoder).
- **Chú ý nguyên tử có điều kiện theo đối tác và tế bào.** SDDSynergy, HSSynergy và CongFu đã cung cấp chú ý hoặc hợp nhất cấu trúc con có điều kiện theo đối tác và/hoặc tế bào. Bộ đọc ra nguyên tử có điều kiện theo ngữ cảnh là một biến thể của những mô hình này.

**Có vẻ mới**
Trong các tìm kiếm của tôi, tôi không thấy mô hình hiệp đồng nào dùng tất cả những điều sau:
- một hàm mất mát xếp hạng theo cặp có trọng số theo độ lớn Loewe, khai thác mẫu âm khó, bên cạnh CE có trọng số theo lớp và một hồi quy Loewe phụ trợ;
- một phép tách chính xác cộng tính so với tương tác của logit, với quy kết tính riêng trên số hạng tương tác;
- các phép thử tính trung thực (đường cong xóa, kiểm tra hợp lý với trọng số ngẫu nhiên hóa, tính nhất quán theo thứ tự) áp dụng cho chính bộ phân loại được đánh giá.

Đây là những đóng góp thực sự. Tuy nhiên, mỗi cái đều là kỹ thuật tiêu chuẩn được du nhập từ các công trình học xếp hạng (learning-to-rank) hoặc AI giải thích được (explainable AI). Việc khớp độ lệch quyết định trên dữ liệu kiểm định là thông lệ.

**Vì sao 4.5**
- Nó hơn một thủ thuật đơn lẻ hiển nhiên (3), vì được ghép lên xương sống GCN tương đồng của DSimSynergy và phần trung thực của giải thích là một sự kết hợp không tầm thường.
- Nó dưới 5–6 vì điểm mới được tuyên bố nổi bật nhất, "đầu song tuyến tính/ba tuyến tính có cổng theo tế bào, được chứng minh là bất biến thứ tự", đã được RECOVER đi trước rất sát.
- Các phần xếp hạng và trung thực có thể ít được khám phá hơn trong lĩnh vực này, nhưng các tìm kiếm của tôi chưa đầy đủ.

Để lập luận về độ mới, bài báo nên trích dẫn trực tiếp RECOVER, DTF và comboFM. Sau đó nên trình bày mục tiêu xếp hạng có tính đến độ lớn và các quy kết tương tác đã kiểm tra tính trung thực như những đóng góp chính, thay vì đầu đối xứng.

Các công trình trước gần nhất đã tìm thấy:

- RECOVER: sequential model optimization platform for combination drug repurposing identifies novel synergistic compounds in vitro (2022) https://arxiv.org/abs/2202.04202: Trùng cao với thiết kế đầu. RECOVER đã xây một mô-đun tổ hợp thuốc bất biến hoán vị từ tổng hợp đối xứng và một tensor song tuyến tính có các lát bị ràng buộc đối xứng, và nó điều kiện hóa mô hình theo dòng tế bào bằng FiLM. Điều đó bao quát phần cốt lõi của 'đầu song tuyến tính/ba tuyến tính đối xứng, có cổng theo tế bào cộng FiLM' của SymTri-Rank. RECOVER khác ở ba điểm: nó dùng hồi quy Bliss, không phải phân loại Loewe; nó không có hàm mất mát xếp hạng; và nó không có các GCN tương đồng GO/ATC hay phân rã quy kết.
- Interpretable Drug Synergy Prediction with Graph Neural Networks for Human-AI Collaboration in Healthcare (2021) https://arxiv.org/abs/2105.07082: Trùng vừa phải. Nó dùng một bộ giải mã phân rã đối xứng (u1^T D^T D u2), khiến điểm hiệp đồng của cặp thuốc bất biến theo thứ tự theo cấu trúc, và nó lập luận cho khả năng diễn giải. Đây là tiền lệ cho đối xứng chính xác thay cho tăng cường dữ liệu. Nó không có số hạng CP có cổng theo tế bào, không có hàm mất mát xếp hạng và không có phép thử tính trung thực.

<a id="limitations"></a>
## Các hạn chế của mức tiên tiến nhất hiện nay (8)

### L1. Ngưỡng cố định 0.5 và cross-entropy có trọng số theo lớp đơn thuần không phù hợp với ~3% dương tính (phương pháp luận (methodological))

Mô hình được huấn luyện bằng BCE/CE có trọng số theo lớp và đánh giá ở ngưỡng cố định 0.5. Trọng số lớp làm thay đổi thang đo của xác suất dự đoán, nên 0.5 không phải điểm vận hành tối ưu cho F1, và BCE tối ưu hóa hợp lý (likelihood) theo từng điểm thay vì mức độ các dương tính được xếp ở đầu bảng, vốn là điều AUPR đo lường. Điều này sẽ biểu hiện thành F1 (0.74) thấp hơn rõ rệt so với mức mà chất lượng xếp hạng (AUROC 0.96) cho phép, và thành phương sai F1 giữa các tập gấp. Một phương pháp tiếp theo có thể tối ưu trực tiếp vùng precision–recall (focal loss, một hàm mất mát thay thế (surrogate loss) theo cặp/AUC hoặc AP, hoặc khai thác mẫu âm khó) và chọn ngưỡng quyết định (hoặc hiệu chuẩn) chỉ trên tập gấp kiểm định. Việc chọn checkpoint theo F1 kiểm định ở 0.5 cũng khiến việc chọn mô hình phụ thuộc vào ngưỡng tùy ý này.

_Bằng chứng:_ "For computing ACC and F1, we applied a default decision threshold of 0.5 to the predicted probabilities"; bộ chuẩn: cross-entropy có trọng số theo lớp, checkpoint theo F1 kiểm định; AUPR 0.77 / F1 0.74 so với AUROC 0.96, ACC 0.98 ("these metrics were already approaching their upper bounds").

### L2. Hiệp đồng được mô hình hóa bằng ghép nối cộng MLP, không có số hạng tương tác thuốc–thuốc hay thuốc–tế bào tường minh (phương pháp luận)

Ba biểu diễn nhúng của mỗi thuốc và biểu diễn nhúng dòng tế bào chỉ đơn giản được ghép nối và đưa vào một FCNN. Theo định nghĩa, hiệp đồng là một tương tác phi cộng tính giữa hai thuốc trong một ngữ cảnh tế bào cụ thể. Ghép nối buộc MLP phải học ngầm các tương tác nhân và theo ngữ cảnh, điều đòi hỏi nhiều dữ liệu với lớp dương tính hiếm. Nó cũng không đưa ra lời giải thích diễn giải được về việc vì sao một cặp cụ thể tương tác. Một phương pháp tiếp theo có thể dùng các mô-đun tương tác tường minh: số hạng song tuyến tính hoặc phân rã tensor thuốc×thuốc×tế bào, chú ý chéo giữa các cấu trúc con của hai thuốc, hoặc gắn cổng có điều kiện theo tế bào (kiểu FiLM) cho biểu diễn nhúng thuốc. Những cách này sẽ cải thiện AUPR và F1, đặc biệt với các cặp có từng thuốc đều phổ biến nhưng hiệp đồng đặc thù theo ngữ cảnh, và sẽ bộc lộ các quy kết theo cặp.

_Bằng chứng:_ "These features are fused and concatenated through drug-drug-cell triplet combinations and input into the prediction module"; Hình 1D: "The concatenated vectors are input into FCNN for prediction".

### L3. Kiến trúc phụ thuộc vào thứ tự thuốc; tính đối xứng chỉ được khuyến khích qua tăng cường dữ liệu (phương pháp luận)

Do ghép nối, nói chung f(A,B,c) ≠ f(B,A,c). Các tác giả thêm các bộ ba đảo ngược vào dữ liệu huấn luyện thay vì xây dựng sẵn tính bất biến hoán vị, và họ không đối xứng hóa lúc kiểm tra. Kết quả là dự đoán và quy kết cho cùng một cặp có thể khác nhau tùy thứ tự đầu vào. Tăng cường dữ liệu trước phép chia 9:1 cũng có thể để các bản đảo chiều (B,A,c) của bộ ba kiểm tra lọt vào tập huấn luyện. Một bộ mã hóa cặp bất biến hoán vị (tổng/tích, hoặc dạng song tuyến tính đối xứng) hoặc lấy trung bình cả hai thứ tự khi suy luận (inference) sẽ làm cho dự đoán và quy kết SHAP nhất quán theo thứ tự, và được kỳ vọng giảm phương sai trên tập giữ lại.

_Bằng chứng:_ "each drug triplet (Drug A, Drug B, Cell line) was augmented by including its reverse ordering ... such that the model learns symmetric representations regardless of input order. Data were partitioned into training and test sets at a 9:1 ratio".

### L4. Bộ mã hóa dòng tế bào bỏ qua đích tác dụng thuốc và cấu trúc đường truyền; giải thích đường truyền là tương quan hậu nghiệm (phương pháp luận)

Dòng tế bào được mã hóa bằng một lớp FC duy nhất trên 949 gen L1000, độc lập với các thuốc đang được kết hợp. Gen đích của thuốc chỉ đi vào gián tiếp, qua trọng số tương đồng BP-Jaccard, và không bao giờ được nối với biểu hiện của các gen đích trong dòng tế bào đó. Giải thích gen và đường truyền được tạo ra sau đó: giá trị SHAP được tính tương quan với biểu hiện, và các gen có PCC > 0.5 được đưa vào ORA dựa trên kiểm định siêu bội (hypergeometric). Kiến trúc không có cấu trúc đường truyền, nên các giải thích KEGG là một bản tóm tắt thống kê ở giai đoạn hai chứ không phải cơ chế trung thực của mô hình. Một phương pháp tiếp theo có thể dùng bộ mã hóa tế bào có nhận biết đích và có cấu trúc đường truyền: các đơn vị nút cổ chai (bottleneck units) theo bộ gen KEGG hoặc GO, với biểu hiện được gắn cổng hoặc chú ý bởi đích của mỗi thuốc và vùng lân cận mạng của chúng. Điều này cho quy kết đường truyền có sẵn, đặc thù theo cặp thuốc, và thiên kiến quy nạp tốt hơn cho chế độ chỉ có 83 dòng tế bào.

_Bằng chứng:_ Phương trình (10): h = σ(W(1)x + b(1)) trên 949 gen; "we computed the correlation between gene expression values and their corresponding SHAP values"; "KEGG pathway enrichment analysis using hypergeometric test-based ORA on genes with positive correlations greater than 0.5".

### L5. Giải thích đến từ một mô hình khác (hồi quy) so với bộ phân loại được đánh giá, và tính trung thực chưa bao giờ được kiểm tra (đánh giá (evaluation))

Phân tích SHAP gen và đường truyền được chạy trên mô hình hồi quy điểm hiệp đồng, và các thuốc trong ca nghiên cứu được chọn dựa trên điểm dự đoán của mô hình hồi quy. Bản thân bộ phân loại được đánh giá chuẩn chưa bao giờ được giải thích. Không có phép thử tính trung thực định lượng nào được báo cáo, như đường cong xóa/chèn, loại bỏ các gen có SHAP cao nhất hoặc các nguyên tử có chú ý cao nhất, hay kiểm tra hợp lý với trọng số ngẫu nhiên hóa. Tính hợp lý chỉ được lập luận qua các giai thoại từ tài liệu. Một phương pháp tiếp theo nên giải thích trực tiếp bộ phân loại và báo cáo các chỉ số trung thực (ví dụ, mức giảm AUPR hoặc xác suất dự đoán khi che top-k gen, đường truyền hoặc nguyên tử được quy kết, so với che ngẫu nhiên). Điều này cũng cho một cách đo lường để chứng minh các giải thích trung thực hơn.

_Bằng chứng:_ "we employed SHAP ... to interpret cell line features within our synergy score prediction model (see Supplementary Note 6)"; "drug combinations were screened and selected based on their synergy scores, which were predicted by the DSimSynergy model".

### L6. Chú ý GAT với gộp cực đại toàn cục là quy kết cấu trúc con không đáng tin cậy (phương pháp luận)

Đặc trưng thuốc ở mức đồ thị dùng gộp cực đại toàn cục theo từng phần tử, nên mỗi chiều đầu ra được quyết định bởi một nguyên tử duy nhất và phần lớn nguyên tử nhận gradient bằng 0. Hệ số chú ý GAT mô tả cách các láng giềng được gán trọng số khi truyền thông điệp (message passing) giữa các nguyên tử, chứ không phải mức đóng góp của mỗi nguyên tử vào dự đoán hiệp đồng. Bài báo chỉ hiển thị các nguyên tử có điểm chú ý lớn hơn 1 cho hai thuốc. Chú ý cũng được tính theo từng thuốc, độc lập với thuốc đối tác và dòng tế bào, nên không thể cho thấy cấu trúc con nào quan trọng với tổ hợp cụ thể này. Các bộ đọc ra dựa trên chú ý hoặc có cổng, có điều kiện theo thuốc đối tác và tế bào, các quy kết tính bằng gradient tích phân hoặc che khuất (occlusion), và một phép thử trung thực bằng che cấu trúc con sẽ giải quyết điều này. Bộ đọc ra phong phú hơn cũng có thể giúp AUPR.

_Bằng chứng:_ Phương trình (9): h_graph = max_i h'_i (GMP); "Attention weight visualization of drug molecular substructures ... (only atoms with scores greater than 1 are shown)"; GAT áp dụng theo từng thuốc, rồi ghép nối.

### L7. GCN trên các mạng tương đồng giả định tính đồng loại mà dữ liệu chỉ ủng hộ yếu (lý thuyết (theoretical))

GCN dùng lan truyền chuẩn hóa đối xứng (Phương trình 5) trên các đồ thị tương đồng BP và ATC, làm trơn đặc trưng MACCS của mỗi thuốc về phía các láng giềng tương đồng. Tuy nhiên, độ tương đồng theo cặp chỉ tương quan yếu với hiệp đồng trung bình (PCC 0.21 với BP, 0.23 với ATC), và chính tính bổ sung đường truyền chứ không phải độ tương đồng mới là cơ chế mà các tác giả viện dẫn. Làm trơn đồng nhất có thể làm mờ các đặc trưng phân biệt những thuốc bổ sung cho nhau. Đóng góp của láng giềng cũng không được bộc lộ dưới dạng giải thích. Trọng số cạnh được học hoặc chú ý trên các mạng tương đồng (kiểu GAT, hoặc cho phép thông điệp âm/dị loại) sẽ cho phép mô hình quyết định láng giềng nào quan trọng và cho ra quy kết ở mức láng giềng. Mức cải thiện sẽ xuất hiện dưới dạng AUPR tốt hơn trên các cặp thuốc không tương đồng nhưng hiệp đồng.

_Bằng chứng:_ "significant positive correlations for both the similarity network based on biological process (PCC = 0.21...) and ... ATC (PCC = 0.23...)"; "drugs form a 'pathway complementarity network' by targeting distinct but interconnected signaling pathways"; Phương trình (5), với ma trận kề A cố định.

### L8. Mô hình phân loại và hồi quy được huấn luyện riêng, nên bộ phân loại không bao giờ thấy điểm Loewe liên tục (phương pháp luận)

Bài toán nhị phân bỏ đi độ lớn của điểm Loewe: các bộ ba có điểm 11 và điểm 80 nhận cùng một nhãn. Các bộ ba trong khoảng (0,10] bị loại hoàn toàn, và mô hình hồi quy được huấn luyện riêng. Độ lớn hiệp đồng là một tín hiệu xếp hạng phong phú cho lớp dương tính hiếm mà bộ phân loại không bao giờ dùng. Huấn luyện đa nhiệm (multi-task training), với một bộ mã hóa dùng chung, đầu phân loại và một đầu hồi quy hoặc xếp hạng Loewe phụ trợ trên cùng các bộ ba huấn luyện (nhãn và phép chia giữ nguyên), có thể cải thiện thứ tự của các dương tính và do đó cải thiện AUPR. Nó cũng sẽ làm cho quy kết gen và đường truyền nhất quán giữa hai nhiệm vụ.

_Bằng chứng:_ "For the binary synergy classification task ... optimized using binary cross-entropy loss. For the synergy score prediction task ... optimized using mean squared error loss"; bài báo mô tả chúng là "two distinct prediction tasks".
