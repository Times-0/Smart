from typing import Optional, TypeVar, Generic, List, Any
from pydantic import BaseModel
from pydantic.generics import GenericModel
from server.core.constants import ServerType
from enum import Enum, auto


class EngineStatus(Enum):
    startup = auto()
    shutdown = auto()


class EngineEvent(BaseModel):
    type: ServerType
    status: EngineStatus

    def __init__(self, type, status):
        super().__init__(type=type, status=status)

    def __str__(self):
        return f"EngineEvent#{self.type.name}::{self.status.name}"

