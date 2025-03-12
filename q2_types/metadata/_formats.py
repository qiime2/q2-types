# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2.plugin.model as model
from qiime2.plugin import ValidationError
from qiime2.metadata import MetadataFileError, Metadata


class ImmutableMetadataFormat(model.TextFileFormat):
    def _validate_(self, level):
        try:
            Metadata.load(str(self))
        except (MetadataFileError,) as e:
            raise ValidationError(str(e))


ImmutableMetadataDirectoryFormat = model.SingleFileDirectoryFormat(
    'ImmutableMetadataDirectoryFormat', 'metadata.tsv',
    ImmutableMetadataFormat)
