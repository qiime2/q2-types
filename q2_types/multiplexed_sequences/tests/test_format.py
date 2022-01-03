# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import shutil
import unittest

from q2_types.multiplexed_sequences import (
    MultiplexedSingleEndBarcodeInSequenceDirFmt,
    MultiplexedPairedEndBarcodeInSequenceDirFmt,
)
from qiime2.plugin.testing import TestPluginBase


class TestMultiplexedSingleEndBarcodeInSequenceDirFmt(TestPluginBase):
    package = 'q2_types.multiplexed_sequences.tests'

    def test_format(self):
        # This test exists mainly to assert that the single-file directory
        # format is defined and functional. More extensive testing is performed
        # on its underlying format (FastqGzFormat).
        filepath = self.get_data_path('forward.fastq.gz')
        shutil.copy(filepath,
                    os.path.join(self.temp_dir.name, 'forward.fastq.gz'))
        format = MultiplexedSingleEndBarcodeInSequenceDirFmt(
            self.temp_dir.name, mode='r')

        # Should not error.
        format.validate()


class TestMultiplexedPairedEndBarcodeInSequenceDirFmt(TestPluginBase):
    package = 'q2_types.multiplexed_sequences.tests'

    def test_format(self):
        # This test exists mainly to assert that the directory format is
        # defined and functional. More extensive testing is performed
        # on its underlying formats (FastqGzFormat).
        for read in ['forward', 'reverse']:
            filepath = self.get_data_path('%s.fastq.gz' % read)
            shutil.copy(filepath,
                        os.path.join(self.temp_dir.name, '%s.fastq.gz' % read))
        format = MultiplexedPairedEndBarcodeInSequenceDirFmt(
            self.temp_dir.name, mode='r')

        # Should not error.
        format.validate()


if __name__ == '__main__':
    unittest.main()
