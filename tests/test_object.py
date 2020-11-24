# SPDX-License-Identifier: MIT

import pytest

from dbus_objects.object import DBusObject, DBusObjectException, dbus_method


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
