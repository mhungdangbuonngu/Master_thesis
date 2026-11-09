# TỔNG QUAN TÀI LIỆU NGHIÊN CỨU (LITERATURE REVIEW): TRÍ TUỆ NHÂN TẠO CÓ KHẢ NĂNG GIẢI THÍCH TRONG DỰ ĐOÁN HIỆP ĐỒNG THUỐC (EXPLAINABLE AI IN DRUG SYNERGY PREDICTION)

---

## 1. Giới thiệu & Đặt vấn đề (Introduction & Problem Statement)

### 1.1. Bối cảnh Y sinh của Liệu pháp Phối hợp Thuốc (Combinatorial Drug Therapy)
Trong điều trị các bệnh lý phức tạp như ung thư, nhiễm trùng kháng thuốc hay rối loạn tự miễn, liệu pháp đơn trị (monotherapy) thường xuyên đối mặt với ba rào cản lớn: **(1) Cơ chế kháng thuốc mắc phải (acquired resistance)** thông qua việc tế bào kích hoạt các đường truyền tín hiệu dự phòng (compensatory/bypass pathways); **(2) Độc tính phụ thuộc liều (dose-limiting toxicity)** khi phải dùng nồng độ cao để đạt hiệu quả lâm sàng; và **(3) Tính không đồng nhất của khối u (tumor heterogeneity)**. 

Liệu pháp phối hợp thuốc tạo ra **hiệu ứng hiệp đồng (Drug Synergy)** — trạng thái mà hiệu quả ức chế tế bào của tổ hợp thuốc lớn hơn đáng kể so với tổng hiệu quả cộng gộp của từng thuốc riêng lẻ — đã trở thành trụ cột của y học chính xác (Precision Oncology). Tuy nhiên, không gian tổ hợp của hàng nghìn hợp chất hóa học trên hàng trăm phân nhóm di truyền bệnh nhân là quá lớn để sàng lọc hoàn toàn bằng thực nghiệm *in vitro* (High-Throughput Screening - HTS) hay *in vivo*.

### 1.2. Sự trỗi dậy của Học sâu và Bài toán "Hộp đen" (The Black-Box Dilemma)
Kể từ sự ra đời của các mô hình tiên phong như **DeepSynergy** (Preuer et al., 2018), các kiến trúc Học sâu (Deep Learning - DL) đã đạt được bước nhảy vọt về độ chính xác dự đoán (AUC, Pearson $r$, MSE) so với các phương pháp học máy truyền thống. Tuy nhiên, nghịch lý lớn nhất ngăn cản việc chuyển dịch các mô hình này vào thử nghiệm lâm sàng là tính chất **"Hộp đen" (Black-box)**.

Trong dược lý hệ thống, một con số dự đoán điểm hiệp đồng cao (ví dụ: điểm Loewe hay Bliss dương cao) mà không đi kèm lời giải thích cơ chế phân tử (Mechanism of Action - MoA) sẽ không có giá trị chuyển giao lâm sàng vì các lý do sau:
1. **Hiện tượng học vẹt và Rò rỉ đặc trưng (Shortcut Learning & Confounding Factors):** Mô hình hộp đen rất dễ học các tương quan giả (spurious correlations) từ nhiễu thực nghiệm hoặc chỉ nhớ tên thuốc phổ biến thay vì học quy luật tương tác sinh hóa thực sự.
2. **Yêu cầu xác thực mục tiêu sinh học (Target & Biomarker Validation):** Các nhà sinh học thực nghiệm cần biết *nhóm chức hóa học nào* (pharmacophore) tương tác với *protein đích nào*, và *dấu ấn sinh học (biomarker) nào* của bệnh nhân quyết định sự nhạy cảm với tổ hợp thuốc đó.
3. **Phân biệt Hiệp đồng trị liệu và Hiệp đồng độc tính (Therapeutic vs. Toxic Synergy):** Hai thuốc có thể cùng tiêu diệt tế bào mạnh mẽ trên đĩa nuôi cấy chỉ vì chúng khuếch đại độc tính chéo không đặc hiệu (off-target toxicity), gây nguy hiểm tính mạng nếu thử nghiệm trên người.

Do đó, **Explainable AI (XAI) trong Drug Synergy** không chỉ là một công cụ bổ trợ để trực quan hóa mô hình, mà đã trở thành một yêu cầu bắt buộc nhằm bắc cầu giữa *Khoa học máy tính* và *Sinh học hệ thống (Systems Biology)*.

---

## 2. Cơ sở Toán học về Định lượng Hiệp đồng và Biểu diễn Dữ liệu

### 2.1. Các Mô hình Tham chiếu Không tương tác (Null Reference Models)
Điểm hiệp đồng $S$ của hai thuốc $A$ và $B$ tại nồng độ $(d_A, d_B)$ luôn được định nghĩa là độ lệch giữa hiệu ứng thực nghiệm quan sát được $E_{AB}$ và hiệu ứng kỳ vọng $E_{\text{expected}}$ nếu hai thuốc không tương tác:

$$S = E_{AB} - E_{\text{expected}}$$

Bốn mô hình toán học chuẩn được sử dụng trong hầu hết các bộ dữ liệu hiện nay bao gồm:
*   **Loewe Additivity:** Giả định hai thuốc có cùng cơ chế tác động (một thuốc chỉ là phiên bản pha loãng của thuốc kia). Phương trình Loewe:
    $$\frac{d_A}{D_A(E_{\text{Loewe}})} + \frac{d_B}{D_B(E_{\text{Loewe}})} = 1$$
    *(Trong đó $D_A(E)$ và $D_B(E)$ là nồng độ đơn thuốc cần thiết để tạo ra hiệu ứng $E$).*
