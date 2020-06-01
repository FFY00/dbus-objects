# SPDX-License-Identifier: MIT

import typing

from typing import Any, Callable, Generator, List, Optional

import dbus_objects.types as our_types
import dbus_objects.util


def dbus_method(interface: str = '', name: Optional[str] = None, return_names: List[str] = [],
                multiple_returns: bool = False) -> Callable[[Callable[..., Any]], our_types.DBusMethod]:
    '''
    Exports a function as a DBus method

    The function must have type annotations, they will be used to resolve the
    method sigature.

    The function name will be used as the DBus method name unless otherwise
    specified in the arguments.

    :param interface: DBus interface name
    :param name: DBus method name
    :param multiple_returns: Returns multiple parameters
    '''

    def decorator(func: Callable[..., Any]) -> our_types.DBusMethod:
        method_name = name
        if not method_name:
            method_name = func.__name__

        dbus_method_func = typing.cast(our_types.DBusMethod, func)

        dbus_method_func.is_dbus_method = True
        dbus_method_func.dbus_signature = dbus_objects.util.get_dbus_signature(func, multiple_returns)
        dbus_method_func.dbus_method_name = dbus_objects.util.dbus_case(method_name)
        dbus_method_func.dbus_interface = interface
        dbus_method_func.dbus_return_names = return_names

        return dbus_method_func
    return decorator


class DBusObject():
    '''
    This class represents a DBus object. It should be subclassed and to export
    DBus methods, you must define typed functions with the
    :meth:`dbus_objects.object.dbus_object` decorator.
    '''

    def __init__(self, name: Optional[str] = None, default_interface: Optional[str] = None):
        '''
        The class name will be used as the DBus object name unless otherwise
        specified in the arguments.

        :param name: DBus object name
        '''
        self.is_dbus_object = True
        self._dbus_name = dbus_objects.util.dbus_case(type(self).__name__ if not name else name)
        self.default_interface = default_interface
        self.server_name: Optional[str] = None

    @property
    def dbus_name(self) -> str:
        return self._dbus_name

    def get_dbus_methods(self) -> Generator[our_types.DBusMethod, our_types.DBusMethod, None]:
        '''
        Returns a dictionary of the DBus methods. The key holds the DBus method
        name and the value holds a reference to the function.
        '''
        for attr in dir(self):
            obj = getattr(self, attr)
            if getattr(obj, 'is_dbus_method', False):
                method = typing.cast(our_types.DBusMethod, obj)
                if self.default_interface:
                    interface = '.'.join([self.default_interface, self._dbus_name])
                elif self.server_name:
                    interface = '.'.join([self.server_name, self._dbus_name])
                else:
                    raise DBusObjectException(f'Missing interface in DBus method \'{method.dbus_method_name}\'')
                method.__dict__['dbus_interface'] = interface  # hack! please let me know if you have a better solution
                yield method


class DBusObjectException(Exception):
    pass
