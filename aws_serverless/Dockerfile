# Sử dụng base image Python 3.12 (Dựa trên Amazon Linux 2023 có glibc 2.34)
FROM public.ecr.aws/lambda/python:3.12

# Lambda đã có sẵn boto3, chỉ cài scikit-learn, xgboost, joblib để tiết kiệm dung lượng
RUN pip install --no-cache-dir scikit-learn xgboost joblib

# Gộp sao chép toàn bộ mã nguồn và 3 file mô hình trong 1 layer duy nhất (tiết kiệm ổ đĩa)
COPY lambda_function.py hybrid_tfidf_vectorizer.joblib hybrid_svd_model.joblib hybrid_xgboost_dense.joblib ${LAMBDA_TASK_ROOT}/

# Thiết lập Lambda Handler
CMD [ "lambda_function.lambda_handler" ]
