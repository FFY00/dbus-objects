# dbus-objects

![checks](https://github.com/FFY00/dbus-objects/workflows/checks/badge.svg)
![tests](https://github.com/FFY00/dbus-objects/workflows/tests/badge.svg)
[![codecov](https://codecov.io/gh/FFY00/dbus-objects/branch/master/graph/badge.svg)](https://codecov.io/gh/FFY00/dbus-objects)
[![PyPI version](https://badge.fury.io/py/dbus-objects.svg)](https://pypi.org/project/dbus-objects/)

DBus objects implementation on top of the Python type system.

Object declarations will be introspected and the equivalent DBus signature
automatically generated. This makes it incredible easy to develop DBus object
providers ("servers"), especially if you are already writing typed Python!

Integrations:
  - [jeepney](https://gitlab.com/takluyver/jeepney) (blocking IO and [trio](https://github.com/python-trio/trio) backends)

```python
import random

from typing import List

import dbus_objects
import dbus_objects.integration.jeepney


class ExampleObject(dbus_objects.DBusObject):
    def __init__(self):
        super().__init__(default_interface_root='io.github.ffy00.dbus_objects.example')
        self._bets = []
        self._name = 'something'

    @dbus_objects.dbus_method()
    def ping(self) -> str:
        return 'Pong!'

    @dbus_objects.dbus_method()
    def print(self, msg: str) -> None:
        print(msg)

    @dbus_objects.dbus_method()
    def sum(self, a: int, b: int) -> int:
        return a + b

    @dbus_objects.dbus_method()
    def save_bet(self, number: int) -> None:
        self._bets.append(number)

    @dbus_objects.dbus_method()
    def get_bets(self) -> List[int]:
        return self._bets

    @dbus_objects.dbus_method()
    def lotery(self) -> int:
        winner = random.choice(self._bets)
        self._bets = []
        return winner

    @dbus_objects.dbus_property()
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        self.name_updated(value)

    name_updated = dbus_objects.dbus_signal(new_name=str)


server = dbus_objects.integration.jeepney.BlockingDBusServer(
    bus='SESSION',
    name='io.github.ffy00.dbus-objects',
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
│   └── org.freedesktop.DBus.Peer
│       └── Ping
├── /io
│   ├── org.freedesktop.DBus.Introspectable
│   │   └── Introspect
│   └── org.freedesktop.DBus.Peer
│       └── Ping
├── /io/github
│   ├── org.freedesktop.DBus.Introspectable
│   │   └── Introspect
│   └── org.freedesktop.DBus.Peer
│       └── Ping
├── /io/github/ffy00
│   ├── org.freedesktop.DBus.Introspectable
│   │   └── Introspect
│   └── org.freedesktop.DBus.Peer
│       └── Ping
├── /io/github/ffy00/dbus_objects
│   ├── org.freedesktop.DBus.Introspectable
│   │   └── Introspect
│   └── org.freedesktop.DBus.Peer
│       └── Ping
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
        ├── Get
        ├── GetAll
        └── Set
```

And, for eg., the following DBus introspection XML for `/io/github/ffy00/dbus_objects/example`:
```xml
<!DOCTYPE node PUBLIC
"-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
"http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd" >
<node>
	<interface name="io.github.ffy00.dbus_objects.example.ExampleObject">
		<method name="Ping">
			<arg direction="out" type="s" />
		</method>
		<method name="Print">
			<arg direction="in" type="s" name="msg" />
		</method>
		<method name="Sum">
			<arg direction="in" type="i" name="a" />
			<arg direction="in" type="i" name="b" />
			<arg direction="out" type="i" />
		</method>
		<method name="SaveBet">
			<arg direction="in" type="i" name="number" />
		</method>
		<method name="GetBets">
			<arg direction="out" type="ai" />
		</method>
		<method name="Lotery">
			<arg direction="out" type="i" />
		</method>
		<property name="Name" type="s" access="readwrite" />
		<signal name="NameUpdated">
			<arg type="s" name="new_name" />
		</signal>
	</interface>
	<interface name="org.freedesktop.DBus.Properties">
		<method name="Get">
			<arg direction="in" type="s" name="interface_name" />
			<arg direction="in" type="s" name="property_name" />
			<arg direction="out" type="v" />
		</method>
		<method name="Set">
			<arg direction="in" type="s" name="interface_name" />
			<arg direction="in" type="s" name="property_name" />
			<arg direction="in" type="v" name="value" />
		</method>
		<method name="GetAll">
			<arg direction="in" type="s" name="interface_name" />
			<arg direction="out" type="a{sv}" />
		</method>
	</interface>
	<interface name="org.freedesktop.DBus.Peer">
		<method name="Ping" />
	</interface>
	<interface name="org.freedesktop.DBus.Introspectable">
		<method name="Introspect">
			<arg direction="out" type="s" name="xml" />
		</method>
	</interface>
</node>
```


### License

MIT
