# SPDX-License-Identifier: MIT

import jeepney_objects.object


def dbus_case(text: str) -> str:
    '''
    Converts text to the DBus object capitalization (camel case with the first
    letter capitalized)
    '''
    def capitalize(text: str) -> str:
        if not text:
            return ''
        if len(text) == 1:
            return text.upper()
        return text[0].upper() + text[1:]
    return ''.join(capitalize(word) for word in text.split('_'))


def dbus_signature(typ: object) -> str:
    '''
    Converts a python type to a DBus signature
    '''
    if typ is str:
        return 's'
    raise jeepney_objects.object.DBusObjectException(f'Can\'t convert \'{typ}\' to a DBus signature')
