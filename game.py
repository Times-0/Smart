import asyncio
import sys
import signal
import functools
from loguru import logger
from server.core.engine import Engine
from server.core.clients.snowclient import SnowClient
from server.core.constants import ServerType
from server.core.utils.module import hot_reload_module
from server.core.config import DATABASE



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


async def setup_database():
    try:
        await DATABASE.connect()
        logger.info("Connected to database")
    except Exception as e:
        logger.exception("Unable to connect to database. Exiting.")
        os._exit(1)


graceful_shutdown_handler = lambda : None

async def main():
    print(r"""

  ____      __  __      _       ____      _____   
 / __"| u U|' \/ '|uU  /"\  uU |  _"\ u  |_ " _|  
<\___ \/  \| |\/| |/ \/ _ \/  \| |_) |/    | |    
 u___) |   | |  | |  / ___ \   |  _ <     /| |\   
 |____/>>  |_|  |_| /_/   \_\  |_| \_\   u |_|U   
  )(  (__)<<,-,,-.   \\    >>  //   \\_  _// \\_  
 (__)      (./  \.) (__)  (__)(__)  (__)(__) (__) 

    """)
    
    from server import handlers
    global graceful_shutdown_handler

    logger.info("Smart CJS server is starting")
    logger.add("logs/smart-{time}.log", rotation="50 MB", retention=10)

    await catch_exceptions()
    await hot_reload_module(handlers)
    await setup_database()

    loop = asyncio.get_event_loop()
    login_server = Engine[SnowClient](
        id = 2000,
        ip = '127.0.0.1',
        port = 6200,
        type = ServerType.LOGIN,
        loop = loop,
        name = 'Login-Server'
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
