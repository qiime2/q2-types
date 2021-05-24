# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

# feature_data needs to be imported before feature_table to avoid circular
# import.
importlib.import_module('q2_types.feature_data')
importlib.import_module('q2_types.feature_table')
importlib.import_module('q2_types.distance_matrix')
importlib.import_module('q2_types.tree')
importlib.import_module('q2_types.ordination')
importlib.import_module('q2_types.sample_data')
importlib.import_module('q2_types.per_sample_sequences')
importlib.import_module('q2_types.bowtie2')
