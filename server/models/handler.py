from typing import List
from pydantic import BaseModel
from server.core.constants import ServerType
from server.events.command import CommandEvent


class CommandData(BaseModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def parse(self, event:CommandEvent):
        raise NotImplementedError("")

    def __str__(self):
        return f"{self.__class__.__name__} <{super().__str__()}>"

