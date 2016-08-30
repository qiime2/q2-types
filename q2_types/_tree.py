# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path

import skbio
from qiime.plugin import SemanticType, TextFileFormat
import qiime.plugin.resource as resource

from .plugin_setup import plugin


Phylogeny = SemanticType('Phylogeny')


# Formats
class NewickFormat(TextFileFormat):
    # TODO: revisit sniffer/validation
    pass


class NewickDirectoryFormat(resource.DirectoryFormat):
    tree = resource.File('tree.nwk', format=NewickFormat)


# Transformers
@plugin.register_transformer
def _1(data: skbio.TreeNode) -> NewickDirectoryFormat:
    df = NewickDirectoryFormat()
    df.tree.set(data, skbio.TreeNode)
    return df


@plugin.register_transformer
def _2(data: skbio.TreeNode) -> NewickFormat:
    ff = NewickFormat()
    with ff.open() as fh:
        data.write(fh, format='newick')
    return ff


@plugin.register_transformer
def _3(df: NewickDirectoryFormat) -> skbio.TreeNode:
    return df.tree.view(skbio.TreeNode)


@plugin.register_transformer
def _4(ff: NewickFormat) -> skbio.TreeNode:
    with ff.open() as fh:
        return skbio.TreeNode.read(fh, format='newick', verify=False)


# Registrations
plugin.register_semantic_type(Phylogeny)
plugin.register_semantic_type_to_format(Phylogeny,
                                        artifact_format=NewickDirectoryFormat)
