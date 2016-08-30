# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json

import biom
import pandas as pd
import qiime
from qiime.plugin import SemanticType, TextFileFormat
import qiime.plugin.resource as resource


from .plugin_setup import plugin


FeatureTable = SemanticType('FeatureTable', field_names='content')

Frequency = SemanticType('Frequency', variant_of=FeatureTable.field['content'])

RelativeFrequency = SemanticType('RelativeFrequency',
                                 variant_of=FeatureTable.field['content'])

PresenceAbsence = SemanticType('PresenceAbsence',
                               variant_of=FeatureTable.field['content'])


# Formats
# TODO: double check that this is text version of biom
class BIOMV1Format(TextFileFormat):
    # TODO: revisit sniffer/validation
    pass


class FeatureTableDirectoryFormat(resource.DirectoryFormat):
    feature_table = resource.File('feature-table.biom', format=BIOMV1Format)


# Transformations
@plugin.register_transformer
def _1(data: biom.Table) -> FeatureTableDirectoryFormat:
    df = FeatureTableDirectoryFormat()
    df.feature_table.set(data, biom.Table)
    return df


@plugin.register_transformer
def _2(data: biom.Table) -> BIOMV1Format:
    ff = BIOMV1Format()
    with ff.open() as fh:
        fh.write(data.to_json(generated_by='qiime %s' % qiime.__version__))
    return ff


@plugin.register_transformer
def _3(df: FeatureTableDirectoryFormat) -> biom.Table:
    return df.feature_table.view(biom.Table)


@plugin.register_transformer
def _4(ff: BIOMV1Format) -> biom.Table:
    with ff.open() as fh:
        return biom.Table.from_json(json.loads(fh))


# Note: this is an old TODO and should be revisited with the new view system.
# TODO: this always returns a pd.DataFrame of floats due to how biom loads
# tables, and we don't know what the dtype of the DataFrame should be. It would
# be nice to have support for a semantic-type override that specifies further
# transformations (e.g. converting from floats to ints or bools as
# appropriate).
@plugin.register_transformer
def _5(df: FeatureTableDirectoryFormat) -> pd.DataFrame:
    return df.feature_table.view(pd.DataFrame)


@plugin.register_transformer
def _6(ff: BIOMV1Format) -> pd.DataFrame:
    with ff.open() as fh:
        table = biom.Table.from_json(json.load(fh))
        array = table.matrix_data.toarray().T
        sample_ids = table.ids(axis='sample')
        feature_ids = table.ids(axis='observation')
        return pd.DataFrame(array, index=sample_ids, columns=feature_ids)


# Registrations
plugin.register_semantic_type(FeatureTable)
plugin.register_semantic_type(Frequency)
plugin.register_semantic_type(RelativeFrequency)
plugin.register_semantic_type(PresenceAbsence)

# TODO: revisit this
plugin.register_semantic_type_to_format(
    FeatureTable[Frequency | RelativeFrequency | PresenceAbsence],
    artifact_format=FeatureTableDirectoryFormat
)
