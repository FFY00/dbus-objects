# SPDX-License-Identifier: MIT

import pytest

from jeepney_objects.object import DBusObject, dbus_method


class ExampleObject(DBusObject):
    @dbus_method()
    def example_method(self) -> str:
        return 'test'

    def normal_method(self):
        pass  # pragma: no cover


@pytest.fixture(scope='session')
def obj():
    return ExampleObject()


@pytest.fixture(scope='session')
def handlers(obj):
    return obj.get_dbus_handlers()
