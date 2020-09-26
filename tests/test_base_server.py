# SPDX-License-Identifier: MIT

import dbus_objects


def test_register_object(server, obj):
    server = dbus_objects.integration.DBusServerBase(
        bus='SESSION',
        name='io.github.ffy00.dbus-objects.tests'
    )

    server.register_object('/io/github/ffy00/dbus_objects/example', obj)
