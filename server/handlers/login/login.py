import asyncio
import json
import nacl.secret
from loguru import logger
from server.models.handler import CommandData
from server.models.database.penguin import Penguin
from server.events.command import CommandEvent
from server.core.constants import ServerType, GAME_SERVER_TYPES
from server.handlers.util import allow_once, has_attribute
from server.core.utils import wait_for_event
from server.events import event


class LoginCommand(CommandData):
    game_server_type:ServerType
    swid:str
    token:str

    @staticmethod
    def parse(event:CommandEvent):
        server_type = event.arguments[0]
        if server_type not in GAME_SERVER_TYPES:
            raise ValueError(f"'{server_type}' not a valid CJS game server")

        return LoginCommand(
            game_server_type = ServerType(GAME_SERVER_TYPES[server_type]),
            swid = event.arguments[1],
            token = event.arguments[2],
        )


async def client_already_in_server(client, swid:str):
    engine = client.engine

    for u in engine.users:
        login_context = u.attributes.get("login_context", {'pid': None})

        if login_context['pid'] == swid:
            return True, u.weakref

    return False, None

async def get_user_object(swid:str):
    try:
        user = await Penguin.objects.get(swid = swid)
    except Exception as e:
        print(e)
        user = None
    finally:
        return user

@event.on(CommandEvent(ServerType.LOGIN, 'force_login'))
@has_attribute('force_login_event')
@allow_once
async def handle_force_login(client, event:CommandData):
    client.attributes['force_login_event'].set()

@event.on(CommandEvent(ServerType.LOGIN, 'login'))
@has_attribute('place_context')
@allow_once
async def handle_login_command(client, event:LoginCommand):
    logger.info(f"{client} trying to login, event = {event}")

    try:
        # authenticate user
        user_session = await client.engine.redis.get(f"session:{event.token}", encoding='utf-8')
        if user_session is None:
            # session doesn't exist, or expired
            await client.send_tag("S_LOGINDEBUG", "user code 900", debug=True)
            await client.send_tag("S_ERROR", 900, "Smart Error", -1, "Invalid token")
            await client.stop(delay=10, msg="Invalid Token")

            return

        user_session = json.loads(user_session)
        user_obj = await get_user_object(event.swid)
        if user_session['pid'] != event.swid or user_obj is None:
            await client.send_tag("S_LOGINDEBUG", "user code 900", debug=True)
            await client.send_tag("S_ERROR", 900, "Smart Error", -1, "Invalid token")
            await client.stop(delay=10, msg="Invalid Token")

            return

        # check if user already in server
        user_in_server, user = await client_already_in_server(client, event.swid)
        if user_in_server:
            await client.send_tag("S_LOGINDEBUG", "Already logged in", debug=True)
            await client.send_tag("S_LOGGEDIN")

            client.attributes['force_login_event'] = asyncio.Event()
            await wait_for_event(client.attributes['force_login_event'], 60) # wait for next 60 sec
            
            if client.attributes['force_login_event'].is_set():
                try:
                    await user.disconnect(msg="Force disconnect from another login")
                except Exception:
                    pass
                del client.attributes['force_login_event']
            else:
                await client.disconnect(msg="connection timeout")
                return

        user_session['worldName'] = "SmartServer"
        user_session['data'] = client.attributes['place_context'].battle_mode.value
        user_session['game_server_type'] = event.game_server_type.value
        user_session['base_asset_url'] = client.attributes['place_context'].base_asset_url
        user_session['name'] = user_obj.nickname
        is_dev_mode = False #event.game_server_type == ServerType.GAME_DEV

        client.attributes['login_context'] = user_session
        logger.debug(f"Authentication successful - {client}")

        key = await client.engine.get_server_key()
        box = nacl.secret.SecretBox(key)

        login_id = box.encrypt(json.dumps(user_session).encode()).hex()

        await client.send_tag("S_LOGIN", login_id)
        await client.send_tag("S_LOGINDEBUG", "Finalizing login", debug=True)

        await client.send_tag("S_WORLDTYPE", user_session['game_server_type'], int(not client.debug_packet))
        await client.send_tag("S_WORLD", client.engine.id, client.engine.name, 
            "0:113140001", str(is_dev_mode).lower(), -1, -1, "smart_control","clubpenguin_town_en_3", -1, "200.5991")

        await client.send_tag("W_ASSETSCOMPLETE")

    except Exception:
        logger.exception(f"Authentication failed - {client}")

        await client.send_tag("S_LOGINDEBUG", "user code 1000", debug=True)
        await client.send_tag("S_ERROR", 901, "Smart Error", -1, "Authentication failed.")
        await client.stop(delay=10)