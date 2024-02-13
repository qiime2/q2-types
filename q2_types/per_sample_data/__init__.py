# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

from ._format import (
    MultiMAGSequencesDirFmt, MultiMAGManifestFormat,
    ContigSequencesDirFmt, MultiBowtie2IndexDirFmt,
    BAMFormat, BAMDirFmt, MultiBAMDirFmt
)
from ._type import (
    MAGs, Contigs, SingleBowtie2Index, MultiBowtie2Index
)

__all__ = [
    'MAGs', 'MultiMAGSequencesDirFmt', 'MultiMAGManifestFormat',
    'ContigSequencesDirFmt', 'Contigs', 'SingleBowtie2Index',
    'MultiBowtie2Index', 'MultiBowtie2IndexDirFmt',
    'BAMFormat', 'BAMDirFmt', 'MultiBAMDirFmt'
]

importlib.import_module('q2_types.per_sample_data._transformer')
