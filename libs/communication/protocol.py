import json
import os
import re
from dataclasses import dataclass


MAX_MESSAGE_BYTES = 256 * 1024
MAX_PENDING = 64
MAX_TIMEOUT = 120
NAME = re.compile(r"^[a-z][a-z0-9_.-]{0,79}$")
DEFAULT_COMPONENTS = ("webserver", "barman", "menestrel", "archiveuse")


class BusError(Exception):
    def __init__(self, message, *, code="unavailable", status=503):
        super().__init__(message)
        self.code = code
        self.status = status

    def data(self):
        return {"message": str(self), "code": self.code, "status": self.status}

    @classmethod
    def from_data(cls, data):
        return cls(data["message"], code=data["code"], status=data["status"])


@dataclass(frozen=True)
class CallContext:
    caller: str


def valid_name(value):
    return isinstance(value, str) and NAME.fullmatch(value) is not None


def token_key(component):
    return "BUS_" + component.upper().replace("-", "_").replace(".", "_") + "_TOKEN"


def configured_tokens():
    return {name: os.environ[token_key(name)] for name in component_names() if os.getenv(token_key(name))}


def component_names():
    names = os.getenv("BUS_COMPONENTS", ",".join(
        DEFAULT_COMPONENTS)).split(",")
    return {name.strip() for name in names if valid_name(name.strip())}


def encode(message):
    text = json.dumps(message, allow_nan=False)
    if len(text.encode("utf-8")) > MAX_MESSAGE_BYTES:
        raise ValueError("Bus message is too large")
    return text


def decode(text):
    if len(text.encode("utf-8")) > MAX_MESSAGE_BYTES:
        raise ValueError("Bus message is too large")
    try:
        message = json.loads(text)
    except RecursionError:
        raise ValueError("Bus message nesting is too deep") from None
    if not isinstance(message, dict):
        raise ValueError("Bus message must be an object")
    return message
