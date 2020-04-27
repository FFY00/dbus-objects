# SPDX-License-Identifier: MIT

import inspect
import functools

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

        sig = inspect.signature(func)
        ret = sig.return_annotation if sig.return_annotation != sig.empty else None
        args = sig.parameters.copy()  # type: ignore
        if args:
            args.popitem(last=False)

        wrapper.is_dbus_method = True  # type: ignore

        if ret and ret is not type(None):  # noqa: E721
            if len(args) > 0:
                raise DBusObjectException('Invalid method - a DBus method can\'t receive *and* return parameters, '
                                          'only one is allowed')

            wrapper.dbus_direction = 'out'  # type: ignore
            wrapper.dbus_signature = jeepney_objects.util.dbus_signature(ret)  # type: ignore
        else:
            wrapper.dbus_direction = 'in'  # type: ignore

        method_name = name
        if not method_name:
            method_name = func.__name__
        wrapper.dbus_method_name = jeepney_objects.util.dbus_case(method_name)  # type: ignore

        return wrapper
    return decorator


class DBusObject():
    def __init__(self, interface_name: Optional[str] = None):
        self.is_dbus_object = True
        self._dbus_interface_name = jeepney_objects.util.dbus_case(type(self).__name__
                                                                   if not interface_name else interface_name)

    @property
    def dbus_interface_name(self) -> str:
        return self._dbus_interface_name

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
