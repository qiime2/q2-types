# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._formats import (
    MAGtoContigsFormat, MAGtoContigsDirFmt, FeatureMapFormat,
    FeatureMapDirFmt
)

from ._types import (
    FeatureMap, MAGtoContigs, TaxonomyToContigs, FunctionToContigs
)
from ._methods import collate_contig_maps

__all__ = [
    "FeatureMap", "MAGtoContigs", "MAGtoContigsFormat", "MAGtoContigsDirFmt",
    "TaxonomyToContigs", "FeatureMapFormat",
    "FeatureMapDirFmt", "FunctionToContigs", "collate_contig_maps"
]
