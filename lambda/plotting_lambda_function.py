
import boto3
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from boto3.dynamodb.conditions import Key
import io
import os


def lambda_handler(event, context):
    # Define the bucket and DynamoDB table names.
    bucket_name = os.environ.get('BUCKET_NAME')
    table_name = os.environ.get('DDB_TABLE_NAME')
    
    # Initialize DynamoDB resource and table.
    dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
    table = dynamodb.Table(table_name)
    
    now = int(time.time())
    start_time = now - 60  # Last 10 seconds.
    
    # Query for recent bucket size records (using primary key: bucket_name & timestamp).
    response_recent = table.query(
         KeyConditionExpression=Key("bucket_name").eq(bucket_name) & Key("timestamp").between(start_time, now)
    )
    recent_items = response_recent.get("Items", [])
    timestamps = [item["timestamp"] for item in recent_items]
    sizes = [item["size_bytes"] for item in recent_items]
    
    print("Recent Items:", recent_items)
    print("Timestamps:", timestamps)
    print("Sizes:", sizes)
    
    # Query for the maximum bucket size ever recorded using the GSI 'MaxSizeIndex'.
    response_max = table.query(
         IndexName="MaxSizeIndex",
         KeyConditionExpression=Key("bucket_name").eq(bucket_name),
         ScanIndexForward=False,  # Descending order so the first item is the max.
         Limit=1
    )
    max_items = response_max.get("Items", [])
    max_size = max_items[0]["size_bytes"] if max_items else 0
    
    # Generate the plot.
    plt.figure(figsize=(8, 6))
    if timestamps and sizes:
        plt.plot(timestamps, sizes, marker="o", linestyle="-", label="Recent Bucket Size")
    else:
        # Plot a default point if no recent data.
        plt.plot([now], [0], marker="o", linestyle="-", label="Recent Bucket Size")
    plt.axhline(y=max_size, color="r", linestyle="--", label="Max Bucket Size: " + str(max_size))
    plt.xlabel("Timestamp")
    plt.ylabel("Size (bytes)")
    plt.title("Bucket Size Change in Last 10 Seconds")
    plt.legend()
    
    # Save the plot to a bytes buffer.
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    
    # Upload the plot to S3 with the object key 'plot'.
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket_name, Key="plot", Body=buf.getvalue(), ContentType="image/png")
    
    return {
        "statusCode": 200,
        "body": "Plot generated and stored in S3 with key \"plot\"."
    }
