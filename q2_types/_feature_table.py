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
import qiime
from qiime.plugin import SemanticType

from .plugin_setup import plugin


FeatureTable = SemanticType('FeatureTable', field_names='content')

Frequency = SemanticType('Frequency', variant_of=FeatureTable.field['content'])

RelativeFrequency = SemanticType('RelativeFrequency',
                                 variant_of=FeatureTable.field['content'])

PresenceAbsence = SemanticType('PresenceAbsence',
                               variant_of=FeatureTable.field['content'])


def validator(data_dir):
    raise NotImplementedError()


def feature_table_to_biom_table(data_dir):
    with open(os.path.join(data_dir, 'feature-table.biom'), 'r') as fh:
        return biom.Table.from_json(json.load(fh))


def biom_table_to_feature_table(view, data_dir):
    with open(os.path.join(data_dir, 'feature-table.biom'), 'w') as fh:
        fh.write(view.to_json(generated_by='qiime %s' % qiime.__version__))


plugin.register_archive_format('feature-table', 1, validator)

plugin.register_archive_format_reader('feature-table', 1, biom.Table,
                                      feature_table_to_biom_table)

plugin.register_archive_format_writer('feature-table', 1, biom.Table,
                                      biom_table_to_feature_table)

plugin.register_semantic_type(FeatureTable)
plugin.register_semantic_type(Frequency)
plugin.register_semantic_type(RelativeFrequency)
plugin.register_semantic_type(PresenceAbsence)

plugin.register_type_to_archive_format(
    FeatureTable[Frequency | RelativeFrequency | PresenceAbsence],
    'feature-table', 1)
