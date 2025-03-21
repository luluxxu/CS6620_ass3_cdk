import aws_cdk as core
import aws_cdk.assertions as assertions

from 6620_ass3.6620_ass3_stack import 6620Ass3Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in 6620_ass3/6620_ass3_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = 6620Ass3Stack(app, "6620-ass3")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