*   **Bliss Independence:** Giả định hai thuốc hoạt động độc lập theo xác suất thống kê thông qua các cơ chế sinh học tách biệt:
    $$E_{\text{Bliss}} = E_A + E_B - E_A E_B$$
*   **HSA (Highest Single Agent):** Giả định hiệu ứng kỳ vọng chỉ bằng hiệu ứng của thuốc mạnh hơn:
    $$E_{\text{HSA}} = \max(E_A, E_B)$$
*   **ZIP (Zero Interaction Potency):** Kết hợp ưu điểm của Loewe và Bliss bằng cách so sánh sự dịch chuyển đường cong liều - đáp ứng (dose-response curves) của từng thuốc khi có mặt thuốc kia.

### 2.2. Các Bộ dữ liệu Chuẩn (Benchmark Datasets)
*   **O'Neil (Merck Dataset, 2016):** 22.737 mẫu thực nghiệm từ 38 thuốc trên 39 dòng tế bào ung thư.
*   **NCI-ALMANAC (2017):** Hơn 300.000 thí nghiệm cặp thuốc từ 104 thuốc đã được FDA phê duyệt trên 60 dòng tế bào thuộc bộ NCI-60.
*   **AstraZeneca-Sanger DREAM Challenge (2019):** Tập trung mạnh vào tính khả giải cơ chế với 11.576 thí nghiệm từ 118 thuốc trên 85 dòng tế bào có hồ sơ đa hệ gen (multi-omics) đầy đủ.
*   **DrugComb & DrugCombDB:** Cơ sở dữ liệu tích hợp lớn nhất hiện nay (>700.000 tổ hợp chuẩn hóa đồng thời cả 4 điểm Loewe, Bliss, HSA, ZIP và điểm nhạy cảm CSS).

---

## 3. Phân loại Hệ thống (Taxonomy) các Phương pháp XAI trong Drug Synergy

Dựa trên kiến trúc mô hình và thời điểm trích xuất lời giải thích, các nghiên cứu XAI trong dự đoán hiệp đồng thuốc được chia thành **5 phân nhóm chính**:

1.  **Nhóm 1: Giải thích hậu kỳ quy gán đặc trưng (Post-hoc Feature Attribution XAI)**
2.  **Nhóm 2: Cơ chế Chú ý Nội tại Đa phương thức (Intrinsic Multi-modal Attention XAI)**
3.  **Nhóm 3: Giải thích trên Đồ thị Phân tử & Mạng lưới Sinh học Dị cấu (Graph & Network Path XAI)**
4.  **Nhóm 4: Mạng Nơ-ron Khả kiến định hướng Sinh học (Biologically-Informed Visible Neural Networks - VNN)**
5.  **Nhóm 5: Mô hình Ngôn ngữ Lớn & Đồ thị Tri thức Nhân quả (LLM, RAG & Causal Knowledge Graphs)**

---

## 4. Phân tích Chuyên sâu từng Nhánh Nghiên cứu & Các Bài báo Kinh điển

### 4.1. Nhóm 1: Giải thích Hậu kỳ Quy gán Đặc trưng (Post-hoc Feature Attribution)
Nhóm phương pháp này coi mô hình dự đoán $f(x)$ là một hộp đen (Gradient Boosting Trees hoặc Deep MLP) và sử dụng các kỹ thuật nhiễu loạn (perturbation) hoặc đạo hàm tích phân (backpropagation/Shapley values) sau khi huấn luyện để định lượng đóng góp $\phi_i$ của từng đặc trưng đầu vào $x_i$.

#### Các nghiên cứu tiêu biểu:
*   **TreeCombo (Janizek et al., *Bioinformatics*, 2018):**
    *   *Kiến trúc & Phương pháp:* Sử dụng thuật toán Extreme Gradient Boosting (XGBoost) kết hợp với **TreeSHAP** (Lundberg & Lee). Đầu vào là vector ghép nối của đặc trưng phân tử thuốc (MACCS/Morgan fingerprints + đích nhắm gen) và biểu hiện gen của dòng tế bào.
    *   *Cơ chế toán học XAI:* Tính giá trị Shapley chính xác trong thời gian đa thức trên cấu trúc cây:
        $$\phi_i(f, x) = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!(|F| - |S| - 1)!}{|F|!} \left[ f_x(S \cup \{i\}) - f_x(S) \right]$$
    *   *Giá trị sinh học:* Xác định được các gen đóng vai trò dấu ấn sinh học cục bộ cho từng bệnh nhân/dòng tế bào và tính toán ma trận tương tác bậc hai (**SHAP Interaction Values**) giữa đặc trưng thuốc và biểu hiện gen.
*   **MARSY (El Khili et al., *Bioinformatics*, 2023):**
    *   *Kiến trúc & Phương pháp:* Mô hình học sâu đa nhiệm (Multitask Deep Learning) dự đoán đồng thời điểm hiệp đồng ZIP và hiệu ứng đơn thuốc. Sử dụng phương pháp quy gán độ dốc tích phân (**Integrated Gradients**) để xếp hạng tầm quan trọng của hàng nghìn gen biểu hiện.
