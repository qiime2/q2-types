# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import MAGSequencesDirFmt

from ._type import MAG, Contig
from ._transformer import MAGIterator

__all__ = ['MAG', 'MAGSequencesDirFmt', 'MAGIterator', 'Contig']

importlib.import_module('q2_types.feature_data_mag._format')
importlib.import_module('q2_types.feature_data_mag._transformer')
importlib.import_module('q2_types.feature_data_mag._type')
