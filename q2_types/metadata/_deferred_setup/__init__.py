# ----------------------------------------------------------------------------
# Copyright (c) 2016-2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib
import pandas as pd
import os
from tempfile import TemporaryDirectory

from .. import (ImmutableMetadataFormat, ImmutableMetadataDirectoryFormat,
                ImmutableMetadata)

from ...plugin_setup import plugin

plugin.register_formats(ImmutableMetadataFormat,
                        ImmutableMetadataDirectoryFormat)

plugin.register_semantic_types(ImmutableMetadata)


def metadata_usage(use):
    with TemporaryDirectory() as tempdir:
        def factory():
            df = pd.DataFrame(
                {'sample-id': ['ghnfu', 'hrhfh'], 'number': [1, 5]}
            )
            df = df.set_index('sample-id')
            df_fp = os.path.join(tempdir, 'metadata.tsv')
            df.to_csv(df_fp, sep='\t')

            md = ImmutableMetadataDirectoryFormat(tempdir, 'r')
            return md

        to_import = use.init_format('my_metadata', factory, ext='.tsv')
        use.import_from_format(
            'metadata',
            semantic_type='ImmutableMetadata',
            variable=to_import,
            view_type='ImmutableMetadataDirectoryFormat'
        )


plugin.register_artifact_class(
    ImmutableMetadata,
    directory_format=ImmutableMetadataDirectoryFormat,
    description=("Immutable sample or feature metadata."),
    examples={'Import immutable metadata': metadata_usage}
)

importlib.import_module('._transformers', __name__)