*   **SHAP-based Chemical-Biological DNN (IEEE BigDataService, 2025/2026):**
    *   *Kiến trúc & Phương pháp:* Thay thế các vector băm (hashed fingerprints) vô nghĩa về mặt sinh học bằng các tập đặc trưng có tên định danh rõ ràng (named functional groups & targeted pathways), sau đó dùng **DeepSHAP** để đối chiếu cơ chế hiệp đồng của các cặp như *Methotrexate + BEZ-235* với y văn lâm sàng.

#### Đánh giá Phê bình (Critical Analysis - Nhóm 1):
*   **Ưu điểm:** Có nền tảng lý thuyết trò chơi vững chắc (tính cộng tính địa phương, tính nhất quán); dễ cài đặt và không làm giảm hiệu năng dự đoán của mô hình gốc.
*   **Nhược điểm chí mạng (Sự sụp đổ của giả thuyết độc lập đặc trưng):** Trong sinh học, biểu hiện của các gen có sự tương quan đồng tuyến tính cực cao (co-expression modules). Khi áp dụng SHAP hoặc LIME lên không gian biểu hiện gen (>10.000 chiều), thuật toán thường chia nhỏ điểm quan trọng cho các gen tương quan hoặc tạo ra các mẫu giả tạo phi sinh học (unrealistic out-of-distribution perturbations), dẫn đến việc chỉ ra các gen "đi kèm" (passenger genes) thay vì gen điều khiển thực sự (driver genes).

---

### 4.2. Nhóm 2: Cơ chế Chú ý Nội tại Đa phương thức (Intrinsic Multi-modal Attention XAI)
Thay vì giải thích hậu kỳ, nhóm này nhúng trực tiếp các lớp **Self-Attention**, **Cross-Attention** hoặc **Bilinear Attention** vào kiến trúc mạng để mô hình tự động gán trọng số tương tác giữa các nguyên tử hóa học (Atoms/Substructures) và các đặc trưng bộ gen (Genes).

#### Các nghiên cứu tiêu biểu:
*   **DeepDDS (Wang et al., *Briefings in Bioinformatics*, 2022):**
    *   *Kiến trúc & Phương pháp:* Biểu diễn phân tử thuốc dưới dạng đồ thị 2D $G_{\text{drug}} = (V_{\text{atom}}, E_{\text{bond}})$ và đưa qua mạng **Graph Attention Network (GAT)** hoặc GCN; biểu hiện gen đưa qua MLP.
    *   *Cơ chế XAI:* Trích xuất hệ số chú ý $\alpha_{ij}$ giữa các nguyên tử lân cận trong phân tử thuốc:
        $$\alpha_{ij} = \text{softmax}_j \left( \text{LeakyReLU}\left( \mathbf{a}^T [\mathbf{W}h_i \parallel \mathbf{W}h_j] \right) \right)$$
        Bằng cách chiếu trọng số $\alpha_{ij}$ lên cấu trúc 2D của thuốc, DeepDDS làm nổi bật các nhóm chức hóa học (chemical substructures/pharmacophores) chịu trách nhiệm chính cho phản ứng hiệp đồng.
*   **DTSyn (Hu et al., *Briefings in Bioinformatics*, 2022):**
    *   *Kiến trúc & Phương pháp:* Thiết kế kiến trúc **Dual-Transformer** gồm 2 nhánh song song:
        1. *Fine-granularity Transformer:* Tính Cross-Attention chi tiết giữa từng nguyên tử của Thuốc A, nguyên tử của Thuốc B và vector nhúng của từng Gen riêng lẻ.
        2. *Coarse-granularity Transformer:* Tính tương tác ở cấp độ toàn cục (Whole-drug representation vs. Whole-cell line representation).
    *   *Cơ chế XAI:* Ma trận chú ý $\mathbf{A} = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}}\right)$ cho phép truy vết trực tiếp xem nguyên tử nào của thuốc đang tương tác ngầm với gen đích nào của tế bào ung thư.
*   **AttenSyn (Wang et al., *J. Chem. Inf. Model.*, 2024) & HypergraphSynergy (Liu et al., 2022):**
    *   Sử dụng cơ chế *Attention-based Graph Pooling* và *Bilinear Attention Network (BAN)* để nắm bắt tương tác bậc ba (Tri-linear interaction: Drug A – Drug B – Cell line) mà không làm mất tính bất biến hoán vị (permutation invariance) giữa Thuốc A và Thuốc B.

#### Đánh giá Phê bình (Critical Analysis - Nhóm 2):
*   **Ưu điểm:** Có khả năng giải thích trực tiếp trên cấu trúc đồ thị phân tử 2D/3D (điều mà SHAP trên vector băm khó làm được); chi phí trích xuất lời giải thích bằng $O(1)$ ngay trong bước suy luận (forward pass).
*   **Nhược điểm ("Attention is not Explanation"):** Nhiều nghiên cứu lý thuyết đã chứng minh trọng số Attention thường phản ánh mức độ pha trộn thông tin trong không gian ẩn hơn là mối quan hệ nhân quả (causal attribution). Hơn nữa, việc kết nối trực tiếp từ *Nguyên tử thuốc* sang *Biểu hiện mRNA của gen* thông qua một phép nhân ma trận Attention là một sự "nhảy cóc sinh học" — bởi thuốc trong thực tế gắn kết với cấu trúc không gian 3D của **Protein**, sau đó tín hiệu mới truyền qua mạng lưới PPI để làm thay đổi biểu hiện mRNA.

