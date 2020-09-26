# SPDX-License-Identifier: MIT

import jeepney.wrappers
import pytest

from dbus_objects.integration.jeepney import BlockingDBusServer


def test_create_error():
    with pytest.raises(jeepney.wrappers.DBusErrorResponse):
        BlockingDBusServer(bus='SESSION', name='org.freedesktop.DBus')
