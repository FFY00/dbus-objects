# SPDX-License-Identifier: MIT

import jeepney
import pytest

from dbus_objects.integration.jeepney import BlockingDBusServer


def test_create_error():
    with pytest.raises(jeepney.DBusErrorResponse):
        BlockingDBusServer(bus='SESSION', name='org.freedesktop.DBus')


def test_listen(jeepney_one_time_server, jeepney_client, jeepney_connection):
    msg = jeepney.new_method_call(jeepney_client, 'Ping', '', tuple())
    reply = jeepney_connection.send_and_get_reply(msg)
    assert reply.body[0] == 'Pong!'
