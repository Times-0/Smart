import asyncio
import weakref
import aioredis
from collections import deque
from loguru import logger
from typing import TypeVar, Generic, Tuple
from server.core.constants import ServerType
from server.events.engine import EngineEvent, EngineStatus
from server.events import event

T = TypeVar("T")

class Engine(Generic[T]):

    server_addr: Tuple[str, int]
    type: ServerType
    protocol: T
    loop: asyncio.AbstractEventLoop

    def __init__(self, *, id:int, ip:str, port:int, type:ServerType, client_protocol:T, loop:asyncio.AbstractEventLoop, max:int = 500, name:str = 'Smart-Server'):
        self.id = id
        self.name = name
        self.max = max
        self.server_addr = (ip, port)
        self.type = ServerType(type)
        self.protocol = client_protocol
        self.loop = loop
        self.users = deque()
        self.weakref = weakref.ref(self)


    async def setup(self):
        self.server = await asyncio.start_server(self.handle_new_connection, self.server_addr[0], self.server_addr[1], loop=self.loop)
        logger.info(f"{self.type.name.title()} server listening on '{self.server_addr[0]}:{self.server_addr[1]}'")

        self.redis = await aioredis.create_redis_pool('redis://localhost')

        await event.emit(EngineEvent(self.type, EngineStatus.startup), self.weakref)

    async def handle_new_connection(self, reader, writer):
        print("new conn:", (reader, writer), type(reader), type(writer))

    async def stop(self):
        await event.emit(EngineEvent(self.type, EngineStatus.shutdown), self.weakref)