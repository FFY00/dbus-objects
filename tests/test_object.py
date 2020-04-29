# SPDX-License-Identifier: MIT


def test_dbus_object(obj):
    assert obj.is_dbus_object
    assert obj.dbus_interface_name == 'ExampleObject'
    assert 'ExampleMethod' in obj.get_dbus_handlers()


def test_dbus_method(obj):
    assert obj.example_method.is_dbus_method
    assert obj.example_method.dbus_method_name
    assert obj.example_method.dbus_signature


def test_call(handlers):
    assert handlers['ExampleMethod']() == 'test'


def test_signature(handlers):
    assert handlers['ExampleMethod'].dbus_signature == ('', 's')
