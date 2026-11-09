# Giải thích bằng đường dẫn mạng chưa được kiểm chứng

**Câu trả lời ngắn:** Nhóm 3 (Graph & Network Path XAI) có khoảng 25 công trình, từ lý thuyết "Complementary Exposure" của Cheng et al. (2019) đến các mô hình dị cấu năm 2025–2026 như SDCInterpreter, CASynergy và HGTSynergy. Tuy vậy, **không bài nào đo định lượng độ trung thực (faithfulness) của lời giải thích trên mạng**. Lời giải thích gần như luôn được "kiểm chứng" bằng case study, enrichment và đối chiếu y văn. Ngoại lệ duy nhất là SDCInterpreter, có script đánh giá lời giải thích nhưng chưa rõ dùng metric gì. Năm 2025–2026, hai benchmark SynVerse (*Brief Bioinform*) và "One-hot news" (*Bioinformatics*) cho thấy baseline one-hot khớp hiệu năng với 16 kiến trúc đã công bố, việc rewiring mạng hầu như không làm giảm PCC, và attribution không tìm lại được đặc trưng thật khi bộ ba (thuốc A, thuốc B, cell line) lặp lại. Như vậy, rất có thể phần lớn các "đường dẫn cơ chế" đã công bố phản ánh việc mô hình nhớ danh tính thuốc và cell line, chứ không phản ánh sinh học. Phát hiện này trùng khớp với kết quả của chính bạn: recall@3 ≤ 0.2, rơi về 0 khi chỉ có ~40 cell line, và MLP thắng GNN. Vì vậy, đề xuất xếp hạng 1 cho luận văn là **một benchmark và giao thức kiểm định lời giải thích đường dẫn cấp tương tác trên mạng PPI/signaling thật**. Giao thức này có cơ chế cài sẵn, có các đối chứng one-hot / shuffle / degree-preserving rewiring, và đo fidelity cùng recall đường dẫn. Đề xuất này mở rộng trực tiếp code IG 3 cấp và kill test bạn đã có, khả thi trong 9–12 tháng, và phù hợp với *Bioinformatics*, *BIB* hoặc *PLOS Comput Biol*. Hai hướng phụ là: giải thích phản thực tế (knockout in silico) trên mạng có hướng/có dấu, và dùng DTI dự đoán làm "hạt giống" cho thuốc chưa biết đích.

Về độ tin cậy của nguồn, báo cáo dùng ba nhãn. **[FT]** nghĩa là ghi chú nghiên cứu đã đọc full text. **[ABS]** nghĩa là chỉ đọc abstract hoặc metadata. **[CHƯA KIỂM CHỨNG]** nghĩa là chỉ dựa trên snippet, nguồn thứ cấp hoặc kiến thức sẵn có, chưa đọc lại bài gốc. Một số full text (OUP, ACS, MDPI, bioRxiv) bị chặn trong phiên nghiên cứu, nên một số chi tiết kiến trúc và số liệu vẫn để trống. Báo cáo ghi rõ những chỗ đó thay vì điền suy đoán.

---

## Nền tảng dược lý mạng: tách biệt topo dự đoán yếu nhưng giải thích tốt

**Cheng, Kovács & Barabási, "Network-based prediction of drug combinations", *Nature Communications* 10:1197 (2019), DOI 10.1038/s41467-019-09186-x [FT].** Đây là nền móng lý thuyết của cả Nhóm 3. Bài này không phải mô hình học máy mà là một chỉ số topo được thiết kế bằng tay. **Separation score** được định nghĩa là s_AB = ⟨d_AB⟩ − (⟨d_AA⟩+⟨d_BB⟩)/2, trong đó d là khoảng cách đường đi ngắn nhất giữa các đích của hai thuốc. Khi s_AB < 0, hai module đích chồng lấn; khi s_AB ≥ 0, chúng tách biệt về topo ([Europe PMC full text](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6416394/fullTextXML)). Mạng nền là một interactome gồm **243.603 tương tác vật lý giữa 16.677 protein, gộp từ 15 cơ sở dữ liệu**. Đích thuốc lấy từ DrugBank, TTD, ChEMBL, BindingDB và các nguồn khác, với ngưỡng ái lực ≤10 µM. Dữ liệu đánh giá gồm 681 tổ hợp của 362 thuốc. Bài phân loại tổ hợp thành sáu lớp "exposure". **Chỉ lớp P2 (Complementary Exposure) có ý nghĩa thống kê với hiệu quả điều trị (P < 1.0×10⁻⁴, permutation test)**. Lớp P2 nghĩa là module đích của cả hai thuốc đều chạm vào module bệnh nhưng nằm ở hai vùng mạng riêng biệt. Ngược lại, Overlapping Exposure (P1) gắn với tác dụng phụ ([Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6416394/fullTextXML)). Về hiệu năng, AUC khi dự đoán tổ hợp hạ áp đã được phê duyệt chỉ đạt **0.589 ± 0.002**, so với 0.489 của baseline hóa tin và 0.529 của baseline tin sinh. Toàn bộ kiểm định là hồi cứu: đối chiếu với tổ hợp đã duyệt, thử nghiệm lâm sàng và y văn, không có thí nghiệm mới. Các hạn chế tác giả nêu gồm: thiên lệch chọn mẫu, không có thông tin liều, chỉ xét cặp, interactome chưa đầy đủ, và chỉ thử trên tăng huyết áp và ung thư. Code tính proximity nằm ở github.com/emreg00/toolbox.

