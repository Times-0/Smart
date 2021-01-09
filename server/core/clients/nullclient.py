import asyncio
import weakref
import shlex
import json
from loguru import logger
from typing import Any
from server.events.command import CommandEvent, SmartCommandEvent
from server.core.constants import SMART_CMD
from server.events import event


class NullClient(object):

    EOF:bytes = b"\r\n"

    def __init__(self, engine, reader:asyncio.StreamReader, writer:asyncio.StreamWriter):
        super().__init__()

        self.engine = engine
        self.writer_stream = writer
        self.reader_stream = reader
        self.weakref = weakref.ref(self)
        self.attributes = dict()

        self.__stop_listening = False
        self.debug_packet = False

        self.smart_id = engine.id
        self.smart_cmd = SMART_CMD

    def __del__(self):
        logger.debug("discarding NullClient object")

    @logger.catch
    async def handle_command_data(self, data:str):
        parsed_data = shlex.split(data)
        if not parsed_data:
            await self.disconnect()
            return 

        command, *_args = parsed_data
        command = command.lstrip("/")

        if command == self.smart_cmd:
            try:
                data = json.loads(data[len(self.smart_cmd)+1:])
                triggerName = data['triggerName']
                triggerType = data['type'] if 'type' in data else triggerName
                data.pop("triggerName", 0), data.pop("type", 0)
            except Exception:
                return 
            await event.emit(SmartCommandEvent(self.engine.type, triggerType, triggerName, data), self.weakref)
        else:
            await event.emit(CommandEvent(self.engine.type, command, *_args), self.weakref)

    @logger.catch
    async def handle_received_data(self, data:bytes):
        data = data.rstrip(self.EOF).decode()
        logger.debug(f"RECV | {self} |\n{data} [server={self.engine.name}]")

        if data.startswith("/"):
            await self.handle_command_data(data)
        else:
            await self.disconnect()
            return

    @logger.catch
    async def send_tag(self, tag:str, *_args, debug = False):
        if debug and not self.debug_packet:
            return 

        tag = f"[{tag}]"
        _args = '|'.join(map(str, _args))
        
        await self.send_line(f"{tag}|{_args}")

    @logger.catch
    async def send_line(self, data:Any):
        if self.writer_stream.is_closing():
            return 

        data = str(data).encode('utf-8')
        logger.debug(f"SEND | {self} |\n{data} [server={self.engine.name}]")

        await self.writer_stream.drain()
        self.writer_stream.write(data + self.EOF)

    async def start_listening(self):
        _buffer = await self.reader_stream.read(24)
        if _buffer.startswith(b"<policy-file-request/>"):
            _buffer = None
            await self.send_line(FLASH_POLICY)

        elif _buffer.endswith(self.EOF):
            await self.handle_received_data(_buffer)
            _buffer = None

        while not self.writer_stream.is_closing():
            try:
                data = await self.reader_stream.readuntil(self.EOF)
                if self.__stop_listening:
                    continue

                if _buffer:
                    data += _buffer
                    _buffer = None

                if data:
                    await self.handle_received_data(data)
                else:
                    await self.disconnect()
                    break

            except asyncio.LimitOverrunError:
                continue
            except (asyncio.CancelledError, asyncio.IncompleteReadError):
                await self.disconnect()
                break
            except Exception:
                logger.error("Exception while trying to read data from client")
                await self.disconnect()
                break

    @logger.catch
    async def disconnect(self, *, msg = None):
        if self.writer_stream.is_closing():
            return

        try:
            await self.send_tag("S_DISCONNECT", (msg if msg is not None else "connection closed cleanly"), -1)
        except Exception:
            pass

        self.writer_stream.close()
        await self.writer_stream.wait_closed()

    async def __stop__task(self, delay, msg):
        try:
            await asyncio.sleep(delay)
            await self.disconnect(msg = msg)
        except Exception:
            pass

    async def stop(self, *, delay, msg = None):
        self.__stop_listening = True
        asyncio.create_task(self.__stop__task(delay, msg))

    def __str__(self):
        return f"{self.__class__.__name__} <{self.writer_stream.get_extra_info('peername')}>"


FLASH_POLICY = '<cross-domain-policy><allow-access-from domain="*" to-ports="*" /></cross-domain-policy>\x00'