---

### 4.3. Nhóm 3: Giải thích trên Mạng lưới Sinh học & Đồ thị Dị cấu (Graph & Network Path XAI)
Để khắc phục điểm yếu "nhảy cóc sinh học" của Nhóm 2, Nhóm 3 tích hợp trực tiếp **Mạng tương tác Protein-Protein (PPI Network)** và **Mạng tương tác Thuốc - Đích (Drug-Target Interaction - DTI)** vào mô hình để tìm ra **đường đi truyền tín hiệu (signaling paths)** hoặc **đồ thị con (subgraphs)** giải thích cơ chế.

#### Các nghiên cứu tiêu biểu:
*   **TranSynergy (Liu & Xie, *PLOS Computational Biology*, 2021):**
    *   *Mã hóa Mạng PPI:* Áp dụng thuật toán **Random Walk with Restart (RWR)** trên mạng PPI (STRING) để lan truyền vector đích nhắm thuốc $p^{(0)}$ thành hồ sơ ảnh hưởng toàn mạng $p^{(\infty)} = \alpha(I - (1-\alpha)W)^{-1}p^{(0)}$.
    *   *Cơ chế XAI (SA-GSEA):* Đóng góp đột phá của TranSynergy là đề xuất quy trình **Shapley Additive Gene Set Enrichment Analysis (SA-GSEA)**. Thay vì dừng lại ở điểm SHAP của từng gen đơn lẻ (dễ bị nhiễu), bài báo dùng điểm SHAP của toàn bộ 2.401 gen để chạy kiểm định làm giàu tập gen (GSEA) trên cơ sở dữ liệu **Reactome Pathways**, từ đó giải mã chính xác các con đường sinh học điều khiển tính hiệp đồng.
*   **GraphSynergy (Yang et al., *JAMIA*, 2021):**
    *   *Kiến trúc & Phương pháp:* Áp dụng **Spatial-based GCN có trọng số Attention** trên các vùng lân cận $k$-hop ($\mathcal{M}_i^{(h)}$) xung quanh đích tác dụng của Thuốc A, Thuốc B và các protein đặc trưng của Dòng tế bào trên mạng PPI.
    *   *Cơ chế XAI:* Định nghĩa tường minh hai hàm điểm số trong không gian nhúng:
        *   **Therapy Score:** Đo mức độ tổ hợp thuốc bao phủ vùng mạng PPI gây bệnh của tế bào ung thư.
        *   **Toxicity Score:** Đo mức độ chồng lấn trực tiếp quá mức giữa hai vùng ảnh hưởng PPI của hai thuốc (cảnh báo độc tính cộng gộp).
*   **MGAE-DC (2022), HANSynergy (*J. Chem. Inf. Model.*, 2024) & SDCInterpreter (*J. Chem. Inf. Model.*, 2025):**
    *   **HANSynergy:** Xây dựng Đồ thị Dị cấu (Heterogeneous Graph) và dùng cơ chế **Meta-path Attention** (ví dụ: $\text{Drug} \rightarrow \text{Protein} \rightarrow \text{Pathway} \rightarrow \text{Cell line}$) để lượng hóa tầm quan trọng của từng loại ngữ nghĩa liên kết.
    *   **SDCInterpreter (2025):** Xây dựng đồ thị có hướng 5 tầng (*Virtual Node $\rightarrow$ Drug $\rightarrow$ Target Gene $\rightarrow$ Biological Pathway $\rightarrow$ Cell line*) và áp dụng kỹ thuật **Learnable Edge Masking** (tương tự *GNNExplainer* tối ưu hóa hàm thông tin tương hỗ $\max_{G_S} MI(Y, G_S)$) để trích xuất các cây đường dẫn nhân quả giải thích vì sao hai thuốc hiệp đồng.

#### Đánh giá Phê bình (Critical Analysis - Nhóm 3):
*   **Ưu điểm:** Bám sát nguyên lý của Dược lý mạng (Network Pharmacology) — đặc biệt là lý thuyết *"Complementary Exposure"* (Cheng et al., *Nature Communications*, 2019), giải thích được cả hai cơ chế: đánh chặn song song (Synthetic Lethality) và đánh chặn nối tiếp.
*   **Nhược điểm:** Phụ thuộc nặng nề vào tính đầy đủ của dữ liệu DTI và PPI đã biết. Đối với các hợp chất hóa học mới hoàn toàn (novel compounds / cold-start drugs) chưa từng được xác định protein đích thực nghiệm ($p^{(0)} = \vec{0}$), các mô hình như TranSynergy hay GraphSynergy sẽ mất khả năng khởi tạo trên mạng PPI. Ngoài ra, mạng PPI tiêu chuẩn (như STRING) là đồ thị tĩnh, không phân biệt đặc thù mô (tissue-agnostic) và thường thiếu chiều hướng tác động (kích hoạt $\rightarrow$ hay ức chế $\dashv$).

---

### 4.4. Nhóm 4: Mạng Nơ-ron Khả kiến Định hướng Sinh học (Biologically-Informed Visible Neural Networks - VNN)
Đây là trường phái **White-box XAI (Giải thích nội tại tuyệt đối)**. Thay vì dùng các lớp ẩn kết nối đầy đủ (Fully Connected Layers) vô nghĩa, toàn bộ cấu trúc liên kết giữa các nơ-ron trong mạng được ép buộc (masked) theo đúng cấu trúc phân cấp của hệ thống sinh học (Gene Ontology hoặc KEGG/Reactome Pathways).

