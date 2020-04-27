# SPDX-License-Identifier: MIT

import pytest

from jeepney_objects.object import DBusObjectException, dbus_method


def test_dbus_method(obj):
    assert obj.example_method.is_dbus_method
    assert obj.example_method.dbus_method_name
    assert obj.example_method.dbus_direction
    assert obj.example_method.dbus_signature


def test_call(handlers):
    assert handlers['ExampleMethod']() == ('s', ('test',))


def test_dbus_method_error():
    @dbus_method()
    def method():
        pass  # pragma: no cover

    with pytest.raises(DBusObjectException):
        method()
