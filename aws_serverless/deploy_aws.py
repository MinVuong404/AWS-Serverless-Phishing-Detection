import os
import sys
import json
import time
import zipfile

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi cp1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import boto3
except ImportError:
    print("Vui lòng cài đặt boto3 để tự động hóa: pip install boto3")
    sys.exit(1)

# ===================================================================
# CẤU HÌNH THÔNG SỐ DEPLOY
# ===================================================================
REGION = os.environ.get('AWS_DEFAULT_REGION', 'ap-southeast-1') # Mặc định Singapore
ADMIN_EMAIL = "your-email@example.com"                          # Thay bằng email thật để nhận cảnh báo
TABLE_NAME = "PhishingDetectionLogs"
SNS_TOPIC_NAME = "PhishingAlertTopic"
FUNCTION_NAME = "PhishingDetectionXGBoost"
ROLE_NAME = "LambdaPhishingXGBoostExecutionRole"
API_NAME = "PhishingDetectionHttpAPI"

# Klayers cho Python 3.11 tại region ap-southeast-1
# Nếu đổi sang us-east-1, thay arn tương ứng
KLAYERS_SKLEARN_ARN = f"arn:aws:lambda:{REGION}:770693421928:layer:Klayers-p311-scikit-learn:4"
KLAYERS_XGBOOST_ARN = f"arn:aws:lambda:{REGION}:770693421928:layer:Klayers-p311-xgboost:4"

