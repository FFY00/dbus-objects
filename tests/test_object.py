# SPDX-License-Identifier: MIT

import pytest

from jeepney_objects.object import DBusObject, DBusObjectException, dbus_method


def test_dbus_object(obj):
    assert obj.is_dbus_object
    assert obj.dbus_interface_name == 'ExampleObject'
    assert 'ExampleMethod' in obj.get_dbus_handlers()


def test_dbus_method(obj):
    assert obj.example_method.is_dbus_method
    assert obj.example_method.dbus_method_name
    assert obj.example_method.dbus_direction
    assert obj.example_method.dbus_signature


def test_call(handlers):
    assert handlers['ExampleMethod']() == ('s', ('test',))


@pytest.mark.xfail(strict=True, raises=DBusObjectException)
def test_inout_method_error():
    class BadObject(DBusObject):
        @dbus_method()
        def inout_method(self, arg: int) -> int:
            return arg  # pragma: no cover


def test_dbus_method_error():
    @dbus_method()
    def method() -> str:
        pass  # pragma: no cover

    with pytest.raises(DBusObjectException):
        method()
