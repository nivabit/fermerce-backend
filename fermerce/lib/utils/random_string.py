import random
import string
import uuid


def random_str(size=7) -> str:
    ran = "".join(
        random.choices(string.ascii_uppercase + uuid.uuid4().hex.upper(), k=size)
    )
    return ran


def generate_orderId(size: int) -> str:
    return f"FM-{random_str(size)}"


def generate_order_Tracking_id(size: int) -> str:
    return f"TR-{random_str(size)}"


def generate_uuid(make_string: bool = False):
    return uuid.uuid4 if not make_string else uuid.uuid4().hex