def deploy():
    print("=" * 65)
    print(f"BẮT ĐẦU TỰ ĐỘNG KHỞI TẠO VÀ DEPLOY HẠ TẦNG LÊN AWS ({REGION})")
    print("=" * 65)
    
    session = boto3.Session(region_name=REGION)
    sts = session.client('sts')
    try:
        caller_identity = sts.get_caller_identity()
        account_id = caller_identity['Account']
        print(f"✓ Đã xác thực AWS Account ID: {account_id}")
    except Exception as e:
        print(f"❌ Lỗi xác thực AWS CLI/Credentials: {e}")
        print("Mẹo: Hãy chạy lệnh `aws configure` để nhập Access Key & Secret Key.")
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(current_dir, 'xgboost_deployment.zip')
    
    # Kiểm tra file ZIP
    if not os.path.exists(zip_path):
        print("\n-> Chưa tìm thấy file xgboost_deployment.zip, đang tự động gọi build_package.py...")
        import build_package
        build_package.build_deployment_package()

    # 1. Tạo bảng DynamoDB
    print("\n1. Khởi tạo Amazon DynamoDB...")
    ddb_client = session.client('dynamodb')
    try:
        ddb_client.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{'AttributeName': 'request_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'request_id', 'AttributeType': 'S'}],
            BillingMode='PROVISIONED',
            ProvisionedThroughput={'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
        )
        print(f"-> Đang tạo bảng DynamoDB '{TABLE_NAME}' (1 RCU / 1 WCU Free Tier)...")
        waiter = ddb_client.get_waiter('table_exists')
        waiter.wait(TableName=TABLE_NAME)
        print(f"✓ Bảng '{TABLE_NAME}' đã sẵn sàng!")
    except ddb_client.exceptions.ResourceInUseException:
        print(f"✓ Bảng '{TABLE_NAME}' đã tồn tại sẵn.")

    # 2. Tạo Amazon SNS Topic
    print("\n2. Khởi tạo Amazon SNS Topic...")
    sns_client = session.client('sns')
    topic_res = sns_client.create_topic(Name=SNS_TOPIC_NAME)
    topic_arn = topic_res['TopicArn']
    print(f"✓ SNS Topic ARN: {topic_arn}")
    
    if ADMIN_EMAIL != "your-email@example.com":
        sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=ADMIN_EMAIL
        )
        print(f"✓ Đã gửi email xác nhận đăng ký tới: {ADMIN_EMAIL} (Hãy vào hộp thư nhấn Confirm subscription!)")
    else:
        print("-> [LƯU Ý] Chưa cập nhật ADMIN_EMAIL trong deploy_aws.py, hãy cập nhật để nhận mail cảnh báo.")

    # 3. Tạo IAM Role cho Lambda
    print("\n3. Khởi tạo IAM Role...")
    iam_client = session.client('iam')
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    role_arn = None
    try:
        create_role_res = iam_client.create_role(
            RoleName=ROLE_NAME,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Role cho phep Lambda chay XGBoost, ghi DynamoDB va gui SNS"
        )
        role_arn = create_role_res['Role']['Arn']
        print(f"✓ Đã tạo IAM Role: {ROLE_NAME}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        get_role_res = iam_client.get_role(RoleName=ROLE_NAME)
        role_arn = get_role_res['Role']['Arn']
        print(f"✓ IAM Role '{ROLE_NAME}' đã tồn tại.")

    # Gán quyền cơ bản CloudWatch Logs
    iam_client.attach_role_policy(
        RoleName=ROLE_NAME,
        PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
    )

    # Gán inline policy cho DynamoDB & SNS
    inline_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["dynamodb:PutItem", "dynamodb:GetItem"],
                "Resource": f"arn:aws:dynamodb:{REGION}:{account_id}:table/{TABLE_NAME}"
            },
            {
                "Effect": "Allow",
                "Action": ["sns:Publish"],
                "Resource": topic_arn
            }
        ]
    }
    iam_client.put_role_policy(
        RoleName=ROLE_NAME,
        PolicyName="DynamoDB_SNS_Access",
        PolicyDocument=json.dumps(inline_policy)
    )
    print("✓ Đã cấp quyền truy cập DynamoDB và SNS cho IAM Role.")
    time.sleep(5) # Đợi IAM Policy lan truyền

    # 4. Khởi tạo / Cập nhật Lambda Function
    print("\n4. Khởi tạo AWS Lambda Function...")
    lambda_client = session.client('lambda')
    
    with open(zip_path, 'rb') as f:
        zipped_code = f.read()

    env_vars = {
        'TABLE_NAME': TABLE_NAME,
        'SNS_TOPIC_ARN': topic_arn
    }

    try:
        create_fn_res = lambda_client.create_function(
            FunctionName=FUNCTION_NAME,
            Runtime='python3.11',
            Role=role_arn,
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': zipped_code},
            Description='Mo hinh XGBoost phan loai phishing real-time',
            Timeout=5,
            MemorySize=512, # 512MB RAM tối ưu cho SVD và XGBoost
            Environment={'Variables': env_vars},
            Layers=[KLAYERS_SKLEARN_ARN, KLAYERS_XGBOOST_ARN]
        )
        lambda_arn = create_fn_res['FunctionArn']
        print(f"✓ Đã tạo mới hàm Lambda: {FUNCTION_NAME}")
    except lambda_client.exceptions.ResourceConflictException:
        print(f"-> Hàm Lambda '{FUNCTION_NAME}' đã tồn tại. Đang cập nhật code và cấu hình...")
        lambda_client.update_function_code(
            FunctionName=FUNCTION_NAME,
            ZipFile=zipped_code
        )
        lambda_client.update_function_configuration(
            FunctionName=FUNCTION_NAME,
            Timeout=5,
            MemorySize=512,
            Environment={'Variables': env_vars},
            Layers=[KLAYERS_SKLEARN_ARN, KLAYERS_XGBOOST_ARN]
        )
        get_fn = lambda_client.get_function(FunctionName=FUNCTION_NAME)
        lambda_arn = get_fn['Configuration']['FunctionArn']
        print(f"✓ Đã cập nhật hàm Lambda '{FUNCTION_NAME}' thành công!")

    # 5. Khởi tạo Amazon API Gateway (HTTP API)
    print("\n5. Khởi tạo Amazon API Gateway (HTTP API)...")
    apigw = session.client('apigatewayv2')
    
    apis = apigw.get_apis()['Items']
    api_id = None
    for api in apis:
        if api.get('Name') == API_NAME:
            api_id = api['ApiId']
            break
            
    if not api_id:
        create_api_res = apigw.create_api(
            Name=API_NAME,
            ProtocolType='HTTP',
            Target=lambda_arn,
            CorsConfiguration={
                'AllowOrigins': ['*'],
                'AllowMethods': ['POST', 'OPTIONS'],
                'AllowHeaders': ['Content-Type']
            }
        )
        api_id = create_api_res['ApiId']
        api_endpoint = create_api_res['ApiEndpoint']
        print(f"✓ Đã tạo HTTP API: {API_NAME} (ID: {api_id})")
    else:
        api_res = apigw.get_api(ApiId=api_id)
        api_endpoint = api_res['ApiEndpoint']
        print(f"✓ HTTP API '{API_NAME}' đã tồn tại (ID: {api_id}).")

    # Cấp quyền cho API Gateway kích hoạt Lambda
    try:
        lambda_client.add_permission(
            FunctionName=FUNCTION_NAME,
            StatementId=f"apigateway-invoke-{api_id}",
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=f"arn:aws:execute-api:{REGION}:{account_id}:{api_id}/*/*"
        )
        print("✓ Đã cấp quyền cho API Gateway invoke Lambda.")
    except lambda_client.exceptions.ResourceConflictException:
        pass

    full_api_url = f"{api_endpoint}/predict"
    print("\n" + "=" * 65)
    print("HOÀN TẤT TRIỂN KHAI HỆ THỐNG SERVERLESS PHISHING THÀNH CÔNG! 🚀")
    print(f"API Endpoint URL: {full_api_url}")
    print("Phương thức gọi: POST (JSON body: {'text': 'noi dung can kiem tra'})")
    print("=" * 65)

if __name__ == '__main__':
    deploy()
