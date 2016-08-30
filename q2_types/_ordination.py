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
def _1(data: skbio.OrdinationResults) -> OrdinationDirectoryFormat:
    df = OrdinationDirectoryFormat()
    df.ordination.set(data, skbio.OrdinationResults)
    return df


@plugin.register_transformer
def _2(data: skbio.OrdinationResults) -> OrdinationFormat:
    ff = OrdinationFormat()
    with ff.open() as fh:
        data.write(fh, format='ordination')
    return ff


@plugin.register_transformer
def _3(df: OrdinationDirectoryFormat) -> skbio.OrdinationResults:
    return df.ordination.view(skbio.OrdinationResults)


@plugin.register_transformer
def _4(ff: OrdinationFormat) -> skbio.OrdinationResults:
    with ff.open() as fh:
        return skbio.OrdinationResults.read(fh, format='ordination',
                                            verify=False)


# Registrations
plugin.register_semantic_type(PCoAResults)
plugin.register_semantic_type_to_format(
    PCoAResults,
    artifact_format=OrdinationDirectoryFormat
)
