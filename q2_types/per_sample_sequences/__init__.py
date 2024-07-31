# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._formats import (CasavaOneEightSingleLanePerSampleDirFmt,
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
                       MultiMAGSequencesDirFmt, MultiMAGManifestFormat,
                       ContigSequencesDirFmt, MultiBowtie2IndexDirFmt,
                       BAMFormat, BAMDirFmt, MultiBAMDirFmt,
                       MultiFASTADirectoryFormat)
from ._types import (Sequences, SequencesWithQuality,
                     PairedEndSequencesWithQuality,
                     JoinedSequencesWithQuality, MAGs, Contigs,
                     SingleBowtie2Index, MultiBowtie2Index,
                     AlignmentMap, MultiAlignmentMap)

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
           'MAGs', 'MultiMAGSequencesDirFmt', 'MultiMAGManifestFormat',
           'ContigSequencesDirFmt', 'Contigs', 'SingleBowtie2Index',
           'MultiBowtie2Index', 'MultiBowtie2IndexDirFmt',
           'BAMFormat', 'BAMDirFmt', 'MultiBAMDirFmt',
           'MultiFASTADirectoryFormat', 'AlignmentMap', 'MultiAlignmentMap']
