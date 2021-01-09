import asyncio
from loguru import logger
from server.models.handler import CommandData
from server.events.command import CommandEvent
from server.core.constants import ServerType
from server.events import event

class VersionCommand(CommandData):
    version: str = '0.0.1'

    @staticmethod
    def parse(event:CommandEvent):
        return VersionCommand()


@event.on(CommandEvent(ServerType.LOGIN, 'version'))
async def handle_version_command(client, event:VersionCommand):
    await client.send_tag("S_VERSION", event.version)
