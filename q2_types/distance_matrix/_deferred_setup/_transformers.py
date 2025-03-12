# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio
import pandas as pd

from .. import LSMatFormat

from ...plugin_setup import plugin


@plugin.register_transformer
def _1(data: skbio.DistanceMatrix) -> LSMatFormat:
    ff = LSMatFormat()
    with ff.open() as fh:
        data.write(fh, format='lsmat')
    return ff


@plugin.register_transformer
def _2(ff: LSMatFormat) -> skbio.DistanceMatrix:
    return skbio.DistanceMatrix.read(str(ff), format='lsmat', verify=False)


@plugin.register_transformer
def _3(ff: LSMatFormat) -> pd.Series:
    dm = skbio.DistanceMatrix.read(str(ff), format='lsmat', verify=False)
    series = dm.to_series()
    assert series.size != 0, ("Distance Matrix must contain more "
                              "than one sample")
    return series


@plugin.register_transformer
def _4(data: pd.Series) -> LSMatFormat:
    ids = data.index.get_level_values(0).unique().union(
         data.index.get_level_values(1).unique(), sort=False).values
    dm_df = pd.DataFrame(data=[], index=ids, columns=ids)
    for index, row in dm_df.iterrows():
        dm_df.loc[index, index] = float(0)
        for col in dm_df.columns:
            if dm_df.loc[index, col] != 0:
                try:
                    dm_df.loc[index, col] = data[index, col]
                    dm_df.loc[col, index] = data[index, col]
                except KeyError:
                    dm_df.loc[index, col] = data[col, index]
                    dm_df.loc[col, index] = data[col, index]
    dm = skbio.DistanceMatrix(dm_df, ids=dm_df.index)
    ff = LSMatFormat()
    with ff.open() as fh:
        dm.write(fh, format='lsmat')
    return ff