#### Các nghiên cứu tiêu biểu:
*   **DrugCell (Kuenzi et al., *Cancer Cell*, 2020):**
    *   *Kiến trúc VNN:* Hệ thống phân cấp **Gene Ontology (GO)** gồm hơn 2.000 thuật ngữ sinh học (từ cấp độ phân tử nhỏ như *DNA repair* đến cấp độ tế bào lớn như *Apoptosis*) được dùng làm khung xương cho mạng nơ-ron. Mỗi GO term được biểu diễn bởi một cụm $k$ nơ-ron ẩn; kết nối chỉ tồn tại giữa các gen và GO term con, hoặc giữa GO term con và GO term cha theo đúng đồ thị có hướng không chu trình (DAG) của sinh học.
    *   *Chỉ số lượng hóa XAI (RLIPP - Relative Local Improvement in Predictive Power):* Để xác định con đường sinh học $p$ nào thực sự điều khiển phản ứng thuốc, DrugCell huấn luyện các mô hình hồi quy tuyến tính cục bộ (Ridge regression) từ trạng thái kích hoạt của node cha $I(p)$ và các node con $I(c_p)$ tới đầu ra, sau đó tính tỷ số:
        $$\text{RLIPP}(p) = \frac{\rho_{\text{parent}}(p) - \rho_{\text{children}}(p)}{\rho_{\text{children}}(p)}$$
        Một giá trị RLIPP cao chứng tỏ tổ hợp phi tuyến tính tại node sinh học $p$ mang lại sức mạnh dự đoán vượt trội so với từng thành phần con cộng lại — từ đó gợi ý trực tiếp việc kết hợp hai thuốc nhắm vào hai nhánh có RLIPP cao nhất (ví dụ: *Paclitaxel + JQ1*).
*   **PathDNN (Deng et al., *J. Chem. Inf. Model.*, 2020) & SynPathy (Tang & Gottlieb, *Briefings in Bioinformatics*, 2022):**
    *   Sử dụng ma trận mặt nạ nhị phân $\mathbf{M} \in \{0, 1\}^{N_{\text{genes}} \times N_{\text{pathways}}}$ lấy từ cơ sở dữ liệu **KEGG** để cắt bỏ mọi trọng số kết nối không có thật về mặt sinh học ($\mathbf{W}_{\text{masked}} = \mathbf{W} \odot \mathbf{M}$).
*   **DIPx (Nguyen et al., *eLife*, 2024/2025):**
    *   Mô hình hóa **Điểm hoạt hóa lộ trình (Pathway Activation Score - PAS)** bằng cách chia mạng lưới sinh học thành 3 phân vùng rõ rệt: *Upstream genes* (gen thượng nguồn), *Downstream genes* (gen hạ nguồn) và *Driver mutations* (đột biến dẫn dắt), cho phép giải thích cá thể hóa trên từng bệnh nhân.

#### Đánh giá Phê bình (Critical Analysis - Nhóm 4):
*   **Ưu điểm:** Độ tin cậy y sinh học cao nhất trong tất cả các nhánh; mỗi nơ-ron ẩn đều có tên gọi sinh học cụ thể, loại bỏ hoàn toàn sự mơ hồ của việc giải thích hậu kỳ.
*   **Nhược điểm (Sự đánh đổi giữa Tính khả giải và Khả năng phát hiện tri thức mới):** Vì cấu trúc mạng bị khóa cứng theo tri thức sinh học hiện có (GO/KEGG), mô hình VNN bị giới hạn dung lượng biểu diễn (inductive bias quá chặt) và **không thể phát hiện ra các tương tác đường chéo mới chưa từng được ghi nhận trong y văn** (unannotated cross-talk pathways).

---

### 4.5. Nhóm 5: Mô hình Ngôn ngữ Lớn, RAG & Đồ thị Tri thức Nhân quả (LLM & Knowledge Graph XAI - Xu hướng 2024–2026)
Sự bùng nổ của Foundation Models và Large Language Models (LLMs) trong y sinh đang định hình lại cách giải thích Drug Synergy từ dạng *trọng số số học* sang dạng *lập luận nhân quả ngôn ngữ tự nhiên (Mechanistic Reasoning)*.

#### Các nghiên cứu tiêu biểu:
*   **KG-Synergy (Zhang et al., *Briefings in Bioinformatics*, 2023) & BioKG-XAI:**
    *   Trích xuất các chuỗi suy luận đa bước (Multi-hop reasoning chains) trên Đồ thị tri thức sinh học lớn (như Hetionet, DRKG).
*   **CancerGPT (Li et al., *npj Digital Medicine*, 2024) & Mechanistically Explainable LLM+RAG Framework (MDPI *Curr. Oncol.*, 2025):**
    *   Kết hợp mô hình ngôn ngữ lớn với **Retrieval-Augmented Generation (RAG)** truy xuất trực tiếp từ PubMed, ClinicalTrials.gov và Knowledge Graphs để vừa dự đoán hiệu quả hiệp đồng trên các mô hiếm gặp (few-shot learning), vừa sinh ra báo cáo giải thích cơ chế dược động học/dược lực học hoàn chỉnh.

---

## 5. Bảng Đối sánh Tổng hợp các Kiến trúc XAI Tiêu biểu

