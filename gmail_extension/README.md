# Hướng Dẫn Cài Đặt & Sử Dụng Gmail Phishing Detector Extension 🛡️

Extension này cho phép bạn tích hợp trực tiếp mô hình **AI Phishing Detection** vào giao diện web của **Gmail (mail.google.com)**.

---

## 1. Các tính năng nổi bật

- **Tự động nhúng nút quét**: Mỗi khi mở email bất kỳ trong Gmail, extension sẽ tự động hiển thị nút **`🛡️ Kiểm tra Phishing (AI)`** trên thanh công cụ của bức thư.
- **Trích xuất thông minh**: Tự động gom tiêu đề, người gửi và nội dung thư để phân tích.
- **Security Banner chuyên nghiệp**:
  - 🚨 **CẢNH BÁO ĐỎ (Phishing/Spam)**: Cảnh báo nguy hiểm kèm % rủi ro, thời gian xử lý và khuyến nghị người dùng không bấm vào link.
  - 🟡 **CẢNH BÁO VÀNG (Cần lưu ý / Tiếp thị)**: Thư quảng cáo, tiếp thị cần lưu ý.
  - 🛡️ **XÁC THỰC XANH (An toàn)**: Thông báo thư hợp lệ và độ tin cậy an toàn.
- **Popup kiểm tra nhanh**: Cho phép dán bất kỳ đoạn text / email nào để kiểm tra ngay từ biểu tượng trên thanh trình duyệt.

---

## 2. Các bước cài đặt vào Trình duyệt (Chrome / Edge / Cốc Cốc / Brave)

Extension được xây dựng theo chuẩn **Manifest V3** mới nhất và có thể nạp trực tiếp chỉ trong 30 giây:

### Bước 1: Mở trang quản lý tiện ích của trình duyệt
- Trên thanh địa chỉ của Google Chrome / Cốc Cốc, gõ: `chrome://extensions/` rồi nhấn Enter.
- *(Nếu dùng Microsoft Edge, gõ: `edge://extensions/`)*.

### Bước 2: Bật chế độ dành cho nhà phát triển (Developer Mode)
- Nhìn lên góc trên cùng bên phải của trang quản lý tiện ích.
- **Gạt công tắc bật `Developer mode` (Chế độ dành cho nhà phát triển)** sang màu xanh.

### Bước 3: Nạp Extension (Load unpacked)
- Sau khi bật Developer mode, nhìn sang góc trên bên trái sẽ xuất hiện nút **`Load unpacked` (Tải tiện ích đã giải nén)**.
- Nhấp vào nút **`Load unpacked`** và duyệt chọn thư mục:
  ```text
  gmail_extension
  ```
- Nhấn **Select Folder**.

Ngay lập tức, tiện ích **"Gmail Phishing Detector - AI Serverless"** với biểu tượng chiếc khiên xanh sẽ xuất hiện trong danh sách!

---

## 3. Cách sử dụng trên Gmail

1. Mở trình duyệt và truy cập vào [Gmail](https://mail.google.com/) *(nhấn `F5` nếu đang mở sẵn)*.
2. Mở một email bất kỳ để đọc nội dung.
3. Bạn sẽ thấy nút màu xanh **`🛡️ Kiểm tra Phishing (AI)`** xuất hiện ngay cạnh các nút thao tác của email.
4. Nhấp vào nút này:
   - Nút sẽ chuyển sang trạng thái: `⏳ Đang phân tích AI...`.
   - Kết quả phân tích sẽ trả về chỉ trong chớp mắt (< 300ms).
   - Một **Security Banner** sẽ hiển thị ngay đầu bức thư, chỉ rõ mức độ rủi ro và khuyến nghị an toàn!
