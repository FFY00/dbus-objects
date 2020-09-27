# SPDX-License-Identifier: MIT

import pytest
import xmldiff.main

import dbus_objects


def test_name():
    server = dbus_objects.integration.DBusServerBase(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects.tests'
    )
    assert server.name == 'io.github.ffy00.dbus-objects.tests'


def test_register_object(obj):
    server = dbus_objects.integration.DBusServerBase(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects.tests'
    )

    server.register_object('/io/github/ffy00/dbus_objects/example', obj)


def test_register_object_duplicate(obj):
    server = dbus_objects.integration.DBusServerBase(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects.tests'
    )

    server.register_object('/io/github/ffy00/dbus_objects/example', obj)

    with pytest.warns(Warning):
        server.register_object('/io/github/ffy00/dbus_objects/example', obj)


def test_introspectable(base_server):
    interospect = base_server._get_method(
        '/io/github/ffy00/dbus_objects',
        'org.freedesktop.DBus.Introspectable',
        'Introspect',
    )

    assert not xmldiff.main.diff_texts(interospect(), '''
        <!DOCTYPE node PUBLIC
        "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
        "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd" >
        <node xmlns:doc="http://www.freedesktop.org/dbus/1.0/doc.dtd"><interface name="org.freedesktop.DBus.Peer"><method name="Ping" /></interface><interface name="org.freedesktop.DBus.Introspectable"><method name="Introspect"><arg direction="out" type="s" name="xml" /></method></interface><node name="example" /></node>
    ''')  # noqa: E501


def test_peer(base_server):
    ping = base_server._get_method(
        '/io/github/ffy00/dbus_objects/example',
        'org.freedesktop.DBus.Peer',
        'Ping',
    )

    assert ping() is None


def test_properties(base_server):
    get = base_server._get_method(
        '/io/github/ffy00/dbus_objects/example',
        'org.freedesktop.DBus.Properties',
        'Get',
    )
    set_ = base_server._get_method(
        '/io/github/ffy00/dbus_objects/example',
        'org.freedesktop.DBus.Properties',
        'Set',
    )
    get_all = base_server._get_method(
        '/io/github/ffy00/dbus_objects/example',
        'org.freedesktop.DBus.Properties',
        'GetAll',
    )

    assert get('interface', 'property') == ('', None)
    assert set_('interface', 'property', 'value') is None
    assert get_all('interface') == {}
