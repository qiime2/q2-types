# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio
from qiime.plugin import SemanticType
import qiime.plugin.model as model

from .plugin_setup import plugin


Phylogeny = SemanticType('Phylogeny', field_names=['type'])

Rooted = SemanticType('Rooted', variant_of=Phylogeny.field['type'])

Unrooted = SemanticType('Unrooted', variant_of=Phylogeny.field['type'])


# Formats
class NewickFormat(model.TextFileFormat):
    def sniff(self):
        sniffer = skbio.io.io_registry.get_sniffer('newick')
        return sniffer(str(self))[0]


NewickDirectoryFormat = model.SingleFileDirectoryFormat(
    'NewickDirectoryFormat', 'tree.nwk', NewickFormat)


# Transformers
@plugin.register_transformer
def _1(data: skbio.TreeNode) -> NewickFormat:
    ff = NewickFormat()
    with ff.open() as fh:
        data.write(fh, format='newick')
    return ff


@plugin.register_transformer
def _2(ff: NewickFormat) -> skbio.TreeNode:
    with ff.open() as fh:
        return skbio.TreeNode.read(fh, format='newick', verify=False)


# Registrations
plugin.register_semantic_type(Phylogeny)
plugin.register_semantic_type(Rooted)
plugin.register_semantic_type(Unrooted)

plugin.register_semantic_type_to_format(Phylogeny[Rooted | Unrooted],
                                        artifact_format=NewickDirectoryFormat)
