# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import MAGtoContigsFormat, MAGtoContigsDirFmt

from ._type import FeatureMap, MAGtoContigs

__all__ = [
    "FeatureMap", "MAGtoContigs", "MAGtoContigsFormat", "MAGtoContigsDirFmt"
]

importlib.import_module("q2_types.feature_map._transformer")
