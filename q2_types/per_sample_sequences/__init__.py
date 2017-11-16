# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
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
                      QIIME1DemuxFormat, QIIME1DemuxDirFmt)
from ._type import (Sequences, SequencesWithQuality,
                    PairedEndSequencesWithQuality,
                    JoinedSequencesWithQuality)

__all__ = ['CasavaOneEightSingleLanePerSampleDirFmt',
           'CasavaOneEightLanelessPerSampleDirFmt',
           'FastqGzFormat', 'YamlFormat', 'FastqManifestFormat',
           'FastqAbsolutePathManifestFormat',
           'SingleLanePerSampleSingleEndFastqDirFmt',
           'SingleLanePerSamplePairedEndFastqDirFmt', 'Sequences',
           'SequencesWithQuality', 'PairedEndSequencesWithQuality',
           'JoinedSequencesWithQuality', 'SingleEndFastqManifestPhred33',
           'SingleEndFastqManifestPhred64', 'PairedEndFastqManifestPhred33',
           'PairedEndFastqManifestPhred64', 'QIIME1DemuxFormat',
           'QIIME1DemuxDirFmt']

importlib.import_module('q2_types.per_sample_sequences._transformer')
