import asyncio
import sys
import signal
import functools
from loguru import logger
from server.core.engine import Engine
from server.core.constants import ServerType

class Nothing(object):
    pass


async def catch_exceptions():
    sys.excepthook = lambda _type, message, stack: logger.opt(exception=(_type, message, stack)).error("Uncaught Exception")


def shutdown(server_list, loop):
    loop.run_until_complete(asyncio.gather(*([server.stop() for server in server_list])))

    # graceful exit
    tasks = [task for task in asyncio.Task.all_tasks() if task is not asyncio.tasks.Task.current_task()]

    [task.cancel() for task in tasks]
    results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

    print('Graceful exit: finished awaiting cancelled tasks, results: {0}'.format(results))

    loop.stop()


graceful_shutdown_handler = lambda : None

async def main():
    global graceful_shutdown_handler

    logger.info("Smart CJS server is starting")
    logger.add("logs/smart-{time}.log", rotation="50 MB")

    await catch_exceptions()

    loop = asyncio.get_event_loop()
    login_server = Engine[Nothing](
        id = 2000,
        ip = '127.0.0.1',
        port = 6200,
        type = ServerType.LOGIN,
        client_protocol = Nothing,
        loop = loop
    )

    logger.info("Booting servers")

    servers = [login_server]
    for server in servers:
        await server.setup()

    graceful_shutdown_handler = functools.partial(shutdown, servers, loop)

    signal.signal(signal.SIGTERM, graceful_shutdown_handler)
    signal.signal(signal.SIGINT, graceful_shutdown_handler)

    logger.info("All servers setup and running")
    

loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(main())
    loop.run_forever()
except Exception as e:
    print("exception occured")
finally:
    graceful_shutdown_handler()
    loop.close()
