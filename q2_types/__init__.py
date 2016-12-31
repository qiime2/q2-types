# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib
import pkg_resources

__version__ = pkg_resources.get_distribution('q2-types').version


importlib.import_module('q2_types.feature_table')
importlib.import_module('q2_types.distance_matrix')
importlib.import_module('q2_types.tree')
importlib.import_module('q2_types.ordination')
importlib.import_module('q2_types.sample_data')
importlib.import_module('q2_types.feature_data')
importlib.import_module('q2_types.per_sample_sequences')
