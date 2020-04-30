# SPDX-License-Identifier: MIT


def test_dbus_object(obj):
    assert obj.is_dbus_object
    assert obj.dbus_name == 'ExampleObject'
    assert 'ExampleMethod' in [method.dbus_method_name for method in obj.get_dbus_methods()]


def test_dbus_method(obj):
    assert obj.example_method.is_dbus_method
    assert obj.example_method.dbus_method_name
    assert obj.example_method.dbus_signature


def test_call(obj_methods):
    for method in obj_methods:
        if method.dbus_method_name == 'ExampleMethod':
            assert method() == 'test'
            return
    assert False


def test_signature(obj_methods):
    for method in obj_methods:
        if method.dbus_method_name == 'ExampleMethod':
            assert method.dbus_signature == ('', 's')
            return
    assert False
