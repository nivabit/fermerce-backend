import json
from fermerce.taskiq.broker import broker
from fermerce.taskiq.utils import create_producer
from fermerce.taskiq.example.queue import test_queue


# Define a task that will be performed by the worker
@broker.task
def process_data(data):
    create_producer(test_queue)(json.dumps(data))
    print("Processing data, {}".format(data))
