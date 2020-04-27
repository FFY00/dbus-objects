# SPDX-License-Identifier: MIT

import pytest
import jeepney.wrappers

from jeepney_objects.integration.blocking import DBusServer


@pytest.fixture(params=['SESSION'])
def server(request):
    server = DBusServer(request.param, 'com.example.object')

    yield server

    server.close()


def test_create(server):
    pass


def test_create_error():
    with pytest.raises(jeepney.wrappers.DBusErrorResponse):
        DBusServer(bus='SESSION', name='org.freedesktop.DBus')
