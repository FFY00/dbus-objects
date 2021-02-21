# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import threading

from typing import Any, Optional

import jeepney
import jeepney.io.blocking

import dbus_objects.integration


class _JeepneyServerBase(dbus_objects.integration.DBusServerBase):
    def __init__(self, bus: str, name: str) -> None:
        super().__init__(bus, name)
        self._logger = logging.getLogger(self.__class__.__name__)

    def _log_topology(self) -> None:
        self._logger.debug('server topology:')
        for line in self._method_tree.show(stdout=False).splitlines():
            self._logger.debug('\t' + line)
        self._logger.info('started listening...')

    def _jeepney_handle_msg(self, msg: jeepney.Message) -> Optional[jeepney.Message]:
        '''
        Handle message

        :param msg: message to handle
        '''
        if msg.header.message_type == jeepney.MessageType.method_call:
            self._logger.debug(f'received message {msg.header.message_type}')
            for key, value in msg.header.fields.items():
                self._logger.debug(f'\t{jeepney.HeaderFields(key).name} = {value}')

            # TODO: validate fields are in msg
            try:
                method, descriptor = self.get_method(
                    msg.header.fields[jeepney.HeaderFields.path],
                    msg.header.fields[jeepney.HeaderFields.interface],
                    msg.header.fields[jeepney.HeaderFields.member],
                )
            except KeyError:
                self._logger.info(
                    'Method not found:',
                    msg.header.fields[jeepney.HeaderFields.path],
                    msg.header.fields[jeepney.HeaderFields.interface],
                    msg.header.fields[jeepney.HeaderFields.member]
                )
                return None

            if jeepney.HeaderFields.signature in msg.header.fields:
                msg_sig = msg.header.fields[jeepney.HeaderFields.signature]
            else:
                msg_sig = ''

            signature_input, signature_output = descriptor.signature

            if signature_input != msg_sig:
                self._logger.debug(
                    'got invalid signature, was expecting '
                    f'{signature_input} but got {msg_sig}'
                )
                return_msg = jeepney.new_error(
                    msg, 'Client Error', 's',
                    tuple([f'Invalid signature, expected {signature_input}'])
                )
            else:
                try:
                    return_args = method(*msg.body)
                except Exception as e:
                    self._logger.error(
                        f'An exception ocurred when try to call method: {descriptor.name}',
                        exc_info=True
                    )
                    return_msg = jeepney.new_error(msg, type(e).__name__, 's', tuple([str(e)]))
                else:
                    return_msg = jeepney.new_method_return(
                        msg,
                        signature_output,
                        (return_args,) if return_args is not None else tuple()
                    )

            return return_msg
        else:
            self._logger.info(f'Unhandled message: {msg} / {msg.header} / {msg.header.fields}')
            return None

    def _get_signal_msg(self, signal: dbus_objects._DBusSignal, path: str, body: Any) -> jeepney.Message:
        emitter = jeepney.wrappers.DBusAddress(path, interface=signal.interface)
        msg = jeepney.new_signal(emitter, signal.name, signal.signature, body)
        return msg


class BlockingDBusServer(_JeepneyServerBase):
    '''
    This class represents a DBus server. It should be instanciated.
    '''

    def __init__(self, bus: str, name: str) -> None:
        '''
        Blocking DBus server built on top of Jeepney

        :param bus: DBus bus (hint: usually SESSION or SYSTEM)
        :param name: DBus name
        '''
        super().__init__(bus, name)
        self._logger = logging.getLogger(self.__class__.__name__)

        self.emit_signal_callback = self.emit_signal

        self._dbus = jeepney.DBus()
        self._conn_start()

    def __del__(self) -> None:
        self.close()  # pragma: no cover

    def _conn_start(self) -> None:
        '''
        Start DBus connection
        '''
        self._conn = jeepney.io.blocking.open_dbus_connection(self._bus)
        jeepney.io.blocking.Proxy(self._dbus, self._conn).RequestName(self._name)

    def _handle_msg(self, msg: jeepney.Message) -> None:
        '''
        Handle message

        :param msg: message to handle
        '''
        return_msg = self._jeepney_handle_msg(msg)
        if return_msg:
            self._conn.send(return_msg)

    def emit_signal(self, signal: dbus_objects._DBusSignal, path: str, body: Any) -> None:
        self._logger.debug(f'emitting signal: {signal.name} {body}')
        self._conn.send_message(self._get_signal_msg(signal, path, body))

    def close(self) -> None:
        '''
        Close the DBus connection
        '''
        self._conn.close()

    def listen(self, delay: float = 0.1, event: Optional[threading.Event] = None) -> None:
        '''
        Start listening and handling messages

        :param delay: loop delay
        :param event: event which can be activated to stop listening
        '''
        self._log_topology()
        try:
            while event is None or event.is_set():
                try:
                    msg = self._conn.receive(timeout=delay)
                except TimeoutError:
                    pass
                except ConnectionResetError:
                    self._logger.debug('connection reset abruptly, restarting...')
                    self._conn_start()
                else:
                    self._handle_msg(msg)
        except KeyboardInterrupt:
            self._logger.info('exiting...')


class TrioDBusServer(_JeepneyServerBase):
    '''
    This class represents a DBus server. It should be instanciated.
    '''

    def __init__(self, bus: str, name: str) -> None:
        '''
        Blocking DBus server built on top of Jeepney

        :param bus: DBus bus (hint: usually SESSION or SYSTEM)
        :param name: DBus name
        '''
        super().__init__(bus, name)
        self._logger = logging.getLogger(self.__class__.__name__)
        # TODO: support signals
        # self.emit_signal_callback = self.emit_signal

    # We can't have an async __init__ method, so we use this as an alternative.
    @classmethod
    async def new(cls, bus: str, name: str) -> TrioDBusServer:
        inst = cls(bus, name)
        await inst._conn_start()
        return inst

    async def _conn_start(self) -> None:
        '''
        Start DBus connection
        '''
        import jeepney.io.trio

        self._conn = await jeepney.io.trio.open_dbus_connection(self._bus)
        async with self._conn.router() as router:
            bus_proxy = jeepney.io.trio.Proxy(jeepney.message_bus, router)
            await bus_proxy.RequestName(self._name)

    async def _handle_msg(self, msg: jeepney.Message) -> None:
        '''
        Handle message

        :param msg: message to handle
        '''
        return_msg = self._jeepney_handle_msg(msg)
        if return_msg:
            await self._conn.send(return_msg)

    async def emit_signal(self, signal: dbus_objects._DBusSignal, path: str, body: Any) -> None:
        self._logger.debug(f'emitting signal: {signal.name} {body}')
        await self._conn.send_message(self._get_signal_msg(signal, path, body))

    async def close(self) -> None:
        '''
        Close the DBus connection
        '''
        await self._conn.aclose()

    async def listen(self) -> None:
        '''
        Start listening and handling messages

        :param delay: loop delay
        '''
        self._log_topology()
        try:
            while True:
                try:
                    msg = await self._conn.receive()
                except ConnectionResetError:
                    self._logger.debug('connection reset abruptly, restarting...')
                    await self._conn_start()
                else:
                    await self._handle_msg(msg)
        except KeyboardInterrupt:
            self._logger.info('exiting...')
