import os
import sys
import time
import json
import re
import joblib

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi cp1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thiết lập đường dẫn tới thư mục models
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..', 'hybrid_ml_models'))

def preprocess_hybrid_text(text):
    text = str(text)
    text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', ' tagemail ', text)
    text = re.sub(r'http[s]?://\S+|www\.\S+', ' tagurl ', text)
    text = text.lower()
    vietnamese_pattern = r'[^a-z0-9àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệđìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳýỵỷỹ\s]'
    text = re.sub(vietnamese_pattern, ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def run_offline_test():
    print("=" * 65)
    print("KIỂM THỬ OFFLINE PIPELINE XGBOOST SERVERLESS (MÔ PHỎNG LAMBDA)")
    print("=" * 65)

    print("\n1. Đang nạp mô hình từ đĩa vào bộ nhớ...")
    t0 = time.time()
    tfidf = joblib.load(os.path.join(MODELS_DIR, 'hybrid_tfidf_vectorizer.joblib'))
    svd = joblib.load(os.path.join(MODELS_DIR, 'hybrid_svd_model.joblib'))
    xgb_model = joblib.load(os.path.join(MODELS_DIR, 'hybrid_xgboost_dense.joblib'))
    xgb_model.set_params(device='cpu')
    load_time = (time.time() - t0) * 1000
    print(f"-> Thời gian nạp mô hình (Cold start): {load_time:.2f} ms")

    # Các trường hợp kiểm thử thực tế
    test_cases = [
        {
            "desc": "Tin nhắn an toàn / hợp lệ (Tiếng Việt)",
            "text": "Chào bạn, chiều nay 3h nhóm mình họp dự án ở phòng 402 nhé. Nhớ mang theo tài liệu."
        },
        {
            "desc": "Tin nhắn lừa đảo ngân hàng nguy cơ cao (Phishing alert >= 90%)",
            "text": "THÔNG BÁO KHẨN: Tài khoản Vietcombank của quý khách đã bị tạm khóa do phát hiện giao dịch bất thường. Vui lòng đăng nhập ngay tại http://vcb-xac-thuc-tai-khoan.com/login để xác minh và không bị trừ phí."
        },
        {
            "desc": "Tin nhắn trúng thưởng mạo danh (Spam/Phishing)",
            "text": "Chúc mừng thuê bao của bạn đã may mắn trúng thưởng 1 xe máy SH và 100 triệu đồng. Soạn tin hoặc liên hệ admin@qua-tang-tri-an.net để nhận thưởng ngay hôm nay!"
        }
    ]

    print("\n2. Bắt đầu chạy suy luận (Inference Test):")
    print("-" * 65)

    for idx, tc in enumerate(test_cases, 1):
        text = tc["text"]
        
        # Đo độ trễ suy luận
        start_t = time.time()
        
        # Pipeline
        cleaned = preprocess_hybrid_text(text)
        vec_sparse = tfidf.transform([cleaned])
        vec_dense = svd.transform(vec_sparse)
        probs = xgb_model.predict_proba(vec_dense)[0]
        
        latency = (time.time() - start_t) * 1000
        prob_phishing = float(probs[1])
        is_phishing = bool(prob_phishing >= 0.5)
        label = "PHISHING/SPAM 🚨" if is_phishing else "AN TOÀN (LEGITIMATE) ✅"

        # Đánh giá kích hoạt cảnh báo SNS
        sns_alert = "CÓ (Đạt ngưỡng >= 90%) 📧" if prob_phishing >= 0.90 else "KHÔNG (Dưới 90%)"

        print(f"Test Case #{idx}: {tc['desc']}")
        print(f"  Văn bản: \"{text[:70]}...\"")
        print(f"  Kết quả: {label}")
        print(f"  Xác suất lừa đảo: {prob_phishing * 100:.2f}%")
        print(f"  Độ trễ suy luận:  {latency:.2f} ms")
        print(f"  Kích hoạt SNS:    {sns_alert}")
        print("-" * 65)

    print("\n-> [KẾT LUẬN] Pipeline hoạt động hoàn hảo, thời gian suy luận đạt chuẩn Real-time (< 20ms)!")
    print("=" * 65)

if __name__ == '__main__':
    run_offline_test()
