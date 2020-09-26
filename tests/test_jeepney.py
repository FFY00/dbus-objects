# SPDX-License-Identifier: MIT

import threading
import time

import jeepney
import jeepney.integrate.blocking
import jeepney.wrappers
import pytest

from dbus_objects.integration.jeepney import BlockingDBusServer


def test_create_error():
    with pytest.raises(jeepney.wrappers.DBusErrorResponse):
        BlockingDBusServer(bus='SESSION', name='org.freedesktop.DBus')


def test_listen(obj):
    server = BlockingDBusServer(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects.tests'
    )

    server.register_object('/io/github/ffy00/dbus_objects/example', obj)

    # start server
    run = threading.Event()
    run.set()
    thread = threading.Thread(target=server.listen, kwargs={'event': run})
    thread.start()

    # clear the event, listen will block until it receives the next message
    time.sleep(0.1)
    run.clear()

    # call Ping()
    client = jeepney.DBusAddress(
        '/io/github/ffy00/dbus_objects/example',
        bus_name='io.github.ffy00.dbus-objects.tests',
        interface='com.example.object.ExampleObject',
    )
    with jeepney.integrate.blocking.connect_and_authenticate(bus='SESSION') as connection:
        msg = jeepney.new_method_call(client, 'Ping', '', tuple())
        reply = connection.send_and_get_reply(msg)
        assert reply[0] == 'Pong!'

    # wait to finish
    thread.join()
