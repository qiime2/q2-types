# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio

from .. import NewickFormat

from ...plugin_setup import plugin


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
