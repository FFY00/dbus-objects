# SPDX-License-Identifier: MIT

import jeepney.bus_messages
import jeepney.integrate.blocking


class DBusServer():
    def __init__(self, bus: str, name: str) -> None:
        self._name = name
        self._conn = jeepney.integrate.blocking.connect_and_authenticate(bus)

        self._dbus = jeepney.bus_messages.DBus()

        self._conn.send_and_get_reply(self._dbus.RequestName(self.name))
        self._conn.router.on_unhandled = self._handle_msg

    def __del__(self) -> None:
        self.close()

    @property
    def name(self) -> str:
        return self._name

    def _handle_msg(self) -> None:
        pass

    def close(self) -> None:
        self._conn.close()
