import boto3
import os
import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

BUCKET_NAME = os.environ['BUCKET_NAME']
TABLE_NAME = os.environ['TABLE_NAME']

def get_s3_bucket_size():
    total_size = 0
    total_objects = 0
    paginator = s3.get_paginator('list_objects_v2')

    for page in paginator.paginate(Bucket=BUCKET_NAME):
        if 'Contents' in page:
            total_objects += len(page['Contents'])
            total_size += sum(obj['Size'] for obj in page['Contents'])

    return total_size, total_objects  

def lambda_handler(event, context):
    logger.info("Received event: %s", event)
    try:
        total_size, total_objects = get_s3_bucket_size()
        logger.info(f"Bucket: {BUCKET_NAME} — Size: {total_size}, Objects: {total_objects}")

        timestamp = datetime.datetime.utcnow().isoformat()

        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                "BucketName": {"S": BUCKET_NAME},
                "Timestamp": {"S": timestamp},
                "TotalSize": {"N": str(total_size)},
                "TotalObjects": {"N": str(total_objects)}
            }
        )

        return {"statusCode": 200, "body": "✅ Bucket size updated."}
    except Exception as e:
        logger.error("Error: %s", str(e))
        return {"statusCode": 500, "body": "❌ Internal server error."}
