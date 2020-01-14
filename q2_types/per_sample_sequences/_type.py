# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from ..sample_data import SampleData
from . import (QIIME1DemuxDirFmt, SingleLanePerSampleSingleEndFastqDirFmt,
               SingleLanePerSamplePairedEndFastqDirFmt)


Sequences = SemanticType('Sequences', variant_of=SampleData.field['type'])
SequencesWithQuality = SemanticType(
    'SequencesWithQuality', variant_of=SampleData.field['type'])
PairedEndSequencesWithQuality = SemanticType(
    'PairedEndSequencesWithQuality', variant_of=SampleData.field['type'])
JoinedSequencesWithQuality = SemanticType(
    'JoinedSequencesWithQuality', variant_of=SampleData.field['type'])

plugin.register_semantic_types(Sequences, SequencesWithQuality,
                               PairedEndSequencesWithQuality,
                               JoinedSequencesWithQuality)

plugin.register_semantic_type_to_format(
    SampleData[Sequences],
    artifact_format=QIIME1DemuxDirFmt
)
plugin.register_semantic_type_to_format(
    SampleData[SequencesWithQuality],
    artifact_format=SingleLanePerSampleSingleEndFastqDirFmt
)
plugin.register_semantic_type_to_format(
    SampleData[JoinedSequencesWithQuality],
    artifact_format=SingleLanePerSampleSingleEndFastqDirFmt
)
plugin.register_semantic_type_to_format(
    SampleData[PairedEndSequencesWithQuality],
    artifact_format=SingleLanePerSamplePairedEndFastqDirFmt
)
