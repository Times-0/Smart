from pydantic import BaseModel


class PlayAction(BaseModel):
    type:str = "playAction"


class SkinRoomToRoom(PlayAction):
    action:str = "skinRoomToRoom"
    className:str = ""
    variant:int = 0
    url:str


class LoadWindow(PlayAction):
    action:str = "loadWindow"
    assetPath:str = None
    windowId:str = None
    assetName:str = None
    layerName:str = "bottomLayer"
    initializationPayload:dict = None
    loadDescription:str = "Loading assets"
    x:int = None
    y:int = None
    xPercent:int = None
    yPercent:int = None
    scale:int = None
    displayHeight:int = None
    displayWidth:int = None
    displayScale:int = None
    showProgress:bool = True
    loadIntoApplicationDomain:bool = False
    timeOut:int = 15000
    windowUrl:str


class CloseWindow(PlayAction):
    action:str = "closeWindow"
    targetWindow:str
    triggerName:str


class ShowWindow(PlayAction):
    action:str = "showWindow"
    targetWindow:str
    triggerName:str


class ScreenRoomToRoomAction(PlayAction):
    action:str = "screenRoomToRoomAction"
    data:int