# SPDX-License-Identifier: MIT

import typing
import xml.etree.ElementTree as ET

import pytest

import dbus_objects.types

from dbus_objects.object import DBusObject, DBusObjectException
from dbus_objects.signature import DBusSignature


@pytest.mark.parametrize(
    ('types', 'signature'),
    [
        (str, 's'),
        (int, 'i'),
        (float, 'd'),
        (dbus_objects.types.Byte, 'y'),
        (dbus_objects.types.UInt16, 'q'),
        (dbus_objects.types.UInt32, 'u'),
        (dbus_objects.types.UInt64, 't'),
        (dbus_objects.types.Int16, 'n'),
        (dbus_objects.types.Int32, 'i'),
        (dbus_objects.types.Int64, 'x'),
        (DBusObject, 'o'),
        (typing.List[int], 'ai'),
        (typing.Dict[str, int], 'a{si}'),
        (typing.Tuple[str, int], '(si)'),
        (typing.List[typing.Tuple[int, int]], 'a(ii)'),
        (typing.List[typing.List[int]], 'aai'),
        (typing.List[typing.List[DBusObject]], 'aao'),
        (typing.Tuple[int, typing.Tuple[int, int]], '(i(ii))'),
        (typing.Dict[str, str], 'a{ss}'),
        (typing.Dict[int, str], 'a{is}'),
        (typing.Dict[str, typing.Tuple[int, int]], 'a{s(ii)}'),
        (typing.Dict[str, typing.Dict[str, str]], 'a{sa{ss}}'),
    ],
)
def test_signature(subtests, types, signature):
    def method() -> types:
        pass  # pragma: no cover

    method_sig = DBusSignature(method, 'method', skip_first_argument=False)

    with subtests.test(msg='DBus signature'):
        assert method_sig.output == signature

    with subtests.test(msg='DBus signature'):
        assert (
            ET.tostring(method_sig.xml).decode() ==
            f'<method name="Method"><arg direction="out" type="{signature}" /></method>'
        )


def test_signature_error():
    with pytest.raises(DBusObjectException):
        DBusSignature._type_signature(complex)


@pytest.mark.parametrize(
    ('input', 'output'),
    [
        ('my_snake_case_string', 'MySnakeCaseString'),
        ('some_string', 'SomeString'),
        ('hope_this_works', 'HopeThisWorks'),
        ('LetsNotBreakCamelCase', 'LetsNotBreakCamelCase'),
        ('HumBetterNotBreak', 'HumBetterNotBreak'),
        ('almostThere', 'AlmostThere'),
        ('_oh_no', 'OhNo'),
        ('__oh_oh_no', 'OhOhNo'),
        ('_oh__oh__oh_no', 'OhOhOhNo'),
        ('hello1', 'Hello1'),
        ('a_b_c', 'ABC'),
    ]
)
def test_dbus_case(input, output):
    def method() -> None:
        pass  # pragma: no cover

    method_sig = DBusSignature(method, input, skip_first_argument=False)

    assert method_sig.name == output


def test_parameters():
    def method1(arg: typing.Dict[str, typing.Dict[str, str]]):
        pass  # pragma: no cover

    def method2() -> typing.List[typing.List[DBusObject]]:
        pass  # pragma: no cover

    def method3(arg: typing.Dict[int, str]) -> typing.Dict[int, str]:
        pass  # pragma: no cover

    def method4(self, arg: typing.Dict[str, typing.Dict[str, str]]) -> int:
        pass  # pragma: no cover

    sig = DBusSignature(method1, 'method1', skip_first_argument=False)
    assert sig.input == 'a{sa{ss}}'
    assert sig.output == ''
    # assert sig.input_names == ['arg']

    sig = DBusSignature(method2, 'method2', skip_first_argument=False)
    assert sig.input == ''
    assert sig.output == 'aao'
    assert sig.input_names == []

    sig = DBusSignature(method3, 'method3', skip_first_argument=False)
    assert sig.input == 'a{is}'
    assert sig.output == 'a{is}'
    # assert sig.input_names == ['arg']

    sig = DBusSignature(
        method4,
        'method4',
        skip_first_argument=True,
        return_names=['ret']
    )
    assert sig.input == 'a{sa{ss}}'
    assert sig.output == 'i'
    assert sig.input_names == ['arg']


def test_get_dbus_sigature_no_annotations():
    def method(arg):
        pass  # pragma: no cover

    with pytest.raises(DBusObjectException):
        DBusSignature(method, 'method', skip_first_argument=False)
