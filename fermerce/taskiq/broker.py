import os
import sys
import time

from taskiq import InMemoryBroker, AsyncBroker
from fermerce.taskiq._repository import consumer_list
from fermerce.taskiq.config import connection
from fermerce.core.settings import config
from taskiq_aio_pika import AioPikaBroker
import taskiq_fastapi

env = os.environ.get("ENVIRONMENT")

# Set up the broker
broker: AsyncBroker = AioPikaBroker(
    url=config.get_broker_url(),
    exchange_name=config.project_name.lower()
    if config.project_name
    else "taskiq",
)

# broker = InMemoryBroker()

# if env and env == "testing":
#     broker = InMemoryBroker()

taskiq_fastapi.init(broker, "main:app")


def run():
    while True:
        try:
            for consumer in consumer_list:
                consumer()
        except connection.connection_errors:
            print("connection revived")
            time.sleep(2)
        except KeyboardInterrupt:
            print("Stopping consumer thread")
            sys.exit(1)


if __name__ == "__main__":
    run()
