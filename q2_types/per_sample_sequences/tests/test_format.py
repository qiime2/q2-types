# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path
import shutil
import unittest

from q2_types.per_sample_sequences import (
    CasavaOneEightSingleLanePerSampleDirFmt,
    CasavaOneEightLanelessPerSampleDirFmt,
    FastqGzFormat, YamlFormat, FastqManifestFormat,
    FastqAbsolutePathManifestFormat,
    SingleEndFastqManifestPhred33, SingleEndFastqManifestPhred64,
    PairedEndFastqManifestPhred33, PairedEndFastqManifestPhred64,
    SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt,
    QIIME1DemuxFormat, QIIME1DemuxDirFmt
)
from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError


class TestAbsoluteFastqManifestFormats(TestPluginBase):
    package = 'q2_types.per_sample_sequences.tests'

    def setUp(self):
        super().setUp()
        self.formats = [FastqAbsolutePathManifestFormat,
                        SingleEndFastqManifestPhred33,
                        SingleEndFastqManifestPhred64,
                        PairedEndFastqManifestPhred33,
                        PairedEndFastqManifestPhred64]

    def test_validate_positive(self):
        for file in ['single-MANIFEST', 'paired-MANIFEST', 'long-MANIFEST']:
            filepath = self.get_data_path('absolute_manifests/%s' % file)
            for format in self.formats:
                format(filepath, mode='r').validate()

    def test_validate_negative(self):
        files = ['no-data-MANIFEST', 'not-MANIFEST',
                 'absolute_manifests/jagged-MANIFEST']
        for file in files:
            filepath = self.get_data_path(file)
            for format in self.formats:
                with self.assertRaisesRegex(ValidationError, format.__name__):
                    format(filepath, mode='r').validate()


class TestRelativeFastqManifestFormats(TestPluginBase):
    package = 'q2_types.per_sample_sequences.tests'

    def test_validate_positive(self):
        for file in ['single-MANIFEST', 'paired-MANIFEST', 'long-MANIFEST']:
            filepath = self.get_data_path('relative_manifests/%s' % file)
            FastqManifestFormat(filepath, mode='r').validate()

    def test_validate_negative(self):
        files = ['no-data-MANIFEST', 'not-MANIFEST',
                 'relative_manifests/jagged-MANIFEST']
        for file in files:
            filepath = self.get_data_path(file)
            with self.assertRaisesRegex(ValidationError,
                                        'FastqManifestFormat'):
                FastqManifestFormat(filepath, mode='r').validate()


class TestFastqGzFormat(TestPluginBase):
    package = 'q2_types.per_sample_sequences.tests'

    def test_validate_positive(self):
        filepath = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz')
        format = FastqGzFormat(filepath, mode='r')

        format.validate()

    def test_validate_negative(self):
        filepath = self.get_data_path('not-fastq.fastq.gz')
        format = FastqGzFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'Header.*1'):
            format.validate()

    def test_validate_mixed_case(self):
        filepath = self.get_data_path('mixed-case.fastq.gz')
        format = FastqGzFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'Lowercase.*2'):
            format.validate()

    def test_validate_uncompressed(self):
        filepath = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq')
        format = FastqGzFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'uncompressed'):
            format.validate()

    def test_incomplete_record_qual(self):
        filepath = self.get_data_path('incomplete-quality.fastq.gz')
        format = FastqGzFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'quality.*9'):
            format.validate()

    def test_incomplete_record_sep(self):
        filepath = self.get_data_path('incomplete-sep.fastq.gz')
        format = FastqGzFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'separator.*9'):
            format.validate()

    def test_incomplete_record_sequence(self):
        filepath = self.get_data_path('incomplete-sequence.fastq.gz')
        format = FastqGzFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'sequence.*9'):
            format.validate()

    def test_invalid_record_sep(self):
        filepath = self.get_data_path('invalid-sep.fastq.gz')
        format = FastqGzFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'separator.*11'):
            format.validate()

    def test_invalid_quality_score_length(self):
        filepath = self.get_data_path('invalid-quality.fastq.gz')
        format = FastqGzFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'length.*9'):
            format.validate()

    def test_partial_record(self):
        filepath = self.get_data_path('partial-record.fastq.gz')
        format = FastqGzFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'sequence.*1'):
            format.validate()


