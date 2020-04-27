# SPDX-License-Identifier: MIT

import pytest

from jeepney_objects.object import DBusObjectException, dbus_method


def test_call(handlers):
    assert handlers['ExampleMethod']() == ('s', ('test',))


def test_is_dbus_method(obj):
    assert obj.example_method.is_dbus_method


def test_dbus_method_error():
    @dbus_method()
    def method():
        pass  # pragma: no cover

    with pytest.raises(DBusObjectException):
        method()
