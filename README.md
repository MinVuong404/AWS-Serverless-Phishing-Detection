# Hướng Dẫn Cài Đặt & Sử Dụng Tiện Ích Gmail Phishing Detector 🛡️

Tiện ích mở rộng (**Chrome Extension - Manifest V3**) hỗ trợ quét và phát hiện email lừa đảo (Phishing & Spam) theo thời gian thực trực tiếp trên giao diện **Gmail** bằng mô hình Trí tuệ nhân tạo (AI).

---

## 📋 Yêu cầu chuẩn bị

- **Trình duyệt hỗ trợ:** Bất kỳ trình duyệt nào chạy nhân Chromium:
  - Google Chrome
  - Microsoft Edge
  - Cốc Cốc
  - Brave
  - Opera
- Thư mục chứa mã nguồn extension: `gmail_extension/`

---

## 🚀 Các bước cài đặt vào trình duyệt (Chỉ mất 1 phút)

### Bước 1: Mở trang Quản lý tiện ích mở rộng (Extensions)
Tùy vào trình duyệt bạn đang sử dụng, sao chép và dán đường dẫn sau vào thanh địa chỉ rồi nhấn **Enter**:
- **Google Chrome / Cốc Cốc:** `chrome://extensions/`
- **Microsoft Edge:** `edge://extensions/`
- **Brave:** `brave://extensions/`

### Bước 2: Bật "Chế độ dành cho nhà phát triển" (Developer Mode)
- Nhìn lên góc trên cùng bên phải của trang quản lý tiện ích.
- Gạt công tắc **Developer mode (Chế độ dành cho nhà phát triển)** sang trạng thái **Bật (ON)**.

### Bước 3: Nạp tiện ích vào trình duyệt (Load unpacked)
- Sau khi bật Developer mode, góc trên bên trái sẽ xuất hiện nút **Load unpacked** *(Tải tiện ích đã giải nén)*.
- Nhấp vào nút **`Load unpacked`**.
- Trong cửa sổ chọn thư mục, điều hướng đến và chọn thư mục:
  ```text
  gmail_extension
  ```
  > ⚠️ **Lưu ý:** Hãy chọn chính xác thư mục `gmail_extension` (thư mục chứa trực tiếp file `manifest.json`), không chọn thư mục cha ngoài cùng của dự án.
- Nhấn **Select Folder** (hoặc *Chọn thư mục*).

🎉 **Hoàn tất!** Tiện ích **"Gmail Phishing Detector - AI Serverless"** với biểu tượng khiên bảo mật sẽ hiển thị ngay trong danh sách tiện ích của bạn.

---

## 📌 Ghim tiện ích lên thanh công cụ (Khuyên dùng)

Để tiện theo dõi và sử dụng nhanh:
1. Nhấp vào biểu tượng **Mảnh ghép (Tiện ích / Extensions)** ở góc trên bên phải thanh công cụ trình duyệt.
2. Tìm tiện ích **Gmail Phishing Detector - AI Serverless**.
3. Nhấp vào biểu tượng **Ghim (Pin 📌)** để tiện ích luôn hiển thị trên thanh công cụ.

---

## 💡 Hướng dẫn sử dụng chi tiết

### Cách 1: Quét trực tiếp trên giao diện Gmail
1. Truy cập vào [Gmail](https://mail.google.com/) *(nếu đang mở sẵn Gmail, hãy nhấn `F5` để tải lại trang)*.
2. Mở một email bất kỳ mà bạn muốn kiểm tra.
3. Bạn sẽ thấy nút màu xanh **`🛡️ Kiểm tra Phishing (AI)`** xuất hiện tự động trên thanh công cụ của bức thư (cạnh các nút Thao tác / Reply).
4. Bấm vào nút **`🛡️ Kiểm tra Phishing (AI)`**:
   - Trạng thái nút chuyển sang `⏳ Đang phân tích AI...`.
   - Kết quả phân tích sẽ hiển thị ngay tức thì (< 300ms) qua **Security Banner** ở đầu bức thư theo 3 cấp độ:
     - 🟢 **An toàn (Safe):** Email hợp lệ, độ tin cậy an toàn cao.
     - 🟡 **Cần lưu ý (Suspicious / Marketing):** Thư quảng cáo hoặc tiếp thị, cần cẩn trọng với các liên kết.
     - 🔴 **Cảnh báo nguy hiểm (Phishing Alert):** Email có dấu hiệu lừa đảo giả mạo cao, khuyến cáo không nhấp link hoặc cung cấp thông tin.

### Cách 2: Kiểm tra nhanh văn bản bất kỳ qua Popup
1. Nhấp trực tiếp vào biểu tượng chiếc khiên **Gmail Phishing Detector** trên thanh công cụ trình duyệt.
2. Dán đoạn văn bản, nội dung thư hoặc đường link nghi ngờ vào ô nhập liệu.
3. Bấm nút **Kiểm tra văn bản** để nhận ngay đánh giá mức độ rủi ro (%) và cảnh báo an toàn.

---

## 🔄 Cách cập nhật tiện ích khi chỉnh sửa mã nguồn

Nếu bạn có bất kỳ thay đổi nào trong thư mục `gmail_extension`:
1. Mở lại trang `chrome://extensions/`.
2. Tìm thẻ tiện ích **Gmail Phishing Detector - AI Serverless**.
3. Nhấn vào biểu tượng **Mũi tên xoay tròn (Reload / Tải lại)**.
4. Quay lại trang Gmail và nhấn `F5` để áp dụng các thay đổi mới.

---

## ❓ Xử lý sự cố thường gặp (Troubleshooting)

| Hiện tượng | Nguyên nhân | Cách xử lý |
| :--- | :--- | :--- |
| **Không thấy nút quét trên Gmail** | Chưa làm mới trang sau khi nạp extension | Nhấn `F5` hoặc tải lại tab Gmail. Đảm bảo bạn đang mở xem một email cụ thể. |
| **Báo lỗi khi "Load unpacked"** | Chọn sai thư mục | Hãy đảm bảo bạn chọn đúng thư mục `gmail_extension` (nơi có file `manifest.json`). |
| **Báo lỗi kết nối API khi bấm quét** | Mất mạng hoặc endpoint chưa phản hồi | Kiểm tra lại kết nối mạng Internet của máy tính. Chờ vài giây rồi bấm thử lại. |
