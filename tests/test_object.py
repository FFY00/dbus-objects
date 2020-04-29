# SPDX-License-Identifier: MIT

import pytest

from jeepney_objects.object import DBusObjectException, dbus_method


def test_dbus_object(obj):
    assert obj.is_dbus_object
    assert obj.dbus_interface_name == 'ExampleObject'
    assert 'ExampleMethod' in obj.get_dbus_handlers()


def test_dbus_method(obj):
    assert obj.example_method.is_dbus_method
    assert obj.example_method.dbus_method_name
    assert obj.example_method.dbus_signature


def test_call(handlers):
    assert handlers['ExampleMethod']() == 'test'


def test_signature(handlers):
    assert handlers['ExampleMethod'].dbus_signature == ('', 's')


def test_dbus_method_error():
    @dbus_method()
    def method() -> str:
        pass  # pragma: no cover

    with pytest.raises(DBusObjectException):
        method()
