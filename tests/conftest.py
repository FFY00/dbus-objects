# SPDX-License-Identifier: MIT

import multiprocessing
import time

import jeepney
import jeepney.io.blocking
import pytest

from dbus_objects.integration import DBusServerBase
from dbus_objects.integration.jeepney import BlockingDBusServer
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


@pytest.fixture()
def jeepney_one_time_server(obj):
    server = BlockingDBusServer(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects.tests'
    )

    server.register_object('/io/github/ffy00/dbus_objects/example', obj)

    # start server
    run = multiprocessing.Event()
    run.set()
    process = multiprocessing.Process(target=server.listen, kwargs={'event': run})
    process.start()

    # clear the event, listen will block until it receives the next message
    time.sleep(0.2)
    run.clear()

    print('is up')
    yield
    print('done')

    # wait to finish
    print('joining')
    process.join()


@pytest.fixture()
def jeepney_client():
    yield jeepney.DBusAddress(
        '/io/github/ffy00/dbus_objects/example',
        bus_name='io.github.ffy00.dbus-objects.tests',
        interface='com.example.object.ExampleObject',
    )


@pytest.fixture(scope='session')
def jeepney_connection():
    with jeepney.io.blocking.open_dbus_connection(bus='SESSION') as connection:
        yield connection
