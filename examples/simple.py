#!/usr/bin/env python
import random

from typing import List

import dbus_objects
import dbus_objects.integration.jeepney


class ExampleObject(dbus_objects.DBusObject):
    def __init__(self):
        super().__init__(default_interface_root='io.github.ffy00.dbus_objects.example')
        self._bets = []
        self._name = 'something'

    @dbus_objects.dbus_method()
    def ping(self) -> str:
        return 'Pong!'

    @dbus_objects.dbus_method()
    def print(self, msg: str) -> None:
        print(msg)

    @dbus_objects.dbus_method()
    def sum(self, a: int, b: int) -> int:
        return a + b

    @dbus_objects.dbus_method()
    def save_bet(self, number: int) -> None:
        self._bets.append(number)

    @dbus_objects.dbus_method()
    def get_bets(self) -> List[int]:
        return self._bets

    @dbus_objects.dbus_method()
    def lotery(self) -> int:
        winner = random.choice(self._bets)
        self._bets = []
        return winner

    @dbus_objects.dbus_property()
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        self.name_updated(value)

    name_updated = dbus_objects.dbus_signal(new_name=str)


server = dbus_objects.integration.jeepney.BlockingDBusServer(
    bus='SESSION',
    name='io.github.ffy00.dbus-objects'
)
server.register_object('/io/github/ffy00/dbus_objects/example', ExampleObject())

server.listen()
