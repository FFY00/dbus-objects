# SPDX-License-Identifier: MIT

import logging
import threading
import time

from typing import Optional

import jeepney
import jeepney.io.blocking

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

        self._dbus = jeepney.DBus()
        self._conn_start()

    def __del__(self) -> None:
        self.close()  # pragma: no cover

    def _conn_start(self) -> None:
        self._conn = jeepney.io.blocking.open_dbus_connection(self._bus)
        jeepney.io.blocking.Proxy(self._dbus, self._conn).RequestName(self._name)

    def _handle_msg(self, msg: jeepney.Message) -> None:
        if msg.header.message_type == jeepney.MessageType.method_call:
            self.__logger.debug(f'received message {msg.header.message_type}')
            for key, value in msg.header.fields.items():
                self.__logger.debug(f'\t{jeepney.HeaderFields(key).name} = {value}')

            # TODO: validate fields are in msg
            try:
                method = self._get_method(
                    msg.header.fields[jeepney.HeaderFields.path],
                    msg.header.fields[jeepney.HeaderFields.interface],
                    msg.header.fields[jeepney.HeaderFields.member],
                )
            except KeyError:
                self.__logger.info(
                    'Method not found:',
                    msg.header.fields[jeepney.HeaderFields.path],
                    msg.header.fields[jeepney.HeaderFields.interface],
                    msg.header.fields[jeepney.HeaderFields.member]
                )
                return

            if jeepney.HeaderFields.signature in msg.header.fields:
                msg_sig = msg.header.fields[jeepney.HeaderFields.signature]
            else:
                msg_sig = ''

            if method.dbus_signature.input != msg_sig:
                self.__logger.debug(
                    'got invalid signature, was expecting '
                    f'{method.dbus_signature.input} but got {msg_sig}'
                )
                return_msg = jeepney.new_error(
                    msg, 'Client Error', 's',
                    tuple([f'Invalid signature, expected {method.dbus_signature.input}'])
                )
            else:
                try:
                    return_args = method(*msg.body)
                except Exception as e:
                    return_msg = jeepney.new_error(msg, type(e).__name__, 's', tuple([str(e)]))
                else:
                    return_msg = jeepney.new_method_return(
                        msg,
                        method.dbus_signature.output,
                        (return_args,) if return_args is not None else tuple()
                    )

            self._conn.send_message(return_msg)
        else:
            self.__logger.info(f'Unhandled message: {msg} / {msg.header} / {msg.header.fields}')

    def close(self) -> None:
        self._conn.close()

    def listen(self, delay: float = 0.01, event: Optional[threading.Event] = None) -> None:
        self.__logger.debug('server topology:')
        for line in self._tree.show(stdout=False).splitlines():
            self.__logger.debug('\t' + line)
        self.__logger.info('started listening...')
        try:
            while event is None or event.is_set():
                try:
                    msg = self._conn.receive()
                except ConnectionResetError:
                    self.__logger.debug('connection reset abruptly, restarting...')
                    self._conn_start()
                else:
                    self._handle_msg(msg)
                time.sleep(delay)
        except KeyboardInterrupt:
            self.__logger.info('exiting...')
