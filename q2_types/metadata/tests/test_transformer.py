# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2
from q2_types.metadata import ImmutableMetadataFormat
from qiime2.plugin.testing import TestPluginBase
from qiime2.metadata import MetadataFileError


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
        filename = 'invalid-metadata-1.tsv'
        with self.assertRaisesRegex(MetadataFileError,
                                    "column name 'bad-id-label'"):
            self.transform_format(ImmutableMetadataFormat, qiime2.Metadata,
                                  filename)
