# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio
from qiime.plugin import SemanticType, TextFileFormat
import qiime.plugin.resource as resource

from .plugin_setup import plugin


PCoAResults = SemanticType('PCoAResults')


# Formats
class OrdinationFormat(TextFileFormat):
    pass


class OrdinationDirectoryFormat(resource.DirectoryFormat):
    ordination = resource.FileFormat('ordination.txt', format=OrdinationFormat)


# Transformers
@plugin.register_transformer
def _1(df: OrdinationDirectoryFormat) -> skbio.OrdinationResults:
    return df.ordination.view(skbio.OrdinationResults)


@plugin.register_transformer
def _2(ff: OrdinationFormat) -> skbio.OrdinationResults:
    with ff.open() as fh:
        return skbio.OrdinationResults.read(fh, format='ordination',
                                            verify=False)


@plugin.register_transformer
def _3(data: skbio.OrdinationResults) -> OrdinationDirectoryFormat:
    df = OrdinationDirectoryFormat()
    df.ordination.set(data, PCoAResults)
    return df


@plugin.register_transformer
def _4(data: skbio.OrdinationResults) -> OrdinationFormat:
    out = OrdinationFormat()
    with out.open() as fh:
        data.write(fh, format='ordination')


# Registrations
plugin.register_semantic_type(PCoAResults)
plugin.register_semantic_type_to_format(
    PCoAResults,
    artifact_format=OrdinationDirectoryFormat
)
