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
                      PairedEndFastqManifestPhred64)
from ._type import SequencesWithQuality, PairedEndSequencesWithQuality
from ._transformer import PerSampleDNAIterators, PerSamplePairedDNAIterators

__all__ = ['CasavaOneEightSingleLanePerSampleDirFmt',
           'CasavaOneEightLanelessPerSampleDirFmt',
           'FastqGzFormat', 'YamlFormat', 'FastqManifestFormat',
           'FastqAbsolutePathManifestFormat',
           'SingleLanePerSampleSingleEndFastqDirFmt',
           'SingleLanePerSamplePairedEndFastqDirFmt', 'SequencesWithQuality',
           'PairedEndSequencesWithQuality', 'PerSampleDNAIterators',
           'PerSamplePairedDNAIterators', 'SingleEndFastqManifestPhred33',
           'SingleEndFastqManifestPhred64', 'PairedEndFastqManifestPhred33',
           'PairedEndFastqManifestPhred64']

importlib.import_module('q2_types.per_sample_sequences._transformer')
