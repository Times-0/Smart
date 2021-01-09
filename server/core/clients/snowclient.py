from server.core.clients.nullclient import NullClient
from server.core.constants import SWFAssetUrl
from server.models.actions.playaction import SkinRoomToRoom, LoadWindow, ShowWindow, CloseWindow
from server.models.actions.immediateaction import CloseCjsnowRoomToRoom
from pydantic import BaseModel
import asyncio

class SnowClient(NullClient):

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

        self.player_select_loaded = False
        self.on_close_window_load_buffer = list()

        self.prematch_join_event = asyncio.Event()
        self.game = None

    def get_url(self, asset_url:str):
        base_url = self.attributes['place_context'].base_asset_url.strip("/")
        prefix = SWFAssetUrl.BASE_URL.value.strip("/")
        try:
            asset_url = SWFAssetUrl.__members__[asset_url] if asset_url in SWFAssetUrl.__members__ else SWFAssetUrl(asset_url)
        except Exception:
            raise ValueError("SWF Url definition doesn't exist")

        return f"{base_url}/{prefix}/{asset_url.value.strip('/')}"

    def get_assets_url(self, asset:str):
        base_url = self.attributes['place_context'].base_asset_url.strip("/")
        return f"{base_url}/{asset.lstrip('/')}"

    async def send_model(self, event_model: BaseModel, ui_id = None, **kw):
        data = event_model.json(**kw)
        await self.send_tag("UI_CLIENTEVENT", ui_id or self.smart_id, "receivedJson", data)


    async def load_player_select(self):
        model = LoadWindow(
            windowUrl = self.get_url("PLAYER_SELECT"),
            windowId = 'PLAYER_SELECT', # makes it easier to identify and communicate
            layerName = "topLayer",
            initializationPayload = {
                "game": "snow",
                "name": self.attributes['login_context']['name'],
                "powerCardsFire": 69,
                "powerCardsWater": 69,
                "powerCardsSnow": 69
            },
            xPercent = 0,
            yPercent = 0
        )

        if not self.player_select_loaded:
            await self.send_model(model, exclude_none = True)
            self.player_select_loaded = True
        else:
            self.on_close_window_load_buffer.append([model, CloseCjsnowRoomToRoom()])
            await self.send_model(CloseWindow(targetWindow = "PLAYER_SELECT", triggerName = "load_player_select"))
