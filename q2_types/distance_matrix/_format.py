# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio.io
import qiime.plugin.model as model

from ..plugin_setup import plugin


class LSMatFormat(model.TextFileFormat):
    def sniff(self):
        sniffer = skbio.io.io_registry.get_sniffer('lsmat')
        return sniffer(str(self))[0]


DistanceMatrixDirectoryFormat = model.SingleFileDirectoryFormat(
    'DistanceMatrixDirectoryFormat', 'distance-matrix.tsv', LSMatFormat)


plugin.register_formats(LSMatFormat, DistanceMatrixDirectoryFormat)
