# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from q2_types.feature_data import FeatureData
from q2_types.per_sample_sequences import ContigSequencesDirFmt
from q2_types.bowtie2 import Bowtie2IndexDirFmt
from q2_types.per_sample_sequences import SingleBowtie2Index

from .. import MAGSequencesDirFmt, MAG, Contig

from ...plugin_setup import plugin

plugin.register_semantic_types(MAG)
plugin.register_semantic_type_to_format(
    FeatureData[MAG],
    artifact_format=MAGSequencesDirFmt
)

plugin.register_semantic_types(Contig)
plugin.register_semantic_type_to_format(
    FeatureData[Contig],
    artifact_format=ContigSequencesDirFmt
)

plugin.register_semantic_type_to_format(
    FeatureData[SingleBowtie2Index],
    artifact_format=Bowtie2IndexDirFmt
)
plugin.register_formats(MAGSequencesDirFmt)

importlib.import_module('._transformers', __name__)
