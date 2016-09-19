# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import (CasavaOneEightSingleLanePerSampleDirFmt, FastqGzFormat,
                      YamlFormat, FastqManifestFormat,
                      SingleLanePerSampleSingleEndFastqDirFmt,
                      SingleLanePerSamplePairedEndFastqDirFmt,
                      QIIME1DemultiplexedFastqDirFmt,
                      QIIME1FastqManifestFormat)
from ._type import SequencesWithQuality, PairedEndSequencesWithQuality

__all__ = ['CasavaOneEightSingleLanePerSampleDirFmt', 'FastqGzFormat',
           'YamlFormat', 'FastqManifestFormat',
           'SingleLanePerSampleSingleEndFastqDirFmt',
           'SingleLanePerSamplePairedEndFastqDirFmt', 'SequencesWithQuality',
           'PairedEndSequencesWithQuality',
           'QIIME1DemultiplexedFastqDirFmt',
           'QIIME1FastqManifestFormat']

importlib.import_module('q2_types.per_sample_sequences._transformer')
