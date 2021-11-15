# SPDX-License-Identifier: MIT

import asyncio
import async_timeout
import contextlib
import jeepney
import jeepney.io.asyncio
import pytest

from dbus_objects.integration.jeepney import AsyncIODBusServer


pytestmark = [
    pytest.mark.asyncio,
]


@pytest.fixture()
async def jeepney_asyncio_server(obj, event_loop):
    server = await AsyncIODBusServer.new(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects.jeepney_asyncio_test',
    )

    server.register_object('/io/github/ffy00/dbus_objects/example', obj)

    listen = event_loop.create_task(server.listen())
    try:
        yield

    finally:
        listen.cancel()
        await server.close()
        with contextlib.suppress(asyncio.CancelledError):
            await listen


@pytest.fixture()
def jeepney_asyncio_client():
    yield jeepney.DBusAddress(
        '/io/github/ffy00/dbus_objects/example',
        bus_name='io.github.ffy00.dbus-objects.jeepney_asyncio_test',
        interface='com.example.object.ExampleObject',
    )


@pytest.fixture()
async def jeepney_asyncio_router():
    async with jeepney.io.asyncio.open_dbus_router(bus='SESSION') as router:
        yield router


async def test_create_error():
    with pytest.raises(jeepney.DBusErrorResponse):
        await AsyncIODBusServer.new(bus='SESSION', name='org.freedesktop.DBus')


async def test_listen_asyncio(jeepney_asyncio_client, jeepney_asyncio_router, jeepney_asyncio_server):
    msg = jeepney.new_method_call(jeepney_asyncio_client, 'Ping', '', tuple())

    async with async_timeout.timeout(3):
        reply = await jeepney_asyncio_router.send_and_get_reply(msg)

    assert reply.header.message_type is jeepney.MessageType.method_return
    assert reply.body[0] == 'Pong!'
