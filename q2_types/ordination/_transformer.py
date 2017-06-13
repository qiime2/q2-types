# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio
import qiime2

from ..plugin_setup import plugin
from . import OrdinationFormat


def _ordination_format_to_ordination_results(ff):
    return skbio.OrdinationResults.read(str(ff), format='ordination',
                                        verify=False)


def _ordination_format_to_dataframe(ff):
    ordination_results = _ordination_format_to_ordination_results(ff)
    df = ordination_results.samples
    df.index.name = 'Sample ID'
    df.columns = ['Axis %d' % i for i in range(1, len(df.columns) + 1)]
    return df


@plugin.register_transformer
def _1(data: skbio.OrdinationResults) -> OrdinationFormat:
    ff = OrdinationFormat()
    data.write(str(ff), format='ordination')
    return ff


@plugin.register_transformer
def _2(ff: OrdinationFormat) -> skbio.OrdinationResults:
    return _ordination_format_to_ordination_results(ff)


@plugin.register_transformer
def _3(ff: OrdinationFormat) -> qiime2.Metadata:
    df = _ordination_format_to_dataframe(ff)
    return qiime2.Metadata(df)
