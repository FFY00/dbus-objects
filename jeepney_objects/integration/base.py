# SPDX-License-Identifier: MIT

from typing import Dict, List, Tuple

import jeepney_objects.object
import jeepney_objects.types


class StandardInterfacesObject(jeepney_objects.object.DBusObject):
    '''
    Standard DBus interfaces implementation

    Provides:
      - org.freedesktop.DBus.Peer
      - org.freedesktop.DBus.Introspectable
      - org.freedesktop.DBus.Properties
      - org.freedesktop.DBus.ObjectManager
    '''
    def __init__(self, methods: Dict[Tuple[str, str, str], jeepney_objects.types.DBusMethod]):
        '''
        :param methods: dictionary holding the registered DBus methods
        '''
        self._methods = methods

    @jeepney_objects.object.dbus_method(interface='org.freedesktop.DBus.Introspectable')
    def introspect(self) -> str:
        return ''


class DBusServerBase():
    def __init__(self, bus: str, name: str) -> None:
        '''
        :param bus: DBus bus (hint: usually SESSION or SYSTEM)
        :param name: DBus name
        '''
        self._bus = bus
        self._name = name

        # path, interface, method_name -> method
        self._methods: Dict[Tuple[str, str, str], jeepney_objects.types.DBusMethod] = {}
        self._interfaces: List[str] = []

    @property
    def name(self) -> str:
        return self._name

    def _register_object(self, path: str, obj: jeepney_objects.object.DBusObject) -> None:
        obj.server_name = self._name
        for method in obj.get_dbus_methods():
            self._methods[(path, method.dbus_interface, method.dbus_method_name)] = method
            if method.dbus_interface not in self._interfaces:
                self._interfaces.append(method.dbus_interface)

    def register_object(self, path: str, obj: jeepney_objects.object.DBusObject) -> None:
        self._register_object(path, obj)
        self._register_object(path, StandardInterfacesObject(self._methods))
