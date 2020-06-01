# SPDX-License-Identifier: MIT

import xml.etree.ElementTree as ET

from typing import Dict, Generator, List, Union

import dbus_objects.types
import dbus_objects.util


def _append_method_args(tree: ET.TreeBuilder, direction: str, sig: str, names: List[str]) -> None:
    opt: Dict[Union[bytes, str], Union[bytes, str]] = {}

    opt['direction'] = direction
    for i, sig in enumerate(sig):
        opt['type'] = sig
        if i < len(names):
            opt['name'] = names[0]
        tree.start('arg', opt)


def append_dbus_method(tree: ET.TreeBuilder, method: dbus_objects.types.DBusMethod) -> None:
    in_sig, out_sig = dbus_objects.util.get_dbus_signature(method, skip_first_argument=True)
    in_names, out_names = dbus_objects.util.get_dbus_method_parameter_names(method)

    tree.start('method', {'name': method.dbus_method_name})

    _append_method_args(tree, 'in', in_sig, in_names)
    _append_method_args(tree, 'out', out_sig, out_names)

    tree.end('method')
