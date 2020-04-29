# SPDX-License-Identifier: MIT

import inspect
import typing

from typing import Any, Callable, Generator, List, Tuple

import jeepney_objects.object
import jeepney_objects.types

if typing.TYPE_CHECKING:  # pragma: no cover
    import collections


def dbus_case(text: str) -> str:
    '''
    Converts text to the DBus object capitalization (camel case with the first
    letter capitalized)

    :param text:
    '''
    def capitalize(text: str) -> str:
        if not text:
            return ''
        if len(text) == 1:
            return text.upper()
        return text[0].upper() + text[1:]
    return ''.join(capitalize(word) for word in text.split('_'))


def dbus_signature(typ: type) -> str:  # noqa: C901
    '''
    Converts a python type to a DBus signature

    :param typ:
    '''
    cls: type = typ if not typing.get_origin(typ) else typing.get_origin(typ)  # type: ignore
    args = typing.get_args(typ)
    # TODO: Variants, File Descriptors, DBus Signature
    if cls is list:
        return 'a' + dbus_signature(args[0])
    elif cls is dict:
        return 'a{' + dbus_signature(args[0]) + dbus_signature(args[1]) + '}'
    elif cls is tuple:
        return '(' + ''.join(dbus_signature(arg) for arg in args) + ')'
    elif cls is str:
        return 's'
    elif cls is float:
        return 'd'
    elif cls is int or cls is jeepney_objects.types.Int32:
        return 'i'
    elif cls is jeepney_objects.types.Byte:
        return 'y'
    elif cls is jeepney_objects.types.UInt16:
        return 'q'
    elif cls is jeepney_objects.types.UInt32:
        return 'u'
    elif cls is jeepney_objects.types.UInt64:
        return 't'
    elif cls is jeepney_objects.types.Int16:
        return 'n'
    elif cls is jeepney_objects.types.Int64:
        return 'x'
    elif isinstance(typ, jeepney_objects.object.DBusObject):
        return 'o'

    raise jeepney_objects.object.DBusObjectException(f'Can\'t convert \'{typ}\' to a DBus signature')


def dbus_signature_from_list(args: List[type]) -> str:
    '''
    Converts a list of python types to a DBus signature

    :param args:
    '''
    return ''.join(dbus_signature(arg) for arg in args)


def _sig_parameters(args: 'collections.OrderedDict[str, inspect.Parameter]') -> Generator[type, type, None]:
    while args:
        key, value = args.popitem(last=False)
        if value.annotation is value.empty:
            raise jeepney_objects.object.DBusObjectException(f'Argument \'{key}\' is missing a type annotation')
        yield value.annotation


def get_dbus_signature(func: Callable[..., Any]) -> Tuple[str, str]:
    '''
    Gets the DBus signature from a function

    :param func: target function
    :returns:
        - direction
        - signature
    '''
    sig = inspect.signature(func)
    ret = sig.return_annotation if sig.return_annotation != sig.empty else None
    args = sig.parameters.copy()  # type: ignore
    if args:
        args.popitem(last=False)

    args = list(_sig_parameters(args))

    if ret and ret is not type(None):  # noqa: E721
        if len(args) > 0:
            raise jeepney_objects.object.DBusObjectException('Invalid method - a DBus method can\'t receive *and* return '
                                                             'parameters, only one is allowed')

        return 'out', dbus_signature(ret)
    else:
        return 'in', dbus_signature_from_list(args)
