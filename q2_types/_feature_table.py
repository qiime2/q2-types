# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json
import os.path

import biom
import ijson
import pandas as pd
import qiime
from qiime.plugin import SemanticType, FileFormat, DataLayout

from .plugin_setup import plugin


FeatureTable = SemanticType('FeatureTable', field_names='content')

Frequency = SemanticType('Frequency', variant_of=FeatureTable.field['content'])

RelativeFrequency = SemanticType('RelativeFrequency',
                                 variant_of=FeatureTable.field['content'])

PresenceAbsence = SemanticType('PresenceAbsence',
                               variant_of=FeatureTable.field['content'])


class BIOMV1Format(FileFormat):
    name = 'biom-v1.0'
    top_level_keys = {
        'id', 'format', 'format_url', 'type', 'generated_by',
        'date', 'rows', 'columns', 'matrix_type', 'matrix_element_type',
        'shape', 'data', 'comment'
    }

    @classmethod
    def sniff(cls, filepath):
        with open(filepath, 'r') as fh:
            try:
                parser = ijson.parse(fh)
                for prefix, event, value in parser:
                    if (prefix, event) == ('', 'map_key'):
                        # `format_url` seems pretty unique to BIOM 1.0.
                        if value == 'format_url':
                            return True
                        elif value not in cls.top_level_keys:
                            return False
            except ijson.JSONError:
                pass
            return False

feature_table_data_layout = DataLayout('feature-table', 1)
feature_table_data_layout.register_file('feature-table.biom', BIOMV1Format)


def feature_table_to_biom_table(data_dir):
    with open(os.path.join(data_dir, 'feature-table.biom'), 'r') as fh:
        return biom.Table.from_json(json.load(fh))


def biom_table_to_feature_table(view, data_dir):
    with open(os.path.join(data_dir, 'feature-table.biom'), 'w') as fh:
        fh.write(view.to_json(generated_by='qiime %s' % qiime.__version__))


# TODO this always returns a pd.DataFrame of floats due to how biom loads
# tables, and we don't know what the dtype of the DataFrame should be. It would
# be nice to have support for a semantic-type override that specifies further
# transformations (e.g. converting from floats to ints or bools as
# appropriate).
def feature_table_to_pandas_dataframe(data_dir):
    with open(os.path.join(data_dir, 'feature-table.biom'), 'r') as fh:
        table = biom.Table.from_json(json.load(fh))
        array = table.matrix_data.toarray().T
        sample_ids = table.ids(axis='sample')
        feature_ids = table.ids(axis='observation')
        return pd.DataFrame(array, index=sample_ids, columns=feature_ids)


plugin.register_data_layout(feature_table_data_layout)

plugin.register_data_layout_reader('feature-table', 1, biom.Table,
                                   feature_table_to_biom_table)

plugin.register_data_layout_writer('feature-table', 1, biom.Table,
                                   biom_table_to_feature_table)

plugin.register_data_layout_reader('feature-table', 1, pd.DataFrame,
                                   feature_table_to_pandas_dataframe)

plugin.register_semantic_type(FeatureTable)
plugin.register_semantic_type(Frequency)
plugin.register_semantic_type(RelativeFrequency)
plugin.register_semantic_type(PresenceAbsence)

plugin.register_type_to_data_layout(
    FeatureTable[Frequency | RelativeFrequency | PresenceAbsence],
    'feature-table', 1)
