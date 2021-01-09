import awebus
import asyncio
import weakref
from loguru import logger
from enum import IntEnum
from inspect import iscoroutinefunction
from functools import partial
from typing import Any, List, Callable, get_type_hints
from typeguard import check_type
from server.core.config import IGNORE_TYPE_HINTS, EVENT_DEBUG

def _is_coro( o ):
    """
    Return True if the given object is a coroutine(-compatible) object
    """
    return asyncio.iscoroutine( o ) or asyncio.iscoroutinefunction( o )


class SmartPriority(IntEnum):
    HIGH = -1
    MODERATE = 0
    LOW = 1


class SmartEvent(awebus.EventMixin):
    
    def __init__( self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ignore_type_hints = kwargs.get('ignore_type_hints', False)
        self.debug = kwargs.get("debug", True)

    @logger.catch
    def on(self, event:Any, *, callback:Callable = None, priority:SmartPriority = SmartPriority.MODERATE):
        listener_event = str(event)

        def listener_handler_wrapper(listener_callback_function:Callable):
            if not hasattr(listener_callback_function, 'function_attributes'):
                listener_callback_function.function_attributes = dict(priority = dict(), conditions = dict())

            listener_callback_function.function_attributes['priority'] = listener_callback_function.function_attributes.get('priority', dict())
            listener_callback_function.function_attributes['priority'][listener_event] = priority
            listener_callback_function.function_attributes['conditions'] = listener_callback_function.function_attributes.get('conditions', list())

            super(SmartEvent, self).on(listener_event, listener_callback_function)

            if self.debug:
                logger.debug(f"added listener - '{listener_callback_function.__module__}::{listener_callback_function.__name__}' to event '{listener_event}'")

            return listener_callback_function

        if callback is not None:
            return listener_handler_wrapper(callback)

        return listener_handler_wrapper


    async def __check_and_enforce_arg_type_hints(self, function:Callable, event:Any, *args, **kwargs):
        hints = get_type_hints(function)

        covars = function.__code__.co_varnames[:function.__code__.co_argcount]

        all_args = kwargs.copy()
        all_args.update(dict(zip(covars, args)))

        if 'event' in covars and 'event' not in all_args:
            all_args['event'] = event


        for argument, argument_value in list(all_args.items()):
            argument_type = type(argument_value)

            if argument_type is weakref.ref:
                argument_type = type(argument_value())
                all_args[argument] = argument_value = weakref.proxy(argument_value())
            elif argument_type is weakref.proxy:
                argument_type = type(argument_value.__weakref__())

            if argument in hints:
                try:
                    check_type(argument, argument_value, hints[argument])
                except TypeError:
                    logger.warning("Event-Callback:{function.__name__}, argument:{argument} - expected object of type '{hint_type}', got '{argument_type}' instead. Attempting cast.",
                        function=function, argument=argument, hint_type=hints[argument], argument_type=argument_type)
                    
                    try:
                        new_argument_value = hints[argument].parse(argument_value) if hasattr(hints[argument], 'parse') else hints[argument](argument_value)
                        all_args[argument] = new_argument_value
                    except:
                        logger.error(f"Event-Callback:{function.__name__}, argument:{argument} - Failed to cast '{argument_type}' to '{hints[argument]}'. Skipping listener and all low-priority callbacks.")

                        return False, None, None
        
        return True, tuple(all_args[i] for i in covars), dict(i for i in all_args.items() if i[0] not in covars)


    @logger.catch
    async def __filter_attributes(self, handlers:List[Callable], event:Any, *args, **kwargs):
        listener_event = str(event)
        _filtered_handlers = list()
        loop = asyncio.get_running_loop()

        for handler in list(handlers):
            conditions = handler.function_attributes.get('conditions', list()) if hasattr(handler, 'function_attributes') else list()

            for condition_handler in conditions:
                try:
                    condition = await (condition_handler(event, *args, **kwargs) 
                        if _is_coro(condition_handler) 
                        else loop.run_in_executor(None, partial(condition_handler, event, *_args, **_kwargs))
                    )
                except Exception as e:
                    break

                if not condition:
                    break
            else:
                _filtered_handlers.append(handler)

        return _filtered_handlers


    @logger.catch
    async def emit(self, event:Any, *args, **kwargs):
        awaitables = list()
        listener_event = str(event)

        handlers = sorted(self._get_and_clean_event_handlers(listener_event), 
            key=lambda f: f.function_attributes.get('priority', {}).get(listener_event, SmartPriority.MODERATE) if hasattr(f, 'function_attributes') else SmartPriority.MODERATE)

        handlers = await self.__filter_attributes(handlers, event, *args, **kwargs)
        loop = asyncio.get_running_loop()

        for handler in handlers:
            type_check_success, _args, _kwargs = await self.__check_and_enforce_arg_type_hints(handler, event, *args, **kwargs)

            if not type_check_success:
                if self.ignore_type_hints:
                    logger.info(f"Event-Callback:{handler.__name__} type-hint incompatibility ignored. The function callback and all low-priority callback is not skipped.")
                    _args, _kwargs = args, kwargs

                else:
                    break

            if _is_coro(handler):
                awaitables.append(handler(*_args, **_kwargs))
            else:
                functionWrapper = partial(handler, *_args, **_kwargs)
                awaitables.append(loop.run_in_executor(None, functionWrapper))

        if self.debug:
            logger.debug(f"emitting {len(awaitables)} listeners for the event '{listener_event}'")

        result = await asyncio.gather(*awaitables, loop=loop)
        return result

event = SmartEvent(ignore_type_hints=IGNORE_TYPE_HINTS, debug=EVENT_DEBUG)