# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import KaijuIndexFormat, KaijuDBDirectoryFormat
from ._type import KaijuDB

__all__ = ["KaijuIndexFormat", "KaijuDBDirectoryFormat", "KaijuDB"]

importlib.import_module('q2_types.kaiju._format')
importlib.import_module('q2_types.kaiju._type')
