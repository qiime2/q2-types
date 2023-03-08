# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from q2_types.metadata import (ImmutableMetadataDirectoryFormat,
                               ImmutableMetadata)
from qiime2.plugin.testing import TestPluginBase


class TestTypes(TestPluginBase):
    package = "q2_types.metadata.tests"

    def test_immutable_metadata_semantic_type_registration(self):
        self.assertRegisteredSemanticType(ImmutableMetadata)

    def test_immutable_metadata_dir_fmt_registration(self):
        self.assertSemanticTypeRegisteredToFormat(
            ImmutableMetadata, ImmutableMetadataDirectoryFormat)
