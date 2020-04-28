# SPDX-License-Identifier: MIT

import typing

from typing import List

import jeepney_objects.object
import jeepney_objects.types


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
