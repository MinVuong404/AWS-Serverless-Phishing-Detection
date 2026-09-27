import json
import time
import uuid
import os
import re
import boto3
import joblib

# -------------------------------------------------------------------
# 1. HÀM TIỀN XỬ LÝ VĂN BẢN (Chuẩn hóa Email, URL, ký tự tiếng Việt)
# -------------------------------------------------------------------
def preprocess_hybrid_text(text):
    text = str(text)
    # Thay thế email và URL bằng token đại diện
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', ' tagemail ', text)
    text = re.sub(r'http[s]?://\S+|www\.\S+', ' tagurl ', text)
    text = text.lower()
    # Giữ lại bảng chữ cái tiếng Việt có dấu, chữ số và khoảng trắng
    vietnamese_pattern = r'[^a-z0-9àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệđìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳýỵỷỹ\s]'
    text = re.sub(vietnamese_pattern, ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# -------------------------------------------------------------------
# 2. KHỞI TẠO MÔ HÌNH Ở GLOBAL SCOPE (Tối ưu Warm Start & Latency)
# -------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(__file__)

print("Đang tải các mô hình vào bộ nhớ Lambda...")
tfidf = joblib.load(os.path.join(CURRENT_DIR, 'hybrid_tfidf_vectorizer.joblib'))
svd = joblib.load(os.path.join(CURRENT_DIR, 'hybrid_svd_model.joblib'))
xgb_model = joblib.load(os.path.join(CURRENT_DIR, 'hybrid_xgboost_dense.joblib'))

# Cấu hình XGBoost chạy CPU trên Lambda
xgb_model.set_params(device='cpu')
print("Nạp mô hình XGBoost thành công!")

# Khởi tạo kết nối AWS Services
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('TABLE_NAME', 'PhishingDetectionLogs')
table = dynamodb.Table(table_name)

sns_client = boto3.client('sns')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')

# -------------------------------------------------------------------
# 3. LAMBDA HANDLER
# -------------------------------------------------------------------
def lambda_handler(event, context):
    start_time = time.time()
    
    # Đọc dữ liệu đầu vào (từ API Gateway hoặc test trực tiếp)
    try:
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        user_input = body.get('text', '').strip()
        if not user_input:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Trường 'text' không được để trống."}, ensure_ascii=False)
            }
    except Exception as e:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Lỗi định dạng JSON: {str(e)}"}, ensure_ascii=False)
        }

    # Pipeline suy luận XGBoost:
    # 1. Tiền xử lý
    cleaned_text = preprocess_hybrid_text(user_input)
    
    # 2. TF-IDF vectorization (Sparse matrix)
    vec_sparse = tfidf.transform([cleaned_text])
    
    # 3. TruncatedSVD dimensionality reduction (Dense matrix)
    vec_dense = svd.transform(vec_sparse)
    
    # 4. Dự đoán xác suất lừa đảo (Nhãn 1: Phishing)
    probabilities = xgb_model.predict_proba(vec_dense)[0]
    prob_phishing = float(probabilities[1])
    is_phishing = bool(prob_phishing >= 0.5)
    label = "PHISHING/SPAM" if is_phishing else "LEGITIMATE/SAFE"
    
    latency_ms = round((time.time() - start_time) * 1000, 2)
    request_id = str(uuid.uuid4())
    timestamp = int(time.time())

    # Ghi nhật ký vào DynamoDB
    try:
        table.put_item(
            Item={
                'request_id': request_id,
                'timestamp': timestamp,
                'text_preview': user_input[:250],
                'label': label,
                'is_phishing': is_phishing,
                'confidence': str(round(prob_phishing, 4)),
                'latency_ms': str(latency_ms),
                'model_used': 'XGBoost-SVD'
            }
        )
    except Exception as db_err:
        print(f"DynamoDB Error: {db_err}")

    # Gửi cảnh báo tự động qua Amazon SNS nếu xác suất >= 90%
    if prob_phishing >= 0.90 and SNS_TOPIC_ARN:
        try:
            alert_message = (
                f"🚨 CẢNH BÁO NGUY HIỂM CAO: PHÁT HIỆN TIN NHẮN PHISHING/SPAM (>= 90%)!\n\n"
                f"- Request ID: {request_id}\n"
                f"- Độ tin cậy lừa đảo: {prob_phishing * 100:.2f}%\n"
                f"- Mô hình: XGBoost (TF-IDF + SVD)\n"
                f"- Trích đoạn nội dung:\n\"{user_input}\"\n\n"
                f"- Độ trễ xử lý: {latency_ms} ms"
            )
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="[AWS Security Alert] Phát hiện Phishing nguy cơ cao!",
                Message=alert_message
            )
        except Exception as sns_err:
            print(f"SNS Error: {sns_err}")

    # Trả về kết quả JSON cho Client
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST,OPTIONS"
        },
        "body": json.dumps({
            "request_id": request_id,
            "label": label,
            "is_phishing": is_phishing,
            "confidence": round(prob_phishing, 4),
            "model": "XGBoost",
            "latency_ms": latency_ms
        }, ensure_ascii=False)
    }
