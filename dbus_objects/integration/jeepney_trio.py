# SPDX-License-Identifier: MIT

import logging

import jeepney
import jeepney.io.trio
import trio

import dbus_objects.integration


class TrioDBusServer(dbus_objects.integration.DBusServerBase):
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
        self.__logger = logging.getLogger(self.__class__.__name__)

    # We can't have an async __init__ method, so we use this as an alternative.
    @classmethod
    async def new(cls, bus: str, name: str) -> 'TrioDBusServer':
        inst = cls(bus, name)
        await inst._conn_start()
        return inst

    async def _conn_start(self) -> None:
        '''
        Start DBus connection
        '''
        self._conn = await jeepney.io.trio.open_dbus_connection(self._bus)
        async with self._conn.router() as router:
            bus_proxy = jeepney.io.trio.Proxy(jeepney.message_bus, router)
            await bus_proxy.RequestName(self._name)

    async def _handle_msg(self, msg: jeepney.Message) -> None:
        '''
        Handle message

        :param msg: message to handle
        '''
        if msg.header.message_type == jeepney.MessageType.method_call:
            self.__logger.debug(f'received message {msg.header.message_type}')
            for key, value in msg.header.fields.items():
                self.__logger.debug(f'\t{jeepney.HeaderFields(key).name} = {value}')

            # TODO: validate fields are in msg
            try:
                method, descriptor = self.get_method(
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

            signature_input, signature_output = descriptor.signature

            if signature_input != msg_sig:
                self.__logger.debug(
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
                    self.__logger.error(
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

            await self._conn.send(return_msg)
        else:
            self.__logger.info(f'Unhandled message: {msg} / {msg.header} / {msg.header.fields}')

    async def close(self) -> None:
        '''
        Close the DBus connection
        '''
        await self._conn.aclose()

    async def listen(self, delay: float = 0.01) -> None:
        '''
        Start listening and handling messages

        :param delay: loop delay
        '''
        self.__logger.debug('server topology:')
        for line in self._method_tree.show(stdout=False).splitlines():
            self.__logger.debug('\t' + line)
        self.__logger.info('started listening...')
        try:
            while True:
                try:
                    msg = await self._conn.receive()
                except ConnectionResetError:
                    self.__logger.debug('connection reset abruptly, restarting...')
                    await self._conn_start()
                else:
                    await self._handle_msg(msg)
                await trio.sleep(delay)
        except KeyboardInterrupt:
            self.__logger.info('exiting...')
