# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import qiime2

from .. import ImmutableMetadataFormat

from ...plugin_setup import plugin


@plugin.register_transformer
def _1(ff: ImmutableMetadataFormat) -> qiime2.Metadata:
    return qiime2.Metadata.load(str(ff))


@plugin.register_transformer
def _2(md: qiime2.Metadata) -> ImmutableMetadataFormat:
    ff = ImmutableMetadataFormat()
    md.save(str(ff.path))
    return ff
