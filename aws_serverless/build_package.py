import os
import shutil
import zipfile
import sys

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi cp1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def build_deployment_package():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    models_dir = os.path.join(project_root, 'hybrid_ml_models')
    
    zip_output_path = os.path.join(current_dir, 'xgboost_deployment.zip')
    
    # Danh sách các tệp cần đóng gói
    required_models = [
        'hybrid_tfidf_vectorizer.joblib',
        'hybrid_svd_model.joblib',
        'hybrid_xgboost_dense.joblib'
    ]
    
    print("=" * 60)
    print("BẮT ĐẦU ĐÓNG GÓI DEPLOYMENT PACKAGE CHO AWS LAMBDA")
    print("=" * 60)
    
    # 1. Kiểm tra sự tồn tại của các file model
    for model_name in required_models:
        model_path = os.path.join(models_dir, model_name)
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Không tìm thấy tệp model: {model_path}")
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"✓ Tìm thấy: {model_name:<35} ({size_mb:.2f} MB)")
        
    lambda_src = os.path.join(current_dir, 'lambda_function.py')
    if not os.path.exists(lambda_src):
        raise FileNotFoundError(f"Không tìm thấy tệp lambda_function.py tại: {lambda_src}")
    print(f"✓ Tìm thấy: {'lambda_function.py':<35} ({os.path.getsize(lambda_src)/1024:.2f} KB)")
    
    # 2. Tạo file ZIP đóng gói
    print(f"\nĐang nén dữ liệu vào: {zip_output_path} ...")
    with zipfile.ZipFile(zip_output_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        # Thêm lambda_function.py
        zipf.write(lambda_src, arcname='lambda_function.py')
        
        # Thêm các tệp model vào thư mục gốc của file ZIP
        for model_name in required_models:
            model_path = os.path.join(models_dir, model_name)
            zipf.write(model_path, arcname=model_name)
            
    # 3. Báo cáo kết quả kích thước
    final_size_mb = os.path.getsize(zip_output_path) / (1024 * 1024)
    print(f"\n-> ĐÃ ĐÓNG GÓI THÀNH CÔNG: {zip_output_path}")
    print(f"-> Dung lượng file ZIP: {final_size_mb:.2f} MB")
    
    if final_size_mb < 50.0:
        print("-> [ĐẠT YÊU CẦU] Dung lượng < 50 MB: Bạn có thể upload trực tiếp lên AWS Lambda Console!")
    else:
        print("-> [LƯU Ý] Dung lượng > 50 MB: Cần tải qua Amazon S3.")
    print("=" * 60)

if __name__ == '__main__':
    build_deployment_package()
