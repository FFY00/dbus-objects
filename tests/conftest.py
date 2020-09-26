# SPDX-License-Identifier: MIT

import pytest

from dbus_objects.integration import DBusServerBase
from dbus_objects.object import DBusObject, dbus_method
from dbus_objects.types import MultipleReturn


class ExampleObject(DBusObject):
    def __init__(self):
        super().__init__(default_interface_root='com.example.object')

    @dbus_method()
    def example_method(self) -> str:
        return 'test'

    def normal_method(self):
        pass  # pragma: no cover

    @dbus_method()
    def ping(self) -> str:
        return 'Pong!'  # pragma: no cover

    @dbus_method()
    def print(self, msg: str) -> None:
        print(msg)  # pragma: no cover

    @dbus_method(multiple_returns=True)
    def multiple(self, msg: str) -> MultipleReturn[int, int]:
        print(msg)  # pragma: no cover


@pytest.fixture(scope='session')
def obj():
    return ExampleObject()


@pytest.fixture()
def obj_methods(obj):
    return obj.get_dbus_methods()


@pytest.fixture()
def base_server(obj):
    server = DBusServerBase(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects.tests'
    )
    server.register_object('/io/github/ffy00/dbus_objects/example', obj)
    yield server
