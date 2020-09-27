# SPDX-License-Identifier: MIT

import inspect
import itertools
import sys
import typing
import xml.etree.ElementTree as ET

from typing import Any, Callable, Iterable, List, Optional, Sequence

import dbus_objects.object
import dbus_objects.types


if sys.version_info < (3, 8):
    import typing_extensions
    typing.get_args = typing_extensions.get_args
    typing.get_origin = typing_extensions.get_origin


class DBusSignature():
    def __init__(
        self,
        func: Callable[..., Any],
        name: str,
        multiple_returns: bool = False,
        return_names: Optional[Sequence[str]] = None,
        skip_first_argument: bool = True,
    ) -> None:
        '''
        Gets the DBus signature from a function

        :param func: target function
        :param skip_first_argument: skips the first argument (for use with class methods)
        :returns:
            - input_signature
            - output_signature
        '''
        self._func = func
        self._name = self.dbus_case(name)
        self._return_names = return_names
        sig = inspect.signature(func)

        args = sig.parameters.copy()  # type: ignore
        ret = sig.return_annotation

        if skip_first_argument and args:
            args.popitem(last=False)

        for key, value in args.items():
            if value.annotation is value.empty:
                raise dbus_objects.object.DBusObjectException(f"Argument '{key}' is missing a type annotation")

        # contruct signature list
        self._in_sigs = self._get_signatures(arg.annotation for arg in args.values())

        if not ret or ret is sig.empty:
            self._out_sigs = []
        elif multiple_returns:
            self._out_sigs = self._get_signatures(typing.get_args(ret))
        elif ret:
            self._out_sigs = [self._type_signature(ret)]

        # contruct signature string
        self._in = ''.join(self._in_sigs)
        self._out = ''.join(self._out_sigs)

        self._build_xml()

    @property
    def name(self) -> str:
        return self._name

    @property
    def input(self) -> str:
        return self._in

    @property
    def output(self) -> str:
        return self._out

    @property
    def input_names(self) -> List[str]:
        sig = inspect.signature(self._func)

        args = sig.parameters.copy()  # type: ignore
        if args:
            args.popitem(last=False)

        return list(name for name in args)

    @property
    def output_names(self) -> Sequence[str]:
        return self._return_names or []

    @staticmethod
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

    @property
    def xml(self) -> ET.Element:
        return self._xml

    def _build_xml(self) -> None:
        self._xml = ET.Element('method', {'name': self.name})

        for direction, signature, names in (
            ('in', self._in_sigs, self.input_names),
            ('out', self._out_sigs, self.output_names),
        ):
            for name, sig in itertools.zip_longest(names, signature):
                data = {
                    'direction': direction,
                    'type': sig,
                }
                if name:
                    data['name'] = name
                ET.SubElement(self._xml, 'arg', data)

        # TODO: export documentation
