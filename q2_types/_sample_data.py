# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
from qiime.plugin import SemanticType, TextFileFormat
import qiime.plugin.resource as resource

from .plugin_setup import plugin


SampleData = SemanticType('SampleData', field_names='type')

AlphaDiversity = SemanticType('AlphaDiversity',
                              variant_of=SampleData.field['type'])


# Formats
class AlphaDiversityFormat(TextFileFormat):
    # TODO: revisit sniffer/validation
    pass


class AlphaDiversityDirectoryFormat(resource.DirectoryFormat):
    alpha_div = resource.File('alpha-diversity.tsv',
                              format=AlphaDiversityFormat)


# Transformers
@plugin.register_transformer
def _1(data: pd.Series) -> AlphaDiversityDirectoryFormat:
    df = AlphaDiversityDirectoryFormat()
    df.alpha_div.set(data, pd.Series)
    return df


@plugin.register_transformer
def _2(data: pd.Series) -> AlphaDiversityFormat:
    ff = AlphaDiversityFormat()
    with ff.open() as fh:
        data.to_csv(fh, sep='\t', header=True)
    return ff


@plugin.register_transformer
def _3(df: AlphaDiversityDirectoryFormat) -> pd.Series:
    return df.alpha_div.view(pd.Series)


@plugin.register_transformer
def _4(ff: AlphaDiversityFormat) -> pd.Series:
    with ff.open() as fh:
        # Since we're wanting to round-trip with pd.Series.to_csv, the pandas
        # docs recommend using from_csv here (rather than the more commonly
        # used pd.read_csv).
        return pd.Series.from_csv(fh, sep='\t', header=0)


# Registrations
plugin.register_semantic_type(SampleData)
plugin.register_semantic_type(AlphaDiversity)

plugin.register_semantic_type_to_format(
    AlphaDiversity,
    artifact_format=AlphaDiversityDirectoryFormat
)
# TODO: revisit this
plugin.register_semantic_type_to_format(
    SampleData[AlphaDiversity],
    artifact_format=AlphaDiversityDirectoryFormat
)
