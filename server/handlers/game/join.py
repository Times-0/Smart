import asyncio
from loguru import logger
from urllib import parse
from server.models.handler import CommandData
from server.events.command import CommandEvent
from server.core.constants import ServerType, BattleType
from server.handlers.util import allow_once
from server.events import event


@event.on(CommandEvent(ServerType.LOGIN, 'join'))
@allow_once
async def handle_join_matchmaking_arena(client):
    client.prematch_join_event.set()