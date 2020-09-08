import asyncio
from loguru import logger
from typing import TypeVar, Generic, Tuple
from server.core.engine import Engine
from server.core.constants import ServerType
from server.events.engine import EngineEvent, EngineStatus
from server.events import event


@event.on(EngineEvent(ServerType.LOGIN, EngineStatus.startup))
async def login_engine_startup(engine: Engine):
    await engine.redis.sadd("cjs_servers", engine.id)
    await engine.redis.hmset_dict(f"cj_server:{engine.id}", {
        'users': 0,
        'max': engine.max,
        'name': engine.name,
        'id': engine.id,
        'ip': engine.server_addr[0],
        'port': engine.server_addr[1]
    })


@event.on(EngineEvent(ServerType.LOGIN, EngineStatus.shutdown))
async def login_engine_startup(engine: Engine):
    await engine.redis.srem('cjs_servers', engine.id)
    await engine.redis.delete(f"cj_server:{engine.id}")