Bài này quan trọng với luận văn vì hai lý do. Thứ nhất, AUC 0.589 cho thấy topo mạng **có giá trị giải thích nhiều hơn giá trị dự đoán**. Đây là cách đặt vấn đề trung thực cho cả hướng nghiên cứu: mạng nên đóng vai prior hoặc ngôn ngữ giải thích, không phải bộ dự đoán độc lập. Thứ hai, s_AB là một **"explainer phi học máy" có sẵn**, có thể dùng làm baseline. Một đường dẫn học được từ GNN nên chứa thông tin vượt quá khoảng cách đường đi ngắn nhất giữa đích của A và B. Nếu không, nó chỉ đang tái tạo lại Cheng 2019. GraphSynergy dùng lại chính interactome này ([GitHub GraphSynergy](https://github.com/JasonJYang/GraphSynergy)), còn phân tích "trọng số đường đi ngắn nhất giữa đích hai thuốc" của DeepSignalingFlow là phiên bản học được của s_AB.

---

## Lan truyền trên PPI và mạng tín hiệu: mười mô hình, không có phép đo fidelity nào

Nhánh này gồm hai họ khác nhau rõ rệt. Họ thứ nhất dùng **PPI toàn bộ hệ gen**: interactome Cheng, STRING, IHP-PING, gồm hàng chục nghìn node. Đại diện là GraphSynergy, TranSynergy, SynerGNet và SynPathy. Họ thứ hai dùng **mạng tín hiệu KEGG được tuyển chọn** (~1.3k–2k gen, có hướng). Họ này thuộc phòng lab của Fuhai Li (WashU). Họ thứ hai nhỏ hơn và có hướng, nên đồ thị con giải thích dễ đọc hơn nhiều.

### TranSynergy: SHAP cộng GSEA, kèm lời thừa nhận rằng attention không phải lời giải thích

**Liu Q. & Xie L., *PLOS Comput Biol* 17(2):e1008653 (2021), DOI 10.1371/journal.pcbi.1008653 [FT].** **Dữ liệu và split:** bộ O'Neil/Merck, tiền xử lý theo DeepSynergy (36 thuốc, 35 cell line, 18.553 điểm dữ liệu). Bài toán chính là hồi quy synergy score; khi cần metric phân lớp thì lấy ngưỡng > 30. Có ba kiểu split: leave-combination-out (nested 5-fold), leave-cell-line-out (theo cụm affinity propagation) và leave-drug-out. **TranSynergy là mô hình duy nhất trong nhánh này, trong số các bài đã kiểm chứng, có cả leave-drug-out lẫn leave-cell-out.** **Kiến trúc:** dùng RWR (α = 0.5) trên STRING để lan truyền vector đích của mỗi thuốc thành profile 2.401 gen. Cell line được biểu diễn bằng DepMap dependency và biểu hiện gen. Phần lõi là transformer self-attention không có positional encoding, theo sau là bộ hồi quy fully connected ([PLOS](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008653)). **Cơ chế giải thích (SA-GSEA):** dùng SHAP GradientExplainer/DeepExplainer tính Shapley value cho từng gen (background k-means, trung bình 10 lần chạy), xếp hạng gen của cell line theo Shapley value, rồi chạy GSEA trên danh sách đã xếp hạng. **Kiểm định lời giải thích:** chỉ có case study trên **7 mẫu** dự đoán đúng với điểm cao (T47D, CAOV3, MSTO-211H), đối chiếu y văn. Chính tác giả viết rằng muốn kết luận chắc hơn thì "có thể cần thêm bằng chứng thực nghiệm". **Kết quả:** ở leave-combo-out, MSE 232, tốt hơn DeepSynergy có ý nghĩa (p < 0.001); Pearson cao hơn ~3%, PR-AUC cao hơn 5.6%. Pearson theo mô dao động từ 0.66 (tuyến tiền liệt) đến 0.79 (buồng trứng). **Hạn chế:** tập gen nhỏ; cold-start yếu; thuốc không có đích đã biết bị biểu diễn kém; không có mutation hay CNV. Đáng chú ý, **tác giả nói thẳng rằng attention weight có thể không giải thích được dự đoán, và đó là lý do họ dùng SHAP**. Đây là một câu trích dẫn rất có giá trị cho luận văn. **Code:** github.com/qiaoliuhub/drug_combination. Có hai điểm [CHƯA KIỂM CHỨNG]: SA-GSEA dùng thư viện Reactome hay thư viện khác, và synergy score có phải là Loewe hay không (rất có thể là Loewe vì bài theo pipeline DeepSynergy).

### GraphSynergy: điểm therapy/toxicity trên interactome Cheng, nhưng công thức không đọc được

**Yang J., Xu Z., Wu W.K.K., Chu Q., Zhang Q., *JAMIA* 28(11):2336–2345 (2021), DOI 10.1093/jamia/ocab162 [ABS]. Bài có erratum, DOI 10.1093/jamia/ocab214** ([OUP](https://academic.oup.com/jamia/article/28/11/2336/6362567)). **Kiến trúc:** spatial GCN trên mạng PPI. Mô hình mã hóa module protein mà cặp thuốc nhắm tới và module protein liên quan đến cell line. Hai điểm "therapy score" và "toxicity score" đánh giá tác dụng dược lý, và một thành phần attention xác định các protein then chốt. **Dữ liệu:** PPI và liên kết thuốc–protein lấy từ interactome Cheng 2019; liên kết cell–protein lấy từ CCLE qua Harmonizome; đánh giá trên DrugCombDB và Oncology-Screen ([GitHub](https://github.com/JasonJYang/GraphSynergy)). **Kết quả:** ACC **0.7553 trên DrugCombDB (+11.94% so với DeepSynergy)** và 0.7557 trên Oncology-Screen. **Giải thích:** các protein có trọng số đóng góp cao gắn với chức năng phân tử như phiên mã và điều hòa phiên mã. **Kiểm định:** theo abstract và nguồn thứ cấp thì chỉ định tính (chú giải chức năng và case study), không có kiểm định fidelity. Các chi tiết sau đều **[CHƯA KIỂM CHỨNG]**, chỉ lấy từ một bản tóm tắt thứ cấp ([BestHub](https://besthub.dev/articles/graphsynergy-a-network-inspired-deep-learning-model-for-predicting-anti-cancer-drug-combinations-eefd2fcf6d43)): hai điểm được gộp qua sigmoid; có bảy baseline (Network Proximity, GraRep, DeepWalk, Node2Vec, DeepSynergy, GCN, KGNN); receptive field 2-hop là tốt nhất; case study NSCLC gợi ý Pemetrexed + Gefitinib. Chính bản tóm tắt đó lại ghi nhầm venue thành "Nature Machine Intelligence". Công thức chính xác của therapy/toxicity score, loại synergy score, protocol split (nhiều khả năng là random) và AUC đều chưa được xác minh vì full text bị paywall. Việc "toxicity score vận hành hóa quan sát rằng Overlapping Exposure gây tác dụng phụ" là suy luận từ thiết kế, không phải điều bài báo khẳng định. **Code:** github.com/JasonJYang/GraphSynergy.

### Họ Fuhai Li: bốn mô hình KEGG, kiểm định thống kê yếu

Bốn mô hình này cùng dựng đồ thị từ khoảng **46–48 pathway tín hiệu ung thư lõi của KEGG** cộng cạnh thuốc–gen từ DrugBank, và đều huấn luyện trên NCI ALMANAC.

**DeepSignalingSynergy:** Zhang H., Feng J., Zeng A., Payne P., Li F., *AMIA Annu Symp Proc* 2020:1364–1372, PMC8075535 [ABS] ([Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMCID:PMC8075535%20OR%20PMCID:PMC8510276&resultType=core&format=json)). Mô hình dùng 46 pathway, giữ lại 21 thuốc có đích trên các gen pathway. Đầu ra của tầng pathway đi vào một DBN để dự đoán synergy score ([bioRxiv](https://www.biorxiv.org/content/10.1101/2020.04.10.036491.full.pdf)). Thông tin "dùng iNNvestigate để lấy độ quan trọng theo tầng, Pearson 0.40, AUC 0.93" chỉ đến từ một bảng so sánh thứ cấp, **[CHƯA KIỂM CHỨNG]**.

**IDSP:** Dong Z., Zhang H., Chen Y., Li F., arXiv:2105.07082 (2021), chỉ có v1 và không có bản bình duyệt [ABS] ([arXiv](https://arxiv.org/abs/2105.07082)). Mô hình học trọng số cạnh bằng một MLP và đọc các tương tác tín hiệu quan trọng từ trọng số đó. Bài thử cả transductive lẫn inductive (gen hoặc pathway chưa thấy). Abstract không có số liệu và không có code; nhiều khả năng đã được SANEpool thay thế.

**SANEpool:** Dong Z., Zhang H., Chen Y., Payne P.R.O., Li F., *Cancers* 15(17):4210 (2023), DOI 10.3390/cancers15174210 [FT] ([Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10486573/fullTextXML)). **Dữ liệu:** NCI-DCD (5.658 đồ thị, 1.364 gen, ~25k cạnh), O'Neil-DCD (4.637 đồ thị) và GDSC-SDD (dữ liệu đơn thuốc). Mục tiêu là hồi quy ComboScore trung bình theo liều. Split là inductive theo cặp thuốc chưa thấy, 5-fold. **Kiến trúc:** 2 lớp GCN và 2 lớp SANEpool. Node attention là điểm cosine với một vector học được, giữ top-k (200 node ở lớp cuối, 90% cạnh). Trọng số cạnh học được nhân Hadamard. Decoder kiểu Decagon, bất biến với thứ tự thuốc. **Giải thích:** độ quan trọng "synergic" và "non-synergic" của một gen được tính bằng tần suất SANEpool chọn gen đó, theo từng cell line. **Kiểm định:** KS test cho thấy hai phân phối khác nhau ở mọi cell line, kèm heatmap và hình đồ thị con. Không có enrichment hay thí nghiệm ướt trong phần đã đọc. **Kết quả:** Pearson **0.656 trên NCI-DCD** so với TranSynergy 0.644. Trên O'Neil, SANEpool đạt 0.614, thấp hơn TranSynergy (0.615), nên **tuyên bố "tốt nhất trên mọi bộ dữ liệu" trong abstract không hoàn toàn đúng**. Cột sai số trong bảng lúc ghi MSE lúc ghi RMSE, không nhất quán.

**DeepSignalingFlow:** Zhang H., Chen Y., Payne P., Li F., *npj Syst Biol Appl* 10:92 (2024), DOI 10.1038/s41540-024-00421-w [FT] ([Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11339460/fullTextXML)). **Dữ liệu:** NCI ALMANAC, O'Neil, DrugComb, DrugCombDB; 5-fold CV. **Đồ thị:** 48 pathway KEGG gồm 2.016 gen, **ma trận kề có hướng**; RNA-seq và CNV lấy từ Cell Model Passports. **Kiến trúc:** WeB-GNN hai chiều, với ma trận trọng số riêng cho chiều upstream→downstream và chiều downstream→upstream, gồm 3 lớp. **Giải thích:** lấy ma trận "flow" trung bình qua 5 fold, tính bậc có trọng số của gen nhân với mức RNA-seq, rồi cắt ngưỡng để được mạng con lõi. Với mỗi tổ hợp, mô hình cộng trọng số cạnh dọc **các đường đi ngắn nhất (độ dài < 5) giữa đích của hai thuốc**. **Kiểm định:** F-test so sánh top-10 với bottom-10 tổ hợp trong mỗi cell line. **Chỉ 21/41 cell line có trọng số đường dẫn cao hơn ở top-10, và ngưỡng ý nghĩa là p < 0.1**. **Kết quả:** Pearson 63.75% trên ALMANAC, so với 44.88% của GCN. **Hạn chế:** chỉ pan-cancer, chưa dùng loại cạnh của KEGG, tác giả tự gọi là nghiên cứu khám phá. **Code:** github.com/FuhaiLiAiLab/DeepSignalingFlow.

Điểm yếu chung của cả họ này là các phép kiểm định thống kê (KS trên tần suất chọn, F-test với p < 0.1 ở một nửa số cell line) **chỉ cho thấy lời giải thích khác nhau giữa các lớp**. Chúng không cho thấy lời giải thích trung thực với mô hình hay đúng về sinh học.

### SynerGNet, SynPathy, PathSynergy, DIPx: bốn mô hình lân cận, bốn mức độ "giải thích" khác nhau

**SynerGNet:** Liu M., Srivastava G., Ramanujam J., Brylinski M., *Biomolecules* 14(3):253 (2024) [FT] ([PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10967862/)). Bài toán phân lớp nhị phân synergistic/antagonistic trên AZ-DREAM (3.272 cặp, tăng cường dữ liệu lên 2.3 triệu mẫu), 5-fold random CV. PPI lấy từ IHP-PING với độ tin cậy ≥ 0.7, gồm 18.997 node. Đặc trưng node gồm biểu hiện, CNV, mutation, điểm STITCH và embedding GO. Kiến trúc là 2 lớp GENConv kèm JK-Net. Kết quả AUC 0.790. Trên tập ngoài DrugCombDB, AUC 0.748 nhưng **FPR lên tới 0.735**. **Bài không có phương pháp giải thích nào**, dù thường được xếp vào nhóm "PPI-GNN". Code: github.com/MengLiu90/SynerGNet.

**SynPathy:** Tang Y.-C. & Gottlieb A., ***Mol Cancer Res* 20(5):762–769 (2022)** [ABS] ([Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1158/1541-7786.MCR-21-0735&resultType=core&format=json)). Đặc trưng là điểm enrichment pathway tính từ khoảng cách PPI giữa đích thuốc và gen của pathway ([eLife DIPx](https://elifesciences.org/articles/100071v1)). Kết quả MSE 70.6 ± 6.4. Phát hiện đáng chú ý: **các cặp càng hiệp đồng thì các pathway đóng góp hàng đầu của chúng càng gần nhau trên mạng PPI**. Kiến trúc chi tiết, split và code chưa được kiểm chứng.

**PathSynergy:** Zhang F., Zhao X., Wei J., Wu L., *Brief Bioinform* 26(2):bbaf192 (2025) [FT] ([OUP](https://academic.oup.com/bib/article/26/2/bbaf192/8119326)). Nhãn nhị phân: score > 10 là dương, < 0 là âm, bỏ phần ở giữa. Dữ liệu O'Neil đã lọc (29 cell line, 6.271 tổ hợp), random 5-fold; tập ngoài gồm 1.252 cặp DrugCombDB. Mô hình gồm GAT trên đồ thị phân tử và CNN trên một "bản đồ pathway" 2D dựng từ MSigDB C2 bằng K-means và PCA. **Mô hình này không dùng mạng PPI**, nên chỉ thuộc Nhóm 3 theo nghĩa rộng. Giải thích bằng gradient trên các pathway. Đây là **bài duy nhất có thí nghiệm ướt** (CCK-8, Chou–Talalay CI, colony formation, transwell trên ung thư gan), nhưng thí nghiệm kiểm chứng *tổ hợp được dự đoán*, không kiểm chứng *lời giải thích pathway*. Kết quả CV: ACC 0.95, AUC 0.98. Trên tập ngoài, AUC rơi xuống 0.81, thấp hơn MGAE-DC (0.89). Code: github.com/ZhangFengyuea300/PathSynergy. Một bản ghi dblp khác cùng nhóm tác giả với nhãn năm 2024 chưa được đối chiếu ([dblp](https://dblp.org/rec/journals/bib/ZhangZWW24)).

**DIPx:** Trac Q.T., Huang Y., Erkers T., …, Pawitan Y., Vu T.N., *eLife* 13:RP100071 (Version of Record 3/6/2025) [FT] ([eLife](https://elifesciences.org/articles/100071)). **Đây là mô hình random forest regressor, không phải mạng nơ-ron.** Đặc trưng là 14.286 pathway activation score (PAS), xây từ tổng biểu hiện của ba tập gen (upstream/đích, downstream, driver) trên 4.762 pathway MSigDB. Nhãn là Loewe score từ Combenefit. Giải thích bằng permutation importance kèm network enrichment analysis; NEA z-score được PAS dự đoán với Spearman 0.46. **Kết quả cho thấy giới hạn của khả năng tổng quát hóa:** Spearman 0.50 trên tổ hợp đã thấy, **0.26 trên tổ hợp chưa thấy (không có ý nghĩa thống kê so với TAIJI-M)**, và **0.09 trên O'Neil khi cả hai thuốc đều chưa thấy**. Code: github.com/tracquangthinh/DIPx.

Ghi chú nghiên cứu còn ghi nhận một số ứng viên chỉ thấy qua snippet và **[CHƯA KIỂM CHỨNG]** chi tiết XAI. DGSSynADR (*Bioinformatics* 2023) dùng đồ thị dị cấu drug-drug/drug-target/PPI ([mirror](https://dbpia.nl.go.kr/bioinformatics/article/39/10/btad607/7301437)). SynergyGTN (*Sci Rep* 2025) tích hợp PPI vào graph transformer ([Nature](https://www.nature.com/articles/s41598-025-12936-1)). TAG-CP (*Expert Syst Appl* 2025) báo cáo rằng đích của các cặp hiệp đồng thường cách nhau 1–2 node trung gian trên IntAct ([ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0957417425001885)). NetSyn và PathDNN chưa được tìm kiếm.

---

## Đồ thị dị cấu, KG, meta-path và hypergraph: chỉ một bài thật sự giải thích bằng đường dẫn

Nếu xếp theo cơ chế giải thích, nhóm này trải trên một phổ rõ ràng. (a) Explainer đường dẫn hoặc đồ thị con thực thụ: chỉ có **SDCInterpreter**. (b) Soi attention weight: HANSynergy, KGANSynergy, HGTSynergy. (c) Tìm đường dẫn hậu kỳ trên đồ thị: SynDRep. (d) Không giải thích: MGAE-DC, HypergraphSynergy, SynergyGraph, CGMS.

### SDCInterpreter: baseline chính cho path XAI trong hiệp đồng thuốc

**Wang S., Yuan H., Hong Z., Chen X. (tác giả liên hệ), Yang X., "Path-based graph neural network for drug synergy prediction and interpretation", *J Chem Inf Model* 2026, 66(1):337–348, DOI 10.1021/acs.jcim.5c02569** ([GitHub README](https://github.com/chenxgscuec/SDCInterpreter); [ACS](https://pubs.acs.org/doi/10.1021/acs.jcim.5c02569); [PubMed](https://pubmed.ncbi.nlm.nih.gov/41469369/)). Bài lên mạng khoảng tháng 12/2025 nhưng nên trích là 2026. **Đồ thị và kiến trúc:** đồ thị dị cấu nối thuốc–gen–pathway–cell line, học biểu diễn node bằng **R-GCN**. Với đầu vào là hai thuốc và một cell line, mô hình dự đoán synergy rồi sinh ra một tập đường dẫn làm lời giải thích sinh học. **Cơ chế giải thích:** một lớp tối ưu hóa mặt nạ cạnh **dựa trên PaGE-Link** học edge mask rồi trích các đường dẫn liên quan nhất ([DeepWiki, tự sinh, thứ cấp](https://deepwiki.com/chenxgscuec/SDCInterpreter)). Một ghi chú khác mô tả bước trích đường dẫn là "mask learning + Dijkstra". **Kiểm định lời giải thích:** repo có các script `interpret.py`, `valid_path.py`, `eval_explanations.py`, cho thấy có một dạng đánh giá định lượng, nhưng **metric chưa được xác định**. **Code:** PyTorch 1.13.1 + DGL 1.1.2. Bộ dữ liệu, số node/cạnh, nguồn pathway và số liệu hiệu năng đều chưa đọc được vì ACS trả về 403. Mô tả "đồ thị có hướng 5 tầng Virtual node → Drug → Target gene → Pathway → Cell line" là hợp lý với PaGE-Link (PaGE-Link cần đường dẫn có hướng giữa nguồn và đích, và một virtual node có thể đóng vai nguồn duy nhất), nhưng **[CHƯA KIỂM CHỨNG]**. Cần mở full text hoặc file `Overview.jpg` trong repo để xác nhận. Không nên nhầm với SDCNet (*BIB* 2022), một R-GCN coi mỗi cell line là một loại quan hệ ([OUP](https://doi.org/10.1093/bib/bbac403)).

### HANSynergy, KGANSynergy, HGTSynergy: attention trên đồ thị dị cấu

**HANSynergy:** Cheng N., Wang L., Liu Y., Song B., Ding C., *J Chem Inf Model* 64(10):4334–4347 (2024), DOI 10.1021/acs.jcim.4c00003 [ABS] ([PubMed](https://pubmed.ncbi.nlm.nih.gov/38709204/)). Đồ thị dị cấu được dựng từ DrugCombDB, PubChem, UniProt và CCLE. Các loại node có vẻ là thuốc, protein và cell line. Mô hình là HAN với attention cấp node và cấp ngữ nghĩa. Lời giải thích đến từ **việc so sánh attention trước và sau khi huấn luyện** để chỉ ra các protein có thể liên quan đến tổ hợp. Đây là bằng chứng ở mức láng giềng, không phải trích đường dẫn, và việc kiểm định có vẻ chỉ định tính. Kết quả: ACC 0.877, AUC 0.947 trên DrugCombDB_early ([X-MOL](https://login.x-mol.com/paper/1788780077418999808)). Kiến trúc đầy đủ, split và code chưa được kiểm chứng.

**KGANSynergy:** Zhang G., Gao Z., Yan C., Wang J., Liang W., Luo J., Luo H., *Brief Bioinform* 24(3):bbad167 (2023) ([dblp](https://dblp1.uni-trier.de/rec/journals/bib/ZhangGYWLLL23.html)). Số bài bbad167 chỉ được xác nhận qua danh mục tham khảo của một bài khác. Mô hình dùng **lan truyền phân cấp trên KG** để gom láng giềng đa nguồn của thuốc và cell line, rồi dùng multi-attention để đánh trọng số láng giềng ([ScienceGate](https://boch.sciencegate.app/works/W4367673946)). Abstract không mô tả explainer đường dẫn nào. Loại thực thể trong KG, metric và code chưa được kiểm chứng.

**HGTSynergy:** Wang X., Huang Y., Zhu H., Mao D., Zhu X., Liu Q., *BMC Bioinformatics* 27:35 (2026), DOI 10.1186/s12859-025-06360-5 [FT] ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12870253/)). **Đồ thị** có một loại node duy nhất là thuốc, với **293 loại cạnh DDI** lấy từ câu mô tả trong DrugBank 5.1.12; meta-path chỉ dài một bước. Đặc trưng cell line gồm biểu hiện, mutation COSMIC và PPI STRING v10.5 qua GCN. **Kiến trúc:** pre-train bộ mã hóa HAN để phân loại loại DDI, rồi chuyển sang bộ dự đoán dùng multi-head attention. **Dữ liệu và split:** O'Neil (22.737 mẫu Loewe), nested 5-fold leave-combination-out. **Kết quả:** PCC 0.75 cho Loewe; phân lớp với ngưỡng 30 đạt ROC-AUC 0.90, PR-AUC 0.63. **"Diễn giải"** gồm t-SNE, ablation attention và một case study y văn, tức là bằng chứng gián tiếp, không có đường dẫn cơ chế. Code: github.com/Bakers-Lab/HGTSynergy.

### MGAE-DC, HypergraphSynergy, SynergyGraph, SynDRep và các mô hình khác: đồ thị dị cấu mà không giải thích

**MGAE-DC:** Zhang P. & Tu S., ***PLoS Comput Biol* 19(3):e1010951 (3/2023)** ([PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10027223/)). Với mỗi cell line, mô hình dựng ba đồ thị cạnh thuốc–thuốc (synergistic, additive, antagonistic) và dùng autoencoder đa kênh. Attention dùng để hợp nhất các cell line. Đây là mô hình **đa quan hệ, không phải KG**, và không có giải thích ở cấp đường dẫn. Thiết kế "ba kênh syn/add/ant" lại rất gần với bài toán 3 lớp của bạn. Code: github.com/yushenshashen/MGAE-DC.

**HypergraphSynergy:** Liu X., Song C., Liu S., Li M., Zhou X., Zhang W., *Bioinformatics* 38(20):4782–4789 (2022) ([OUP](https://academic.oup.com/bioinformatics/article/38/20/4782/6674505)). Mỗi bộ ba hiệp đồng (thuốc–thuốc–cell line) là một hyperedge, học bằng HGNN. Không có cơ chế giải thích. HERMES (*Bioinformatics* 2025) phê phán rằng mô hình này tổng quát hóa kém cho tổ hợp mới ([arXiv](https://arxiv.org/html/2406.10778v2)).

**SynergyGraph:** có trên PubMed với PMID 41444381 ([PubMed](https://pubmed.ncbi.nlm.nih.gov/41444381/)) và được trang của nhóm AUT liệt kê là *Sci Rep* 2025. Pipeline là KG embedding → hypergraph → UniGAT, đánh giá trên một tập con nhỏ của DrugComb ([AUT](https://bioinformatics.aut.ac.ir/publication/2025-mehrabani-synergygraph-predicting-cell/)). Tác giả, DOI và cơ chế giải thích đều **[CHƯA KIỂM CHỨNG]**.

**SynDRep:** Shalaby K.S. et al., *Bioinform Adv* 5(1):vbaf092 (2025) ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12148216/)). KG Human Brain Pharmacome có 136.838 node và 72 loại quan hệ. Mô hình dùng KGE của PyKEEN cộng random forest, đạt ROC-AUC 0.796. Lời giải thích là **tìm đường dẫn chung bằng NetworkX sau khi đã có dự đoán**, chỉ định tính. Độ chính xác top-rank thuốc–thuốc chỉ **54.65%, gần ngẫu nhiên**.

Một số mô hình khác cũng không có giải thích đường dẫn. **Gu J. et al., *BIB* 24(5):bbad285 (2023)** là framework model-agnostic dùng DDI làm mẫu âm đáng tin cậy và supervised contrastive learning trên KG ([dblp](https://dblp1.uni-trier.de/rec/journals/bib/GuBYLKK23.html)). **CGMS** (*Bioinformatics* 2023) coi mỗi bộ ba là một đồ thị đầy đủ dị cấu ([PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10256571/)). **KGLGANSynergy** (*J Transl Med* 2025) dùng attention cục bộ và toàn cục trên KG ([Springer](https://link.springer.com/article/10.1186/s12967-025-07545-5)). **KnowDDI** (*Commun Med* 2024) là bài về DDI chứ không phải hiệp đồng, nhưng học được "explaining paths" trên KG lớn, nên là khuôn mẫu thiết kế đáng tham khảo ([Nature](https://www.nature.com/articles/s43856-024-00486-y)).

---

## Thế hệ 2024–2026: mạng đặc thù cell line và mask nhân quả, nhưng vẫn kiểm định định tính

**CASynergy:** Li H., Zheng L., Li L., Chen Y., Li J., Zheng C., Su Y., *PLoS Comput Biol* 21(10):e1013567 (2025) [FT] ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12548910/)). Đây là "công thức mẫu" của năm 2025. **Đồ thị:** từ một PPI gồm 15.790 protein và 217.160 cạnh, mô hình dựng mạng đặc thù cho từng cell line bằng cách chọn protein then chốt từ CCLE rồi nối chúng bằng Dijkstra cộng heuristic kiểu Steiner. **Kiến trúc:** GCN trên đồ thị phân tử, GCN trên mạng cell line, và cross-attention. **Giải thích:** module causal attention học soft mask node và cạnh, tách đồ thị thành phần "causal" và phần "shortcut". Top 25% gen được đưa vào Enrichr KEGG. **Kiểm định:** chỉ định tính. Trong top 100 tổ hợp dự đoán, **14 tổ hợp có y văn ủng hộ**. **Bỏ causal attention chỉ làm AUC giảm từ 0.8740 xuống 0.8645**. **Split:** có drug cold-start, combo cold-start và cell cold-start trên Oncology-Screen (21 thuốc, 29 cell line), nhưng cả 21 thuốc đều đã biết đích. Code: github.com/ahu-bioinf-lab/CASynergy. Mức thay đổi AUC khoảng 0.01 cho thấy module "nhân quả" gần như không đóng góp vào độ chính xác. Giá trị giải thích của nó chưa từng được kiểm tra.

**SynCell:** Peng K. et al., arXiv:2511.17695 (v4 tháng 3/2026, preprint) ([arXiv](https://arxiv.org/html/2511.17695v3)). Đồ thị dị cấu thuốc–protein–cell dựng từ NCI-ALMANAC, PrimeKG, STRING, DepMap và DrugBank. Dùng một mạng STRING toàn cục (1.257 protein); ngữ cảnh cell line đến từ cạnh "expresses" cho top 20% gen theo biểu hiện. Bài tuyên bố có "biological interpretability" nhưng không phân tích lời giải thích nào, và **các bảng kết quả mâu thuẫn nội bộ**.

Các bài sau mới chỉ thấy abstract hoặc snippet, nên đều **[CHƯA KIỂM CHỨNG]** về split, code và kiểm định:

| Bài | Ý chính |
|---|---|
| **DRUGSYNC** (bioRxiv 2024.12.05.627115) ([bioRxiv](https://www.biorxiv.org/content/10.1101/2024.12.05.627115v1.full.pdf)) | GCN trên STRING |
| **HyperSynergyX** (*IEEE JBHI* 2026) ([DOI](https://doi.org/10.1109/jbhi.2026.3673550)) | Tổ hợp ba thuốc bằng hypergraph random walk; KG-RAG truy xuất đồ thị con và LLM sinh giả thuyết dạng văn bản |
| **SYNERGIE** (*iScience* 2026) ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13053784/)) | Network controllability và RWR trên PPI, kèm Bayesian optimization; không dùng deep learning |
| **MD-Syn** (*Front Pharmacol* 2025) ([Frontiers](https://www.frontiersin.org/journals/pharmacology/articles/10.3389/fphar.2025.1564339/pdf)) | node2vec trên PPI gồm 978 gen landmark |
| **PDTSyn** (*BIB* 2026) ([OUP](https://academic.oup.com/bib/article/27/2/bbag199/8662206)) | Domain generalization, coi mỗi cell line là một domain |
| **HIG-Syn** (*Bioinformatics* 2025) ([PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12261487/)) | Hypergraph |
| **HERMES** (*Bioinformatics* btae750) ([PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11745903/)) | Biểu diễn thực thể dị cấu |

Ba công trình không thuộc Nhóm 3 nhưng định hình chuẩn mực mới. **VINCENT** (Chuang F.-S. et al., arXiv:2608.25841, 8/2026) giải thích bằng **cặp motif**, mỗi motif lấy từ một thuốc, và kiểm tra bằng nhiễu loạn cục bộ lặp lại. Mean motif recall đạt **0.826 trên 25 cặp có chú giải y văn, so với 0.49–0.66 của các baseline** ([arXiv](https://arxiv.org/abs/2608.25841)). Đây là bài đầu tiên đưa ra lời giải thích **cấp tương tác có đánh giá định lượng**, nhưng chỉ ở mức phân tử. **DeepSynBa** (*Bioinformatics* 2026, btag416) dự đoán toàn bộ ma trận liều–đáp ứng với tham số bề mặt diễn giải được, nhưng không có attribution trên mạng ([OUP](https://academic.oup.com/bioinformatics/article/42/7/btag416/8712837)). **CETExplainer** (arXiv:2408.17129) dùng R-GCN cho đáp ứng đơn thuốc trên 4 loại cạnh, với ground truth dựng từ láng giềng một bước. Best F1@k đạt 0.6594, và stability được đo bằng độ chồng lấn lời giải thích qua các epoch ([arXiv](https://arxiv.org/html/2408.17129v2)). CETExplainer là khuôn mẫu cho cách dựng ground truth "nhất quán láng giềng".

---

## Bảng đối sánh các mô hình Nhóm 3

| Mô hình (venue, năm) | Đồ thị | Kiến trúc | Cơ chế giải thích | Kiểm định lời giải thích | Split mạnh nhất | Code |
|---|---|---|---|---|---|---|
| Cheng 2019 (*Nat Commun*) | Interactome 16.677 protein | Không học (s_AB) | Separation / exposure class | Hồi cứu với tổ hợp đã duyệt | — | Một phần |
| TranSynergy (*PLOS CB* 2021) | STRING + RWR | Transformer | SHAP + GSEA (SA-GSEA) | 7 case study | Leave-drug, leave-cell | Có |
| GraphSynergy (*JAMIA* 2021) | Interactome Cheng | Spatial GCN + attention | Therapy/toxicity score, protein attention | Chú giải chức năng (định tính) | Chưa rõ | Có |
| DeepSignalingSynergy (*AMIA* 2020) | 46 pathway KEGG | Tầng pathway + DBN | iNNvestigate [CHƯA KIỂM CHỨNG] | Chưa rõ | Chưa rõ | Chưa rõ |
| IDSP (arXiv 2021) | 46 pathway KEGG | GNN với trọng số cạnh học được | Trọng số cạnh | Không có số liệu | Inductive (gen) | Không |
| SANEpool (*Cancers* 2023) | KEGG ~1.4k gen | GCN + attention pooling | Tần suất chọn node | KS test | Cặp chưa thấy | Chưa rõ |
| DeepSignalingFlow (*npj SBA* 2024) | KEGG có hướng, 2.016 gen | GNN hai chiều | Trọng số flow trên đường đi ngắn nhất | F-test, 21/41 cell, p < 0.1 | Random 5-fold | Có |
| SynerGNet (*Biomolecules* 2024) | IHP-PING ~19k | GENConv + JK | Không có | — | Random | Có |
| SynPathy (*Mol Cancer Res* 2022) | Khoảng cách PPI tới pathway | Deep learning | Pathway đóng góp | Khoảng cách PPI | Chưa rõ | Dữ liệu trên figshare |
| PathSynergy (*BIB* 2025) | Không có PPI (bản đồ pathway) | GAT + CNN | Gradient trên pathway | Thí nghiệm ướt cho tổ hợp, không cho lời giải thích | Random + tập ngoài | Có |
| DIPx (*eLife* 2025) | PAS + NEA | Random forest | Permutation importance | Case study y văn | Combo chưa thấy | Có |
| SDCInterpreter (*JCIM* 2026) | KG thuốc–gen–pathway–cell | R-GCN | Edge mask PaGE-Link → đường dẫn | Có script, metric chưa rõ | Chưa rõ | Có |
| HANSynergy (*JCIM* 2024) | Dị cấu thuốc–protein–cell | HAN | Attention trước/sau huấn luyện | Định tính | Chưa rõ | Chưa rõ |
| KGANSynergy (*BIB* 2023) | KG | KG attention | Attention láng giềng | Chưa rõ | Chưa rõ | Chưa rõ |
| MGAE-DC (*PLOS CB* 2023) | 3 kênh DDI syn/add/ant | Graph autoencoder | Không có | — | Chưa rõ | Có |
| HypergraphSynergy (*Bioinf* 2022) | Hyperedge bộ ba | HGNN | Không có | — | Combo/cell chưa thấy | Có |
| HGTSynergy (*BMC Bioinf* 2026) | 293 loại cạnh DDI | HAN pre-train | t-SNE, ablation attention | Gián tiếp | Leave-combo | Có |
| SynDRep (*Bioinf Adv* 2025) | KG não 72 loại quan hệ | KGE + RF | Tìm đường dẫn hậu kỳ | Y văn | Nested CV | Có |
| CASynergy (*PLOS CB* 2025) | PPI đặc thù cell line (Steiner) | GCN + causal mask | Mask node/cạnh → Enrichr | 14/100 có y văn | Cold-start ×3 | Có |
| SynCell (arXiv 2025–26) | STRING + cạnh "expresses" | GNN dị cấu | Tuyên bố có, không phân tích | Không có | Thuốc/cell chưa thấy | Chưa rõ |

Bảng cho thấy hai mẫu số chung. **Cột "kiểm định lời giải thích" không có ô nào chứa fidelity, sparsity hay recall đối chiếu ground truth.** Và **chỉ TranSynergy cùng CASynergy chạy split cold-start**, trong khi SynVerse đã chỉ ra rằng chính các split đó mới làm lộ vấn đề.

---

## Mười một chỗ cần sửa trong file tổng quan của bạn

Các chỗ dưới đây đều dựa trên ghi chú nghiên cứu. Nên sửa trước khi đưa file vào chương 2 của luận văn.

| # | Mục trong file tổng quan | Nội dung hiện tại | Cần sửa thành | Nguồn |
|---|---|---|---|---|
| 1 | SDCInterpreter (4.3, bảng 5, tham khảo 17) | "*JCIM* 2025"; "Learnable Edge Masking tương tự GNNExplainer, max MI(Y, G_S)"; đồ thị có hướng 5 tầng có virtual node | ***JCIM* 2026, 66(1):337–348**, DOI 10.1021/acs.jcim.5c02569 (online 12/2025). Tác giả Wang S., …, Chen X. Explainer **dựa trên PaGE-Link** (path-enforcing edge mask cho link prediction dị cấu) chạy trên R-GCN, không phải GNNExplainer. Mô tả 5 tầng / virtual node **chưa được nguồn nào xác nhận** | [GitHub](https://github.com/chenxgscuec/SDCInterpreter) |
| 2 | "KG-Synergy (Zhang et al., *BIB* 2023)" (4.5, tham khảo 13) | Trích xuất chuỗi suy luận đa bước trên Hetionet/DRKG; đặt ở Nhóm 5 | **Không có bài nào tên như vậy.** Gần như chắc chắn là **KGANSynergy** (Zhang G. et al., *BIB* 24(3):bbad167, 2023). Bài này dùng attention trên láng giềng KG, không phải multi-hop reasoning chain. Bài nên chuyển về Nhóm 3 (dị cấu/KG). Có thể cân nhắc thêm Gu et al. *BIB* 2023 bbad285 | [dblp](https://dblp1.uni-trier.de/rec/journals/bib/ZhangGYWLLL23.html) |
| 3 | PaGE-Link (nếu trích) | KDD 2023 | **WWW 2023** (Proc. ACM Web Conference, tr. 3784–3793), arXiv 2302.12465 | [arXiv](https://arxiv.org/pdf/2302.12465.pdf) |
| 4 | DIPx (4.4, bảng 5, tham khảo 16) | "Nguyen et al."; "Pathway-based White-box" đặt trong nhóm VNN; multi-omics (Expr, Mutation, CNV) | Tác giả **Trac Q.T., …, Vu T.N.**; *eLife* 13:RP100071 (VoR 2025). Đây là **random forest regressor** trên PAS, không phải mạng nơ-ron VNN. Giải thích bằng permutation importance. PAS tính từ **biểu hiện** của các tập gen upstream/downstream/driver; ghi chú không xác nhận việc dùng mutation hay CNV làm đặc trưng. Spearman trên combo chưa thấy chỉ 0.26 (không có ý nghĩa) | [eLife](https://elifesciences.org/articles/100071) |
| 5 | GraphSynergy | *JAMIA* 2021 | Venue *JAMIA* 28(11):2336–2345 là **đúng**; một số nguồn thứ cấp ghi nhầm là *Bioinformatics* hoặc *Nature Machine Intelligence*. Có **erratum** (ocab214). Mô tả công thức therapy/toxicity score ("bao phủ module bệnh", "chồng lấn quá mức") **chưa được kiểm chứng** từ full text | [OUP](https://academic.oup.com/jamia/article/28/11/2336/6362567) |
| 6 | MGAE-DC (4.3) | "MGAE-DC (2022)", đặt cạnh các mô hình dị cấu có giải thích | ***PLoS Comput Biol* 19(3), 2023**. Mô hình là autoencoder đa kênh trên đồ thị thuốc–thuốc theo từng cell line, **không có giải thích đường dẫn** | [PMC](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10027223/) |
| 7 | HANSynergy (4.3, tham khảo 15) | Meta-path Drug→Protein→Pathway→Cell line; trích chung "Wang Z. et al., AttenSyn & HANSynergy" | Tác giả **Cheng N., Wang L., Liu Y., Song B., Ding C.**, *JCIM* 64(10):4334–4347. Cần tách thành tham khảo riêng với AttenSyn. Node type theo abstract là thuốc/protein/cell line; **không có bằng chứng về node pathway**. Giải thích dựa trên attention trước/sau huấn luyện | [PubMed](https://pubmed.ncbi.nlm.nih.gov/38709204/) |
| 8 | SynPathy (4.4) | *Brief Bioinform* 2022; mặt nạ nhị phân KEGG | ***Mol Cancer Res* 20(5):762–769, 2022**. Đặc trưng là điểm enrichment pathway tính từ khoảng cách PPI giữa đích thuốc và gen pathway. Mô tả "mặt nạ KEGG" chưa được xác nhận | [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1158/1541-7786.MCR-21-0735&resultType=core&format=json) |
| 9 | TranSynergy (4.3) | SA-GSEA trên Reactome "giải mã chính xác" pathway | Phần đã đọc **không xác nhận Reactome**. Kiểm định chỉ có 7 case study, và tác giả tự nhận diễn giải là giả thuyết. Nên bỏ chữ "chính xác" | [PLOS](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008653) |
| 10 | Phê bình Nhóm 3 (4.3) | Mạng PPI tĩnh, không đặc thù mô, không có hướng | Đã lỗi thời một phần: DeepSignalingFlow dùng KEGG **có hướng**; CASynergy và SynCell dựng mạng **đặc thù cell line**. Khoảng trống còn lại là mạng **có dấu** (kích hoạt/ức chế) và việc chứng minh mạng đặc thù thắng one-hot | [Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11339460/fullTextXML); [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12548910/) |
| 11 | Toàn bộ Nhóm 3 | Thiếu các bài 2024–2026 | Bổ sung CASynergy (*PLOS CB* 2025), HGTSynergy (*BMC Bioinf* 2026), SynCell (preprint), DeepSignalingFlow (*npj SBA* 2024), và đặc biệt là **SynVerse** cùng **One-hot news** cho phần phê bình | xem các mục trên |

---

## Kiểm toán năm 2025–2026: one-hot khớp hiệu năng 16 kiến trúc, rewiring mạng gần như vô hại

Phần phê bình quan trọng nhất với Nhóm 3 không nằm trong bài nào của nhóm này, mà nằm trong hai benchmark độc lập. **SynVerse** (Tasnina N., Haghani M., Murali T.M., *Brief Bioinform* 26(6):bbaf676, 2025) đánh giá 16 mô hình, tổ hợp từ 8 loại đặc trưng (bao gồm target profile và **RWR trên PPI**) với bộ mã hóa GCN hoặc Transformer, trên DrugComb và O'Neil, với bốn kiểu split ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12753315)). Trên cặp chưa thấy, PCC đạt 0.78–0.94, **nhưng không mô hình nào tốt hơn có ý nghĩa so với MLP one-hot** (0.81 so với 0.84 của MARSY; 0.88 so với 0.91 của SynergyX). Shuffle đặc trưng thuốc hoặc cell không gây ảnh hưởng đáng kể. Khi **rewiring mạng giữ nguyên strength, các mô hình vẫn giữ phần lớn PCC**. Từ đó tác giả kết luận rằng mô hình khai thác phân phối synergy riêng của từng thuốc. Dưới leave-drug và leave-cell-line, hiệu năng kém và không mô hình nào thắng baseline. **One-hot news** (Çandır E.B., Kuru H.I., Rattray M., Çiçek A.E., Tastan O., *Bioinformatics* 42(3):btag040, 2026) cho thấy thay đặc trưng bằng one-hot chỉ làm MSE thay đổi khoảng −1% đến +3%. Trên DrugComb leave-drug-out, MatchMaker chỉ đạt PCC 0.13, so với 0.10 của one-hot. Quan trọng nhất cho XAI: trên dữ liệu tổng hợp, **attribution tìm lại được đặc trưng thật (Jaccard ≈ 1.0) khi thực thể không lặp lại, nhưng chỉ đạt Jaccard ≈ 0.2–0.4 khi bộ ba thuốc–thuốc–cell lặp lại** ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13005728/)). Tác giả quy lỗi cho chính cách đặt bài toán theo bộ ba.

Hai kết quả này có ba hệ quả trực tiếp cho các tuyên bố giải thích dựa trên mạng. Thứ nhất, nếu rewiring PPI không làm giảm hiệu năng thì **lời giải thích đường dẫn trên PPI thật không thể được coi mặc nhiên là sinh học**. Một đường dẫn "cơ chế" vẫn xuất hiện, với độ nổi bật tương tự, trên mạng đã rewiring thì đó là sản phẩm của topo hoặc của việc ghi nhớ, không phải của sinh học. Chưa bài nào trong Nhóm 3 chạy kiểm tra này. Thứ hai, enrichment KEGG trên top gen (CASynergy, TranSynergy) và đối chiếu y văn (14/100 tổ hợp) **không phân biệt được lời giải thích thật với lời giải thích từ mô hình ghi nhớ**. Lý do là các gen gần đích thuốc vốn đã nằm trong pathway của thuốc đó. Thứ ba, các kết quả của bạn **tái hiện độc lập** phát hiện của One-hot news ở cấp gen: recall@3 ≤ 0.2, giảm về 0 khi có 40 cell line (gần với 39 cell của O'Neil), và MLP thắng GNN. Đây không phải điểm yếu cần giấu đi. **Đây là bằng chứng sơ bộ cho một paper.**

Lý thuyết XAI trên đồ thị củng cố thêm lập luận này. Faber, Moghaddam & Wattenhofer (KDD 2021) chỉ ra năm cạm bẫy khi so lời giải thích với ground truth đã cài sẵn, trong đó cạm bẫy chính là GNN có thể không dùng motif đã cài ([DBLP](https://dblp.org/rec/conf/kdd/FaberMW21)). Đây chính là hiện tượng recall@3 thấp của bạn. Azzolin et al. (ICLR 2025) chứng minh rằng các metric faithfulness không thay thế được cho nhau. Với GNN chính quy đơn ánh, lời giải thích trung thực tuyệt đối lại hoàn toàn không mang thông tin. Faithfulness cũng gắn chặt với hành vi OOD ([arXiv](https://arxiv.org/abs/2406.15156v2)). Về attention, Hu et al. (arXiv 2410.06950) cho thấy nhiễu nhỏ làm thay đổi đáng kể attention của GAT ([arXiv](https://arxiv.org/abs/2410.06950v1)), và Shin et al. (arXiv 2406.04612) cho thấy lấy trung bình attention qua các lớp là chưa đủ ([arXiv](https://arxiv.org/html/2406.04612v1)). Như vậy, HANSynergy, KGANSynergy, GraphSynergy và SANEpool, vốn đều dựa trên attention hoặc pooling, sẽ không thuyết phục được reviewer nếu thiếu kiểm tra fidelity bằng nhiễu loạn. Cuối cùng là nhiễu nhãn: một preprint phân tích 391.652 ma trận DrugComb báo cáo **Loewe chỉ tương quan r = 0.28 với ZIP và r = 0.33 với Bliss**, và 21–34% ma trận bị một phương pháp gọi là synergy trong khi phương pháp khác gọi là antagonism ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13060067/)). Các con số này **[CHƯA KIỂM CHỨNG]** từ full text. Với bài toán 3 lớp Loewe ±10 của bạn, đây là lý do cần báo cáo độ nhạy của lời giải thích theo loại score.

Để công bằng, cũng cần trình bày lập luận mạnh nhất của phía ngược lại. One-hot đứng ngang hiệu năng không có nghĩa là mạng vô dụng cho *giải thích*. Mạng có thể vẫn là không gian giả thuyết hữu ích, giống AUC 0.589 của Cheng 2019 nhưng vẫn có p < 10⁻⁴ cho lớp P2. Điều cần làm vì vậy không phải bỏ Nhóm 3, mà là **đo xem lời giải thích mạng chứa bao nhiêu thông tin vượt quá danh tính thực thể và vượt quá topo ngẫu nhiên**.

---

## Bộ công cụ explainer chuyển giao được từ XAI đồ thị

Ghi chú nghiên cứu **không tìm thấy bài nào áp dụng PaGE-Link, Power-Link, xPath, CF-GNNExplainer hay GSAT cho đồ thị hiệp đồng thuốc**, trừ việc SDCInterpreter dựa trên PaGE-Link. Các phương pháp chính:

**Explainer dạng đường dẫn:**
- **PaGE-Link** (Zhang S. et al., WWW 2023) học edge mask theo từng loại cạnh, có ràng buộc ép các cạnh được chọn tạo thành đường dẫn từ nguồn tới đích, sau đó tìm k đường dẫn ngắn nhất trên đồ thị đã nhân trọng số mask. Runtime tuyến tính theo số cạnh, và 78.79% phản hồi trong đánh giá người dùng ưa thích lời giải thích của nó ([arXiv](https://arxiv.org/pdf/2302.12465.pdf)). Thông tin "78.79%" lấy từ một bản tóm tắt.
- **Power-Link** (KDD 2024) là explainer đường dẫn cho knowledge graph completion ([liner](https://liner.com/review/pathbased-explanation-for-knowledge-graph-completion)).
- **xPath** (AAAI 2023) giải thích bằng cặp (node, đường ảnh hưởng) qua rewiring ([arXiv](https://arxiv.org/pdf/2312.15237)).

**Explainer phản thực tế:**
- **CF-GNNExplainer** (AISTATS 2022) chỉ xóa cạnh, tìm tập xóa tối thiểu làm lật dự đoán ([arXiv](https://arxiv.org/pdf/2102.03322v4)). Cách này phù hợp với "knockout in silico" và có thể đối chiếu với DepMap CRISPR.

**Attribution tương tác:**
- **Integrated Hessians** (Janizek et al., JMLR 2021) mở rộng IG cho tương tác bậc 2 và đã được áp dụng cho dữ liệu tổ hợp thuốc AML ([JMLR](https://jmlr.org/papers/v22/20-1223.html)).
- **Janizek et al., *Nat Biomed Eng* 2023** dùng Shapley interaction index giữa thuốc và gen trên ensemble XGBoost ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11149694)). Bài cho thấy độ chính xác dự đoán không phản ánh chất lượng lời giải thích, và ensemble nâng cosine similarity giữa các attribution từ **0.77 lên 0.98**. Bài cũng kiểm chứng bằng DepMap (P empirical ≤ 0.026).

**Mô hình tự giải thích:**
- **GSAT** (ICML 2022) dùng stochastic edge attention với information bottleneck ([arXiv](https://arxiv.org/abs/2201.12987)). Theo Azzolin et al., kiểu mô hình mô-đun này thoát khỏi kết quả "lời giải thích trung thực thì vô thông tin" ([arXiv](https://arxiv.org/abs/2406.15156v2)).

**Metric đánh giá:**
- **GraphFramEx** (LoG 2022) tách Fid+ (tính cần) và Fid− (tính đủ), gộp lại thành characterization score ([PMLR](https://proceedings.mlr.press/v198/amara22a.html)).
- **GraphXAI/ShapeGGen** (*Sci Data* 2023) cung cấp GEA, GEF và GES ([arXiv](https://arxiv.org/abs/2208.09339v2)).
- Công thức chính xác của hai bộ metric này đánh dấu [CHƯA KIỂM CHỨNG]; cần đọc lại PDF.

**Điểm kết nối với code của bạn:** cấp (iii) "interaction" của bạn, Δ(A,B) − E_r Δ(A,r) − E_r Δ(r,B) + E_{r,r'} Δ(r,r'), về cấu trúc chính là **sai phân bậc hai trong Shapley interaction index** của Grabisch & Roubens (1999). Cả hai cùng có dạng v(S∪{i,j}) − v(S∪{i}) − v(S∪{j}) + v(S) ([doi](https://doi.org/10.1007/s001820050125)). Bạn đang ở vị trí thuận lợi để đưa khái niệm này từ cấp gen lên **cấp đường dẫn hoặc cạnh**. Ghi chú xác nhận chưa ai làm điều này cho GNN hiệp đồng.

---

## Bảy khoảng trống, và chỉ ba khoảng trống vừa sức luận văn thạc sĩ

| # | Khoảng trống | Hiện trạng (bằng chứng) | Mức mở | Phù hợp luận văn thạc sĩ? |
|---|---|---|---|---|
| G1 | Đo định lượng fidelity của lời giải thích đường dẫn/đồ thị con trong hiệp đồng | Không bài nào trong bảng đối sánh có; SDCInterpreter có script nhưng metric chưa rõ | **Mở** | **Rất phù hợp**: tiếp nối kill test có sẵn |
| G2 | Đối chứng rewiring và one-hot **cho lời giải thích** (không chỉ cho hiệu năng) | SynVerse chỉ làm cho hiệu năng; One-hot news làm cho attribution đặc trưng, chưa làm cho đường dẫn mạng | **Mở** | **Rất phù hợp** |
| G3 | Attribution cấp tương tác (không cộng tính) trên mạng gen | VINCENT mới làm ở cấp motif phân tử; mạng thì chưa ([arXiv](https://arxiv.org/abs/2608.25841)) | **Mở ở cấp mạng** | **Phù hợp**: code IG cấp (iii) là điểm khởi đầu |
| G4 | Mạng có dấu và có hướng (OmniPath/SIGNOR) với explainer đường dẫn | DeepSignalingFlow có hướng nhưng không có dấu; CASCADE thuộc logic modelling ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7399174/)) | Mở với deep learning | Trung bình: tốn công tiền xử lý |
| G5 | Giải thích phản thực tế kiểu knockout, kiểm chứng bằng DepMap/SynLethDB | Chưa có bài nào cho bộ ba hiệp đồng | Mở | Trung bình |
| G6 | DTI dự đoán làm hạt giống cho thuốc chưa biết đích | Chưa có; leave-drug PCC chỉ ≈ 0.10–0.13 | Mở | Rủi ro cao |
| G7 | Giải thích phụ thuộc liều | DeepSynBa dự đoán theo liều nhưng không giải thích trên mạng | Mở | Thấp: cần dữ liệu ma trận liều |

---

## Ba đề xuất luận văn, xếp hạng theo khả năng thành paper

### Đề xuất 1 (khuyến nghị): "Lời giải thích đường dẫn có thật sự là sinh học?" — benchmark và giao thức kiểm định cấp tương tác

**Ý tưởng:** biến phát hiện "recall@3 thấp, MLP thắng GNN" thành đóng góp chính. Bạn xây một giao thức kiểm định cho lời giải thích trên mạng PPI/signaling, rồi áp dụng nó lên các explainer đại diện của Nhóm 3. Đề xuất này đóng cùng lúc G1, G2 và G3.

**Câu hỏi nghiên cứu:**
- **RQ1:** Lời giải thích trên PPI thật có khác lời giải thích trên PPI đã degree-preserving rewiring hay không? Lấy "explanation survival rate" làm chỉ số.
- **RQ2:** Lời giải thích cấp tương tác (cấp iii) có giảm nhầm lẫn với hiệu ứng chính *ở cấp đường dẫn* như nó đã làm ở cấp gen (main@3 từ 0.40 xuống 0.15) hay không?
- **RQ3:** Số cell line và mức lặp lại của bộ ba ảnh hưởng thế nào đến khả năng tìm lại cơ chế? Câu hỏi này tổng quát hóa phát hiện 40 cell → recall 0 của bạn và kết quả Jaccard 0.2–0.4 của One-hot news.

**Phương pháp:**
1. Thay PPI ngẫu nhiên trong `make_synthetic.py` bằng **topo thật**: STRING có ngưỡng, và một mạng con KEGG ~2k gen như của DeepSignalingFlow.
2. Cài sẵn cơ chế theo lý thuyết Cheng. Ví dụ: hiệp đồng xảy ra khi đích A và đích B nằm trên hai nhánh song song cùng hội tụ về một gen downstream (đúng mẫu "Complementary Exposure"), hoặc khi chúng chạm một cặp SynLethDB, có gating theo biểu hiện của cell line. Giữ nguyên ba nhóm gen Z/W/M như thiết kế hiện tại.
3. Mở rộng explainer từ gen lên đường dẫn theo bốn hướng:
   - IG cạnh (edge-mask IG);
   - PaGE-Link có hai nguồn A và B, mask đối xứng hóa;
   - GNNExplainer/CF-GNNExplainer;
   - phiên bản **interaction** của cả ba, áp dụng công thức ANOVA trục thuốc cho điểm cạnh.
4. Thêm hai baseline phi học máy là **s_AB của Cheng** và **đường đi ngắn nhất giữa đích hai thuốc**. Đây là điểm mạnh riêng: nếu explainer GNN không thắng được s_AB thì chính điều đó đã là một phát hiện.
5. Chạy **kiểm tra Faber**: ablate motif đã cài và xác nhận độ chính xác của mô hình sụp đổ, để chứng minh mô hình thật sự dùng motif. Chỉ khi qua kiểm tra này mới chấm recall.

**Thí nghiệm và đối chứng:**
- **Mô hình:** GCN đối xứng hiện có, GAT, và một GSAT-style self-explaining. Đối chứng gồm **one-hot MLP**, MLP kiểu DeepSynergy, **shuffle đặc trưng**, **degree-preserving rewiring** (và strength-preserving theo SynVerse), và **mạng ngẫu nhiên**.
- **Split:** leave-combo, leave-drug, leave-cell.
- **Dữ liệu thật:** O'Neil, bổ sung cell line từ DrugComb hoặc NCI-ALMANAC để giảm vấn đề 40 cell line. Nhãn 3 lớp Loewe ±10; phân tích độ nhạy với Bliss/ZIP và ngưỡng 5/20.
- **Kiểm chứng sinh học** theo các tầng mà ghi chú đề xuất:
  - độ chồng lấn với đích DrugBank;
  - enrichment KEGG/Reactome của MoA đã biết;
  - DepMap gene effect mạnh hơn ở các cell line có hiệp đồng;
  - enrichment cặp SL;
  - một positive control là BRAF+MEK (dabrafenib + trametinib) với đường dẫn kỳ vọng BRAF→MEK1/2→ERK. Lưu ý control này cần cell line BRAF-V600, và cần kiểm tra cặp thuốc có trong dữ liệu hay không. Trích dẫn NEJM 2012 là [CHƯA KIỂM CHỨNG] lại.

**Metric:**
- recall@k và main@k cho gen **và** cho đường dẫn (path-Jaccard với ground truth);
- Fid+, Fid− và characterization score, kèm biến thể ROAR (retrain sau khi xóa) để tránh OOD theo Azzolin;
- sparsity;
- stability qua 5 seed × 5 fold, báo cosine giữa các seed, kèm baseline ensemble theo Janizek;
- **rewiring-survival rate**: tỷ lệ cạnh hoặc đường dẫn top-k vẫn nổi bật khi chạy trên mạng đã rewiring. Chỉ số này thấp là tốt.

**Kết quả "thắng" ở cả hai nhánh:** nếu explainer cấp tương tác vượt trội và lời giải thích không sống sót qua rewiring, paper có tính xây dựng. Nếu mọi explainer thất bại, paper trở thành một nghiên cứu phản biện kiểu One-hot news, vốn đã được *Bioinformatics* chấp nhận. **Venue:** *Bioinformatics*, *BIB*, *PLOS Comput Biol*. Có thể nộp bản workshop trước (NeurIPS/ICML workshop về ML for drug discovery hoặc XAI, IEEE BIBM, ACM-BCB); đây là gợi ý suy luận, ghi chú không có nguồn về chính sách venue. **Rủi ro:** (i) PaGE-Link cho link prediction cần chỉnh lại cho bộ ba, với hai nguồn và ngữ cảnh cell line; (ii) chi phí tính toán trên STRING toàn bộ, giảm bằng cách giới hạn k-hop quanh đích; (iii) reviewer có thể cho rằng dữ liệu bán tổng hợp là "do mình tự thiết kế". Có thể giảm rủi ro (iii) bằng cách thiết kế nhiều kiểu cơ chế, và bắt buộc kèm thí nghiệm trên dữ liệu thật với rewiring.

### Đề xuất 2: knockout in silico trên mạng tín hiệu có dấu và có hướng

**Ý tưởng:** dùng KEGG có hướng (như DeepSignalingFlow) hoặc OmniPath/SIGNOR có dấu. Huấn luyện GNN có message passing tách theo dấu và hướng. Giải thích bằng **CF-GNNExplainer chỉ xóa cạnh, và chỉ ở cấp gen**: tìm tập gen nhỏ nhất mà xóa đi làm lật syn → add. **RQ:** knockout counterfactual có tương quan với DepMap CRISPR gene effect và với SynLethDB hơn so với IG hoặc attention không? Mạng có dấu có tạo ra lời giải thích dạng "A ức chế X, X kích hoạt Y, B ức chế Y" mà chuyên gia đánh giá được không? **Đối chứng:** giống Đề xuất 1, cộng thêm mạng bị đảo dấu ngẫu nhiên. **Venue:** *PLOS Comput Biol*, *BIB*, *JCIM*. **Rủi ro:** mạng có dấu chỉ phủ ít gen nên mất nhiều thuốc; mô hình có thể không dùng mạng (GNN ≤ MLP), khi đó counterfactual chỉ giải thích việc ghi nhớ; tiền xử lý OmniPath tốn thời gian. Đề xuất này phù hợp nhất nếu được **gộp làm một chương mở rộng của Đề xuất 1** ("explainer phản thực tế" là một cột trong benchmark), thay vì làm một luận văn riêng.

### Đề xuất 3: DTI dự đoán làm hạt giống cho thuốc chưa biết đích

**Ý tưởng:** đây là hướng 6.1 trong file tổng quan của bạn. Một nhánh dự đoán xác suất DTI từ SMILES, rồi dùng vector đó làm p⁽⁰⁾ cho RWR hoặc GNN trên PPI. **RQ:** với leave-drug-out, hạt giống dự đoán có thắng one-hot không, và lời giải thích có ổn định khi thay đích thật bằng đích dự đoán không? **Lý do xếp cuối:** SynVerse và One-hot news cho thấy leave-drug PCC chỉ khoảng 0.10–0.13 với mọi đặc trưng. Sai số DTI cộng dồn vào lời giải thích. Bài toán lại có hai mô hình lồng nhau, quá nặng cho một luận văn thạc sĩ. Nên coi đây là phần "future work", hoặc một thí nghiệm nhỏ: thay đích thật bằng đích dự đoán và đo độ suy giảm của recall đường dẫn.

### Xếp hạng và khuyến nghị

| Hạng | Đề xuất | Tính mới | Khả thi (9–12 tháng) | Tận dụng code sẵn có | Khả năng thành paper |
|---|---|---|---|---|---|
| 1 | Benchmark kiểm định lời giải thích đường dẫn cấp tương tác + đối chứng rewiring | Cao (G1+G2+G3 chưa ai làm) | Cao | Rất cao (IG 3 cấp, kill test, baseline MLP) | Cao: thắng ở cả hai nhánh kết quả |
| 2 | Knockout counterfactual trên mạng có dấu/có hướng | Cao (G4+G5) | Trung bình | Trung bình | Trung bình–cao; tốt nhất khi gộp vào hạng 1 |
| 3 | DTI dự đoán làm hạt giống cho cold-start | Trung bình | Thấp | Thấp | Thấp–trung bình |

**Khuyến nghị:** chọn Đề xuất 1, và dành 1–2 tháng cuối cho một "lát cắt" của Đề xuất 2 (CF-GNNExplainer cấp gen kèm đối chiếu DepMap) để tăng chiều sâu sinh học.

**Lộ trình 12 tháng gợi ý:**

| Tháng | Công việc |
|---|---|
| 1–2 | Chạy lại kill test với 5 seed × 5 fold; thay PPI ngẫu nhiên bằng STRING/KEGG thật; cài cơ chế Complementary Exposure; thêm kiểm tra Faber |
| 3–4 | Viết explainer cấp cạnh/đường dẫn (edge-IG, PaGE-Link hai nguồn, GNNExplainer) và phiên bản interaction; thêm baseline s_AB |
| 5–6 | Đối chứng one-hot / shuffle / rewiring; metric Fid±, ROAR, stability, rewiring-survival; trả lời RQ1–RQ3 trên dữ liệu bán tổng hợp |
| 7–8 | Dữ liệu thật: O'Neil + bổ sung cell line từ ALMANAC/DrugComb; ba kiểu split; độ nhạy theo Loewe/Bliss/ZIP |
| 9 | Kiểm chứng sinh học: DepMap, SynLethDB, enrichment, positive control MAPK; tùy chọn lát cắt CF-GNNExplainer |
| 10 | Bản workshop hoặc hội nghị (BIBM, ACM-BCB) |
| 11–12 | Viết luận văn và bản journal (*Bioinformatics*/*BIB*); công bố code |

**Mốc ra quyết định (gate):** cuối tháng 6, nếu GNN trên mạng thật vẫn không thắng one-hot và lời giải thích vẫn sống sót qua rewiring, hãy chuyển trọng tâm paper sang hướng phản biện ("network path explanations in synergy models are not biological"), thay vì cố cải thiện kiến trúc.

---

## Kết luận

Nhóm 3 đã đi từ một chỉ số topo được thiết kế bằng tay (s_AB) đến các explainer học mask trên đồ thị dị cấu (SDCInterpreter, CASynergy). Nhưng trong suốt bảy năm đó, tiêu chuẩn kiểm định lời giải thích gần như không thay đổi: vẫn là case study, enrichment và đối chiếu y văn. Các benchmark năm 2025–2026 làm vấn đề này trở nên cấp bách. Khi rewiring mạng không làm giảm hiệu năng và attribution thất bại dưới cấu trúc bộ ba lặp lại, thì một "đường dẫn cơ chế" nếu không có đối chứng chỉ là một giả thuyết đẹp, chưa phải một kết quả. Điều cần thay đổi trong cách hiểu là: câu hỏi mở của Nhóm 3 không còn là "kiến trúc đồ thị nào dự đoán tốt hơn", mà là **"lời giải thích trên mạng chứa bao nhiêu thông tin vượt quá danh tính thực thể và topo ngẫu nhiên"**.

Lợi thế lớn nhất của bạn là đã có đúng những công cụ mà lĩnh vực đang thiếu: một toán tử interaction cùng cấu trúc với Shapley interaction index, một kill test có ground truth, và một kết quả tiêu cực trung thực (MLP thắng GNN, recall sụp đổ ở 40 cell). Nâng các công cụ đó từ cấp gen lên cấp đường dẫn, rồi đặt chúng cạnh đối chứng rewiring và baseline s_AB của Cheng, sẽ tạo ra một đóng góp mà SDCInterpreter, CASynergy hay SynVerse đều chưa làm. Đóng góp này có giá trị bất kể kết quả cuối cùng là lời giải thích mạng có ý nghĩa sinh học hay không.
