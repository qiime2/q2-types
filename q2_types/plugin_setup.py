# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

import qiime.plugin

from q2_types import __version__

plugin = qiime.plugin.Plugin(
    name='types',
    version=__version__,
    website='https://github.com/qiime2/q2-types',
    package='q2_types'
)

importlib.import_module('q2_types._feature_table')
importlib.import_module('q2_types._distance_matrix')
importlib.import_module('q2_types._tree')
importlib.import_module('q2_types._ordination')
importlib.import_module('q2_types._sample_data')
importlib.import_module('q2_types._feature_data')
