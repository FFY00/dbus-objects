#!/usr/bin/env python

import trio

import dbus_objects
import dbus_objects.integration.jeepney


class ExampleObject(dbus_objects.DBusObject):
    def __init__(self):
        super().__init__(default_interface_root='io.github.ffy00.dbus_objects.example')

    @dbus_objects.dbus_method()
    def ping(self) -> str:
        return 'Pong!'


async def main():
    server = await dbus_objects.integration.jeepney.TrioDBusServer.new(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects',
    )
    server.register_object('/io/github/ffy00/dbus_objects/example', ExampleObject())
    await server.listen()

trio.run(main)
