# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import (CasavaOneEightSingleLanePerSampleDirFmt,
                      CasavaOneEightLanelessPerSampleDirFmt,
                      FastqGzFormat, YamlFormat,
                      FastqManifestFormat, FastqAbsolutePathManifestFormat,
                      SingleLanePerSampleSingleEndFastqDirFmt,
                      SingleLanePerSamplePairedEndFastqDirFmt,
                      SingleEndFastqManifestPhred33,
                      SingleEndFastqManifestPhred64,
                      PairedEndFastqManifestPhred33,
                      PairedEndFastqManifestPhred64,
                      SingleEndFastqManifestPhred33V2,
                      SingleEndFastqManifestPhred64V2,
                      PairedEndFastqManifestPhred33V2,
                      PairedEndFastqManifestPhred64V2,
                      QIIME1DemuxFormat, QIIME1DemuxDirFmt,
                      SampleIdIndexedSingleEndPerSampleDirFmt,
                      EMPMultiplexedDirFmt,
                      ErrorCorrectionDetailsFmt,
                      ErrorCorrectionDetailsDirFmt,
                      EMPSingleEndDirFmt,
                      EMPSingleEndCasavaDirFmt,
                      EMPPairedEndDirFmt,
                      EMPPairedEndCasavaDirFmt)

from ._type import (Sequences, SequencesWithQuality,
                    PairedEndSequencesWithQuality,
                    JoinedSequencesWithQuality,
                    RawSequences,
                    EMPSingleEndSequences,
                    EMPPairedEndSequences,
                    ErrorCorrectionDetails)

__all__ = ['CasavaOneEightSingleLanePerSampleDirFmt',
           'CasavaOneEightLanelessPerSampleDirFmt',
           'FastqGzFormat', 'YamlFormat', 'FastqManifestFormat',
           'FastqAbsolutePathManifestFormat',
           'SingleLanePerSampleSingleEndFastqDirFmt',
           'SingleLanePerSamplePairedEndFastqDirFmt', 'Sequences',
           'SequencesWithQuality', 'PairedEndSequencesWithQuality',
           'JoinedSequencesWithQuality', 'SingleEndFastqManifestPhred33',
           'SingleEndFastqManifestPhred64', 'PairedEndFastqManifestPhred33',
           'PairedEndFastqManifestPhred64', 'SingleEndFastqManifestPhred33V2',
           'SingleEndFastqManifestPhred64V2',
           'PairedEndFastqManifestPhred33V2',
           'PairedEndFastqManifestPhred64V2', 'QIIME1DemuxFormat',
           'QIIME1DemuxDirFmt', 'SampleIdIndexedSingleEndPerSampleDirFmt',
           'RawSequences', 'EMPSingleEndSequences', 'EMPPairedEndSequences',
           'EMPMultiplexedDirFmt',
           'ErrorCorrectionDetails', 'ErrorCorrectionDetailsFmt',
           'ErrorCorrectionDetailsDirFmt', 'EMPSingleEndDirFmt',
           'EMPSingleEndCasavaDirFmt', 'EMPPairedEndDirFmt',
           'EMPPairedEndCasavaDirFmt']

importlib.import_module('q2_types.per_sample_sequences._transformer')
