from pydantic import BaseModel


class ImmediateAction(BaseModel):
    type:str = "immediateAction"


class SetWorldId(ImmediateAction):
    action:str = "setWorldId"
    worldId:int


class SetBaseAssetUrl(ImmediateAction):
    action:str = "setBaseAssetUrl"
    baseAssetUrl:str


class SetFontPath(ImmediateAction):
    action:str = "setFontPath"
    defaultFontPath:str


class JsonPayload(ImmediateAction):
    action:str = "jsonPayload"
    targetWindow:str 
    triggerName:str
    jsonPayload:dict


class CloseCjsnowRoomToRoom(ImmediateAction):
    action:str = 'closeCjsnowRoomToRoom'
    moveToPlayerSelect:bool = False