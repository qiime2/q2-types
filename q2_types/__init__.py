# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

importlib.import_module('q2_types.per_sample_sequences')
importlib.import_module('q2_types.feature_map')
importlib.import_module('q2_types.feature_table')
importlib.import_module('q2_types.tree')
importlib.import_module('q2_types.ordination')
importlib.import_module('q2_types.sample_data')
importlib.import_module('q2_types.metadata')
importlib.import_module('q2_types.multiplexed_sequences')
importlib.import_module('q2_types.kraken2')
importlib.import_module('q2_types.feature_data_mag')
importlib.import_module('q2_types.genome_data')
importlib.import_module('q2_types.kaiju')
importlib.import_module('q2_types.reference_db')
importlib.import_module('q2_types.profile_hmms')