| Tên Mô hình (Năm) | Phân nhóm XAI | Đầu vào Thuốc (Drug Input) | Đầu vào Sinh học (Cell/Bio Input) | Kỹ thuật Giải thích Cốt lõi | Cấp độ Giải thích (Granularity) | Hạn chế Chính |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TreeCombo** (2018) | Post-hoc Attribution | Morgan Fingerprints + Drug Targets | Gene Expression | **TreeSHAP** & SHAP Interaction Values | Từng Gen & Đặc trưng hóa học | Nhạy cảm với hiện tượng đa cộng tuyến giữa các gen |
| **DrugCell** (2020) | Intrinsic VNN (White-box) | Morgan Fingerprints | Somatic Mutations (Genotype) | **Kiến trúc GO DAG** + Chỉ số **RLIPP** | Hệ thống phân cấp Gene Ontology (Pathways) | Không dùng biểu hiện gen (RNA-seq); bị giới hạn bởi tri thức GO đã biết |
| **TranSynergy** (2021) | Network + Post-hoc Hybrid | RWR Profile trên mạng PPI từ Drug Targets | Gene Expression + Gene Dependency | Self-Attention + **SA-GSEA (SHAP + GSEA)** | Gen đơn lẻ & Lộ trình Reactome Pathways | Không áp dụng được cho thuốc mới chưa biết Protein đích |
| **GraphSynergy** (2021) | Graph & Network Path | Protein Targets trên mạng PPI | Cell-specific Proteins trên PPI | **Spatial GCN Attention** + Therapy/Toxicity Score | Đỉnh Protein & Cây lân cận $k$-hop trên PPI | Không xét đến cấu trúc hóa học SMILES của thuốc |
| **DeepDDS** (2022) | Intrinsic Attention | Đồ thị phân tử 2D (GCN/GAT) | Gene Expression (MLP) | **Atom-level Graph Attention Weights** | Nhóm chức hóa học (Chemical Substructures) | Thiếu cầu nối cơ chế giữa Nguyên tử thuốc và Mạng lưới Protein |
| **DTSyn** (2022) | Intrinsic Multi-modal Attention | Đồ thị phân tử GCN + SMILES | Gene Expression | **Dual-Transformer Cross-Attention** | Cặp tương tác (Atom/Substructure – Gene) | Trọng số Attention dễ bị nhiễu trên không gian chiều cao |
| **MARSY** (2023) | Post-hoc Attribution | Differential Gene Expression Signature | Cancer Cell Gene Expression | **Integrated Gradients** trên Multitask DNN | Dấu ấn sinh học Gen (Genomic Biomarkers) | Giải thích ở mức tương quan thống kê, thiếu cấu trúc đường dẫn |
| **SDCInterpreter** (2025) | Heterogeneous Graph XAI | Cấu trúc Thuốc + Đích nhắm | Directed Graph (Gene $\rightarrow$ Pathway $\rightarrow$ Cell) | **Learnable Edge Masking** (Subgraph/Path XAI) | Chuỗi nhân quả: Drug $\rightarrow$ Gene $\rightarrow$ Pathway | Độ phức tạp tính toán cao khi tối ưu hóa mặt nạ đồ thị |
| **DIPx** (2025) | Pathway-based White-box | Drug Target Profile | Multi-omics (Expr, Mutation, CNV) | **Pathway Activation Score (PAS)** (Up/Downstream) | Hoạt độ con đường tín hiệu cá thể hóa | Yêu cầu dữ liệu phân tách thượng nguồn/hạ nguồn khắt khe |

---

## 6. Phân tích Lập luận Chặt chẽ: 5 Thách thức Mở & Khoảng trống Nghiên cứu (Research Gaps)

Một bài tổng quan tài liệu xuất sắc cần chỉ ra được những mâu thuẫn nội tại và khoảng trống chưa được giải quyết trong các công trình hiện tại. Dưới đây là 5 luận điểm cốt lõi bạn có thể dùng để đặt nền móng cho đề tài nghiên cứu của mình:

### 6.1. Khoảng trống giữa "Cấu trúc Hóa học (SMILES)" và "Đích Sinh học (PPI/Pathway)" trong bài toán Cold-Start
*   **Lập luận:** Hiện tại tồn tại sự phân cực rõ rệt giữa hai dòng mô hình:
    *   Các mô hình dựa trên mạng PPI/Pathway (như *TranSynergy*, *GraphSynergy*, *DIPx*) giải thích cơ chế sinh học rất tốt, nhưng **bắt buộc phải biết trước tập protein đích thực nghiệm (known drug targets)** của thuốc. Khi gặp một hợp chất hóa học mới đang thử nghiệm tiền lâm sàng (chỉ có công thức SMILES, chưa biết đích tác dụng), các mô hình này hoàn toàn tê liệt.
    *   Ngược lại, các mô hình dựa trên đồ thị phân tử (như *DeepDDS*, *DTSyn*) nhận trực tiếp SMILES nên dự đoán được cho thuốc mới, nhưng lại bỏ qua mạng PPI/Pathway, dẫn đến lời giải thích sinh học nông cạn.
*   **Hướng giải quyết tiềm năng:** Xây dựng kiến trúc **End-to-End Unified Explainable Framework**: Nhánh 1 dự đoán xác suất tương tác Thuốc - Đích (DTI prediction) trực tiếp từ đồ thị phân tử 2D/3D của thuốc mới, sau đó lấy vector xác suất đích nhắm đó làm hạt giống khởi tạo $p^{(0)}$ để lan truyền trên mạng PPI/Pathway có hướng.

