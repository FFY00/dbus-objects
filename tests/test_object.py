# SPDX-License-Identifier: MIT

import xml.etree.ElementTree as ET

import pytest
import xmldiff

from dbus_objects import DBusObject, DBusObjectException, DBusObjectWarning, dbus_method


def test_dbus_object(obj):
    assert obj.is_dbus_object
    assert obj.dbus_name == 'ExampleObject'
    assert 'ExampleMethod' in [
        descriptor.name
        for _method, descriptor in obj.get_dbus_methods()
    ]


def test_call(obj_methods):
    for method, descriptor in obj_methods:
        if descriptor.name == 'ExampleMethod':
            assert method() == 'test'
            return
    assert False  # pragma: no cover


def test_signature(obj_methods):
    for _method, descriptor in obj_methods:
        if descriptor.name == 'ExampleMethod':
            assert descriptor.signature == ('', 's')
            return
    assert False  # pragma: no cover


def test_signature_multiple_return(obj_methods):
    for _method, descriptor in obj_methods:
        if descriptor.name == 'Multiple':
            assert descriptor.signature == ('s', 'ii')
            return
    assert False  # pragma: no cover


def test_no_interface():
    class TestObject(DBusObject):
        @dbus_method()
        def method() -> None:
            pass  # pragma: no cover

    with pytest.raises(DBusObjectException):
        list(TestObject().get_dbus_methods())


def test_property(obj_properties):
    for getter, setter, descriptor in obj_properties:
        if descriptor.name == 'Prop':
            assert descriptor.signature == 's'
            setter('something else')
            assert getter() == 'something else'
            return
    assert False  # pragma: no cover


def test_signal(obj_signals):
    for _callback, descriptor in obj_signals:
        if descriptor.name == 'Signal':
            assert descriptor.signature == 'is'
            assert list(descriptor.signature) == ['i', 's']
            return
    assert False  # pragma: no cover


def test_signal_call(signal_server, signal_obj):
    assert not signal_server.emitted_signal
    signal_obj.signal(30, 'test')
    assert signal_server.emitted_signal == (
        'Signal',
        '/io/github/ffy00/dbus_objects/example',
        (30, 'test'),
    )


def test_custom_signal_call(signal_server, signal_obj):
    assert not signal_server.emitted_signal
    signal_obj.custom_signal(1, 2)
    assert signal_server.emitted_signal == (
        'SpecialSignal',
        '/io/github/ffy00/dbus_objects/example',
        (1, 2),
    )


def test_method_xml(obj_methods):
    for _method, descriptor in obj_methods:
        if descriptor.name == 'ExampleMethod':
            assert not xmldiff.main.diff_texts(
                ET.tostring(descriptor.xml).decode(),
                (
                    '<method name="ExampleMethod"><arg direction="out" '
                    f'type="{descriptor.signature[1]}" /></method>'
                )
            )
            return
    assert False  # pragma: no cover


def test_property_xml(obj_properties):
    for _getter, _setter, descriptor in obj_properties:
        if descriptor.name == 'Prop':
            assert not xmldiff.main.diff_texts(
                ET.tostring(descriptor.xml).decode(),
                (
                    f'<property name="Prop" type="{descriptor.signature}" '
                    'access="readwrite" />'
                )
            )
            return
    assert False  # pragma: no cover


def test_signal_xml(obj_signals):
    for _method, descriptor in obj_signals:
        if descriptor.name == 'Signal':
            print(ET.tostring(descriptor.xml))
            assert not xmldiff.main.diff_texts(
                ET.tostring(descriptor.xml).decode(),
                (
                    '<signal name="Signal"><arg type="i" name="value" />'
                    '<arg type="s" name="other_value" /></signal>'
                )
            )
            return
    assert False  # pragma: no cover


def test_register_unsupported_signal_warning(base_server, signal_obj):
    with pytest.warns(DBusObjectWarning, match=(
        "Object 'ExampleObjectWithSignal' emits signals but the server "
        "'DBusServerBase' does not support this. Signals will not be emitted."
    )):
        base_server.register_object('/io/github/ffy00/dbus_objects/example', signal_obj)
