import boto3

s3_client = boto3.client(
    "s3",
    # endpoint_url="http://minio:9000",  # В докере
    endpoint_url="http://localhost:9000",  # На локалке
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
    region_name="us-east-1",
)

S3_BUCKET = "posts"