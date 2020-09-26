# SPDX-License-Identifier: MIT

import logging
import multiprocessing
import time

from typing import Union

import jeepney.bus_messages
import jeepney.integrate.blocking
import jeepney.low_level
import jeepney.wrappers

import dbus_objects.integration


class BlockingDBusServer(dbus_objects.integration.DBusServerBase):
    '''
    This class represents a DBus server. It should be instanciated.
    '''

    def __init__(self, bus: str, name: str) -> None:
        '''
        :param bus: DBus bus (hint: usually SESSION or SYSTEM)
        :param name: DBus name
        '''
        super().__init__(bus, name)
        self.__logger = logging.getLogger(self.__class__.__name__)
        self._conn = jeepney.integrate.blocking.connect_and_authenticate(self._bus)

        self._dbus = jeepney.bus_messages.DBus()

        self._conn.send_and_get_reply(self._dbus.RequestName(self._name))
        self._conn.router.on_unhandled = self._handle_msg

    def __del__(self) -> None:
        self.close()  # pragma: no cover

    def _handle_msg(self, msg: jeepney.low_level.Message) -> None:
        if msg.header.message_type == jeepney.low_level.MessageType.method_call:
            self.__logger.debug(f'received message {msg.header.message_type}')
            for key, value in msg.header.fields.items():
                self.__logger.debug(f'\t{jeepney.low_level.HeaderFields(key).name} = {value}')

            try:
                method = self._get_method(
                    msg.header.fields[jeepney.low_level.HeaderFields.path],
                    msg.header.fields[jeepney.low_level.HeaderFields.interface],
                    msg.header.fields[jeepney.low_level.HeaderFields.member],
                )
            except KeyError:
                self.__logger.info(
                    'Method not found:',
                    msg.header.fields[jeepney.low_level.HeaderFields.path],
                    msg.header.fields[jeepney.low_level.HeaderFields.interface],
                    msg.header.fields[jeepney.low_level.HeaderFields.member]
                )
                return

            # TODO: verify signature (inc. types)
            return_args = method(*msg.body)

            return_msg = jeepney.wrappers.new_method_return(
                msg,
                method.dbus_signature.output,
                (return_args,) if return_args is not None else tuple()
            )
            self._conn.send_message(return_msg)
        else:
            self.__logger.info(f'Unhandled message: {msg} / {msg.header} / {msg.header.fields}')

    def close(self) -> None:
        self._conn.close()

    def listen(self, delay: float = 0.01, event: Union[bool, multiprocessing.Event] = True) -> None:
        self.__logger.debug('server topology:')
        for line in self._tree.show(stdout=False).splitlines():
            self.__logger.debug('\t' + line)
        self.__logger.info('started listening...')
        try:
            while event.is_set():
                self._conn.recv_messages()
                time.sleep(delay)
        except KeyboardInterrupt:
            self.__logger.info('exiting...')
