# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import shutil
import unittest

# from qiime2.plugin import ValidationError

from q2_types.multiplexed_sequences import (
    MultiplexedSingleEndBarcodeInSequenceDirFmt,
    MultiplexedPairedEndBarcodeInSequenceDirFmt,
    MultiplexedFastaQualDirFmt,
    # EMPMultiplexedDirFmt,
    # ErrorCorrectionDetailsDirFmt, EMPSingleEndDirFmt,
    # EMPSingleEndCasavaDirFmt, EMPPairedEndDirFmt,
    # EMPPairedEndCasavaDirFmt
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


class TestMultiplexedFastaQualDirFmt(TestPluginBase):
    package = 'q2_types.multiplexed_sequences.tests'

    def test_format(self):
        # This test exists mainly to assert that the directory format is
        # defined and functional.
        for fn in ['reads.fasta', 'reads.qual']:
            filepath = self.get_data_path(fn)
            shutil.copy(filepath,
                        os.path.join(self.temp_dir.name, fn))
        format = MultiplexedFastaQualDirFmt(self.temp_dir.name, mode='r')

        # Should not error.
        format.validate()

# These test may or may not be useful for future testing
# class TestEMPMultiplexedDirFmt(TestPluginBase):
#     package = 'q2_types.per_sample_sequences.tests'

#     def test_validate_positive(self):
#         filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',
#                      'Human-Kneecap_S1_L001_R2_001.fastq.gz',
#                      'Human-Armpit_S2_L001_R1_001.fastq.gz',
#                      'Human-Armpit_S2_L001_R2_001.fastq.gz')
#         for filename in filenames:
#             filepath = self.get_data_path(filename)
#             shutil.copy(filepath, self.temp_dir.name)

#         format = EMPMultiplexedDirFmt(self.temp_dir.name, mode='r')
#         format.validate()

#     def test_validate_negative(self):
#         filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',
#                      'Human-Kneecap_S1_L001_R2_001.fastq.gz',
#                      'Human-Armpit_S2_L001_R1_001.fastq.gz',
#                      'Human-Armpit_S2_L001_R2_001.fastq.gz',
#                      'Human-Other_S3_L001_R1_001.fastq.gz')
#         for filename in filenames:
#             filepath = self.get_data_path(filename)
#             shutil.copy(filepath, self.temp_dir.name)

#         format = EMPMultiplexedDirFmt(self.temp_dir.name, mode='r')
#         with self.assertRaisesRegex(ValidationError,
#                                     'EMPMultiplexedDirFmt'):
#             format.validate()


# class TestEMPSingleEndDirFmt(TestPluginBase):
#     package = 'q2_types.per_sample_sequences.tests'

#     def test_validate_positive(self):
#         filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',
#                      'Human-Armpit_S2_L001_R1_001.fastq.gz',
#                      'Human-Other_S3_L001_R1_001.fastq.gz',
#                      'Human-Other_S4_L001_R1_001.fastq.gz',
#                      'Human-Other_S5_L001_R1_001.fastq.gz',
#                      'Human-Other_S6_L001_R1_001.fastq.gz',
#                      'Human-Other_S7_L001_R1_001.fastq.gz')
#         for filename in filenames:
#             filepath = self.get_data_path(filename)
#             shutil.copy(filepath, self.temp_dir.name)

#             format = EMPSingleEndDirFmt(self.temp_dir.name, mode='r')
#             format.validate()

#     def test_validate_negative(self):
#         filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',
#                      'Human-Armpit_S2_L001_R1_001.fastq.gz',
#                      'Human-Other_S3_L001_R1_001.fastq.gz',
#                      'Human-Other_S4_L001_R1_001.fastq.gz',
#                      'Human-Other_S5_L001_R1_001.fastq.gz',
#                      'Human-Other_S6_L001_R1_001.fastq.gz',
#                      'Human-Other_S7_L001_R1_001.fastq.gz')
#         for filename in filenames:
#             filepath = self.get_data_path(filename)
#             shutil.copy(filepath, self.temp_dir.name)

#         format = EMPSingleEndDirFmt(self.temp_dir.name, mode='r')
#         with self.assertRaisesRegex(ValidationError,
#                                     'EMPSingleEndDirFmt'):
#             format.validate()


# class TestEMPSingleEndCasavaDirFmt(TestPluginBase):
#     package = 'q2_types.per_sample_sequences.tests'

#     def test_validate_positive(self):
#         filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',
#                      'Human-Armpit_S2_L001_R1_001.fastq.gz',
#                      'Human-Other_S3_L001_R1_001.fastq.gz',
#                      'Human-Other_S4_L001_R1_001.fastq.gz',
#                      'Human-Other_S5_L001_R1_001.fastq.gz',
#                      'Human-Other_S6_L001_R1_001.fastq.gz',
#                      'Human-Other_S7_L001_R1_001.fastq.gz')
#         for filename in filenames:
#             filepath = self.get_data_path(filename)
#             shutil.copy(filepath, self.temp_dir.name)

#             format = EMPSingleEndCasavaDirFmt(self.temp_dir.name, mode='r')
#             format.validate()

#     def test_validate_negative(self):
#         filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',
#                      'Human-Armpit_S2_L001_R1_001.fastq.gz',
#                      'Human-Other_S3_L001_R1_001.fastq.gz',
#                      'Human-Other_S4_L001_R1_001.fastq.gz',
#                      'Human-Other_S5_L001_R1_001.fastq.gz',
#                      'Human-Other_S6_L001_R1_001.fastq.gz',
#                      'Human-Other_S7_L001_R1_001.fastq.gz')
#         for filename in filenames:
#             filepath = self.get_data_path(filename)
#             shutil.copy(filepath, self.temp_dir.name)

#         format = EMPSingleEndCasavaDirFmt(self.temp_dir.name, mode='r')
#         with self.assertRaisesRegex(ValidationError,
#                                     'EMPSingleEndCasavaDirFmt'):
#             format.validate()


# class TestEMPPairedEndDirFmt(TestPluginBase):
#     package = 'q2_types.per_sample_sequences.tests'

#     def test_validate_positive(self):
#         filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',
#                      'Human-Kneecap_S1_L001_R2_001.fastq.gz',
#                      'Human-Armpit_S2_L001_R1_001.fastq.gz',
#                      'Human-Armpit_S2_L001_R2_001.fastq.gz',
#                      'Human-Other_S3_L001_R1_001.fastq.gz',
#                      'Human-Other_S3_L001_R2_001.fastq.gz'
#                      )
#         for filename in filenames:
#             filepath = self.get_data_path(filename)
#             shutil.copy(filepath, self.temp_dir.name)

#             format = EMPPairedEndDirFmt(self.temp_dir.name, mode='r')
#             format.validate()

#     def test_validate_negative(self):
#         filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',
#                      'Human-Kneecap_S1_L001_R2_001.fastq.gz',
#                      'Human-Armpit_S2_L001_R1_001.fastq.gz',
#                      'Human-Armpit_S2_L001_R2_001.fastq.gz',
#                      'Human-Other_S3_L001_R1_001.fastq.gz',
#                      'Human-Other_S3_L001_R2_001.fastq.gz'
#                      )
#         for filename in filenames:
#             filepath = self.get_data_path(filename)
#             shutil.copy(filepath, self.temp_dir.name)

#         format = EMPPairedEndDirFmt(self.temp_dir.name, mode='r')
#         with self.assertRaisesRegex(ValidationError,
#                                     'EMPPairedEndDirFmt'):
#             format.validate()

#     class TestEMPPairedEndCasavaDirFmt(TestPluginBase):
#         package = 'q2_types.per_sample_sequences.tests'

#         def test_validate_positive(self):
#             filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',
#                          'Human-Kneecap_S1_L001_R2_001.fastq.gz',
#                          'Human-Armpit_S2_L001_R1_001.fastq.gz',
#                          'Human-Armpit_S2_L001_R2_001.fastq.gz',
#                          'Human-Other_S3_L001_R1_001.fastq.gz',
#                          'Human-Other_S3_L001_R2_001.fastq.gz'
#                          )
#             for filename in filenames:
#                 filepath = self.get_data_path(filename)
#                 shutil.copy(filepath, self.temp_dir.name)

#        format = EMPPairedEndCasavaDirFmt(self.temp_dir.name, mode='r')
#                 format.validate()

#         def test_validate_negative(self):
#             filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',
#                          'Human-Kneecap_S1_L001_R2_001.fastq.gz',
#                          'Human-Armpit_S2_L001_R1_001.fastq.gz',
#                          'Human-Armpit_S2_L001_R2_001.fastq.gz',
#                          'Human-Other_S3_L001_R1_001.fastq.gz',
#                          'Human-Other_S3_L001_R2_001.fastq.gz',
#                          )
#             for filename in filenames:
#                 filepath = self.get_data_path(filename)
#                 shutil.copy(filepath, self.temp_dir.name)

#             format = EMPPairedEndCasavaDirFmt(self.temp_dir.name, mode='r')
#             with self.assertRaisesRegex(ValidationError,
#                                         'EMPPairedEndCasavaDirFmt'):
#                 format.validate()

#     class TestErrorCorrectionDetailsDirFmt(TestPluginBase):
#         package = 'q2_types.per_sample_sequences.tests'

#         def test_validate_positive(self):
#             filenames = ('error_correction_details/positive.tsv')
#             for filename in filenames:
#                 filepath = self.get_data_path(filename)
#                 shutil.copy(filepath, self.temp_dir.name)

#                 format = ErrorCorrectionDetailsDirFmt(self.temp_dir.name,
#                                                       mode='r')
#                 format.validate()

#         def test_validate_negative(self):
#             filenames = ('error_correction_details/invalid.tsv')
#             for filename in filenames:
#                 filepath = self.get_data_path(filename)
#                 shutil.copy(filepath, self.temp_dir.name)

#   format = ErrorCorrectionDetailsDirFmt(self.temp_dir.name, mode='r')
#             with self.assertRaisesRegex(ValidationError,
#                                         'ErrorCorrectionDetailsDirFmt'):
#                 format.validate()


if __name__ == '__main__':
    unittest.main()
