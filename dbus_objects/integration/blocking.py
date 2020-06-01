# SPDX-License-Identifier: MIT

import time

import jeepney.bus_messages
import jeepney.low_level
import jeepney.integrate.blocking

import dbus_objects.integration.base


class DBusServer(dbus_objects.integration.base.DBusServerBase):
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
            print('Message')
            print(f'\ttype = {msg.header.message_type}')
            for key, value in msg.header.fields.items():
                print(f'\t(field) {key} = {value}')

            interface = msg.header.fields[jeepney.low_level.HeaderFields.interface]

            if interface in self.interfaces:
                pass
            else:
                print(f'Unhandled message (unkown interface)! {interface}')

        else:
            print(f'Unhandled message! {msg} / {msg.header} / {msg.header.fields}')

    def close(self) -> None:
        self._conn.close()

    def listen(self, delay: float = 0.01) -> None:
        while True:
            self._conn.recv_messages()
            time.sleep(delay)
