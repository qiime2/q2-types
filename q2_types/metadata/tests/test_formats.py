# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import shutil

from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError

from q2_types.metadata import (ImmutableMetadataDirectoryFormat,
                               ImmutableMetadataFormat)


class TestFormats(TestPluginBase):
    package = "q2_types.metadata.tests"

    def test_metadata_format_validate_positive(self):
        filepath = self.get_data_path('metadata.tsv')
        format = ImmutableMetadataFormat(filepath, mode='r')

        format.validate()

    def test_metadata_dir_format_validate_positive(self):
        filepath = self.get_data_path('metadata.tsv')
        shutil.copy(filepath, self.temp_dir.name)
        format = ImmutableMetadataDirectoryFormat(self.temp_dir.name, mode='r')

        format.validate()

    def test_metadata_format_validate_negative(self):
        filepath = self.get_data_path('invalid-metadata-1.tsv')
        format = ImmutableMetadataFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    "column name 'bad-id-label'"):
            format.validate()
