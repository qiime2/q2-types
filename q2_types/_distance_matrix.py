# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path

import skbio
from qiime.plugin import SemanticType

from .plugin_setup import plugin


DistanceMatrix = SemanticType('DistanceMatrix')


def validator(data_dir):
    raise NotImplementedError()


def distance_matrix_to_skbio_distance_matrix(data_dir):
    with open(os.path.join(data_dir, 'distance-matrix.tsv'), 'r') as fh:
        return skbio.DistanceMatrix.read(fh, format='lsmat', verify=False)


def skbio_distance_matrix_to_distance_matrix(view, data_dir):
    with open(os.path.join(data_dir, 'distance-matrix.tsv'), 'w') as fh:
        view.write(fh, format='lsmat')


plugin.register_data_layout('distance-matrix', 1, validator)

plugin.register_data_layout_reader('distance-matrix', 1, skbio.DistanceMatrix,
                                   distance_matrix_to_skbio_distance_matrix)

plugin.register_data_layout_writer('distance-matrix', 1, skbio.DistanceMatrix,
                                   skbio_distance_matrix_to_distance_matrix)

plugin.register_semantic_type(DistanceMatrix)

plugin.register_type_to_data_layout(DistanceMatrix, 'distance-matrix', 1)
