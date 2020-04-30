# SPDX-License-Identifier: MIT

import inspect
import typing

from typing import Any, Callable, List, Tuple

import jeepney_objects.object
import jeepney_objects.types


def dbus_case(text: str) -> str:
    '''
    Converts text to the DBus object capitalization (camel case with the first
    letter capitalized)

    :param text: text to convert
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

    :param typ: python type to convert
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
    elif cls is jeepney_objects.object.DBusObject:
        return 'o'

    raise jeepney_objects.object.DBusObjectException(f'Can\'t convert \'{typ}\' to a DBus signature')


def dbus_signature_from_list(args: List[type]) -> str:
    '''
    Converts a list of python types to a DBus signature

    :param args: python type list
    '''
    return ''.join(dbus_signature(arg) for arg in args)


def get_dbus_signature(func: Callable[..., Any], skip_first_argument: bool = True) -> Tuple[str, str]:
    '''
    Gets the DBus signature from a function

    :param func: target function
    :param skip_first_argument: skips the first argument (for use with class methods)
    :returns:
        - input_signature
        - output_signature
    '''
    sig = inspect.signature(func)

    args = sig.parameters.copy()  # type: ignore
    ret = sig.return_annotation

    if skip_first_argument and args:
        args.popitem(last=False)

    for key, value in args.items():
        if value.annotation is value.empty:
            raise jeepney_objects.object.DBusObjectException(f'Argument \'{key}\' is missing a type annotation')

    args = dbus_signature_from_list(list(arg.annotation for arg in args.values()))

    if not ret or ret is sig.empty:
        ret = ''
    elif typing.get_origin(ret) is jeepney_objects.types.DBusReturn:
        print(typing.get_args(ret))
        print(typing.get_args(typing.get_args(ret)))
        ret = dbus_signature_from_list(list(typing.get_args(typing.get_args(ret)[0])))
    elif ret:
        ret = dbus_signature(ret)

    return args, ret
