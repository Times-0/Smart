import asyncio
import weakref
import aioredis
import nacl.utils
import nacl.secret
from collections import deque
from loguru import logger
from typing import TypeVar, Generic, Tuple, Type, Deque
from server.core.constants import ServerType
from server.events.engine import EngineEvent, EngineStatus
from server.events.client import ClientStatusEvent, ClientStatus
from server.events import event

import gc

T = TypeVar("T")

class Engine(Generic[T]):

    server_addr: Tuple[str, int]
    type: ServerType
    protocol: Type[T]
    loop: asyncio.AbstractEventLoop
    users: Deque[T]

    def __init__(self, *, id:int, ip:str, port:int, type:ServerType, loop:asyncio.AbstractEventLoop, max:int = 500, name:str = 'Smart-Server'):
        super(Engine, self).__init__()
        
        self.id = id
        self.name = name
        self.max = max
        self.server_addr = (ip, port)
        self.type = ServerType(type)
        self.protocol = None
        self.loop = loop
        self.users = deque()
        self.weakref = weakref.ref(self)

    async def get_server_key(self):
        key = await self.redis.get("cjs_key")

        if key is None:
            key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
            await self.redis.set("cjs_key", key)

        return key
 
    async def __get_protocol(self):
        return (self.__orig_class__.__args__[0] if hasattr(self, "__orig_class__") else None) if self.protocol is None else self.protocol

    async def set_protocol(self, protocol):
        if self.protocol is not None:
            raise ValueError("Protocol is not None. Cannot override protocol once set.")

        self.protocol = protocol

    async def setup(self):
        self.protocol = await self.__get_protocol()
        if self.protocol is None:
            logger.error("Set protocol class to Engine using type hints eg: 'Engine[Penguin](...)', or set it manually set_protocol(...)")
            raise TypeError("Expected a class, got None instead")

        self.server = await asyncio.start_server(self.handle_new_connection, self.server_addr[0], self.server_addr[1], loop=self.loop)
        logger.info(f"{self.type.name.title()} server listening on '{self.server_addr[0]}:{self.server_addr[1]}'")

        self.redis = await aioredis.create_redis_pool('redis://localhost')

        await event.emit(EngineEvent(self.type, EngineStatus.startup), self.weakref)

    async def handle_new_connection(self, reader, writer):
        client = self.protocol(self, reader, writer)
        logger.info(f"new client connection: {client}")

        self.users.append(client)

        await event.emit(ClientStatusEvent(client.engine.type, ClientStatus.connected), client.weakref)
        await client.start_listening()

        if client in self.users:
            self.users.remove(client)

        await event.emit(ClientStatusEvent(client.engine.type, ClientStatus.disconnected), client.weakref)
        logger.info(f"client disconnected: {client}")

        client.engine = None
        del client
        gc.collect()


    async def stop(self):
        await event.emit(EngineEvent(self.type, EngineStatus.shutdown), self.weakref)

