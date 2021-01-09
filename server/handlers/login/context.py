import asyncio
from loguru import logger
from urllib import parse
from server.models.handler import CommandData
from server.events.command import CommandEvent
from server.core.constants import ServerType, BattleType
from server.handlers.util import allow_once
from server.events import event

class PlaceContextCommand(CommandData):
    place:str
    battle_mode:BattleType
    base_asset_url:str

    @staticmethod
    def parse(event:CommandEvent):
        uri_params = dict(parse.parse_qsl(event.arguments[1]))
        return PlaceContextCommand(
            place = event.arguments[0],
            battle_mode = int(uri_params['battleMode']),
            base_asset_url = uri_params['base_asset_url']
        )


@event.on(CommandEvent(ServerType.LOGIN, 'place_context'))
@allow_once
async def handle_placecontext_command(client, event:PlaceContextCommand):
    client.attributes['place_context'] = event