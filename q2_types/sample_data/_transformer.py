# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd

from ..plugin_setup import plugin
from . import AlphaDiversityFormat


@plugin.register_transformer
def _1(data: pd.Series) -> AlphaDiversityFormat:
    ff = AlphaDiversityFormat()
    with ff.open() as fh:
        data.to_csv(fh, sep='\t', header=True)
    return ff


@plugin.register_transformer
def _2(ff: AlphaDiversityFormat) -> pd.Series:
    with ff.open() as fh:
        # Using `dtype=object` and `set_index` to avoid type casting/inference
        # of any columns or the index.
        df = pd.read_csv(fh, sep='\t', header=0, dtype=object)
        df.set_index(df.columns[0], drop=True, append=False, inplace=True)
        df.index.name = None
        return pd.to_numeric(df.iloc[:, 0])
