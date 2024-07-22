# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

import pandas as pd

import qiime2.plugin
import qiime2.sdk

from q2_types import __version__

citations = qiime2.plugin.Citations.load('citations.bib', package='q2_types')
plugin = qiime2.plugin.Plugin(
    name='types',
    version=__version__,
    website='https://github.com/qiime2/q2-types',
    package='q2_types',
    description=('This QIIME 2 plugin defines semantic types and '
                 'transformers supporting microbiome analysis.'),
    short_description='Plugin defining types for microbiome analysis.'
)

plugin.register_views(pd.Series, pd.DataFrame,
                      citations=[citations['mckinney-proc-scipy-2010']])

importlib.import_module('q2_types.bowtie2._deferred_setup')
