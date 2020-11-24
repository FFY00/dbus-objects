# SPDX-License-Identifier: MIT

from __future__ import annotations

import inspect
import sys
import typing

from typing import Any, Callable, Iterable, Iterator, List, Optional, Sequence, Type

import dbus_objects.object
import dbus_objects.types


if sys.version_info < (3, 8):
    import typing_extensions
    typing.get_args = typing_extensions.get_args
    typing.get_origin = typing_extensions.get_origin


class DBusSignature():
    def __init__(
        self,
        annotations: Sequence[Type[Any]],
        names: Optional[Sequence[str]]
    ) -> None:
        self._list = self._get_signatures(annotations)
        self._names = names

    def __iter__(self) -> Iterator[Any]:
        return iter(self._list)

    def __str__(self) -> str:
        return ''.join(self._list)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({str(self)})'

    @property
    def names(self) -> Optional[Sequence[str]]:
        return self._names

    @classmethod
    def from_parameters(
        cls,
        func: Callable[..., Any],
        skip_first_argument: bool = True,
    ) -> DBusSignature:
        sig = inspect.signature(func)
        args = sig.parameters.copy()  # type: ignore

        # remove self if it is a class method
        if skip_first_argument and args:
            args.popitem(last=False)

        for name, value in args.items():
            if value.annotation is value.empty:
                raise dbus_objects.object.DBusObjectException(
                    f'Argument is missing a type annotation: {name} ({func})'
                )

        return cls(
            [arg.annotation for arg in args.values()],
            [name for name in args],
        )

    @classmethod
    def from_return(
        cls,
        func: Callable[..., Any],
        return_names: Optional[Sequence[str]] = None,
        multiple_returns: bool = False,
    ) -> DBusSignature:
        sig = inspect.signature(func)
        ret = sig.return_annotation

        annotations: List[Type[Any]]
        if not ret or ret is sig.empty:
            annotations = []
        elif multiple_returns:
            annotations = list(typing.get_args(ret))
        elif ret:
            annotations = [ret]

        return cls(annotations, return_names)

    @classmethod
    def _type_signature(cls, typ: type) -> str:  # noqa: C901
        '''
        Converts a python type to a DBus signature

        :param typ: python type to convert
        '''
        attr_class: type = typ if not typing.get_origin(typ) else typing.get_origin(typ)  # type: ignore
        args = typing.get_args(typ)
        # TODO: Variants, File Descriptors, DBus Signature
        if attr_class is dbus_objects.types.Variant:
            return 'v'
        elif attr_class is list:
            return 'a' + cls._type_signature(args[0])
        elif attr_class is dict:
            return 'a{' + cls._type_signature(args[0]) + cls._type_signature(args[1]) + '}'
        elif attr_class is tuple:
            return '(' + ''.join(cls._type_signature(arg) for arg in args) + ')'
        elif attr_class is str:
            return 's'
        elif attr_class is float:
            return 'd'
        elif attr_class is int or attr_class is dbus_objects.types.Int32:
            return 'i'
        elif attr_class is dbus_objects.types.Byte:
            return 'y'
        elif attr_class is dbus_objects.types.UInt16:
            return 'q'
        elif attr_class is dbus_objects.types.UInt32:
            return 'u'
        elif attr_class is dbus_objects.types.UInt64:
            return 't'
        elif attr_class is dbus_objects.types.Int16:
            return 'n'
        elif attr_class is dbus_objects.types.Int64:
            return 'x'
        elif attr_class is dbus_objects.object.DBusObject:
            return 'o'

        raise dbus_objects.object.DBusObjectException(f'Can\'t convert \'{typ}\' to a DBus signature')

    @classmethod
    def _get_signatures(cls, args: Iterable[type]) -> List[str]:
        '''
        Converts a list of python types to a DBus signature

        :param args: python type list
        '''
        signature = []
        for arg in args:
            signature.append(cls._type_signature(arg))

        return signature


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
