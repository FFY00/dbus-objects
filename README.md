# dbus-objects ![checks](https://github.com/FFY00/dbus-objects/workflows/checks/badge.svg) ![tests](https://github.com/FFY00/dbus-objects/workflows/tests/badge.svg) [![codecov](https://codecov.io/gh/FFY00/dbus-objects/branch/master/graph/badge.svg)](https://codecov.io/gh/FFY00/dbus-objects)

DBus objects implementation on top of the Python type system.

Integrations:
  - [jeepney](https://gitlab.com/takluyver/jeepney)

```python
import random

from typing import List

import dbus_objects.object
import dbus_objects.integration.jeepney


class ExampleObject(dbus_objects.object.DBusObject):
    def __init__(self):
        super().__init__(default_interface_root='io.github.ffy00.dbus_objects.example')
        self._bets = []

    @dbus_objects.object.dbus_method()
    def ping(self) -> str:
        return 'Pong!'

    @dbus_objects.object.dbus_method()
    def print(self, msg: str) -> None:
        print(msg)

    @dbus_objects.object.dbus_method()
    def sum(self, a: int, b: int) -> int:
        return a + b

    @dbus_objects.object.dbus_method()
    def save_bet(self, number: int) -> None:
        self._bets.append(number)

    @dbus_objects.object.dbus_method()
    def get_bets(self) -> List[int]:
        return self._bets

    @dbus_objects.object.dbus_method()
    def lotery(self) -> int:
        winner = random.choice(self._bets)
        self._bets = []
        return winner


server = dbus_objects.integration.jeepney.BlockingDBusServer(
    bus='SESSION',
    name='io.github.ffy00.dbus-objects'
)
server.register_object('/io/github/ffy00/dbus_objects/example', ExampleObject())

server.listen()
```

This example will generate the following server topology:
```
paths
├── /
│   ├── org.freedesktop.DBus.Introspectable
│   │   └── Introspect
│   ├── org.freedesktop.DBus.Peer
│   │   └── Ping
│   └── org.freedesktop.DBus.Properties
│       └── GetAll
├── /io
│   ├── org.freedesktop.DBus.Introspectable
│   │   └── Introspect
│   ├── org.freedesktop.DBus.Peer
│   │   └── Ping
│   └── org.freedesktop.DBus.Properties
│       └── GetAll
├── /io/github
│   ├── org.freedesktop.DBus.Introspectable
│   │   └── Introspect
│   ├── org.freedesktop.DBus.Peer
│   │   └── Ping
│   └── org.freedesktop.DBus.Properties
│       └── GetAll
├── /io/github/ffy00
│   ├── org.freedesktop.DBus.Introspectable
│   │   └── Introspect
│   ├── org.freedesktop.DBus.Peer
│   │   └── Ping
│   └── org.freedesktop.DBus.Properties
│       └── GetAll
├── /io/github/ffy00/dbus_objects
│   ├── org.freedesktop.DBus.Introspectable
│   │   └── Introspect
│   ├── org.freedesktop.DBus.Peer
│   │   └── Ping
│   └── org.freedesktop.DBus.Properties
│       └── GetAll
└── /io/github/ffy00/dbus_objects/example
    ├── io.github.ffy00.dbus_objects.example.ExampleObject
    │   ├── GetBets
    │   ├── Lotery
    │   ├── Ping
    │   ├── Print
    │   ├── SaveBet
    │   └── Sum
    ├── org.freedesktop.DBus.Introspectable
    │   └── Introspect
    ├── org.freedesktop.DBus.Peer
    │   └── Ping
    └── org.freedesktop.DBus.Properties
        └── GetAll
```

And, for eg., the following DBus introspection XML for `/io/github/ffy00/dbus_objects/example`:
```xml
<!DOCTYPE node PUBLIC
"-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
"http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd" >
<node xmlns:doc="http://www.freedesktop.org/dbus/1.0/doc.dtd">
    <interface name="io.github.ffy00.dbus_objects.example.ExampleObject">
        <method name="GetBets">
            <arg direction="out" type="ai" />
        </method>
        <method name="Lotery">
            <arg direction="out" type="i" />
        </method>
        <method name="Ping">
            <arg direction="out" type="s" />
        </method>
        <method name="Print">
            <arg direction="in" type="s" name="msg" />
        </method>
        <method name="SaveBet">
            <arg direction="in" type="i" name="number" />
        </method>
        <method name="Sum">
            <arg direction="in" type="i" name="a" />
            <arg direction="in" type="i" name="b" />
            <arg direction="out" type="i" />
        </method>
    </interface>
    <interface name="org.freedesktop.DBus.Properties">
        <method name="GetAll">
            <arg direction="in" type="s" name="interface_name" />
            <arg direction="out" type="a{sv}" />
        </method>
    </interface>
    <interface name="org.freedesktop.DBus.Introspectable">
        <method name="Introspect">
            <arg direction="out" type="s" name="xml" />
        </method>
    </interface>
    <interface name="org.freedesktop.DBus.Peer">
        <method name="Ping" />
    </interface>
</node>
```

### Dependencies

- [treelib](https://github.com/caesar0301/treelib)

Tests:
  - [pytest](https://github.com/pytest-dev/pytest)


### License

MIT
