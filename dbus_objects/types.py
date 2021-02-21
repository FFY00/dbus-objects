# SPDX-License-Identifier: MIT

'''
Custom Python types
'''

from __future__ import annotations

import sys
import typing


if sys.version_info < (3, 9):
    import typing_extensions as _typing
else:
    _typing = typing


# flake8/pygflakes is mad: https://github.com/PyCQA/pyflakes/issues/594
Byte = _typing.Annotated[int, 'y']  # noqa: F821
'''DBus byte'''

UInt16 = _typing.Annotated[int, 'q']  # noqa: F821
'''DBus uint16'''

UInt32 = _typing.Annotated[int, 'u']  # noqa: F821
'''DBus uint32'''

UInt64 = _typing.Annotated[int, 't']  # noqa: F821
'''DBus uint64'''

Int16 = _typing.Annotated[int, 'n']  # noqa: F821
'''DBus int16'''

Int32 = _typing.Annotated[int, 'i']  # noqa: F821
'''DBus int32'''

Int64 = _typing.Annotated[int, 'x']  # noqa: F821
'''DBus int64'''

Signature = _typing.Annotated[str, 'g']  # noqa: F821
'''DBus signature'''

Variant = _typing.Annotated[typing.Tuple[str, typing.Any], 'v']  # noqa: F821
'''DBus variant'''

MultipleReturn = typing.Tuple  # type: ignore
'''Multiple return type. Used when you want to return multiple variables in a DBus method'''
