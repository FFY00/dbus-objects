# SPDX-License-Identifier: MIT

import typing

import pytest

import dbus_objects.types

from dbus_objects.object import DBusObject, DBusObjectException
from dbus_objects.signature import DBusSignature


def test_signature():
    assert DBusSignature._type_signature(str) == 's'
    assert DBusSignature._type_signature(int) == 'i'
    assert DBusSignature._type_signature(float) == 'd'
    assert DBusSignature._type_signature(dbus_objects.types.Byte) == 'y'
    assert DBusSignature._type_signature(dbus_objects.types.UInt16) == 'q'
    assert DBusSignature._type_signature(dbus_objects.types.UInt32) == 'u'
    assert DBusSignature._type_signature(dbus_objects.types.UInt64) == 't'
    assert DBusSignature._type_signature(dbus_objects.types.Int16) == 'n'
    assert DBusSignature._type_signature(dbus_objects.types.Int32) == 'i'
    assert DBusSignature._type_signature(dbus_objects.types.Int64) == 'x'
    assert DBusSignature._type_signature(DBusObject) == 'o'
    assert DBusSignature._type_signature(typing.List[int]) == 'ai'
    assert DBusSignature._type_signature(typing.Dict[str, int]) == 'a{si}'
    assert DBusSignature._type_signature(typing.Tuple[str, int]) == '(si)'
    assert DBusSignature._type_signature(typing.List[typing.Tuple[int, int]]) == 'a(ii)'
    assert DBusSignature._type_signature(typing.List[typing.List[int]]) == 'aai'
    assert DBusSignature._type_signature(typing.List[typing.List[DBusObject]]) == 'aao'
    assert DBusSignature._type_signature(typing.Tuple[int, typing.Tuple[int, int]]) == '(i(ii))'
    assert DBusSignature._type_signature(typing.Dict[str, str]) == 'a{ss}'
    assert DBusSignature._type_signature(typing.Dict[int, str]) == 'a{is}'
    assert DBusSignature._type_signature(typing.Dict[str, typing.Tuple[int, int]]) == 'a{s(ii)}'
    assert DBusSignature._type_signature(typing.Dict[str, typing.Dict[str, str]]) == 'a{sa{ss}}'
    '''
    assert DBusSignature._type_signature_from_list([
        dbus_objects.types.Byte,
        dbus_objects.types.Byte,
        dbus_objects.types.Byte,
        dbus_objects.types.Byte,
        dbus_objects.types.UInt32,
        dbus_objects.types.UInt32,
        typing.List[typing.Tuple[dbus_objects.types.Byte, dbus_objects.types.Byte]]
    ]) == 'yyyyuua(yy)'
    with pytest.raises(DBusObjectException):
        DBusSignature._type_signature_from_list(object)
    '''


def test_dbus_case():
    assert DBusSignature.dbus_case('my_snake_case_string') == 'MySnakeCaseString'
    assert DBusSignature.dbus_case('some_string') == 'SomeString'
    assert DBusSignature.dbus_case('hope_this_works') == 'HopeThisWorks'
    assert DBusSignature.dbus_case('LetsNotBreakCamelCase') == 'LetsNotBreakCamelCase'
    assert DBusSignature.dbus_case('HumBetterNotBreak') == 'HumBetterNotBreak'
    assert DBusSignature.dbus_case('almostThere') == 'AlmostThere'
    assert DBusSignature.dbus_case('_oh_no') == 'OhNo'
    assert DBusSignature.dbus_case('__oh_oh_no') == 'OhOhNo'
    assert DBusSignature.dbus_case('_oh__oh__oh_no') == 'OhOhOhNo'
    assert DBusSignature.dbus_case('hello1') == 'Hello1'
    assert DBusSignature.dbus_case('a_b_c') == 'ABC'


def test_get_dbus_signature():
    def method1(arg: typing.Dict[str, typing.Dict[str, str]]):
        pass  # pragma: no cover

    def method2() -> typing.List[typing.List[DBusObject]]:
        pass  # pragma: no cover

    def method3(arg: typing.Dict[int, str]) -> typing.Dict[int, str]:
        pass  # pragma: no cover

    sig = DBusSignature(method1, 'Method1', skip_first_argument=False)
    assert sig.input == 'a{sa{ss}}'
    assert sig.output == ''

    sig = DBusSignature(method2, 'Method2', skip_first_argument=False)
    assert sig.input == ''
    assert sig.output == 'aao'

    sig = DBusSignature(method3, 'Method3', skip_first_argument=False)
    assert sig.input == 'a{is}'
    assert sig.output == 'a{is}'


def test_get_dbus_sigature_no_annotations():
    def method(arg):
        pass  # pragma: no cover

    with pytest.raises(DBusObjectException):
        DBusSignature(method, 'Method', skip_first_argument=False)
