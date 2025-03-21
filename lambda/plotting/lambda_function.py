import boto3
import matplotlib.pyplot as plt
import io
import datetime
from boto3.dynamodb.conditions import Key

# AWS Clients
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

# Constants
BUCKET_NAME = "testbucket-lu-6620ass2"
TABLE_NAME = "S3-object-size-history"
PLOT_FILE = "plot.png"

def fetch_recent_size_data():
    """Fetches bucket size data from DynamoDB for the last 10 seconds."""
    now = datetime.datetime.utcnow()
    ten_seconds_ago = now - datetime.timedelta(seconds=10)

    table = dynamodb.Table(TABLE_NAME)
    
    response = table.query(
        KeyConditionExpression=Key("BucketName").eq(BUCKET_NAME) & 
                              Key("Timestamp").between(int(ten_seconds_ago.timestamp()), int(now.timestamp()))
    )

    items = response.get("Items", [])
    if not items:
        return [], [], 0  # No data found

    timestamps, sizes = zip(
        *[(item["Timestamp"], int(item["SizeBytes"])) for item in items]
    )

    max_size = max(sizes) if sizes else 0
    return timestamps, sizes, max_size

def fetch_historical_max():
    """Gets the historical max size from DynamoDB."""
    table = dynamodb.Table(TABLE_NAME)

    response = table.scan(ProjectionExpression="SizeBytes")
    sizes = [int(item["SizeBytes"]) for item in response.get("Items", [])]

    return max(sizes) if sizes else 0

def plot_data(timestamps, sizes, historical_max):
    """Generates and saves the plot to S3."""
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, sizes, marker="o", linestyle="-", label="Recent Size")
    plt.axhline(y=historical_max, color="r", linestyle="--", label="Historical High")

    plt.xlabel("Timestamp")
    plt.ylabel("Size (Bytes)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()

    # Save plot to in-memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # Upload to S3
    s3.put_object(Bucket=BUCKET_NAME, Key=PLOT_FILE, Body=buf, ContentType="image/png")

    print(f"✅ Plot uploaded to s3://{BUCKET_NAME}/{PLOT_FILE}")

def lambda_handler(event, context):
    timestamps, sizes, recent_max = fetch_recent_size_data()
    historical_max = fetch_historical_max()

    if not timestamps:
        return {"statusCode": 400, "body": "No data found"}

    plot_data(timestamps, sizes, historical_max)

    return {
        "statusCode": 200,
        "body": f"Plot saved at s3://{BUCKET_NAME}/{PLOT_FILE}"
    }
