# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import shutil
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

    def _transformer_test_helper(self, source, target, filenames):
        transformer = self.get_transformer(source, target)

        for filename in filenames:
            filepath = self.get_data_path(filename)
            shutil.copy(filepath, self.temp_dir.name)
        shutil.copy(filepath, self.temp_dir.name)
        input = source(self.temp_dir.name, mode='r')

        obs = transformer(input)

        self.assertIsInstance(obs, target)

    def test_slpssefdf_to_per_sample_dna_iterators(self):
        filenames = ('MANIFEST', 'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz')
        self._transformer_test_helper(SingleLanePerSampleSingleEndFastqDirFmt,
                                      PerSampleDNAIterators, filenames)

    def test_slpspefdf_to_per_sample_paired_dna_iterators(self):
        filenames = ('MANIFEST', 'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz')
        self._transformer_test_helper(SingleLanePerSamplePairedEndFastqDirFmt,
                                      PerSamplePairedDNAIterators, filenames)

    def test_casava_one_eight_single_lane_per_sample_dirfmt_to_slpssefdf(self):
        filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',)
        self._transformer_test_helper(CasavaOneEightSingleLanePerSampleDirFmt,
                                      SingleLanePerSampleSingleEndFastqDirFmt,
                                      filenames)

    def test_casava_one_eight_single_lane_per_sample_dirfmt_to_slpspefdf(self):
        filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',)
        self._transformer_test_helper(CasavaOneEightSingleLanePerSampleDirFmt,
                                      SingleLanePerSamplePairedEndFastqDirFmt,
                                      filenames)

if __name__ == '__main__':
    unittest.main()
