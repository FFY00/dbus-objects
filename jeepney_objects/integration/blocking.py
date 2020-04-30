# SPDX-License-Identifier: MIT

import jeepney.bus_messages
import jeepney.low_level
import jeepney.integrate.blocking

import jeepney_objects.integration.base


class DBusServer(jeepney_objects.integration.base.DBusServerBase):
    '''
    This class represents a DBus server. It should be instanciated.
    '''

    def __init__(self, bus: str, name: str) -> None:
        '''
        :param bus: DBus bus (hint: usually SESSION or SYSTEM)
        :param name: DBus name
        '''
        super().__init__(bus, name)
        self._conn = jeepney.integrate.blocking.connect_and_authenticate(self._bus)

        self._dbus = jeepney.bus_messages.DBus()

        self._conn.send_and_get_reply(self._dbus.RequestName(self._name))
        self._conn.router.on_unhandled = self._handle_msg

    def __del__(self) -> None:
        self.close()  # pragma: no cover

    def _handle_msg(self, msg: jeepney.low_level.Message) -> None:
        if msg.header.message_type == jeepney.low_level.MessageType.method_call:
            interface = msg.header.fields[jeepney.low_level.HeaderFields.interface]

            if interface in self._interfaces:
                pass

    def close(self) -> None:
        self._conn.close()
