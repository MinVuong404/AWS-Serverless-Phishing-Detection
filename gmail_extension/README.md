# Hướng Dẫn Cài Đặt & Sử Dụng Gmail Phishing Detector Extension

Extension này cho phép bạn tích hợp trực tiếp mô hình **XGBoost AI Serverless** vừa deploy trên AWS vào giao diện web của **Gmail (mail.google.com)**.

---

## 1. Các tính năng nổi bật

- **Tự động nhúng nút quét**: Mỗi khi bạn mở một email bất kỳ trong Gmail, extension sẽ tự động hiển thị nút **`🛡️ Kiểm tra Phishing (AI)`** trên thanh công cụ của bức thư.
- **Trích xuất thông minh**: Tự động gom tiêu đề, người gửi và nội dung bức thư để gửi về AWS Lambda phân tích.
- **Hiển thị Security Banner chuyên nghiệp**:
  - 🚨 **CẢNH BÁO ĐỎ (Phishing/Spam)**: Báo động nguy hiểm kèm % rủi ro, thời gian xử lý và khuyến nghị người dùng không bấm vào link.
  - 🛡️ **XÁC THỰC XANH (An toàn)**: Thông báo thư hợp lệ và độ tin cậy an toàn.
- **Popup kiểm tra nhanh**: Cho phép dán bất kỳ đoạn text nào để quét ngay từ biểu tượng extension trên thanh trình duyệt.

---

## 2. Các bước cài đặt vào Trình duyệt (Chrome / Edge / Cốc Cốc / Brave)

Extension được xây dựng theo chuẩn **Manifest V3** mới nhất và có thể nạp trực tiếp chỉ trong 30 giây:

### Bước 1: Mở trang quản lý tiện ích của trình duyệt
- Trên thanh địa chỉ của Google Chrome, gõ: `chrome://extensions/` rồi nhấn Enter.
- *(Nếu dùng Microsoft Edge, gõ: `edge://extensions/`)*.

### Bước 2: Bật chế độ dành cho nhà phát triển (Developer Mode)
- Nhìn lên góc trên cùng bên phải của trang quản lý tiện ích.
- **Gạt công tắc bật `Developer mode` (Chế độ dành cho nhà phát triển)** sang màu xanh.

### Bước 3: Nạp Extension (Load unpacked)
- Sau khi bật Developer mode, nhìn sang góc trên bên trái sẽ xuất hiện nút **`Load unpacked` (Tải tiện ích đã giải nén)**.
- Nhấp vào nút **`Load unpacked`** và duyệt chọn thư mục:
  `e:\Dev\Dự đoán phising\gmail_extension`
- Nhấn **Select Folder**.

Ngay lập tức, tiện ích **"Gmail Phishing Detector - AI Serverless"** với biểu tượng chiếc khiên xanh sẽ xuất hiện trong danh sách!

---

## 3. Cách sử dụng & Demo thực tế trên Gmail

1. Mở trình duyệt và truy cập vào [Gmail](https://mail.google.com/).
2. Mở một email bất kỳ để đọc nội dung.
3. Bạn sẽ thấy nút màu xanh **`🛡️ Kiểm tra Phishing (AI)`** xuất hiện ngay cạnh các nút thao tác của email (Reply / More) hoặc phía trên phần nội dung thư.
4. Nhấp vào nút này:
   - Nút sẽ chuyển sang trạng thái: `⏳ Đang phân tích AI...`.
   - Kết quả phân tích từ mô hình XGBoost trên AWS Lambda sẽ trả về chỉ trong chớp mắt (< 300ms).
   - Một **Banner bảo mật** sẽ trượt xuống ngay đầu bức thư, hiển thị rõ ràng tỷ lệ % rủi ro lừa đảo và khuyến nghị an toàn!
