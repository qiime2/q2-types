# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime.plugin import SemanticType

from ..plugin_setup import plugin
from ..sample_data import SampleData
from . import (SingleLanePerSampleSingleEndFastqDirFmt,
               SingleLanePerSamplePairedEndFastqDirFmt)


SequencesWithQuality = SemanticType(
    'SequencesWithQuality', variant_of=SampleData.field['type'])
PairedEndSequencesWithQuality = SemanticType(
    'PairedEndSequencesWithQuality', variant_of=SampleData.field['type'])

plugin.register_semantic_types(SequencesWithQuality,
                               PairedEndSequencesWithQuality)

plugin.register_semantic_type_to_format(
    SampleData[SequencesWithQuality],
    artifact_format=SingleLanePerSampleSingleEndFastqDirFmt
)
plugin.register_semantic_type_to_format(
    SampleData[PairedEndSequencesWithQuality],
    artifact_format=SingleLanePerSamplePairedEndFastqDirFmt
)
