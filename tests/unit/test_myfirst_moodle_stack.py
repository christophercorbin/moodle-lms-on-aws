import aws_cdk as core
import aws_cdk.assertions as assertions

from myfirst_moodle.myfirst_moodle_stack import MyfirstMoodleStack

# example tests. To run these tests, uncomment this file along with the example
# resource in myfirst_moodle/myfirst_moodle_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MyfirstMoodleStack(app, "myfirst-moodle")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
