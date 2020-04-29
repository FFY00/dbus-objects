# SPDX-License-Identifier: MIT

import typing

import pytest

import jeepney_objects.types

from jeepney_objects.object import DBusObject, DBusObjectException
from jeepney_objects.util import get_dbus_signature, dbus_case, dbus_signature, dbus_signature_from_list


def test_signature():
    assert dbus_signature(str) == 's'
    assert dbus_signature(int) == 'i'
    assert dbus_signature(float) == 'd'
    assert dbus_signature(jeepney_objects.types.Byte) == 'y'
    assert dbus_signature(jeepney_objects.types.UInt16) == 'q'
    assert dbus_signature(jeepney_objects.types.UInt32) == 'u'
    assert dbus_signature(jeepney_objects.types.UInt64) == 't'
    assert dbus_signature(jeepney_objects.types.Int16) == 'n'
    assert dbus_signature(jeepney_objects.types.Int32) == 'i'
    assert dbus_signature(jeepney_objects.types.Int64) == 'x'
    assert dbus_signature(DBusObject) == 'o'
    assert dbus_signature(typing.List[int]) == 'ai'
    assert dbus_signature(typing.Dict[str, int]) == 'a{si}'
    assert dbus_signature(typing.Tuple[str, int]) == '(si)'
    assert dbus_signature(typing.List[typing.Tuple[int, int]]) == 'a(ii)'
    assert dbus_signature(typing.List[typing.List[int]]) == 'aai'
    assert dbus_signature(typing.List[typing.List[DBusObject]]) == 'aao'
    assert dbus_signature(typing.Tuple[int, typing.Tuple[int, int]]) == '(i(ii))'
    assert dbus_signature(typing.Dict[str, str]) == 'a{ss}'
    assert dbus_signature(typing.Dict[int, str]) == 'a{is}'
    assert dbus_signature(typing.Dict[str, typing.Tuple[int, int]]) == 'a{s(ii)}'
    assert dbus_signature(typing.Dict[str, typing.Dict[str, str]]) == 'a{sa{ss}}'
    assert dbus_signature_from_list([
        jeepney_objects.types.Byte,
        jeepney_objects.types.Byte,
        jeepney_objects.types.Byte,
        jeepney_objects.types.Byte,
        jeepney_objects.types.UInt32,
        jeepney_objects.types.UInt32,
        typing.List[typing.Tuple[jeepney_objects.types.Byte, jeepney_objects.types.Byte]]
    ]) == 'yyyyuua(yy)'
    with pytest.raises(DBusObjectException):
        dbus_signature(object)


def test_dbus_case():
    assert dbus_case('my_snake_case_string') == 'MySnakeCaseString'
    assert dbus_case('some_string') == 'SomeString'
    assert dbus_case('hope_this_works') == 'HopeThisWorks'
    assert dbus_case('LetsNotBreakCamelCase') == 'LetsNotBreakCamelCase'
    assert dbus_case('HumBetterNotBreak') == 'HumBetterNotBreak'
    assert dbus_case('almostThere') == 'AlmostThere'
    assert dbus_case('_oh_no') == 'OhNo'
    assert dbus_case('__oh_oh_no') == 'OhOhNo'
    assert dbus_case('_oh__oh__oh_no') == 'OhOhOhNo'
    assert dbus_case('hello1') == 'Hello1'
    assert dbus_case('a_b_c') == 'ABC'


def test_get_dbus_sigature_empty():
    def method():
        pass  # pragma: no cover

    with pytest.raises(DBusObjectException):
        get_dbus_signature(method, ignore_first=False)


def test_get_dbus_sigature_no_annotations():
    def method(arg):
        pass  # pragma: no cover

    with pytest.raises(DBusObjectException):
        get_dbus_signature(method, ignore_first=False)
