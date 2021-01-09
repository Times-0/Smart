from typing import Optional, TypeVar, Generic, List, Any
from pydantic import BaseModel
from pydantic.generics import GenericModel
from server.core.constants import ServerType
from enum import Enum, auto


class ClientStatus(Enum):
    connected = auto()
    disconnected = auto()


class ClientStatusEvent(BaseModel):
    server_type: ServerType
    status: ClientStatus

    def __init__(self, server_type, status):
        super().__init__(status=status, server_type=server_type)

    def __str__(self):
        return f"ClientStatusEvent#{self.status.name}, {self.server_type.name}"

