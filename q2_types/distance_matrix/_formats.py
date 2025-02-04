# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio.io
import qiime2.plugin.model as model


class LSMatFormat(model.TextFileFormat):
    def sniff(self):
        sniffer = skbio.io.io_registry.get_sniffer('lsmat')
        return sniffer(str(self))[0]


DistanceMatrixDirectoryFormat = model.SingleFileDirectoryFormat(
    'DistanceMatrixDirectoryFormat', 'distance-matrix.tsv', LSMatFormat)
