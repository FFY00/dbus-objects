# SPDX-License-Identifier: MIT

import multiprocessing
import time

import jeepney
import jeepney.io.blocking
import pytest

from dbus_objects import DBusObject, custom_dbus_signal, dbus_method, dbus_property, dbus_signal
from dbus_objects.integration import DBusServerBase
from dbus_objects.integration.jeepney import BlockingDBusServer
from dbus_objects.types import MultipleReturn


class ExampleObject(DBusObject):
    def __init__(self):
        super().__init__(default_interface_root='com.example.object')
        self._property = 'some property'

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
        return 1, 2  # pragma: no cover

    @dbus_property()
    def prop(self) -> str:
        return self._property

    @prop.setter
    def prop(self, value: str):
        self._property = value


class ExampleObjectWithSignal(DBusObject):
    def __init__(self):
        super().__init__(default_interface_root='com.example.object')

    signal = dbus_signal(
        value=int,
        other_value=str,
    )
    signal2 = dbus_signal(float, int)
    custom_signal = custom_dbus_signal(name='SpecialSignal')(int, int)
    custom_signal2 = custom_dbus_signal(name='SpecialSignal2')(
        name=str,
        age=int,
    )


class DummyServer(DBusServerBase):
    def __init__(self, bus: str, name: str):
        super().__init__(bus, name)
        self.emit_signal_callback = self.emit_signal
        self.emitted_signal = None

    def emit_signal(self, signal, path, body):
        self.emitted_signal = (signal.name, path, body)


@pytest.fixture(scope='session')
def obj():
    return ExampleObject()


@pytest.fixture()
def obj_methods(obj):
    return obj.get_dbus_methods()


@pytest.fixture()
def obj_properties(obj):
    return obj.get_dbus_properties()


@pytest.fixture()
def signal_obj():
    return ExampleObjectWithSignal()


@pytest.fixture()
def obj_signals(signal_obj):
    return signal_obj.get_dbus_signals()


@pytest.fixture()
def signal_server(signal_obj):
    server = DummyServer(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects.tests'
    )
    server.register_object('/io/github/ffy00/dbus_objects/example', signal_obj)
    yield server


@pytest.fixture()
def base_server(obj):
    server = DBusServerBase(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects.tests'
    )
    server.register_object('/io/github/ffy00/dbus_objects/example', obj)
    yield server


@pytest.fixture()
def jeepney_one_time_server(obj, signal_obj):
    server = BlockingDBusServer(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects.tests'
    )

    server.register_object('/io/github/ffy00/dbus_objects/example', obj)
    server.register_object('/io/github/ffy00/dbus_objects/example_signal', signal_obj)

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
