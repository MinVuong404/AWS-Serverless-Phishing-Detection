# Mô hình Machine Learning (Pre-trained Weights)

Thư mục này chứa 3 tệp trọng số mô hình đã được huấn luyện sẵn phục vụ nhận diện thư điện tử lừa đảo (Phishing & Spam) theo thời gian thực:

| Tệp mô hình | Thuật toán / Kỹ thuật | Kích thước | Vai trò trong Pipeline |
| :--- | :--- | :--- | :--- |
| **`hybrid_tfidf_vectorizer.joblib`** | TF-IDF n-gram (Word & Char) | ~738 KB | Trích xuất đặc trưng từ vựng n-gram từ văn bản đã qua tiền xử lý Regex, tạo ma trận thưa. |
| **`hybrid_svd_model.joblib`** | Truncated SVD (LSA) | ~34.3 MB | Giảm số chiều của không gian ma trận TF-IDF xuống vector đặc 300 chiều để tối ưu suy luận. |
| **`hybrid_xgboost_dense.joblib`** | Gradient Boosted Trees (XGBoost) | ~1.18 MB | Mô hình phân loại nhị phân chính, dự đoán xác suất lừa đảo ($P \in [0, 1]$). |

---

### Quy trình suy luận (Inference Pipeline):
```
[Văn bản thô]
      │
      ▼
[Tiền xử lý Regex (Chuẩn hóa tiếng Việt, tagemail, tagurl)]
      │
      ▼
[TF-IDF Vectorizer]
      │
      ▼
[Truncated SVD (Giảm chiều)]
      │
      ▼
[XGBoost Classifier]
      │
      ▼
[Xác suất lừa đảo & Nhãn cảnh báo]
```
