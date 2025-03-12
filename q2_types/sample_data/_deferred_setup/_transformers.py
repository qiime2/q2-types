# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import numpy as np

import qiime2

from .. import AlphaDiversityFormat

from ...plugin_setup import plugin


def _read_alpha_diversity(fh):
    # Using `dtype=object` and `set_index` to avoid type casting/inference
    # of any columns or the index.
    df = pd.read_csv(fh, sep='\t', header=0, dtype=object)
    df.set_index(df.columns[0], drop=True, append=False, inplace=True)
    df.index.name = None
    # casting of columns adapted from SO post:
    # https://stackoverflow.com/a/36814203/3424666
    cols = df.columns
    df[cols] = df[cols].apply(pd.to_numeric, errors='ignore')
    return df


@plugin.register_transformer
def _1(data: pd.Series) -> AlphaDiversityFormat:
    ff = AlphaDiversityFormat()
    with ff.open() as fh:
        data.to_csv(fh, sep='\t', header=True)
    return ff


@plugin.register_transformer
def _2(ff: AlphaDiversityFormat) -> pd.Series:
    with ff.open() as fh:
        df = _read_alpha_diversity(fh)
        series = df.iloc[:, 0]
        if not np.issubdtype(series, np.number):
            raise ValueError('Non-numeric values detected in alpha diversity '
                             'estimates.')
        return series


@plugin.register_transformer
def _3(ff: AlphaDiversityFormat) -> qiime2.Metadata:
    with ff.open() as fh:
        df = _read_alpha_diversity(fh)
        df.index.name = 'Sample ID'
        return qiime2.Metadata(df)
