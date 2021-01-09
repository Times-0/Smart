import asyncio
from loguru import logger
from server.models.handler import CommandData
from server.models.actions.immediateaction import JsonPayload
from server.models.actions.playaction import CloseWindow, ScreenRoomToRoomAction
from server.events.command import CommandEvent, SmartCommandEvent
from server.core.constants import ServerType, TileEnum
from server.core.constants import READY_SPRITES, TILE_MAP_START, TILE_MAP_LOAD, HEIGHT_MAP_START, HEIGHT_MAP_LOAD
from server.core.session import ElementType
from server.handlers.util import allow_once, has_attribute
from server.events import event
import server.events


@event.on(SmartCommandEvent(ServerType.LOGIN, 'action', 'funnel_choose_your_element_1'))
async def handle_choose_element_action(client):
    client.attributes['funnel_choose_your_element_1'] = True

@event.on(SmartCommandEvent(ServerType.LOGIN, 'action', 'funnel_stats_2'))
@has_attribute('funnel_choose_your_element_1')
async def handle_choose_element_2_action(client):
    client.attributes['funnel_stats_2'] = True

@event.on(SmartCommandEvent(ServerType.LOGIN, 'action', 'funnel_matchmaking_3'))
async def handle_funnel_matchmaking_3(client):
    pass

@event.on(SmartCommandEvent(ServerType.LOGIN, 'jsonPayload', 'mmElementSelected'))
@has_attribute('funnel_stats_2')
async def handle_choose_ninja(client, event):
    matchmaker = client.engine.match
    element = event.data['element']
    tip_mode = event.data['tipMode']
    if element not in ElementType.__members__:
        await client.disconnect(msg="Logic error")
        return

    element = ElementType.__members__[element]
    client.attributes['login_context']['element'] = element
    client.attributes['login_context']['tip_mode'] = int(tip_mode)

    await matchmaker.element_queue[element].put(client)

@event.on(SmartCommandEvent(ServerType.LOGIN, 'action', 'funnel_prepare_to_battle_4'))
@has_attribute('match_found')
async def handle_funnel_prepare_to_battle_4(client):
    await asyncio.sleep(2.5)
    await client.send_tag('S_GOTO', client.attributes['login_context']['arena_name'], 'snow_arena', '',
                    f"battleMode={client.attributes['login_context']['data']}&tipMode={client.attributes['login_context']['tip_mode']}&isMuted={str(client.attributes['login_context']['isMuted']).lower()}&base_asset_url={client.attributes['login_context']['base_asset_url']}")
    
    await client.send_model(ScreenRoomToRoomAction(data=0))
