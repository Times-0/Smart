import sys
import databases
from typing import List

from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret


VERSION = "0.0.1"

config = Config(".env")

DEBUG: bool = config("DEBUG", cast=bool, default=False)

SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret, default="5df9db467ed2c905bcc1")

DATABASE_URL:str = config("DATABASE_URL", cast=str, default="mysql://root:@localhost:3306/timeline")
DATABASE:databases.Database = databases.Database(DATABASE_URL)

IGNORE_TYPE_HINTS:bool = config("IGNORE_TYPE_HINTS", cast=bool, default=False)
EVENT_DEBUG:bool = config("EVENT_DEBUG", cast=bool, default=True)