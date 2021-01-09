import asyncio 

async def wait_for_event(evt, timeout):
    try:
        await asyncio.wait_for(evt.wait(), timeout)
    except asyncio.TimeoutError:
        pass

    return evt.is_set()
