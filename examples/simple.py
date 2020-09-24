#!/usr/bin/env python
import random

from typing import List

import dbus_objects.integration.jeepney
import dbus_objects.object


class ExampleObject(dbus_objects.object.DBusObject):
    def __init__(self):
        super().__init__(default_interface_root='io.github.ffy00.dbus_objects.example')
        self._bets = []

    @dbus_objects.object.dbus_method()
    def ping(self) -> str:
        return 'Pong!'

    @dbus_objects.object.dbus_method()
    def print(self, msg: str) -> None:
        print(msg)

    @dbus_objects.object.dbus_method()
    def sum(self, a: int, b: int) -> int:
        return a + b

    @dbus_objects.object.dbus_method()
    def save_bet(self, number: int) -> None:
        self._bets.append(number)

    @dbus_objects.object.dbus_method()
    def get_bets(self) -> List[int]:
        return self._bets

    @dbus_objects.object.dbus_method()
    def lotery(self) -> int:
        winner = random.choice(self._bets)
        self._bets = []
        return winner


server = dbus_objects.integration.jeepney.BlockingDBusServer(
    bus='SESSION',
    name='io.github.ffy00.dbus-objects'
)
server.register_object('/io/github/ffy00/dbus_objects/example', ExampleObject())

server.listen()
