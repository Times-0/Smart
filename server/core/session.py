import asyncio
import weakref
import os
from enum import Enum
from typing import Dict
from loguru import logger
from server.events import event
from server.core.constants import BattleType


class ElementType(Enum):
    fire = "1"
    water = "2"
    snow = "4"

class MatchFound:

    def __init__(self, _type:BattleType):
        self._type = _type

    def __str__(self):
        return f"MatchFound<{self._type}>"

class Dummy:
    def __init__(self, name="Dummy"):
        self.attributes = {
            'login_context': {
                'name': name
            }
        }

        self.prematch_join_event = asyncio.Event()

    async def send_tag(self, *a, **kw):
        pass

    async def send_model(self, *a, **kw):
        pass

    async def load_player_select(self, *a, **kw):
        pass

    def __weakref__(self):
        return self

class MatchMaker(object):
    element_queue: Dict[ElementType, asyncio.Queue]
    type: BattleType
    dev: bool

    def __init__(self, type:BattleType, is_dev = False):
        self.element_queue = {
            e: asyncio.Queue()
            for i, e in ElementType.__members__.items()
        }

        self.match_maker_task = asyncio.create_task(self.start_matchmaking())
        self.dev = is_dev
        self.type = type
        logger.info("MatchMaker initiated")

    def __get_player_from_queue(self, queue):
        async def __get_from_queue():
            player = await queue.get()

            if player.__weakref__() is None:
                return await __get_from_queue()

            return player

        return __get_from_queue()

    async def start_matchmaking(self):
        logger.info("MatchMaker is running")
        if self.dev:
            await self.element_queue[ElementType.fire].put(Dummy("Fire dummy"))
            await self.element_queue[ElementType.water].put(Dummy("Water dummy"))
        try:
            while True:
                match_aws = [self.__get_player_from_queue(self.element_queue[i]) for i in self.element_queue]
                match = await asyncio.gather(*match_aws)

                match_found = dict(zip(self.element_queue, match))
                key = os.urandom(4).hex()
                logger.info(f"Match found: {', '.join(map(lambda p: p.attributes['login_context']['name'], match))} [key={key}]")

                await event.emit(MatchFound(self.type), match_found, key)

                if self.dev:
                    await self.element_queue[ElementType.fire].put(Dummy("Fire dummy"))
                    await self.element_queue[ElementType.water].put(Dummy("Water dummy"))

        except asyncio.CancelledError:
            logger.info("MatchMaker is cancelled")
        finally:
            logger.exception("MatchMaker has been stopped")
