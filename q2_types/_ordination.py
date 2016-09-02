# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio
from qiime.plugin import SemanticType
import qiime.plugin.resource as model

from .plugin_setup import plugin


PCoAResults = SemanticType('PCoAResults')


# Formats
class OrdinationFormat(model.TextFileFormat):
    def sniff(self):
        sniffer = skbio.io.io_registry.get_sniffer('ordination')
        return sniffer(str(self))[0]


OrdinationDirectoryFormat = model.SingleFileDirectoryFormat(
    'OrdinationDirectoryFormat', 'ordination.txt', OrdinationFormat)


# Transformers
@plugin.register_transformer
def _1(data: skbio.OrdinationResults) -> OrdinationFormat:
    ff = OrdinationFormat()
    data.write(str(ff), format='ordination')
    return ff


@plugin.register_transformer
def _2(ff: OrdinationFormat) -> skbio.OrdinationResults:
    return skbio.OrdinationResults.read(str(ff), format='ordination',
                                        verify=False)


# Registrations
plugin.register_semantic_type(PCoAResults)
plugin.register_semantic_type_to_format(
    PCoAResults,
    artifact_format=OrdinationDirectoryFormat
)
