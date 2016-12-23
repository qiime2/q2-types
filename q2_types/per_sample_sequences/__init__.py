# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import (CasavaOneEightSingleLanePerSampleDirFmt, FastqGzFormat,
                      YamlFormat, FastqManifestFormat,
                      SingleLanePerSampleSingleEndFastqDirFmt,
                      SingleLanePerSamplePairedEndFastqDirFmt)
from ._type import SequencesWithQuality, PairedEndSequencesWithQuality
from ._transformer import PerSampleDNAIterators, PerSamplePairedDNAIterators

__all__ = ['CasavaOneEightSingleLanePerSampleDirFmt', 'FastqGzFormat',
           'YamlFormat', 'FastqManifestFormat',
           'SingleLanePerSampleSingleEndFastqDirFmt',
           'SingleLanePerSamplePairedEndFastqDirFmt', 'SequencesWithQuality',
           'PairedEndSequencesWithQuality', 'PerSampleDNAIterators',
           'PerSamplePairedDNAIterators']

importlib.import_module('q2_types.per_sample_sequences._transformer')
