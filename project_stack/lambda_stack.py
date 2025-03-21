from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

class LambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, *, bucket: s3.IBucket, table: dynamodb.ITable, **kwargs):
        super().__init__(scope, id, **kwargs)

        # ✅ Define the bucket **only once**
        code_bucket = s3.Bucket.from_bucket_name(self, "CodeBucket", "lambda-code-storage-lu")

        self.size_tracking_lambda = _lambda.Function(
            self, "SizeTrackingLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_bucket(code_bucket, "size-tracking.zip"),  # ✅ Use the defined bucket
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "TABLE_NAME": table.table_name,
            }
        )

        # ✅ Permissions
        bucket.grant_read_write(self.size_tracking_lambda)
        table.grant_read_write_data(self.size_tracking_lambda)