### 6.2. Sự nhầmẫn giữa "Tương quan Thống kê (Correlation)" và "Cơ chế Nhân quả (Causality / Intervention)"
*   **Lập luận:** Bản chất của thuốc tác động lên tế bào là một **can thiệp nhân quả (Causal Intervention - toán tử $do(X=x)$ của Judea Pearl)** làm thay đổi trạng thái mạng lưới sinh học, chứ không phải là một quan sát thụ động. Hầu hết các kỹ thuật XAI hiện tại (SHAP, Integrated Gradients, Attention) chỉ đo lường tương quan thống kê trên phân phối dữ liệu huấn luyện. Nếu hai gen $G_1$ và $G_2$ cùng nằm dưới sự điều khiển của một yếu tố phiên mã, mô hình có thể gán toàn bộ điểm giải thích cho gen hệ quả $G_2$ thay vì gen đích thực sự $G_1$.
*   **Hướng giải quyết tiềm năng:** Tích hợp **Giải thích Phản thực tế (Counterfactual Explanations)** và **Causal Graph Neural Networks** kết hợp với dữ liệu nhiễu loạn gen thực nghiệm (như **LINCS L1000** hoặc **CRISPR knock-out screens / DepMap**) để huấn luyện mô hình học quan hệ nhân quả thực sự.

### 6.3. Hạn chế của Đồ thị PPI Vô hướng và Bất biến theo Mô (Static & Context-Agnostic PPI Networks)
*   **Lập luận:** Các bài báo hiện nay sử dụng chung một đồ thị PPI tĩnh (lấy từ STRING hoặc BioGRID) cho mọi dòng tế bào ung thư (từ ung thư phổi, ung thư vú đến ung thư máu). Tuy nhiên, về mặt sinh học, nếu một protein không được biểu hiện hoặc bị đột biến mất chức năng trong dòng tế bào ung thư phổi, thì các cạnh nối với protein đó trên mạng PPI thực chất không tồn tại trong tế bào đó.
*   **Hướng giải quyết tiềm năng:** Xây dựng **Cell-line Specific Dynamic PPI/Pathway Graphs** (Đồ thị PPI động đặc trưng theo từng dòng tế bào), trong đó trọng số cạnh $e_{ij}^{(c)}$ của mạng PPI được điều biến động (modulated/pruned) bởi chính mức độ đồng biểu hiện gen (transcriptomics/proteomics) của dòng tế bào $c$ trước khi đưa vào thuật toán Graph XAI.

### 6.4. Thiếu các Chỉ số Đánh giá Định lượng Chuẩn cho XAI Y sinh (Lack of Quantitative XAI Evaluation Metrics)
*   **Lập luận:** Hầu hết các bài báo XAI trong Drug Synergy hiện nay chỉ đánh giá tính khả giải một cách **định tính và chủ quan (Qualitative Case Studies / Cherry-picking)**: Tác giả chọn ra 2–3 cặp thuốc có điểm dự đoán cao nhất, vẽ biểu đồ nhiệt Attention hoặc danh sách 10 gen có SHAP cao nhất, rồi tìm vài bài báo trên PubMed có nhắc đến các gen đó để kết luận mô hình "có khả năng giải thích tốt". Cách làm này thiếu tính khái quát và dễ mắc lỗi thiên kiến xác nhận (confirmation bias).
*   **Hướng giải quyết tiềm năng:** Thiết lập bộ thước đo định lượng nghiêm ngặt cho XAI trong Drug Synergy:
    1.  **Biological Faithfulness / Ground-truth Alignment:** Đo độ trùng lặp (Precision@K, Recall@K, AUROC, Jaccard Index) giữa các gen/pathways được XAI xếp hạng cao nhất với dữ liệu thực nghiệm **CRISPR Dual-Knockout (Synthetic Lethality screens - SynLethDB)** hoặc dữ liệu **LINCS L1000 perturbed signatures**.
    2.  **Fidelity+ / Fidelity- (Sufficiency & Comprehensiveness):** Đo mức độ sụt giảm điểm dự đoán khi che (masking) các đồ thị con/pathways quan trọng nhất mà thuật toán XAI chỉ ra.
    3.  **Stability / Robustness:** Đảm bảo lời giải thích không bị thay đổi hỗn loạn khi thêm nhiễu nhỏ vào biểu hiện gen.

### 6.5. Bỏ qua Yếu tố Phụ thuộc Liều lượng (Dose-Dependent Explanations)
*   **Lập luận:** Hai loại thuốc có thể tạo ra hiệu ứng đối kháng (antagonism) ở nồng độ thấp nhưng lại hiệp đồng mạnh (synergy) ở nồng độ cao do sự bão hòa thụ thể hoặc kích hoạt đích phụ (off-target effects at high doses). Tuy nhiên, đa số các mô hình hiện tại gộp toàn bộ ma trận liều thành một điểm số trung bình duy nhất, dẫn đến lời giải thích XAI không phản ánh được sự dịch chuyển cơ chế theo nồng độ thuốc.

---

## 7. Đề xuất Quy trình Nghiên cứu Chuẩn (Recommended Research Workflow)

Nếu bạn đang bắt đầu xây dựng một công trình nghiên cứu mới về **XAI in Drug Synergy**, dưới đây là khung thiết kế phương pháp luận (Methodology Pipeline) có tính cạnh tranh cao nhất để công bố trên các tạp chí Q1 (như *Briefings in Bioinformatics*, *Bioinformatics*, *Journal of Chemical Information and Modeling*):

