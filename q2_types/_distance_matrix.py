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


DistanceMatrix = SemanticType('DistanceMatrix')


# Formats
class LSMatFormat(TextFileFormat):
    # TODO: revisit sniffer/validation
    pass


class DistanceMatrixDirectoryFormat(resource.DirectoryFormat):
    distance_matrix = resource.File('distance-matrix.tsv', format=LSMatFormat)


# Transformers
@plugin.register_transformer
def _1(data: skbio.DistanceMatrix) -> DistanceMatrixDirectoryFormat:
    df = DistanceMatrixDirectoryFormat()
    df.distance_matrix.set(data, skbio.DistanceMatrix)
    return df


@plugin.register_transformer
def _2(data: skbio.DistanceMatrix) -> LSMatFormat:
    ff = LSMatFormat()
    with ff.open() as fh:
        data.write(fh, format='lsmat')
    return ff


@plugin.register_transformer
def _3(df: DistanceMatrixDirectoryFormat) -> skbio.DistanceMatrix:
    return df.distance_matrix.view(skbio.DistanceMatrix)


@plugin.register_transformer
def _4(ff: LSMatFormat) -> skbio.DistanceMatrix:
    with ff.open() as fh:
        return skbio.DistanceMatrix(fh, format='lsmat', verify=False)


# Registrations
plugin.register_semantic_type(DistanceMatrix)
plugin.register_semantic_type_to_format(
    DistanceMatrix,
    artifact_format=DistanceMatrixDirectoryFormat
)
