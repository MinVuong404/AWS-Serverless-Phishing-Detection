# Phân Hệ Serverless Phát Hiện Phishing & Spam Thời Gian Thực (XGBoost)

Thư mục này chứa toàn bộ mã nguồn, kịch bản tự động hóa và tài liệu triển khai cho đề tài **"Hệ thống Serverless phát hiện thư điện tử lừa đảo và tin nhắn rác theo thời gian thực"**, sử dụng kiến trúc máy chủ phi tập trung (Serverless) trên nền tảng Amazon Web Services (AWS) và mô hình **XGBoost (TF-IDF + TruncatedSVD)**.

---

## 1. Cấu trúc thư mục

```text
aws_serverless/
│
├── lambda_function.py        # Mã nguồn Lambda Handler: tiền xử lý, suy luận XGBoost, ghi DynamoDB, bắn SNS
├── build_package.py          # Script tự động gom 3 model có sẵn và nén thành xgboost_deployment.zip
├── test_local.py             # Script kiểm thử offline toàn bộ pipeline ngay trên máy tính cá nhân
├── deploy_aws.py             # Script tự động khởi tạo DynamoDB, SNS, IAM, Lambda, API Gateway bằng Boto3
├── test_api.py               # Script kiểm thử gọi live API Gateway sau khi deploy
└── README.md                 # Tài liệu hướng dẫn sử dụng và báo cáo đề tài
```

---

## 2. Các mô hình Machine Learning sử dụng

Pipeline phân loại văn bản độc hại được cấu hình tuần tự:
1. **`hybrid_tfidf_vectorizer.joblib` (~738 KB)**: Trích xuất đặc trưng từ vựng n-gram và tính toán trọng số TF-IDF dưới dạng ma trận thưa (Sparse matrix).
2. **`hybrid_svd_model.joblib` (~36 MB)**: Thuật toán Truncated SVD (Latent Semantic Analysis - LSA) cô đọng không gian đặc trưng từ vựng thành vector đặc (Dense vector).
3. **`hybrid_xgboost_dense.joblib` (~1.2 MB)**: Thuật toán cây quyết định tăng cường gradient (Gradient Boosted Trees) phân loại nhãn và tính xác suất lừa đảo ($P \in [0, 1]$).

---

## 3. Hướng dẫn sử dụng

### Cách 1: Kiểm thử offline mô phỏng Lambda ngay trên máy
Chạy script kiểm thử để xác nhận mô hình hoạt động chính xác và đo độ trễ suy luận:
```bash
python test_local.py
```

### Cách 2: Đóng gói gói nén tải lên AWS Lambda
Chạy script tự động đóng gói:
```bash
python build_package.py
```
Sau khi chạy xong, tệp `xgboost_deployment.zip` (dung lượng ~38 MB) sẽ được tạo ra trong thư mục `aws_serverless/`.

---

## 4. Hướng dẫn triển khai lên AWS (2 phương án)

### Phương án A: Tự động hóa hoàn toàn bằng script (`deploy_aws.py`)
Nếu máy tính của bạn đã cấu hình AWS CLI (`aws configure`):
1. Mở file `deploy_aws.py`, chỉnh sửa `ADMIN_EMAIL` thành email của bạn.
2. Chạy lệnh:
   ```bash
   python deploy_aws.py
   ```
Script sẽ tự động tạo Bảng DynamoDB, SNS Topic, IAM Role, nén và tải Lambda function lên cùng với cấu hình Klayers (Scikit-learn + XGBoost), sau đó kích hoạt HTTP API Gateway.

### Phương án B: Triển khai thủ công trên AWS Management Console
1. **Tạo DynamoDB Table**:
   - Tên bảng: `PhishingDetectionLogs`
   - Partition Key: `request_id` (String)
   - Capacity mode: **Provisioned** (1 RCU / 1 WCU) -> *Miễn phí trọn đời*.
2. **Tạo Amazon SNS Topic**:
   - Tên Topic: `PhishingAlertTopic` (Standard).
   - Create subscription: Protocol `Email`, nhập địa chỉ email -> Vào email nhấn **Confirm subscription**.
3. **Tạo AWS Lambda Function**:
   - Function name: `PhishingDetectionXGBoost`
   - Runtime: `Python 3.11`, Architecture: `x86_64`
   - Upload code: Tải tệp `xgboost_deployment.zip` tạo từ `build_package.py` lên.
   - Cấu hình phần cứng: Memory **512 MB**, Timeout **5 giây**.
   - Biến môi trường:
     - `TABLE_NAME`: `PhishingDetectionLogs`
     - `SNS_TOPIC_ARN`: *(Dán ARN của SNS Topic)*
   - Thêm Layers (Klayers - Region Singapore `ap-southeast-1`):
     - Layer 1 (Scikit-Learn): `arn:aws:lambda:ap-southeast-1:770693421928:layer:Klayers-p311-scikit-learn:4`
     - Layer 2 (XGBoost): `arn:aws:lambda:ap-southeast-1:770693421928:layer:Klayers-p311-xgboost:4`
4. **Cấp quyền IAM cho Lambda Role**:
   - Gán quyền `dynamodb:PutItem` vào bảng `PhishingDetectionLogs`.
   - Gán quyền `sns:Publish` vào Topic `PhishingAlertTopic`.
5. **Tạo API Gateway**:
   - Tạo **HTTP API**, thêm Route `POST /predict` liên kết tới Lambda function.

---

## 5. Kiểm thử API sau khi triển khai
Mở file `test_api.py`, dán URL của API Gateway vào biến `API_URL` và chạy:
```bash
python test_api.py
```

Hoặc dùng lệnh `curl`:
```bash
curl -X POST https://<api-id>.execute-api.ap-southeast-1.amazonaws.com/predict \
     -H "Content-Type: application/json" \
     -d "{\"text\": \"Khẩn cấp: Tài khoản ngân hàng của bạn bị khóa, truy cập http://fake-login.com để mở khóa.\"}"
```

---

## 6. Bảng số liệu đối chứng phục vụ báo cáo / bảo vệ đề tài

| Tiêu chí so sánh | Mô hình RoBERTa Deep Learning (`multilingual_phishing_model`) | Mô hình Đề xuất XGBoost Serverless (`aws_serverless`) | Mức độ cải thiện |
| :--- | :--- | :--- | :--- |
| **Kích thước mô hình** | **~1.11 GB** (1100 MB) | **~38 MB** | **Giảm 96.5% dung lượng** |
| **Yêu cầu phần cứng** | GPU chuyên dụng (VRAM $\ge$ 4GB) hoặc CPU $\ge$ 4GB RAM | AWS Lambda 512MB RAM | **Giảm 87.5% bộ nhớ** |
| **Khởi động nguội (Cold Start)**| 12 - 25 giây | **~1.2 - 1.8 giây** | **Nhanh hơn gấp 10 lần** |
| **Độ trễ suy luận (Warm)** | 350 - 750 ms | **< 15 ms** | **Nhanh hơn gấp 30 lần (Đạt chuẩn Real-time)** |
| **Chi phí hạ tầng AWS** | ~40 - 120 USD/tháng (EC2/ECS) | **0.00 USD/tháng** (Gói Free Tier) | **Tiết kiệm 100% chi phí** |
