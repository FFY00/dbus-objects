# SPDX-License-Identifier: MIT

import jeepney
import jeepney.bus_messages
import jeepney.io.blocking
import pytest

from dbus_objects.integration.jeepney import BlockingDBusServer


def test_create_error():
    with pytest.raises(jeepney.DBusErrorResponse):
        BlockingDBusServer(bus='SESSION', name='org.freedesktop.DBus')


def test_listen(jeepney_one_time_server, jeepney_client, jeepney_connection):
    msg = jeepney.new_method_call(jeepney_client, 'Ping', '', tuple())
    reply = jeepney_connection.send_and_get_reply(msg)
    assert reply.body[0] == 'Pong!'


def test_emit_signal(jeepney_one_time_server, signal_obj, jeepney_connection):
    rule = jeepney.bus_messages.MatchRule(
        type='signal',
        interface='com.example.object.ExampleObjectWithSignal',
        member='Signal',
        path='/io/github/ffy00/dbus_objects/example_signal',
    )

    bus_proxy = jeepney.io.blocking.Proxy(
        jeepney.bus_messages.message_bus,
        jeepney_connection,
    )
    bus_proxy.AddMatch(rule)

    signal_obj.signal(30, 'test')

    with jeepney_connection.filter(rule) as queue:
        signal_msg = jeepney_connection.recv_until_filtered(queue)

    assert signal_msg.header.fields[jeepney.HeaderFields.signature] == 'is'
    assert signal_msg.body == (30, 'test')
