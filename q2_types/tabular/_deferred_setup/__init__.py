# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from .. import (NDJSONFileFormat,
                DataResourceSchemaFileFormat,
                TabularDataResourceDirFmt,
                TableJSONLFileFormat, TableJSONLDirFmt,
                StatsTable, Pairwise, Dist1D,
                Matched, Independent, Ordered, Unordered, Multi,
                NestedOrdered, NestedUnordered)

from ...plugin_setup import plugin

plugin.register_formats(NDJSONFileFormat, DataResourceSchemaFileFormat,
                        TabularDataResourceDirFmt)
plugin.register_formats(TableJSONLFileFormat, TableJSONLDirFmt)


plugin.register_semantic_types(StatsTable, Pairwise, Dist1D,
                               NestedOrdered, NestedUnordered, Matched,
                               Independent, Ordered, Unordered, Multi)

plugin.register_semantic_type_to_format(
    Dist1D[Ordered | Unordered | NestedOrdered | NestedUnordered | Multi,
           Matched | Independent] |
    StatsTable[Pairwise],
    TableJSONLDirFmt)

importlib.import_module('._transformers', __name__)
importlib.import_module('._validators', __name__)


__all__ = [
    'StatsTable', 'Pairwise', 'Dist1D', 'NestedOrdered', 'NestedUnordered',
    'Matched', 'Independent', 'Ordered', 'Unordered', 'Multi',
    'NDJSONFileFormat', 'DataResourceSchemaFileFormat',
    'TabularDataResourceDirFmt', 'TableJSONLFileFormat', 'TableJSONLDirFmt',
]
