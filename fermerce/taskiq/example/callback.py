from fermerce.taskiq.utils import message_ack


@message_ack
def example_callback(body, message):
    print(body)
