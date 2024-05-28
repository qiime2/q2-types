# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import (
        MAGSequencesDirFmt,
        OrthologAnnotationDirFmt,
        OrthologFileFmt
        )
from ._methods import partition_feature_data_mags, collate_feature_data_mags, \
        collate_ortholog_annotations

from ._type import MAG, NOG, OG, KEGG, Contig
from ._transformer import MAGIterator

__all__ = [
        'MAG', 'MAGSequencesDirFmt', 'MAGIterator', 'NOG', 'OG', 'KEGG',
        'OrthologAnnotationDirFmt', 'OrthologFileFmt', 'Contig',
        'partition_feature_data_mags', 'collate_feature_data_mags',
        'collate_ortholog_annotations',
        ]

importlib.import_module('q2_types.feature_data_mag._format')
importlib.import_module('q2_types.feature_data_mag._transformer')
importlib.import_module('q2_types.feature_data_mag._type')
