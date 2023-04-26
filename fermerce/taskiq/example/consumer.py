from fermerce.taskiq.utils import create_consumer
from fermerce.taskiq.example.queue import test_queue
from fermerce.taskiq.example.callback import example_callback


example_consumer = create_consumer(test_queue, example_callback)
