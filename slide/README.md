# Slide

Hai bộ slide, dựng **thẳng trên file template của trường** bằng `python-pptx`.

| File | Nội dung |
|---|---|
| `01_kien_thuc_nen.pptx` | Kiến thức nền: sinh học tối thiểu, hiệp đồng thuốc, dữ liệu, học máy, giải thích mô hình |
| `02_tong_quan_du_an.pptx` | Dự án SynGT: bài toán, câu hỏi nghiên cứu, dữ liệu, kiến trúc, so sánh, kết quả |

## Dựng lại

```bash
cd slide
python3 build_01.py
python3 build_02.py
```

Sửa nội dung trong hai file `build_0*.py`, đừng sửa thẳng file `.pptx`: lần dựng sau sẽ ghi đè.

## Cách làm

`deck.py` mở `Copy of HUST_PPT_template_2022_Blue_16x9.pptx`, xóa 25 slide mẫu, rồi thêm slide mới trên chính các layout của template. Nhờ vậy deck kế thừa đúng khổ slide 13,333 × 7,5 inch, slide master, thanh navy, đường kẻ đỏ và logo trường, thay vì mô phỏng lại bằng ảnh nền.

- Tiêu đề mỗi slide nằm trong placeholder trên thanh navy: Arial 28 pt, đậm, màu trắng.
- Thân slide từ y = 1,15" tới y = 6,72". Lề trái 0,37", bề rộng 12,59".
- Bảng màu lấy từ template: navy `00376F`, đỏ `C00000`, xanh `1C6EA4`, lục `157B6E`, vàng `B07A00`, xám `5A6B7B`.

`deck.py` cung cấp các hàm dựng khối: `cover`, `content`, `divider`, `card`, `box`, `table`, `lines`, `arrow`, `stat`, `note`.

## Hai cái bẫy đã gặp

1. **Bảng tự cao hơn chiều cao đặt cho hàng.** Ô nào xuống dòng thì hàng giãn ra, nên bảng luôn cao hơn tính toán. Quy tắc: bảng là phần tử cuối cùng của cột chứa nó, dòng chú thích đặt phía trên bảng.
2. **Phải kiểm tra bằng ảnh, không bằng mã.** Sau khi dựng, render ra JPG rồi soi từng slide:

```bash
SK=/root/.claude/skills/synced/effdbcd2-bb45-40b7-bc24-4e93d3730cd1_165f13a5-ead1-4f78-b896-cd2077ad7dad/pptx
python $SK/scripts/office/validate.py 01_kien_thuc_nen.pptx --original "Copy of HUST_PPT_template_2022_Blue_16x9.pptx"
python $SK/scripts/office/soffice.py --headless --convert-to pdf 01_kien_thuc_nen.pptx
pdftoppm -jpeg -r 110 01_kien_thuc_nen.pdf qa/01
```

## Chỗ cần điền tay

`[Họ và tên]`, `[MSHV]`, `[Tên giảng viên]` ở slide bìa của cả hai file.

`assets/hust_logo.png` là logo ngang trích từ template, chỉ dùng cho slide bìa.
