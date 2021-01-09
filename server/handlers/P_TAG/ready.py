import asyncio
from loguru import logger
from server.models.handler import CommandData
from server.events.command import CommandEvent
from server.core.constants import ServerType, TileEnum
from server.core.constants import READY_SPRITES, TILE_MAP_START, TILE_MAP_LOAD, HEIGHT_MAP_START, HEIGHT_MAP_LOAD
from server.handlers.util import allow_once, has_attribute
from server.events import event


@event.on(CommandEvent(ServerType.LOGIN, 'ready'))
@has_attribute('login_context')
@allow_once
async def handle_ready_command(client):
    await client.send_tag("W_INPUT", "smart", "4375706:1", 2, 3, 0, "smart")
    await client.send_tag("W_PLACE", "smart:lobby", 1, 0)

    for sprite in READY_SPRITES:
        await client.send_tag("S_LOADSPRITE", sprite)

    await client.send_tag("UI_CROSSWORLDSWFREF", client.smart_id, 0, "SmartWindowManager", 
        0, 0, 0, 0, 0, 
        client.get_url("WINDOW_MANAGER"),
        f"/{client.smart_cmd}"
    )

    await client.send_tag("UI_ALIGN", client.smart_id, "0", "0", "center", "scale_none")
    await client.send_tag("UI_BGCOLOR", 34, 164, 243) # blue color
    await client.send_tag("UI_BGSPRITE", "smart:bg", 0, 0, 0, 0) # 0 => tile image

    await client.send_tag("P_MAPBLOCK", "t", "1", "1", TILE_MAP_START)
    await client.send_tag("P_MAPBLOCK", "h", "1", "1", HEIGHT_MAP_START)
    #await client.send_tag("P_ZOOMLIMIT", -1, -1)
    await client.send_tag("P_RENDERFLAGS", 0, 48)
    await client.send_tag("P_VIEW", 5) # viewmode, should try other values
    #await client.send_tag("P_LOCKVIEW", "0") # overrides above, wtf?
    await client.send_tag("P_ELEVSCALE", 0.031250)
    await client.send_tag("P_RELIEF", 1)
    await client.send_tag("P_LOCKSCROLL", 1, 0, 0, 0)
    await client.send_tag("P_LOCKOBJECTS", 0)
    await client.send_tag("P_HEIGHTMAPDIVISIONS", 1)
    await client.send_tag("P_CAMERA3D", *([0] * 15), 864397819904, 0, 0, 0)
    await client.send_tag("P_DRAG", 1) # lol
    await client.send_tag("P_CAMLIMITS", 0, 0, 0, 0)
    #await client.send_tag("P_LOCKRENDERSIZE", "0", "1024", "768") # racist
    
    for i in range(6):
        _id = f"smart:{7940006 + i}"
        await client.send_tag("P_TILE", i, '', 0, 1, '', f'smart:{i}', f'SMART_TILE_{TileEnum(_id).name}','0','0','0', _id)

    await client.send_tag("P_PHYSICS", *([0] * 7), 1)
    await client.send_tag("P_ASSETSCOMPLETE")


@event.on(CommandEvent(ServerType.LOGIN, 'place_ready'))
@has_attribute('login_context')
@allow_once
async def handle_place_ready_command(client):
    await client.send_tag('O_HERE', 4, 'smart:1', 5, 2.5, 0, 1, 0, 0, 0, 'SMART_PLAYER_OBJ', 'smart:1', 0, 1, 0)
    await client.send_tag('P_CAMERA', 4.48438, 2.48438, 0, 0, 1)
    await client.send_tag('P_ZOOM', '1.000000')
    await client.send_tag('P_LOCKZOOM', 1)
    await client.send_tag('P_LOCKCAMERA', 1)
    await client.send_tag('O_PLAYER', 4)

    client.attributes['player_object_id'] = 4