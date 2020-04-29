# SPDX-License-Identifier: MIT

import functools
import typing

from typing import Any, Callable, Dict, Optional

import jeepney_objects.types as our_types
import jeepney_objects.util


def dbus_method(name: Optional[str] = None) -> Callable[[Callable[..., Any]], our_types.DBusMethod]:
    '''
    Exports a function as a DBus method

    The direction will be detected automatically based on the type hints
    '''

    def decorator(func: Callable[..., Any]) -> our_types.DBusMethod:
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

        method_name = name
        if not method_name:
            method_name = func.__name__

        dbus_method_wrapper = typing.cast(our_types.DBusMethod, wrapper)

        dbus_method_wrapper.is_dbus_method = True
        dbus_method_wrapper.dbus_signature = jeepney_objects.util.get_dbus_signature(func)
        dbus_method_wrapper.dbus_method_name = jeepney_objects.util.dbus_case(method_name)

        return dbus_method_wrapper
    return decorator


class DBusObject():
    def __init__(self, interface_name: Optional[str] = None):
        self.is_dbus_object = True
        self._dbus_interface_name = jeepney_objects.util.dbus_case(type(self).__name__
                                                                   if not interface_name else interface_name)

    @property
    def dbus_interface_name(self) -> str:
        return self._dbus_interface_name

    def get_dbus_handlers(self) -> Dict[str, our_types.DBusMethod]:
        '''
        Returns a dictionary of the DBus method handlers
        '''
        handlers = {}

        for attr in dir(self):
            obj = getattr(self, attr)
            if getattr(obj, 'is_dbus_method', False):
                handlers[obj.dbus_method_name] = obj

        return handlers


class DBusObjectException(Exception):
    pass
