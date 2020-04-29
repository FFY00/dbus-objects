# SPDX-License-Identifier: MIT

import pytest

from jeepney_objects.integration.blocking import DBusServer
from jeepney_objects.object import DBusObject, dbus_method


class ExampleObject(DBusObject):
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


@pytest.fixture(scope='session')
def obj():
    return ExampleObject()


@pytest.fixture(scope='session')
def handlers(obj):
    return obj.get_dbus_handlers()


@pytest.fixture(params=['SESSION'])
def server(request):
    server = DBusServer(request.param, 'com.example.object')

    yield server

    server.close()
