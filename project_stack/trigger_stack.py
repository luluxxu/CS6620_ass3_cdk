from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
)
from constructs import Construct

class TriggerStack(Stack):
    def __init__(self, scope: Construct, id: str, *, bucket_name: str, lambda_fn: _lambda.IFunction, **kwargs):
        super().__init__(scope, id, **kwargs)

        # ✅ Import bucket inside the stack's scope
        bucket = s3.Bucket.from_bucket_name(self, "ImportedBucket", bucket_name)

        # ✅ Set up notifications
        bucket.add_event_notification(s3.EventType.OBJECT_CREATED, s3n.LambdaDestination(lambda_fn))
        bucket.add_event_notification(s3.EventType.OBJECT_REMOVED, s3n.LambdaDestination(lambda_fn))
