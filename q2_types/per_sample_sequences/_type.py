# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from ..sample_data import SampleData
from . import (QIIME1DemuxDirFmt, SingleLanePerSampleSingleEndFastqDirFmt,
               SingleLanePerSamplePairedEndFastqDirFmt, EMPSingleEndDirFmt,
               EMPPairedEndDirFmt, ErrorCorrectionDetailsDirFmt)


Sequences = SemanticType('Sequences', variant_of=SampleData.field['type'])
SequencesWithQuality = SemanticType(
    'SequencesWithQuality', variant_of=SampleData.field['type'])
PairedEndSequencesWithQuality = SemanticType(
    'PairedEndSequencesWithQuality', variant_of=SampleData.field['type'])
JoinedSequencesWithQuality = SemanticType(
    'JoinedSequencesWithQuality', variant_of=SampleData.field['type'])
RawSequences = SemanticType('RawSequences')
EMPSingleEndSequences = SemanticType('EMPSingleEndSequences')
EMPPairedEndSequences = SemanticType('EMPPairedEndSequences')
ErrorCorrectionDetails = SemanticType('ErrorCorrectionDetails')

plugin.register_semantic_types(Sequences, SequencesWithQuality,
                               PairedEndSequencesWithQuality,
                               JoinedSequencesWithQuality,
                               RawSequences, EMPSingleEndSequences,
                               EMPPairedEndSequences,
                               ErrorCorrectionDetails)

plugin.register_artifact_class(
    SampleData[Sequences],
    directory_format=QIIME1DemuxDirFmt,
    description=("Collections of sequences associated with specified samples "
                 "(i.e., demultiplexed sequences).")
)
plugin.register_artifact_class(
    SampleData[SequencesWithQuality],
    directory_format=SingleLanePerSampleSingleEndFastqDirFmt,
    description=("Collections of sequences with quality scores associated "
                 "with specified samples (i.e., demultiplexed sequences).")
)
plugin.register_artifact_class(
    SampleData[JoinedSequencesWithQuality],
    directory_format=SingleLanePerSampleSingleEndFastqDirFmt,
    description=("Collections of joined paired-end sequences with quality "
                 "scores associated with specified samples (i.e., "
                 "demultiplexed sequences).")
)
plugin.register_artifact_class(
    SampleData[PairedEndSequencesWithQuality],
    directory_format=SingleLanePerSamplePairedEndFastqDirFmt,
    description=("Collections of unjoined paired-end sequences with quality "
                 "scores associated with specified samples (i.e., "
                 "demultiplexed sequences).")
)
plugin.register_semantic_type_to_format(
    RawSequences,
    artifact_format=EMPSingleEndDirFmt
)

plugin.register_semantic_type_to_format(
    EMPSingleEndSequences,
    artifact_format=EMPSingleEndDirFmt
)

plugin.register_semantic_type_to_format(
    EMPPairedEndSequences,
    artifact_format=EMPPairedEndDirFmt
)

plugin.register_semantic_type_to_format(
    ErrorCorrectionDetails,
    artifact_format=ErrorCorrectionDetailsDirFmt
)
