# SPDX-License-Identifier: MIT

import logging
import os.path
import textwrap
import typing
import warnings
import xml.etree.ElementTree as ET

from typing import Any, Dict, Optional

import treelib

import dbus_objects.object
import dbus_objects.types


# These few following classes implement the standard interfaces


class _Introspectable(dbus_objects.object.DBusObject):
    '''
    https://dbus.freedesktop.org/doc/dbus-specification.html#standard-interfaces-introspectable
    '''
    _XML_DOCTYPE = textwrap.dedent('''\
    <!DOCTYPE node PUBLIC
    "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
    "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd" >
    ''')

    def __init__(
        self,
        path: str,
        method_tree: Optional[treelib.Tree] = None,
        property_tree: Optional[treelib.Tree] = None,
    ):
        '''
        :param path: path where the onject is being resgistered
        :param method_tree: DBus server method tree
        '''
        super().__init__(
            name='Introspectable',
            default_interface_root='org.freedesktop.DBus',
        )
        self._path = path
        self._method_tree = method_tree
        self._property_tree = property_tree

    @dbus_objects.object.dbus_method(return_names=('xml',))
    def introspect(self) -> str:  # noqa: C901
        xml = ET.Element('node', {'xmlns:doc': 'http://www.freedesktop.org/dbus/1.0/doc.dtd'})
        interfaces: Dict[str, ET.Element] = {}

        def get_interface(name: str) -> ET.Element:
            if name not in interfaces:
                interfaces[name] = ET.SubElement(xml, 'interface', {'name': name})
            return interfaces[name]

        # add interfaces
        if self._method_tree and self._path in self._method_tree:
            for node in self._method_tree.children(self._path):
                interface = get_interface(node.tag)
                for method_node in self._method_tree.children(node.identifier):
                    method, descriptor = method_node.data
                    interface.append(descriptor.xml)
        if self._property_tree and self._path in self._property_tree:
            for node in self._property_tree.children(self._path):
                interface = get_interface(node.tag)
                for property_node in self._property_tree.children(node.identifier):
                    getter, setter, descriptor = property_node.data
                    interface.append(descriptor.xml)

        # add nodes (subpaths)
        if self._method_tree:
            for node in self._method_tree.children('paths'):
                if node.identifier == self._path or self._path.startswith(node.identifier):
                    continue
                if os.path.dirname(node.identifier) == self._path:
                    ET.SubElement(xml, 'node', {'name': os.path.basename(node.identifier)})

        return self._XML_DOCTYPE + ET.tostring(xml).decode()


class _Peer(dbus_objects.object.DBusObject):
    '''
    https://dbus.freedesktop.org/doc/dbus-specification.html#standard-interfaces-peer
    '''
    def __init__(self) -> None:
        super().__init__(
            name='Peer',
            default_interface_root='org.freedesktop.DBus',
        )

    @dbus_objects.object.dbus_method()
    def ping(self) -> None:
        return

    # TODO: GetMachineId() - how to reliably get the ID?


class _Properties(dbus_objects.object.DBusObject):
    '''
    https://dbus.freedesktop.org/doc/dbus-specification.html#standard-interfaces-properties
    '''
    def __init__(self, obj: dbus_objects.object.DBusObject) -> None:
        super().__init__(
            name='Properties',
            default_interface_root='org.freedesktop.DBus',
        )
        self._obj = obj

    @dbus_objects.object.dbus_method()
    def get(self, interface_name: str, property_name: str) -> dbus_objects.types.Variant:
        # TODO: interface == ''
        return '', None

    @dbus_objects.object.dbus_method(name='set')
    def set_(self, interface_name: str, property_name: str, value: dbus_objects.types.Variant) -> None:
        # TODO: interface == ''
        pass

    @dbus_objects.object.dbus_method()
    def get_all(self, interface_name: str) -> Dict[str, dbus_objects.types.Variant]:
        return {
            descriptor.name: (descriptor.signature, getter())
            for getter, setter, descriptor in self._obj.get_dbus_properties()
        }

    # TODO: PropertiesChanged


# TODO: org.freedesktop.DBus.ObjectManager


