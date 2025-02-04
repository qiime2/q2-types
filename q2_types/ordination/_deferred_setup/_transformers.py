# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import skbio

import qiime2

from .. import OrdinationFormat, ProcrustesStatisticsFmt

from ...plugin_setup import plugin


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


@plugin.register_transformer
def _4(data: pd.DataFrame) -> ProcrustesStatisticsFmt:
    ff = ProcrustesStatisticsFmt()
    qiime2.Metadata(data).save(str(ff))
    return ff


@plugin.register_transformer
def _5(ff: ProcrustesStatisticsFmt) -> pd.DataFrame:
    df = qiime2.Metadata.load(str(ff)).to_dataframe()
    return df.astype({
        'true M^2 value': float,
        'p-value for true M^2 value': float,
        'number of Monte Carlo permutations': int,
    }, copy=True, errors='raise')


@plugin.register_transformer
def _6(ff: ProcrustesStatisticsFmt) -> qiime2.Metadata:
    return qiime2.Metadata.load(str(ff))
