import boto3
import time
import os

def lambda_handler(event, context):
    # Bucket and table names
    bucket_name = os.environ.get('BUCKET_NAME')
    table_name = os.environ.get('DDB_TABLE_NAME')
    
    if not bucket_name or not table_name:
        raise ValueError("Missing required environment variables: BUCKET_NAME or DDB_TABLE_NAME")
    
    # Create an S3 client and a DynamoDB resource
    s3_client = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table(table_name)
    
    total_size = 0
    total_objects = 0
    
    # List all objects in the bucket using a paginator
    paginator = s3_client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket_name):
        if 'Contents' in page:
            for obj in page['Contents']:
                total_objects += 1
                total_size += obj['Size']
    
    # Get current Unix timestamp
    timestamp = int(time.time())
    
    # Build the record to insert
    item = {
        'bucket_name': bucket_name,
        'timestamp': timestamp,
        'size_bytes': total_size,
        'total_objects': total_objects
    }
    
    # Insert record into DynamoDB
    try:
        table.put_item(Item=item)
        print(f"Successfully recorded: {item}")
    except Exception as e:
        print(f"Error inserting into DynamoDB: {e}")
        return {
            'statusCode': 500,
            'body': f"Failed to record S3 data to DynamoDB: {e}"
        }
    
    return {
        'statusCode': 200,
        'body': f"Recorded {total_objects} objects ({total_size} bytes) for bucket {bucket_name} at {timestamp}"
    }
