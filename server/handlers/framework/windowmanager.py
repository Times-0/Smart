import asyncio
from loguru import logger
from server.models.handler import CommandData
from server.models.actions.immediateaction import SetWorldId, SetBaseAssetUrl, SetFontPath, CloseCjsnowRoomToRoom, JsonPayload
from server.models.actions.playaction import SkinRoomToRoom, LoadWindow, ShowWindow, CloseWindow, ScreenRoomToRoomAction
from server.events.command import CommandEvent, SmartCommandEvent
from server.core.constants import ServerType, TileEnum
from server.core.constants import READY_SPRITES, TILE_MAP_START, TILE_MAP_LOAD, HEIGHT_MAP_START, HEIGHT_MAP_LOAD
from server.handlers.util import allow_once, has_attribute
from server.events import event
import server.events


@event.on(SmartCommandEvent(ServerType.LOGIN, 'windowManagerReady'))
@has_attribute('player_object_id')
@allow_once
async def handle_windowmanager_ready_trigger(client):
    await client.send_model(SetWorldId(worldId = client.smart_id))
    await client.send_model(SetBaseAssetUrl(baseAssetUrl = client.attributes['place_context'].base_asset_url))
    await client.send_model(SetFontPath(defaultFontPath = client.get_assets_url("fonts/")))
    await client.send_tag("UI_ALIGN", client.smart_id, "0", "0", "center", "scale_none")
    await client.send_model(SkinRoomToRoom(url = client.get_url("LOADING_SCREEN"), variant = client.attributes['login_context']['data']))
    await client.send_model(LoadWindow(windowUrl = client.get_url("ERROR_HANDLER")))
    await client.load_player_select()

    client.attributes['can_recv_BIAction'] = True

@event.on(SmartCommandEvent(ServerType.LOGIN, 'jsonPayload', 'payloadBILogAction'))
@has_attribute('can_recv_BIAction')
async def handle_jsonbipayload(client, event:SmartCommandEvent):
    logger.warning(f"action recvd: action={event.data['action']}, data={event.data}")
    await server.events.event.emit(SmartCommandEvent(client.engine.type, "action", event.data['action'], event.data), client)

@event.on(SmartCommandEvent(ServerType.LOGIN, 'jsonPayload', 'quit'))
async def handle_exit_game(client):
    await client.send_model(LoadWindow(windowUrl = client.get_url("EXT_INTERFACE"), layerName = 'toolLayer'))
    await client.stop(delay = 2)

@event.on(SmartCommandEvent(ServerType.LOGIN, 'windowClosed'))
async def handle_window_closed_execute_buffer(client):
    if not client.on_close_window_load_buffer:
        return 

    model = client.on_close_window_load_buffer.pop(0)
    if isinstance(model, list):
        for m in model:
            await client.send_model(m)
    else:
        await client.send_model(model)

@event.on(SmartCommandEvent(ServerType.LOGIN, 'roomToRoomMinTime'))
async def handle_roomToRoomMinTime(client):
    if client.game and client.game.waiting_for_players:
        await client.send_model(ScreenRoomToRoomAction(data=1))
