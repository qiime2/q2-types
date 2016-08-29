# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path

import skbio
import skbio.io
from qiime.plugin import SemanticType, TextFileFormat
import qiime.plugin.resource as resource

from .plugin_setup import plugin


DistanceMatrix = SemanticType('DistanceMatrix')


plugin.register_semantic_type(DistanceMatrix)
plugin.register_type_to_directory_format(DistanceMatrix, 'distance-matrix')


# Formats
class LSMatFormat(TextFileFormat):
    pass


class DistanceMatrixDirectoryFormat(resource.DirectoryFormat):
    distance_matrix = resource.File('distance-matrix.tsv', format=LSMatFormat)


# Transformers
@plugin.register_transformation
def _1(dm: DistanceMatrix) -> DistanceMatrixDirectoryFormat:
    df = DistanceMatrixDirectoryFormat()
    df.distance_matrix.set(dm, DistanceMatrix)
    return df

@plugin.register_transformation
def _2(dm: DistanceMatrix) -> LSMatFormat:
    out = LSMatFormat()
    with out.open() as fh:
        dm.write(fh, format='lsmat')
    return out

@plugin.register_transformation
def _3(df: DistanceMatrixDirectoryFormat) -> LSMatFormat:
    return df.distance_matrix.view(DistanceMatrix)

@plugin.register_transformation
def _4(lsmat: LSMatFormat) -> DistanceMatrix:
    with lsmat.open() as fh:
        return skbio.DistanceMatrix(fh, format='lsmat', verify=False)
