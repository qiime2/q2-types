# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio.io
import qiime2.plugin.model as model

from ..plugin_setup import plugin


class NewickFormat(model.TextFileFormat):
    def sniff(self):
        sniffer = skbio.io.io_registry.get_sniffer('newick')
        return sniffer(str(self))[0]


NewickDirectoryFormat = model.SingleFileDirectoryFormat(
    'NewickDirectoryFormat', 'tree.nwk', NewickFormat)


plugin.register_formats(NewickFormat, NewickDirectoryFormat)