class _DBusTree(treelib.Tree):  # type: ignore
    def __init__(self) -> None:
        super().__init__()
        self._paths = self.create_node(identifier='paths')

    def get_path_node(self, path: str) -> treelib.Node:
        '''
        Fetches the path

        :param path: path
        '''
        if self.contains(path):
            return self.get_node(path)
        else:
            return self.create_node(identifier=path, parent=self._paths)

    def get_interface_node(self, path: str, interface: str, create: bool = False) -> treelib.Node:
        '''
        Fetches the interface for given path and interface name. Optionally
        creates it if not found.

        :param path: interface path
        :param interface: interface name
        :param create: whether to create the interface or not if missing
        '''
        path_node = self.get_path_node(path)
        for node in self.children(path):
            if node.tag == interface:
                return node
        return self.create_node(interface, parent=path_node,)

    def get_element(self, path: str, interface: str, name: str) -> Any:
        '''
        Fetches the element for given path, interface and element name

        :param path: element path
        :param interface: element interface
        :param interface: element name
        '''
        if self.contains(path):
            # search for interfaces (2nd level)
            for interface_node in self.children(path):
                if interface_node.tag == interface:
                    # search for methods (3rd level)
                    for method_node in self.children(interface_node.identifier):
                        if method_node.tag == name:
                            return method_node.data
                    break  # right interface but didn't find the method
        raise KeyError(f'Element not found: path={path} interface={interface} name={name}')


class DBusServerBase():
    def __init__(self, bus: str, name: str) -> None:
        '''
        DBus server base

        Implements the object registration and method storage logic.
        Subclasses can use get_method to fetch the method they want to
        dispatch.

        :param bus: DBus bus (hint: usually SESSION or SYSTEM)
        :param name: DBus name
        '''
        self.__logger = logging.getLogger(self.__class__.__name__)
        self._bus = bus
        self._name = name
        self._method_tree = _DBusTree()
        self._property_tree = _DBusTree()

    @property
    def name(self) -> str:
        '''
        DBus name
        '''
        return self._name

    def get_method(self, path: str, interface: str, method: str) -> dbus_objects.object._DBusMethodTuple:
        '''
        Fetches the method for given path, interface and method name

        :param path: method path
        :param interface: method interface
        :param interface: method name
        '''
        return typing.cast(
            dbus_objects.object._DBusMethodTuple,
            self._method_tree.get_element(path, interface, method)
        )

    def get_property(self, path: str, interface: str, method: str) -> dbus_objects.object._DBusPropertyTuple:
        '''
        Fetches the property for given path, interface and property name

        :param path: property path
        :param interface: property interface
        :param interface: property name
        '''
        return typing.cast(
            dbus_objects.object._DBusPropertyTuple,
            self._property_tree.get_element(path, interface, method)
        )

    def _register_element(
        self,
        tree: _DBusTree,
        path: str,
        interface: str,
        name: str,
        data: Any,
        ignore_warn: bool,
    ) -> None:
        interface_node = tree.get_interface_node(path, interface)
        for node in tree.children(interface_node.identifier):
            if node.tag == name:
                if not ignore_warn:
                    warnings.warn(
                        f'Element already registered! '
                        f'path={path} '
                        f'interface={interface} '
                        f'name={name} '
                    )
                break
        else:  # no break
            tree.create_node(name, data=data, parent=interface_node)

    def _register_object(
        self,
        path: str,
        obj: dbus_objects.object.DBusObject,
        ignore_warn: bool = False
    ) -> None:
        '''
        Low level object registration logic

        :param path: object path
        :param obj: object
        :param ignore_warn: ignores the duplicated object warning, you want to
                            set this when registering the standard interfaces
        '''
        for method, method_descriptor in obj.get_dbus_methods():
            self._register_element(
                self._method_tree,
                path,
                method_descriptor.interface,
                method_descriptor.name,
                (method, method_descriptor),
                ignore_warn,
            )
        for getter, setter, property_descriptor in obj.get_dbus_properties():
            self._register_element(
                self._property_tree,
                path,
                property_descriptor.interface,
                property_descriptor.name,
                (getter, setter, property_descriptor),
                ignore_warn,
            )

    def register_object(self, path: str, obj: dbus_objects.object.DBusObject) -> None:
        '''
        Registers the object into the server

        :param path: object path
        :param obj: object
        '''
        self.__logger.debug(f'registering {obj.dbus_name} in {path}')
        # TODO: validate paths, interfaces and method names
        self._register_object(path, obj)
        self._register_object(path, _Properties(obj), ignore_warn=True)
        do = True
        while do:
            self._register_object(path, _Peer(), ignore_warn=True)
            self._register_object(
                path,
                _Introspectable(path, self._method_tree, self._property_tree),
                ignore_warn=True
            )
            do = path != '/'
            path = os.path.dirname(path)
