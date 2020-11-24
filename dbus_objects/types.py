# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
import typing


if sys.version_info < (3, 8):
    import typing_extensions
    typing.Literal = typing_extensions.Literal
    typing.Protocol = typing_extensions.Protocol


Byte = typing.TypeVar('Byte', int, int)
UInt16 = typing.TypeVar('UInt16', int, int)
UInt32 = typing.TypeVar('UInt32', int, int)
UInt64 = typing.TypeVar('UInt64', int, int)
Int16 = typing.TypeVar('Int16', int, int)
Int32 = typing.TypeVar('Int32', int, int)
Int64 = typing.TypeVar('Int64', int, int)
Signature = typing.TypeVar('Signature', str, bytes)

_Variant = typing.Tuple[str, typing.Any]
Variant = typing.TypeVar('Variant', _Variant, _Variant)

MultipleReturn = typing.Tuple  # type: ignore
