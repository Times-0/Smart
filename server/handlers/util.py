import weakref
from functools import partial
from typing import Any, Callable


def __attribute_constraint(attribute:str):
    async def handle_attribute_condition(event:Any, client, *_, **__):
        client = weakref.proxy(client()) if isinstance(client, weakref.ref) else client
        return attribute in client.attributes

    return handle_attribute_condition

def has_attribute(attribute:str, *more_attribute):

    def add_attr_constraint(callback_function:Callable):
        if not hasattr(callback_function, 'function_attributes'):
            callback_function.function_attributes = dict(conditions = list())

        callback_function.function_attributes['conditions'].append(__attribute_constraint(attribute))
        [callback_function.function_attributes['conditions'].append(__attribute_constraint(attr)) for attr in more_attribute]
        return callback_function

    return add_attr_constraint


def __allow_once_constraint(function_id:str):
    allow_once_attribute = f"allow_once_{function_id}"
    async def handle_allow_once_condition(event:Any, client, *_, **__):
        client = weakref.proxy(client()) if isinstance(client, weakref.ref) else client
        if allow_once_attribute in client.attributes:
            return False

        client.attributes[allow_once_attribute] = True
        return True

    return handle_allow_once_condition

def allow_once(callback_function:Callable):
    if not hasattr(callback_function, 'function_attributes'):
            callback_function.function_attributes = dict(conditions = list())

    callback_function.function_attributes['conditions'].append(__allow_once_constraint(str(id(callback_function))))
    return callback_function