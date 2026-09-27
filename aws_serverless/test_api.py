import json
import time
import urllib.request
import urllib.error

# Cấu hình URL endpoint API Gateway của bạn sau khi deploy
# Ví dụ: "https://abcdef1234.execute-api.ap-southeast-1.amazonaws.com/predict"
API_URL = "https://<YOUR_API_ID>.execute-api.ap-southeast-1.amazonaws.com/predict"

def send_prediction_request(text_content):
    payload = json.dumps({"text": text_content}).encode('utf-8')
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    start_time = time.time()
    try:
        with urllib.request.urlopen(req) as response:
            round_trip_ms = round((time.time() - start_time) * 1000, 2)
            status_code = response.getcode()
            response_body = json.loads(response.read().decode('utf-8'))
            return status_code, response_body, round_trip_ms
    except urllib.error.HTTPError as e:
        round_trip_ms = round((time.time() - start_time) * 1000, 2)
        return e.code, e.read().decode('utf-8'), round_trip_ms
    except Exception as err:
        return 500, str(err), 0

def run_tests():
    print("=" * 65)
    print("KIỂM THỬ TRỰC TIẾP LIVE API GATEWAY SERVERLESS PHISHING")
    print(f"Target URL: {API_URL}")
    print("=" * 65)

    if "<YOUR_API_ID>" in API_URL:
        print("\n[LƯU Ý] Bạn hãy thay thế biến `API_URL` bằng URL thật từ API Gateway sau khi tạo xong!")
        print("Ví dụ: https://xyz.execute-api.ap-southeast-1.amazonaws.com/predict\n")
        return

    samples = [
        {
            "type": "HỢP LỆ (HAM)",
            "text": "Alo, anh đã nhận được tài liệu báo cáo của em gửi qua mail rồi nhé. Mai trao đổi thêm."
        },
        {
            "type": "LỪA ĐẢO NGUY HIỂM CAO (PHISHING >= 90%)",
            "text": "CẢNH BÁO: Thẻ tín dụng của bạn đã bị khóa tạm thời. Đăng nhập ngay vào http://fake-security-update.com/otp để xác thực trong 15 phút hoặc bị phạt phí 5 triệu đồng."
        }
    ]

    for sample in samples:
        print(f"\n-> Gửi yêu cầu: [{sample['type']}]")
        status, res, rtt = send_prediction_request(sample["text"])
        print(f"HTTP Status: {status} (Khứ hồi mạng: {rtt} ms)")
        print(f"Kết quả trả về:")
        print(json.dumps(res, indent=2, ensure_ascii=False))
        print("-" * 65)

if __name__ == '__main__':
    run_tests()
