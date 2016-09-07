# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio
import skbio.io
from qiime.plugin import SemanticType
import qiime.plugin.model as model

from .plugin_setup import plugin


__all__ = [
    # Types
    'DistanceMatrix',
    # Formats
    'LSMatFormat',
    'DistanceMatrixDirectoryFormat'
]


DistanceMatrix = SemanticType('DistanceMatrix')


# Formats
class LSMatFormat(model.TextFileFormat):
    def sniff(self):
        sniffer = skbio.io.io_registry.get_sniffer('lsmat')
        return sniffer(str(self))[0]


DistanceMatrixDirectoryFormat = model.SingleFileDirectoryFormat(
    'DistanceMatrixDirectoryFormat', 'distance-matrix.tsv', LSMatFormat)


# Transformers
@plugin.register_transformer
def _1(data: skbio.DistanceMatrix) -> LSMatFormat:
    ff = LSMatFormat()
    with ff.open() as fh:
        data.write(fh, format='lsmat')
    return ff


@plugin.register_transformer
def _2(ff: LSMatFormat) -> skbio.DistanceMatrix:
    return skbio.DistanceMatrix.read(str(ff), format='lsmat', verify=False)


# Registrations
plugin.register_semantic_type(DistanceMatrix)
plugin.register_semantic_type_to_format(
    DistanceMatrix,
    artifact_format=DistanceMatrixDirectoryFormat
)
