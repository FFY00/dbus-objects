# SPDX-License-Identifier: MIT

import pytest

from jeepney_objects.object import DBusObjectException
from jeepney_objects.util import dbus_case, dbus_signature


def test_signature():
    assert dbus_signature(str) == 's'
    with pytest.raises(DBusObjectException):
        dbus_signature(object)


def test_dbus_case():
    assert dbus_case('my_snake_case_string') == 'MySnakeCaseString'
    assert dbus_case('some_string') == 'SomeString'
    assert dbus_case('hope_this_works') == 'HopeThisWorks'
    assert dbus_case('LetsNotBreakCamelCase') == 'LetsNotBreakCamelCase'
    assert dbus_case('HumBetterNotBreak') == 'HumBetterNotBreak'
    assert dbus_case('almostThere') == 'AlmostThere'
    assert dbus_case('_oh_no') == 'OhNo'
    assert dbus_case('__oh_oh_no') == 'OhOhNo'
    assert dbus_case('_oh__oh__oh_no') == 'OhOhOhNo'
    assert dbus_case('hello1') == 'Hello1'
    assert dbus_case('a_b_c') == 'ABC'
