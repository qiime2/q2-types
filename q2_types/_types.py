# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json

import biom
import skbio
import pandas as pd
from qiime.plugin import Type
from qiime import __version__


class DistanceMatrix(Type, variant_of=(Type.Artifact, Type.Metadata)):
    def load(self, data_reader):
        fh = data_reader.get_file('distance-matrix.tsv')
        return skbio.DistanceMatrix.read(fh)

    def save(self, data, data_writer):
        fh = data_writer.create_file('distance-matrix.tsv')
        data.write(fh)

    def get_columns(self, data):
        columns = data.ids
        # TODO implement controlled vocabulary for column types
        return pd.Series([None] * len(columns), index=columns)

    def get_values(self, data, column):
        return pd.Series(data[column], index=data.ids)


class PCoAResults(Type, variant_of=(Type.Artifact, Type.Metadata)):
    def load(self, data_reader):
        fh = data_reader.get_file('pcoa-results.txt')
        return skbio.OrdinationResults.read(fh)

    def save(self, data, data_writer):
        fh = data_writer.create_file('pcoa-results.txt')
        data.write(fh)

    def get_columns(self, data):
        columns = ['PC%d' % i for i in range(1, len(data.samples.columns) + 1)]
        # TODO implement controlled vocabulary for column types
        return pd.Series([None] * len(columns), index=columns)

    def get_values(self, data, column):
        column_idx = int(column.split('PC')[1]) - 1
        return pd.Series(data.samples.columns.iloc[column_idx],
                         index=data.samples.index)


class Phylogeny(Type, variant_of=Type.Artifact):
    def load(self, data_reader):
        fh = data_reader.get_file('phylogeny.nwk')
        return skbio.TreeNode.read(fh)

    def save(self, data, data_writer):
        fh = data_writer.create_file('phylogeny.nwk')
        data.write(fh)


class FeatureTable(Type, variant_of=(Type.Artifact, Type.Metadata),
                   fields='Content'):
    class Content:
        pass

    def load(self, data_reader):
        fh = data_reader.get_file('feature-table.biom')
        return biom.Table.from_json(json.load(fh))

    def save(self, data, data_writer):
        fh = data_writer.create_file('feature-table.biom')
        fh.write(data.to_json(generated_by='qiime %s' % __version__))

    def get_columns(self, data):
        columns = data.ids(axis='observation')
        return pd.Series([None] * len(columns), index=columns)

    def get_values(self, data, column):
        return pd.Series(data.data(column, axis='observation'),
                         index=data.ids(axis='sample'))


class Frequency(Type, variant_of=FeatureTable.Content):
    pass


class RelativeFrequency(Type, variant_of=FeatureTable.Content):
    pass


class PresenceAbsence(Type, variant_of=FeatureTable.Content):
    pass
