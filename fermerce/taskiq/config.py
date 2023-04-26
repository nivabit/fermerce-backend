import kombu
from fermerce.core.settings import config
from kombu import Exchange


exchange = Exchange(name=config.app_name, type=config.app_task_type)

connection = kombu.Connection(
    transport=config.broker_type,
    hostname=config.get_broker_url(include_virtue=False),
    virtual_host=config.broker_virtual_host,
    username=config.broker_user,
    password=config.broker_password,
    port=config.broker_port,
    heartbeat=10,
)
