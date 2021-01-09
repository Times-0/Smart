from typing import List
from pydantic import BaseModel
from server.core.constants import ServerType


class CommandEvent(BaseModel):
    server_type: ServerType
    command: str
    arguments: List[str]    

    def __init__(self, server_type:ServerType, command:str, *arguments:List[str]):
        super().__init__(command=command, arguments=arguments, server_type=server_type)

    def __str__(self):
        return f"CommandEvent<{self.command}, {self.server_type}>"


class SmartCommandEvent(BaseModel):
    server_type: ServerType
    command: str
    trigger: str
    data: dict

    def __init__(self, server_type:ServerType, command:str, trigger:str = None, data:dict = None):
        super().__init__(server_type=server_type, command=command, trigger=trigger or command, data=data or {})

    def __str__(self):
        return f"SmartCommandEvent<{self.command}-{self.trigger}, {self.server_type}>"
