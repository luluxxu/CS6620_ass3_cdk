from aws_cdk import App
from project_stack.s3_stack import S3Stack
from project_stack.project_stack import StorageStack
from project_stack.lambda_stack import LambdaStack
from project_stack.trigger_stack import TriggerStack

app = App()

s3_stack = S3Stack(app, "S3Stack")

storage_stack = StorageStack(app, "StorageStack",
    bucket=s3_stack.bucket
)

lambda_stack = LambdaStack(app, "LambdaStack",
    bucket=s3_stack.bucket,
    table=storage_stack.table
)

# ✅ Pass just the bucket name
trigger_stack = TriggerStack(app, "TriggerStack",
    bucket_name=s3_stack.bucket.bucket_name,
    lambda_fn=lambda_stack.size_tracking_lambda
)

app.synth()
