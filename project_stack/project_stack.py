from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
)
from constructs import Construct

class StorageStack(Stack):
    def __init__(self, scope: Construct, id: str, *, bucket: s3.IBucket, **kwargs):
        super().__init__(scope, id, **kwargs)

        table_name = self.node.try_get_context("table_name")

        # ✅ Create DynamoDB Table (No S3 bucket here!)
        self.table = dynamodb.Table(
            self, "S3ObjectSizeHistory",
            table_name=table_name,
            partition_key=dynamodb.Attribute(name="BucketName", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Timestamp", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST
        )

        self.table.add_global_secondary_index(
            index_name="TimestampIndex",
            partition_key=dynamodb.Attribute(name="BucketName", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="Timestamp", type=dynamodb.AttributeType.STRING)
        )
