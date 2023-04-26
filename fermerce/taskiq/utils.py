import functools
import os
import typing as t
import socket
import importlib.util

import taskiq
from fermerce.taskiq.config import connection
import kombu


def create_producer(queue: kombu.Queue, content_type: str = "application/json"):
    def produce(message):
        with connection as conn:
            producer = conn.Producer(serializer="json")
            producer.publish(
                body=message,
                exchange=queue.exchange,
                declare=[queue],
                routing_key=queue.routing_key,
                content_type=content_type,
                retry=True,
                retry_policy={
                    "interval_start": 0,  # First retry immediately,
                    "interval_step": 2,  # then increase by 2s for every retry.
                    "interval_max": 30,  # but don't exceed 30s between retries.
                    "max_retries": 30,  # give up after 30 tries.
                },
            )

    return produce


def create_consumer(queue: kombu.Queue, callback_fun: t.Callable[..., t.Any], accept=["json"]):
    consumer = kombu.Consumer(
        connection,
        queues=[queue],
        callbacks=[callback_fun],
        accept=accept,
    )

    def establish_connection():
        revived_connection = connection.clone()
        revived_connection.ensure_connection(max_retries=3)
        channel = revived_connection.channel()
        consumer.revive(channel)
        consumer.consume()
        return revived_connection

    def consume():
        new_conn = establish_connection()
        while True:
            try:
                new_conn.drain_events(timeout=2)
            except socket.timeout:
                new_conn.heartbeat_check()

    return consume


def discover(directory, recursive=True):
    actors = []
    path = os.path.join(os.getcwd() + directory)
    for root, dirs, files in os.walk(path, topdown=True):
        for name in files:
            if name.endswith(".py"):
                module_path = os.path.join(root, name)
                module_name = os.path.splitext(module_path)[0].replace(os.path.sep, ".")
                module_spec = importlib.util.spec_from_file_location(module_name, module_path)

                module = importlib.util.module_from_spec(module_spec)
                module_spec.loader.exec_module(module)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(
                        attr,
                    ):
                        actors.append(attr)
        if not recursive:
            break
    return actors


def message_ack(func):
    @functools.wraps(func)
    def wrapper(body: dict, message: any):
        func(body, message)
        message.ack()

    return wrapper
