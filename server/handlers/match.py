from server.core.session import MatchMaker, ElementType, MatchFound
from server.models.actions.immediateaction import JsonPayload
from server.core.engine import Engine
from server.core.constants import ServerType, BattleType
from server.events.engine import EngineEvent, EngineStatus
from server.core.match.nullgame import NullGame
from server.events import event
import asyncio

NormalMM = TuskMM = None

@event.on(EngineEvent(ServerType.LOGIN, EngineStatus.startup))
async def login_engine_startup(engine: Engine):
    global NormalMM, TuskMM
    NormalMM = NormalMM or MatchMaker(BattleType.NORMAL, is_dev = True)
    engine.match = NormalMM

@event.on(MatchFound(BattleType.NORMAL))
async def handle_match_found(match:dict, match_key:str):
    place_id = f"smart:10001" # easier if it's a constant
    place_name = f"snow_{match_key}"
    desc = "3 PvP Battle Arena"

    match_data = {
        e.value: p.attributes['login_context']['name']
        for e, p in match.items()
    }

    game = NullGame(place_id, place_name, ServerType.GAME_NORMAL)
    clients = []

    for e, client in match.items():
        await client.send_tag("W_PLACELIST", 
            place_id,
            place_name,
            desc,
            "1", # instance id (almost always 1)
            "9", # width
            "5", # height
            "0", # load type
            "1", # read mode
            "8", # obj id
            "0"  # dev server
        )

        await client.send_model(JsonPayload(
            targetWindow="PLAYER_SELECT", 
            triggerName="matchFound", 
            jsonPayload=match_data
        ))

        client.attributes['match_found'] = match_key
        client.attributes['login_context']['arena_name'] = place_name
        client.attributes['client_match_ready'] = False

        client.prematch_join_event.clear()
        client.game = game

        clients.append(client)

    asyncio.create_task(game.start_prematch(clients))