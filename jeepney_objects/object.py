# SPDX-License-Identifier: MIT

import typing

from typing import Any, Callable, Dict, Optional

import jeepney_objects.types as our_types
import jeepney_objects.util


def dbus_method(name: Optional[str] = None) -> Callable[[Callable[..., Any]], our_types.DBusMethod]:
    '''
    Exports a function as a DBus method

    The function must have type annotations, they will be used to resolve the
    method sigature.

    The function name will be used as the DBus method name unless otherwise
    specified in the arguments.

    :param name: DBus method name
    '''

    def decorator(func: Callable[..., Any]) -> our_types.DBusMethod:
        method_name = name
        if not method_name:
            method_name = func.__name__

        dbus_method_func = typing.cast(our_types.DBusMethod, func)

        dbus_method_func.is_dbus_method = True
        dbus_method_func.dbus_signature = jeepney_objects.util.get_dbus_signature(func)
        dbus_method_func.dbus_method_name = jeepney_objects.util.dbus_case(method_name)

        return dbus_method_func
    return decorator


class DBusObject():
    '''
    This class represents a DBus object. It should be subclassed and to export
    DBus methods, you must define typed functions with the
    :meth:`jeepney_objects.object.dbus_object` decorator.
    '''

    def __init__(self, name: Optional[str] = None):
        '''
        The class name will be used as the DBus object name unless otherwise
        specified in the arguments.

        :param name: DBus object name
        '''
        self.is_dbus_object = True
        self._dbus_name = jeepney_objects.util.dbus_case(type(self).__name__ if not name else name)

    @property
    def dbus_name(self) -> str:
        return self._dbus_name

    def get_dbus_methods(self) -> Dict[str, our_types.DBusMethod]:
        '''
        Returns a dictionary of the DBus methods. The key holds the DBus method
        name and the value holds a reference to the function.
        '''
        methods = {}

        for attr in dir(self):
            obj = getattr(self, attr)
            if getattr(obj, 'is_dbus_method', False):
                methods[obj.dbus_method_name] = obj

        return methods


class DBusObjectException(Exception):
    pass
