import asyncio
import weakref
import json
from loguru import logger
from typing import Any
from server.models.actions.playaction import SkinRoomToRoom, LoadWindow, ShowWindow, CloseWindow
from server.events.command import CommandEvent, SmartCommandEvent
from server.core.constants import ServerType
from collections import deque
from server.events import event


class NullGame(object):

    MAX_WAITING_TIME:int = 30
    id:str
    name:str
    type:ServerType

    def __init__(self, id:str, name:str, type:ServerType):
        super().__init__()

        self.id = id
        self.name = name
        self.type = type
        self.users = deque()
        self.weakref = weakref.ref(self)
        self.waiting_for_players = True

    async def start_match_logic(self):
        self.waiting_for_players = False
        
        for client in self.users:
            client.engine = self
            await client.send(CloseWindow(targetWindow = "PLAYER_SELECT", triggerName = "start_match_logic"))

    async def __prematch_user_join(self, user):
        await user.prematch_join_event.wait()
        self.users.append(user)

    async def start_prematch(self, users:list):
        try:
            logger.info(f"Prematch {self.name}")
            users_login_aws = list(self.__prematch_user_join(user) for user in users)
            users_aws = asyncio.gather(*users_login_aws)

            await asyncio.wait_for(users_aws, timeout=self.MAX_WAITING_TIME)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            pass
        finally:
            if len(self.users) > 2:
                await self.start_match_logic()
            else:
                logger.info(f"Match not found: {self.name}, 60s timeout")
                for user in users:
                    if user.__weakref__() is not None:
                        user.game = None
                        await user.load_player_select()

    def __del__(self):
        logger.debug("discarding NullGame object")
