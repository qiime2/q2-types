# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os

import pandas as pd
from q2_types.feature_data import DNAFASTAFormat

from q2_types.plugin_setup import plugin

from q2_types.per_sample_data._util import _mag_manifest_helper
from q2_types.per_sample_data._format import (
    MultiMAGManifestFormat,
    MultiMAGSequencesDirFmt,
    MultiFASTADirectoryFormat
)


@plugin.register_transformer
def _1(dirfmt: MultiFASTADirectoryFormat) \
        -> MultiMAGSequencesDirFmt:
    return _mag_manifest_helper(
        dirfmt, MultiMAGSequencesDirFmt,
        MultiMAGManifestFormat, DNAFASTAFormat)


@plugin.register_transformer
def _21(ff: MultiMAGManifestFormat) -> pd.DataFrame:
    df = pd.read_csv(str(ff), header=0, comment='#')
    df.filename = df.filename.apply(
        lambda f: os.path.join(ff.path.parent, f))
    df.set_index(['sample-id', 'mag-id'], inplace=True)
    return df