class TestFormats(TestPluginBase):
    package = 'q2_types.per_sample_sequences.tests'

    def test_yaml_format_validate_positive(self):
        filepath = self.get_data_path('metadata.yml')
        format = YamlFormat(filepath, mode='r')

        format.validate()

    def test_yaml_format_validate_negative(self):
        filepath = self.get_data_path('not-metadata.yml')
        format = YamlFormat(filepath, mode='r')

        with self.assertRaisesRegex(ValidationError, 'YamlFormat'):
            format.validate()

    def test_casava_one_eight_slanepsample_dir_fmt_validate_positive(self):
        filepath = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz')
        shutil.copy(filepath, self.temp_dir.name)

        format = CasavaOneEightSingleLanePerSampleDirFmt(
            self.temp_dir.name, mode='r')

        format.validate()

    def test_casava_one_eight_slanepsample_dir_fmt_validate_negative(self):
        filepath = self.get_data_path('not-fastq.fastq.gz')
        shutil.copy(filepath, self.temp_dir.name)

        format = CasavaOneEightSingleLanePerSampleDirFmt(
            self.temp_dir.name, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'CasavaOneEightSingleLanePer'):
            format.validate()

    def test_casava_one_eight_slanepsample_dir_fmt_subdirectories(self):
        bad_dir = os.path.join(self.temp_dir.name, 'Human_Kneecap')
        os.mkdir(bad_dir)
        bad_name = os.path.join(bad_dir, 'S1_L001_R1_001.fastq.gz')

        fastq = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz')
        shutil.copy(fastq, bad_name)

        format = CasavaOneEightSingleLanePerSampleDirFmt(self.temp_dir.name,
                                                         mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'subdirectory.*Human_Kneecap'):
            format.validate()

    def test_casava_one_eight_slanepsample_dir_fmt_missing_directions(self):
        f = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz')
        r = self.get_data_path(
            'paired_end_data/Human-Kneecap_S1_L001_R2_001.fastq.gz')

        shutil.copy(f, self.temp_dir.name)
        shutil.copy(r, self.temp_dir.name)
        shutil.copy(
            f, os.path.join(self.temp_dir.name,
                            'Human-Other_S1_L001_R1_001.fastq.gz'))

        format = CasavaOneEightSingleLanePerSampleDirFmt(self.temp_dir.name,
                                                         mode='r')

        with self.assertRaisesRegex(ValidationError, 'matching.*Human-Other'):
            format.validate()

    def test_casava_one_eight_slanepsample_dir_fmt_duplicate_forwards(self):
        f = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz')

        shutil.copy(f, self.temp_dir.name)
        shutil.copy(
            f, os.path.join(self.temp_dir.name,
                            'Human-Kneecap_S2_L001_R1_001.fastq.gz'))

        format = CasavaOneEightSingleLanePerSampleDirFmt(self.temp_dir.name,
                                                         mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'Duplicate.*Human-Kneecap'):
            format.validate()

    def test_casava_one_eight_slanepsample_dir_fmt_duplicate_reverse(self):
        r = self.get_data_path(
            'paired_end_data/Human-Kneecap_S1_L001_R2_001.fastq.gz')

        shutil.copy(r, self.temp_dir.name)
        shutil.copy(
            r, os.path.join(self.temp_dir.name,
                            'Human-Kneecap_S2_L001_R2_001.fastq.gz'))

        format = CasavaOneEightSingleLanePerSampleDirFmt(self.temp_dir.name,
                                                         mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'Duplicate.*Human-Kneecap'):
            format.validate()

    def test_miseq_demux_dir_fmt_validate_positive(self):
        filepath = self.get_data_path('Human-Kneecap_S1_R1_001.fastq.gz')
        shutil.copy(filepath, self.temp_dir.name)

        format = CasavaOneEightLanelessPerSampleDirFmt(self.temp_dir.name,
                                                       mode='r')

        format.validate()

    def test_miseq_demux_dir_fmt_validate_negative(self):
        filepath = self.get_data_path('not-fastq.fastq.gz')
        shutil.copy(filepath, self.temp_dir.name)

        format = CasavaOneEightLanelessPerSampleDirFmt(self.temp_dir.name,
                                                       mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'CasavaOneEightLanelessPerSampleDirFmt'):
            format.validate()

    def test_slanepsample_single_end_fastq_dir_fmt_validate_positive(self):
        filenames = ('single_end_data/MANIFEST', 'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz')
        for filename in filenames:
            filepath = self.get_data_path(filename)
            shutil.copy(filepath, self.temp_dir.name)

        format = SingleLanePerSampleSingleEndFastqDirFmt(
            self.temp_dir.name, mode='r')

        format.validate()

    def test_slanepsample_single_end_fastq_dir_fmt_validate_negative(self):
        filenames = ('single_end_data/MANIFEST', 'metadata.yml',
                     'not-fastq.fastq.gz')
        for filename in filenames:
            filepath = self.get_data_path(filename)
            shutil.copy(filepath, self.temp_dir.name)

        format = SingleLanePerSampleSingleEndFastqDirFmt(
            self.temp_dir.name, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'SingleLanePerSampleSingle'):
            format.validate()

    def test_slanepsample_single_end_fastq_dir_fmt_validate_bad_paired(self):
        filenames = ('paired_end_data/MANIFEST', 'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz',
                     'paired_end_data/Human-Kneecap_S1_L001_R2_001.fastq.gz')
        for filename in filenames:
            filepath = self.get_data_path(filename)
            shutil.copy(filepath, self.temp_dir.name)

        format = SingleLanePerSampleSingleEndFastqDirFmt(
            self.temp_dir.name, mode='r')

        with self.assertRaisesRegex(ValidationError, 'Forward and reverse'):
            format.validate()

    def test_slanepsample_paired_end_fastq_dir_fmt_validate_positive(self):
        filenames = ('paired_end_data/MANIFEST', 'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz',
                     'paired_end_data/Human-Kneecap_S1_L001_R2_001.fastq.gz')
        for filename in filenames:
            filepath = self.get_data_path(filename)
            shutil.copy(filepath, self.temp_dir.name)

        format = SingleLanePerSamplePairedEndFastqDirFmt(
            self.temp_dir.name, mode='r')

        format.validate()

    def test_slanepsample_paired_end_fastq_dir_fmt_validate_negative(self):
        filenames = ('paired_end_data/MANIFEST', 'metadata.yml',
                     'not-fastq.fastq.gz')
        for filename in filenames:
            filepath = self.get_data_path(filename)
            shutil.copy(filepath, self.temp_dir.name)

        format = SingleLanePerSamplePairedEndFastqDirFmt(
            self.temp_dir.name, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'SingleLanePerSamplePaired'):
            format.validate()

    def test_slanepsample_paired_end_fastq_dir_fmt_validate_missing_pair(self):
        filenames = ('single_end_data/MANIFEST', 'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz')
        for filename in filenames:
            filepath = self.get_data_path(filename)
            shutil.copy(filepath, self.temp_dir.name)

        format = SingleLanePerSamplePairedEndFastqDirFmt(
            self.temp_dir.name, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'paired'):
            format.validate()


