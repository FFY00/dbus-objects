# SPDX-License-Identifier: MIT

import jeepney
import jeepney.io.trio
import pytest
import trio

from dbus_objects.integration.jeepney import TrioDBusServer


pytestmark = [
    pytest.mark.trio,
]


@pytest.fixture()
async def jeepney_trio_server(obj, nursery):
    server = await TrioDBusServer.new(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects.jeepney_trio_test',
    )

    server.register_object('/io/github/ffy00/dbus_objects/example', obj)

    # start server
    nursery.start_soon(server.listen)


@pytest.fixture()
def jeepney_trio_client():
    yield jeepney.DBusAddress(
        '/io/github/ffy00/dbus_objects/example',
        bus_name='io.github.ffy00.dbus-objects.jeepney_trio_test',
        interface='com.example.object.ExampleObject',
    )


@pytest.fixture()
async def jeepney_trio_router():
    async with jeepney.io.trio.open_dbus_router(bus='SESSION') as router:
        yield router


async def test_create_error():
    with pytest.raises(jeepney.DBusErrorResponse):
        await TrioDBusServer.new(bus='SESSION', name='org.freedesktop.DBus')


async def test_listen_trio(jeepney_trio_client, jeepney_trio_router, jeepney_trio_server):
    msg = jeepney.new_method_call(jeepney_trio_client, 'Ping', '', tuple())

    with trio.fail_after(3):
        reply = await jeepney_trio_router.send_and_get_reply(msg)

    assert reply.header.message_type is jeepney.MessageType.method_return
    assert reply.body[0] == 'Pong!'