1.  **Tầng Biểu diễn Đa phương thức (Multi-modal Representation Layer):**
    *   *Thuốc:* Kết hợp Đồ thị phân tử 2D/3D (hoặc Pre-trained Chemical Language Model như **ChemBERTa / Uni-Mol**) với Hồ sơ đích nhắm xác suất (Predicted/Known DTI).
    *   *Tế bào:* Kết hợp Multi-omics (Gene Expression + Mutation + Copy Number Variation / CRISPR Dependency từ CCLE/DepMap).
2.  **Tầng Kiến trúc Đồ thị Sinh học Có hướng & Động (Context-aware Biological Graph Layer):**
    *   Xây dựng đồ thị phân cấp: $\text{Substructure} \rightarrow \text{Drug} \rightarrow \text{Target Protein (trên mạng PPI động)} \rightarrow \text{Biological Pathway (KEGG/Reactome)} \rightarrow \text{Cell Fate}$.
3.  **Tầng Giải thích Đa cấp độ (Hierarchical XAI Module):**
    *   *Cấp độ Hóa học:* Dùng SubgraphX hoặc Attention Masking để chỉ ra nhóm chức hóa học hoạt tính.
    *   *Cấp độ Hệ thống Sinh học:* Dùng Path-based GNNExplainer kết hợp điểm kích hoạt VNN (như RLIPP hoặc SA-GSEA) để trích xuất **Top-$K$ đường dẫn tín hiệu hiệp đồng (Synergistic Signaling Paths)**.
4.  **Tầng Kiểm định Định lượng (Quantitative XAI Benchmarking):**
    *   Kiểm định chéo kết quả giải thích của mô hình với cơ sở dữ liệu **SynLethDB (Synthetic Lethality)** và **LINCS L1000** trên cả hai kịch bản chia dữ liệu khắt khe: *Leave-Drug-Combinations-Out* và *Leave-Cell-Lines-Out*.

---

## 8. Danh mục Tài liệu Tham khảo Trọng tâm (Selected Bibliography)

1.  **Preuer, K., et al. (2018).** *DeepSynergy: predicting anti-cancer drug synergy with Deep Learning*. Bioinformatics, 34(9), 1538–1546.
2.  **Janizek, J. D., et al. (2018).** *Explainable machine learning prediction of synergistic drug combinations for precision oncology (TreeCombo)*. Bioinformatics / bioRxiv.
3.  **Cheng, F., Kovács, I. A., & Barabási, A. L. (2019).** *Network-based prediction of drug combinations*. Nature Communications, 10(1), 1197.
4.  **Menden, M. P., et al. (2019).** *Community assessment to advance computational prediction of cancer drug combinations in a pharmacogenomic screen (AstraZeneca-Sanger DREAM Challenge)*. Nature Communications, 10(1), 2674.
5.  **Kuenzi, B. M., et al. (2020).** *Predicting drug response and synergy using a deep learning model of human cancer cells (DrugCell)*. Cancer Cell, 38(5), 672–684.
6.  **Deng, L., et al. (2020).** *PathDNN: a pathway-guided deep neural network for predicting cancer drug sensitivity and synergy*. Journal of Chemical Information and Modeling.
7.  **Liu, Q., & Xie, L. (2021).** *TranSynergy: Mechanism-driven interpretable deep neural network for the synergistic prediction and pathway deconvolution of drug combinations*. PLOS Computational Biology, 17(2), e1008653.
8.  **Yang, J., et al. (2021).** *GraphSynergy: a network-inspired deep learning model for anticancer drug combination prediction*. Journal of the American Medical Informatics Association (JAMIA), 28(11), 2336–2345.
9.  **Wang, J., et al. (2022).** *DeepDDS: deep graph neural network with attention mechanism to predict synergistic drug combinations*. Briefings in Bioinformatics, 23(1), bbab390.
10. **Hu, J., et al. (2022).** *DTSyn: a dual-transformer-based neural network to predict synergistic drug combinations*. Briefings in Bioinformatics, 23(5), bbac302.
11. **Tang, Y. C., & Gottlieb, A. (2022).** *SynPathy: predicting drug synergy through drug-associated pathways using deep learning*. Briefings in Bioinformatics.
12. **El Khili, M. R., et al. (2023).** *MARSY: a multitask deep-learning framework for prediction of drug combination synergy scores*. Bioinformatics, 39(4), btad177.
13. **Zhang, P., et al. (2023).** *KG-Synergy: Knowledge graph-enhanced deep learning for drug synergy prediction and mechanism explanation*. Briefings in Bioinformatics.
14. **Li, T., et al. (2024).** *CancerGPT: Few-shot drug pair synergy prediction using large pretrained language models*. npj Digital Medicine, 7(1), 40.
15. **Wang, Z., et al. (2024).** *AttenSyn & HANSynergy: Attention-based and Heterogeneous Graph Neural Networks for Anticancer Synergistic Drug Combination Prediction*. Journal of Chemical Information and Modeling.
16. **Nguyen, T., et al. (2024/2025).** *DIPx: Pathway activation model for personalized prediction of drug synergy*. eLife.
17. **SDCInterpreter (2025).** *Path-Based Graph Neural Network for Drug Synergy Prediction and Interpretation*. Journal of Chemical Information and Modeling.