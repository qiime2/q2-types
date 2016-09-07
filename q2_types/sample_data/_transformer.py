# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
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
        # Since we're wanting to round-trip with pd.Series.to_csv, the pandas
        # docs recommend using from_csv here (rather than the more commonly
        # used pd.read_csv).
        return pd.Series.from_csv(fh, sep='\t', header=0)