class TestQIIME1DemuxFormat(TestPluginBase):
    package = 'q2_types.per_sample_sequences.tests'

    def setUp(self):
        super().setUp()

        self.positives = [
            'empty', 'short.fna', 'long.fna', 'single-record.fna',
            'with-descriptions.fna', 'split-libraries-output.fna'
        ]
        self.negatives = [
            'incomplete.fna', 'empty-header.fna',
            'invalid-header.fna', 'description-only.fna', 'blank-line.fna',
            'no-underscore-in-id.fna', 'no-sample-id.fna',
            'no-secondary-id.fna', 'duplicate-ids.fna', 'empty-seq.fna',
            'not-dna.fna'
        ]

    def test_file_format_validate_positive(self):
        for file in self.positives:
            filepath = self.get_data_path('qiime1-demux-format/%s' % file)
            QIIME1DemuxFormat(filepath, mode='r').validate()

    def test_file_format_validate_negative(self):
        for file in self.negatives:
            filepath = self.get_data_path('qiime1-demux-format/%s' % file)
            with self.assertRaisesRegex(ValidationError, 'QIIME1DemuxFormat'):
                QIIME1DemuxFormat(filepath, mode='r').validate()

    def test_directory_format_validate_positive(self):
        for file in self.positives:
            filepath = self.get_data_path('qiime1-demux-format/%s' % file)
            shutil.copy(filepath, os.path.join(self.temp_dir.name, 'seqs.fna'))

            QIIME1DemuxDirFmt(self.temp_dir.name, mode='r').validate()

    def test_directory_format_validate_negative(self):
        for file in self.negatives:
            filepath = self.get_data_path('qiime1-demux-format/%s' % file)
            shutil.copy(filepath, os.path.join(self.temp_dir.name, 'seqs.fna'))

            with self.assertRaisesRegex(ValidationError, 'QIIME1DemuxFormat'):
                QIIME1DemuxDirFmt(self.temp_dir.name, mode='r').validate()

    def test_directory_format_wrong_filename(self):
        filepath = self.get_data_path('qiime1-demux-format/short.fna')
        shutil.copy(filepath, self.temp_dir.name)

        with self.assertRaisesRegex(ValidationError,
                                    'QIIME1DemuxDirFmt.*seqs\.fna'):
            QIIME1DemuxDirFmt(self.temp_dir.name, mode='r').validate()


if __name__ == "__main__":
    unittest.main()
