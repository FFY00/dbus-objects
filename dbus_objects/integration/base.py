# SPDX-License-Identifier: MIT

import collections

from typing import Dict, List, DefaultDict

import dbus_objects.object
import dbus_objects.types


MethodDict = DefaultDict[str, DefaultDict[str, Dict[str, dbus_objects.types.DBusMethod]]]


class StandardInterfacesObject(dbus_objects.object.DBusObject):
    '''
    Standard DBus interfaces implementation

    Provides:
      - org.freedesktop.DBus.Peer
      - org.freedesktop.DBus.Introspectable
      - org.freedesktop.DBus.Properties
      - org.freedesktop.DBus.ObjectManager
    '''
    def __init__(self, methods: MethodDict):
        '''
        :param methods: dictionary holding the registered DBus methods
        '''
        self._methods = methods

    @dbus_objects.object.dbus_method(interface='org.freedesktop.DBus.Introspectable')
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

        # path -> interface -> method_name -> method
        self._methods: MethodDict = collections.defaultdict(lambda: collections.defaultdict(dict))

    @property
    def name(self) -> str:
        return self._name

    @property
    def interfaces(self) -> List[str]:
        return [interface for interface in self._methods]

    def _register_object(self, path: str, obj: dbus_objects.object.DBusObject) -> None:
        obj.server_name = self._name
        for method in obj.get_dbus_methods():
            self._methods[path][method.dbus_interface][method.dbus_method_name] = method

    def register_object(self, path: str, obj: dbus_objects.object.DBusObject) -> None:
        self._register_object(path, obj)
        self._register_object(path, StandardInterfacesObject(self._methods))
