from kombu import Queue
from fermerce.taskiq.config import exchange


test_queue = Queue(
    name="tasks",
    exchange=exchange,
    routing_key="tasks",
)
