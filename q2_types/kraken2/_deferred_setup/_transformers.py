# ----------------------------------------------------------------------------
# Copyright (c) 2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd

from .. import Kraken2ReportFormat, Kraken2OutputFormat, Kraken2DBReportFormat

from ...plugin_setup import plugin


@plugin.register_transformer
def _1(ff: Kraken2ReportFormat) -> pd.DataFrame:
    df, cols = ff._to_dataframe()
    df.columns = cols.keys()
    return df


@plugin.register_transformer
def _2(ff: Kraken2OutputFormat) -> pd.DataFrame:
    df, cols = ff._to_dataframe()
    df.columns = cols
    return df


@plugin.register_transformer
def _3(ff: Kraken2DBReportFormat) -> pd.DataFrame:
    df, cols = ff._to_dataframe()
    df.columns = cols.keys()
    return df
