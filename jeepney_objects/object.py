# SPDX-License-Identifier: MIT

import functools
import typing

from typing import Any, Callable, Dict, Optional, Tuple

import jeepney_objects.util


def dbus_method(name: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    '''
    Exports a function as a DBus method

    The direction will be detected automatically based on the type hints
    '''
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            '''
            DBus function wrapper

            Will make sure the function is not called when defined outside
            DBusObject
            '''
            owner = args[0] if len(args) else None
            if not isinstance(owner, DBusObject):
                raise DBusObjectException('Tried to use a DBus method outside DBusObject')

            return func(*args, **kwargs)

        types = typing.get_type_hints(func)

        wrapper.is_dbus_method = True  # type: ignore

        if types.get('return'):
            wrapper.dbus_direction = 'out'  # type: ignore
            wrapper.dbus_signature = jeepney_objects.util.dbus_signature(types['return'])  # type: ignore
        else:
            wrapper.dbus_direction = 'in'  # type: ignore

        method_name = name
        if not method_name:
            method_name = func.__name__
        wrapper.dbus_method_name = jeepney_objects.util.dbus_case(method_name)  # type: ignore

        return wrapper
    return decorator


class DBusObject():
    def get_dbus_handlers(self) -> Dict[str, Callable[..., Any]]:
        '''
        Returns a dictionary of the DBus method handlers
        '''
        def generate_handler(method: Callable[..., Any]) -> Callable[..., Any]:
            def handler(*args: Any, **kwargs: Any) -> Tuple[str, Tuple[Any]]:
                return (method.dbus_signature, (method(*args, **kwargs),))  # type: ignore
            return handler

        handlers = {}

        for attr in dir(self):
            obj = getattr(self, attr)
            if getattr(obj, 'is_dbus_method', False):
                handlers[obj.dbus_method_name] = generate_handler(obj)

        return handlers


class DBusObjectException(Exception):
    pass
