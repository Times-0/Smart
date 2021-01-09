from enum import Enum, auto


class ServerType(Enum):
    LOGIN       = -1
    GAME_NORMAL = 0
    GAME_TUSK   = 1


class BattleType(Enum):
    NORMAL = 0
    TUSK   = 1


class SWFAssetUrl(Enum):
    BASE_URL       = "/minigames/cjsnow/en_US/deploy/swf"
    WINDOW_MANAGER = "/windowManager/windowmanager_done.swf"
    LOADING_SCREEN = "/ui/assets/cjsnow_loadingscreenassets.swf"
    ERROR_HANDLER  = "/ui/windows/cardjitsu_snowerrorhandler.swf"
    PLAYER_SELECT  = "/ui/windows/cardjitsu_snowplayerselect.swf"
    EXT_INTERFACE  = "/ui/windows/cardjitsu_snowexternalinterfaceconnector.swf"
    SNOW_CLOSE     = "/ui/windows/cardjitsu_snowclose.swf"
    SNOW_ROUNDS    = "/ui/windows/cardjitsu_snowrounds.swf"
    SNOW_UI        = "/ui/windows/cardjitsu_snowui.swf"
    SNOW_TIMER     = "/ui/windows/cardjitsu_snowtimer.swf"
    SNOW_INFO      = "/ui/windows/cardjitsu_snowinfotip.swf"
    STAMP_EARNED   = "/ui/windows/stampearned.swf"


class TileEnum(Enum):
    EMPTY    = "smart:7940006"
    BLUE     = "smart:7940007"
    GREEN    = "smart:7940008"
    GREY     = "smart:7940009"
    PURPLE   = "smart:7940010"
    WHITE    = "smart:7940011"

    LOAD      = "smart:7940012"
    OPEN      = "smart:7940013"
    ENEMY     = "smart:7940014"
    PENGUIN   = "smart:7940015"
    OBSTRACLE = "smart:7940020"
    PENGUIN_OCCUPIED   = "smart:7940016"
    PENGUIN_UNOCCUPIED = "smart:7940017"
    ENEMY_OCCUPIED = "smart:7940018"
    ENEMY_UNOCCUPIED = "smart:7940019"


GAME_SERVER_TYPES = dict(live=0, dev=1)

READY_SPRITES = {"smart:100307", "smart:100319", "smart:100303", "smart:100308", "smart:100318", "smart:100306", "smart:100310", "smart:100312", "smart:100315", "smart:100316", "smart:100317", "smart:100313", "smart:100314", "smart:100302", "smart:100299", "smart:100240", "smart:100241", "smart:100309", "smart:100378", "smart:100320", "smart:100304", "smart:100343", "smart:100321", "smart:1840011", "smart:1840012", "smart:1840010"}

TILE_MAP_START = "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAFCAAAAACyOJm3AAAADklEQVQImWNghgEGIlkADWEAiDEh28IAAAAASUVORK5CYII="
TILE_MAP_LOAD = "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAFCAAAAACyOJm3AAAAHUlEQVQImWNgZeRkZARidgZGCGBnZ2CFMVHEoOoADJEAhIsKxDUAAAAASUVORK5CYII="

HEIGHT_MAP_START = "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAGCAAAAADfm1AaAAAADklEQVQImWOohwMG8pgA1rMdxRJRFewAAAAASUVORK5CYII="
HEIGHT_MAP_LOAD = "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAGCAAAAADfm1AaAAAADklEQVQImWNogAMG8pgA3m8eAacnkzQAAAAASUVORK5CYII="

SMART_CMD = "smartcmd"