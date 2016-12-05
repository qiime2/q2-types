# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

from q2_types.per_sample_sequences import (
    PerSampleDNAIterators, PerSamplePairedDNAIterators,
    SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt,
    CasavaOneEightSingleLanePerSampleDirFmt
)
from qiime.plugin.testing import TestPluginBase


class TestTransformers(TestPluginBase):
    package = "q2_types.per_sample_sequences.tests"

    def test_slpssefdf_to_per_sample_dna_iterators(self):
        filenames = ('single_end_data/MANIFEST', 'metadata.yml',
                     'single_end_data/Human-Kneecap_S1_L001_R1_001.fastq.gz')
        input, obs = self.transform_format(
            SingleLanePerSampleSingleEndFastqDirFmt, PerSampleDNAIterators,
            filenames=filenames
        )

    def test_slpspefdf_to_per_sample_paired_dna_iterators(self):
        filenames = ('paired_end_data/MANIFEST', 'metadata.yml',
                     'paired_end_data/Human-Kneecap_S1_L001_R1_001.fastq.gz',
                     'paired_end_data/Human-Kneecap_S1_L001_R2_001.fastq.gz')
        input, obs = self.transform_format(
            SingleLanePerSamplePairedEndFastqDirFmt,
            PerSamplePairedDNAIterators, filenames=filenames
        )

    def test_casava_one_eight_single_lane_per_sample_dirfmt_to_slpssefdf(self):
        filenames = ('single_end_data/Human-Kneecap_S1_L001_R1_001.fastq.gz',)
        input, obs = self.transform_format(
            CasavaOneEightSingleLanePerSampleDirFmt,
            SingleLanePerSampleSingleEndFastqDirFmt, filenames=filenames
        )

    def test_casava_one_eight_single_lane_per_sample_dirfmt_to_slpspefdf(self):
        filenames = ('single_end_data/Human-Kneecap_S1_L001_R1_001.fastq.gz',)
        input, obs = self.transform_format(
            CasavaOneEightSingleLanePerSampleDirFmt,
            SingleLanePerSamplePairedEndFastqDirFmt, filenames=filenames
        )


if __name__ == '__main__':
    unittest.main()
