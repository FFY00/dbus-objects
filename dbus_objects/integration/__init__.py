# SPDX-License-Identifier: MIT

import logging
import os.path
import textwrap
import typing
import warnings
import xml.etree.ElementTree as ET

from typing import Dict

import treelib

import dbus_objects.object
import dbus_objects.types


class _StandardInterfacesObject(dbus_objects.object.DBusObject):
    '''
    Standard DBus interfaces implementation

    Provides:
      - org.freedesktop.DBus.Peer
      - org.freedesktop.DBus.Introspectable
      - org.freedesktop.DBus.Properties
      - org.freedesktop.DBus.ObjectManager
    '''
    _XML_DOCTYPE = textwrap.dedent('''\
    <!DOCTYPE node PUBLIC
    "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
    "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd" >
    ''')

    def __init__(self, path: str, dbus_tree: treelib.Tree):
        '''
        :param methods: dictionary holding the registered DBus methods
        '''
        super().__init__()
        self._path = path
        self._tree = dbus_tree

    @dbus_objects.object.dbus_method(interface='org.freedesktop.DBus.Peer')
    def ping(self) -> None:
        return

    @dbus_objects.object.dbus_method(
        interface='org.freedesktop.DBus.Introspectable',
        return_names=('xml',),
    )
    def introspect(self) -> str:
        xml = ET.Element('node', {'xmlns:doc': 'http://www.freedesktop.org/dbus/1.0/doc.dtd'})

        # add interfaces
        for node in self._tree.children(self._path):
            interface = ET.SubElement(xml, 'interface', {'name': node.tag})
            for method_node in self._tree.children(node.identifier):
                interface.append(method_node.data.dbus_signature.xml)

        # add nodes (subpaths)
        for node in self._tree.children('paths'):
            if node.identifier == self._path or self._path.startswith(node.identifier):
                continue
            if os.path.dirname(node.identifier) == self._path:
                ET.SubElement(xml, 'node', {'name': os.path.basename(node.identifier)})

        return self._XML_DOCTYPE + ET.tostring(xml).decode()

    @dbus_objects.object.dbus_method(interface='org.freedesktop.DBus.Properties')
    def get_all(self, interface_name: str) -> Dict[str, dbus_objects.types.Variant]:
        return {}


class DBusServerBase():
    def __init__(self, bus: str, name: str) -> None:
        '''
        :param bus: DBus bus (hint: usually SESSION or SYSTEM)
        :param name: DBus name
        '''
        self.__logger = logging.getLogger(self.__class__.__name__)
        self._bus = bus
        self._name = name

        self._tree = treelib.Tree()
        self._paths = self._tree.create_node(identifier='paths')

    @property
    def name(self) -> str:
        return self._name

    def _get_path_node(self, path: str) -> treelib.Node:
        if self._tree.contains(path):
            return self._tree.get_node(path)
        else:
            return self._tree.create_node(identifier=path, parent=self._paths)

    def _get_interface_node(self, path: str, interface: str, create: bool = False) -> treelib.Node:
        path_node = self._get_path_node(path)
        for node in self._tree.children(path):
            if node.tag == interface:
                return node
        return self._tree.create_node(interface, parent=path_node,)

    def _get_method(self, path: str, interface: str, method: str) -> dbus_objects.types.DBusMethod:
        if self._tree.contains(path):
            # search for interfaces (2nd level)
            for interface_node in self._tree.children(path):
                if interface_node.tag == interface:
                    # search for methods (3rd level)
                    for method_node in self._tree.children(interface_node.identifier):
                        if method_node.tag == method:
                            return typing.cast(dbus_objects.types.DBusMethod, method_node.data)
                    break  # right interface but didn't find the method
        raise KeyError(f"Method not found: path={path} interface={interface} method={method}")

    def _register_object(
        self,
        path: str,
        obj: dbus_objects.object.DBusObject,
        ignore_warn: bool = False
    ) -> None:
        for method in obj.get_dbus_methods():
            if not method.dbus_interface:
                raise ValueError('Method has no DBus interface')
            interface_node = self._get_interface_node(path, method.dbus_interface)
            for node in self._tree.children(interface_node.identifier):
                if node.tag == method.dbus_signature.name:
                    if not ignore_warn:
                        warnings.warn(
                            'Object already registered! '
                            f'path={path} '
                            f'interface={method.dbus_interface} '
                            f'method={method.dbus_signature.name} '
                        )
                    break
            else:  # no break
                self._tree.create_node(method.dbus_signature.name, data=method, parent=interface_node)

    def register_object(self, path: str, obj: dbus_objects.object.DBusObject) -> None:
        self.__logger.debug(f'registering {obj.dbus_name} in {path}')
        # TODO: validate paths, interfaces and method names
        self._register_object(path, obj)
        do = True
        while do:
            self._register_object(
                path,
                _StandardInterfacesObject(path, self._tree),
                ignore_warn=True
            )
            do = path != '/'
            path = os.path.dirname(path)
