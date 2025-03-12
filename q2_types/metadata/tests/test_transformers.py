# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2
from qiime2.plugin.testing import TestPluginBase
from qiime2.metadata import MetadataFileError

from q2_types.metadata import ImmutableMetadataFormat


class TestTransformers(TestPluginBase):
    package = "q2_types.metadata.tests"

    def test_metadata_format_to_metadata(self):
        filename = 'metadata.tsv'
        _, obs = self.transform_format(ImmutableMetadataFormat,
                                       qiime2.Metadata,
                                       filename)
        exp_md = qiime2.Metadata.load(self.get_data_path(filename))
        self.assertEqual(obs, exp_md)

    def test_non_metadata(self):
        with self.assertRaisesRegex(MetadataFileError,
                                    "column name 'bad-id-label'"):
            transformer = self.get_transformer(
                ImmutableMetadataFormat, qiime2.Metadata)
            input = self.get_data_path('invalid-metadata-1.tsv')
            transformer(input)

    def test_metadata_to_metadata_format(self):
        filename = 'metadata.tsv'
        transformer = self.get_transformer(qiime2.Metadata,
                                           ImmutableMetadataFormat)

        # round-trip the file by loading as qiime2.Metadata, transforming to
        # the file format, and then loading the result as qiime2.Metadata
        md = qiime2.Metadata.load(self.get_data_path(filename))
        obs = transformer(md)
        obs_md = qiime2.Metadata.load(obs.path)

        exp_md = qiime2.Metadata.load(self.get_data_path(filename))
        self.assertEqual(obs_md, exp_md)
