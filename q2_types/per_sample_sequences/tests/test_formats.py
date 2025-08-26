# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path
import shutil
import unittest
import string
from pathlib import Path
from unittest.mock import patch, Mock

import pandas as pd

from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError

from q2_types.multiplexed_sequences import ErrorCorrectionDetailsFmt
from q2_types.per_sample_sequences import (
    CasavaOneEightSingleLanePerSampleDirFmt,
    CasavaOneEightLanelessPerSampleDirFmt,
    FastqGzFormat, YamlFormat, FastqManifestFormat,
    FastqAbsolutePathManifestFormat,
    SingleEndFastqManifestPhred33, SingleEndFastqManifestPhred64,
    PairedEndFastqManifestPhred33, PairedEndFastqManifestPhred64,
    SingleEndFastqManifestPhred33V2, SingleEndFastqManifestPhred64V2,
    PairedEndFastqManifestPhred33V2, PairedEndFastqManifestPhred64V2,
    SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt,
    QIIME1DemuxFormat, QIIME1DemuxDirFmt,
    SampleIdIndexedSingleEndPerSampleDirFmt, MultiMAGManifestFormat,
    MultiFASTADirectoryFormat, MultiBowtie2IndexDirFmt, ContigSequencesDirFmt,
    MultiBAMDirFmt, BAMDirFmt
)


class TestAbsoluteFastqManifestV2Formats(TestPluginBase):
    package = 'q2_types.per_sample_sequences.tests'

    def setUp(self):
        super().setUp()
        self.se_formats = [SingleEndFastqManifestPhred33V2,
                           SingleEndFastqManifestPhred64V2]
        self.pe_formats = [PairedEndFastqManifestPhred33V2,
                           PairedEndFastqManifestPhred64V2]

    def template_manifest(self, filepath, ctx):
        with open(filepath) as fh:
            tmpl = string.Template(fh.read())
        basename = os.path.basename(filepath)
        file_ = os.path.join(self.temp_dir.name, basename)
        with open(file_, 'w') as fh:
            fh.write(tmpl.substitute(**ctx))
        return file_

    def test_validate_se_positive(self):
        s1 = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz')
        s2 = self.get_data_path('Human-Armpit.fastq.gz')
        fp = self.get_data_path('absolute_manifests_v2/single-MANIFEST')
        manifest = self.template_manifest(fp, {'s1': s1, 's2': s2})

        for fmt in self.se_formats:
            fmt(manifest, mode='r').validate()

    def test_validate_pe_positive(self):
        s1f = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz')
        s1r = self.get_data_path('Human-Armpit.fastq.gz')
        s2f = self.get_data_path('Human-Armpit_S2_L001_R1_001.fastq.gz')
        s2r = self.get_data_path('Human-Kneecap_S1_R1_001.fastq.gz')

        fp = self.get_data_path('absolute_manifests_v2/paired-MANIFEST')
        manifest = self.template_manifest(fp, {'s1f': s1f, 's1r': s1r,
                                               's2f': s2f, 's2r': s2r})

        for fmt in self.pe_formats:
            fmt(manifest, mode='r').validate()

    def test_extra_columns(self):
        s1f = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz')
        s1r = self.get_data_path('Human-Armpit.fastq.gz')
        s2f = self.get_data_path('Human-Armpit_S2_L001_R1_001.fastq.gz')
        s2r = self.get_data_path('Human-Kneecap_S1_R1_001.fastq.gz')

        fp = self.get_data_path('absolute_manifests_v2/multicol-MANIFEST')
        manifest = self.template_manifest(fp, {'s1f': s1f, 's1r': s1r,
                                               's2f': s2f, 's2r': s2r})

        for fmt in self.se_formats:
            fmt(manifest, mode='r').validate()

    def test_invalid_metadata(self):
        manifest = self.get_data_path('absolute_manifests/single-MANIFEST')

        for fmt in self.se_formats:
            with self.assertRaisesRegex(ValidationError, 'unrecognized ID'):
                fmt(manifest, mode='r').validate()

    def test_missing_column_se(self):
        manifest = self.get_data_path('absolute_manifests_v2/paired-MANIFEST')

        for fmt in self.se_formats:
            with self.assertRaisesRegex(ValidationError, 'is not a column'):
                fmt(manifest, mode='r').validate()

    def test_missing_columns_pe(self):
        manifest = self.get_data_path('absolute_manifests_v2/single-MANIFEST')

        for fmt in self.pe_formats:
            with self.assertRaisesRegex(ValidationError, 'is not a column'):
                fmt(manifest, mode='r').validate()

    def test_invalid_column_type(self):
        manifest = self.get_data_path('absolute_manifests_v2/numeric-MANIFEST')

        for fmt in self.se_formats:
            with self.assertRaisesRegex(ValidationError, 'is not a column'):
                fmt(manifest, mode='r').validate()

    def test_missing_files(self):
        manifest = self.get_data_path('absolute_manifests_v2/missing-MANIFEST')

        for fmt in self.pe_formats:
            with self.assertRaisesRegex(
                    ValidationError,
                    'Missing.*line 1.*absolute-filepath'):
                fmt(manifest, mode='r').validate()

    def test_path_not_found(self):
        # we make sure the file is missing by skipping the templating step
        manifest = self.get_data_path('absolute_manifests_v2/single-MANIFEST')

        for fmt in self.se_formats:
            with self.assertRaisesRegex(
                    ValidationError,
                    'line 1.*absolute-filepath.*Human-Kneecap'):
                fmt(manifest, mode='r').validate()

    def test_duplicate_filepaths(self):
        s1 = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz')
        fp = self.get_data_path('absolute_manifests_v2/single-MANIFEST')
        manifest = self.template_manifest(fp, {'s1': s1, 's2': s1})

        for fmt in self.se_formats:
            with self.assertRaisesRegex(
                    ValidationError,
                    'line 2.*absolute-filepath.*Peanut-Eyeball.*'
                    'line 1.*absolute-filepath.*Human-Kneecap'):
                fmt(manifest, mode='r').validate()

    def test_paired_end_records_match(self):
        '''
        Tests that an error is raised when a pair of read mate files do not
        have an equal number of records.
        '''
        unmatched_manifest = self.get_data_path(
            'unmatched_paired_end/MANIFEST'
        )
        file_fwd_unmatch = self.get_data_path(
            'unmatched_paired_end/sample-name-1_S1_L001_R1_001.fastq.gz'
        )
        file_rev_unmatch = self.get_data_path(
            'unmatched_paired_end/sample-name-1_S1_L001_R2_001.fastq.gz'
        )
        manifest = self.template_manifest(
           unmatched_manifest, {'r1': file_fwd_unmatch, 'r2': file_rev_unmatch}
        )

        for fmt in self.pe_formats:
            with self.assertRaisesRegex(
                ValidationError,
                "A pair of paired-end files were found not to have the same "
                "number of records"
            ):
                fmt(manifest, mode='r').validate()


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
        s1 = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz')

        for file in ['single-MANIFEST', 'paired-MANIFEST', 'long-MANIFEST']:
            filepath = self.get_data_path('absolute_manifests/%s' % file)
            with open(filepath) as fh:
                tmpl = string.Template(fh.read())
            file_ = os.path.join(self.temp_dir.name, file)
            with open(file_, 'w') as fh:
                fh.write(tmpl.substitute(path=os.path.dirname(s1)))

            for format in self.formats:
                format(file_, mode='r').validate()

    def test_validate_negative_no_data(self):
        filepath = self.get_data_path('no-data-MANIFEST')
        for format in self.formats:
            with self.assertRaisesRegex(ValidationError, 'No header found'):
                format(filepath, mode='r').validate()

    def test_validate_negative_empty(self):
        filepath = self.get_data_path('empty-MANIFEST')
        for format in self.formats:
            with self.assertRaisesRegex(ValidationError, 'No header found'):
                format(filepath, mode='r').validate()

    def test_validate_negative_header_no_records(self):
        filepath = self.get_data_path('empty-records-MANIFEST')
        for format in self.formats:
            with self.assertRaisesRegex(ValidationError, 'No sample records'):
                format(filepath, mode='r').validate()

    def test_validate_negative_not_manifest(self):
        filepath = self.get_data_path('not-MANIFEST')
        for format in self.formats:
            with self.assertRaisesRegex(ValidationError, 'line 1.*filename'):
                format(filepath, mode='r').validate()

    def test_validate_negative_jagged_manifest(self):
        filepath = self.get_data_path('absolute_manifests/jagged-MANIFEST')
        for format in self.formats:
            with self.assertRaisesRegex(ValidationError,
                                        'line 3.*could not be found'):
                format(filepath, mode='r').validate()

    def test_validate_negative_invalid_direction(self):
        s1 = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz')

        with open(self.get_data_path('invalid-direction-MANIFEST')) as fh:
            tmpl = string.Template(fh.read())
        file_ = os.path.join(self.temp_dir.name, 'invalid-direction-MANIFEST')
        with open(file_, 'w') as fh:
            fh.write(tmpl.substitute(path=os.path.dirname(s1)))

        for format in self.formats:
            with self.assertRaisesRegex(ValidationError, 'direction.*peanut'):
                format(file_, mode='r').validate()


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

    def test_casava_one_eight_slanepsample_dir_fmt_manifest_property(self):
        filepath = self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz')
        shutil.copy(filepath, self.temp_dir.name)

        format = CasavaOneEightSingleLanePerSampleDirFmt(
            self.temp_dir.name, mode='r')

        format.validate()
        self.assertTrue(True)
        self.assertIsInstance(format.manifest, pd.DataFrame)

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

    def test_casava_one_eight_slanepsample_dir_fmt_paired_match(self):
        '''
        Tests that an error is raised when a pair of read mate files do not
        have an equal number of records.
        '''
        file_path_fwd = self.get_data_path(
            'unmatched_paired_end/sample-name-1_S1_L001_R1_001.fastq.gz'
        )
        file_path_rev = self.get_data_path(
            'unmatched_paired_end/sample-name-1_S1_L001_R2_001.fastq.gz'
        )

        shutil.copy(file_path_fwd, self.temp_dir.name)
        shutil.copy(file_path_rev, self.temp_dir.name)

        format = CasavaOneEightSingleLanePerSampleDirFmt(
            self.temp_dir.name, mode='r'
        )

        with self.assertRaisesRegex(
            ValidationError,
            "A pair of paired-end files were found not to have the same "
            "number of records"
        ):
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

    def test_sample_id_indexed_fastq_dir_fmt(self):
        filenames = ('Human-Armpit.fastq.gz',
                     # regardless of how much the file name looks like
                     # Casava, everything before the .fastq.gz should be
                     # treated as the sample id
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz')
        for filename in filenames:
            filepath = self.get_data_path(filename)
            shutil.copy(filepath, self.temp_dir.name)

        format = SampleIdIndexedSingleEndPerSampleDirFmt(
            self.temp_dir.name, mode='r')

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

    def test_slanepsample_paired_end_fastq_dir_fmt_incorrect_filenames(self):
        filenames = ('single_end_data/MANIFEST.txt', 'metadata.yml.txt',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz',
                     'paired_end_data/Human-Kneecap_S1_L001_R2_001.fastq.gz')
        for filename in filenames:
            filepath = self.get_data_path(filename)
            shutil.copy(filepath, self.temp_dir.name)

        format = SingleLanePerSamplePairedEndFastqDirFmt(
            self.temp_dir.name, mode='r')

        with self.assertRaisesRegex(ValidationError,
                                    'Missing one or more files.*MANIFEST'):
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
                                    r'QIIME1DemuxDirFmt.*seqs\.fna'):
            QIIME1DemuxDirFmt(self.temp_dir.name, mode='r').validate()


class TestErrorCorrectionDetailsFmt(TestPluginBase):
    package = 'q2_types.per_sample_sequences.tests'

    def test_validate_positive(self):
        fp = self.get_data_path('error_correction_details/positive.tsv')
        ErrorCorrectionDetailsFmt(fp, mode='r').validate()

    def test_validate_invalid_format(self):
        fp = self.get_data_path('error_correction_details/invalid.tsv')
        with self.assertRaisesRegex(ValidationError,
                                    'Failed to locate header.'):
            ErrorCorrectionDetailsFmt(fp, mode='r').validate()

    def test_validate_missing_columns(self):
        fp = self.get_data_path('error_correction_details/missing_columns.tsv')
        with self.assertRaisesRegex(ValidationError,
                                    'barcode-corrected.*is not a column'):
            ErrorCorrectionDetailsFmt(fp, mode='r').validate()


class TestMultiMAGManifestFormat(TestPluginBase):
    package = 'q2_types.per_sample_sequences.tests'

    def template_manifest(self, filepath, ctx):
        with open(filepath) as fh:
            tmpl = string.Template(fh.read())
        basename = os.path.basename(filepath)
        file_ = os.path.join(self.temp_dir.name, basename)
        with open(file_, 'w') as fh:
            fh.write(tmpl.substitute(**ctx))
        return file_

    def test_multifasta_manifest(self):
        manifest_fp = self.get_data_path('manifests/MANIFEST-mags-fa')
        format = MultiMAGManifestFormat(manifest_fp, mode='r')

        format.validate()

    def test_multifasta_manifest_missing_column(self):
        manifest_fp = self.get_data_path('manifests/MANIFEST-missing-column')
        format = MultiMAGManifestFormat(manifest_fp, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'Found header .* with the following labels'):
            format.validate()

    def test_multifasta_manifest_missing_file(self):
        manifest_fp = self.get_data_path('manifests/MANIFEST-missing-filepath')
        format = MultiMAGManifestFormat(manifest_fp, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'Line 2 has 2 cells .* expected 3'):
            format.validate()

    def test_multifasta_manifest_no_samples(self):
        manifest_fp = self.get_data_path('manifests/MANIFEST-no-samples')
        format = MultiMAGManifestFormat(manifest_fp, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'No sample records found'):
            format.validate()

    def test_multifasta_manifest_empty(self):
        manifest_fp = self.get_data_path('manifests/MANIFEST-empty')
        format = MultiMAGManifestFormat(manifest_fp, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'No header found, expected'):
            format.validate()


class TestMultiFormats(TestPluginBase):
    package = 'q2_types.per_sample_sequences.tests'

    def test_multifasta_dirfmt_fa(self):
        dirpath = self.get_data_path('mags/mags-fa')
        format = MultiFASTADirectoryFormat(dirpath, mode='r')

        format.validate()

    def test_multifasta_dirfmt_fasta(self):
        dirpath = self.get_data_path('mags/mags-fasta')
        format = MultiFASTADirectoryFormat(dirpath, mode='r')

        format.validate()

    def test_multifasta_dirfmt_unorganized(self):
        dirpath = self.get_data_path('mags/mags-unorganized')
        format = MultiFASTADirectoryFormat(dirpath, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'should be .* per-sample directories'):
            format.validate()

    def test_multifasta_dirfmt_sample_dict(self):
        filepath = self.get_data_path('mags/mags-fasta')
        shutil.copytree(filepath, self.temp_dir.name, dirs_exist_ok=True)
        multifasta = MultiFASTADirectoryFormat(self.temp_dir.name, mode='r')

        obs = multifasta.sample_dict()
        exp = {
            'sample1': {
                'mag1': str(Path(multifasta.path / 'sample1/mag1.fasta')),
                'mag2': str(Path(multifasta.path / 'sample1/mag2.fasta')),
                'mag3': str(Path(multifasta.path / 'sample1/mag3.fasta'))
            },
            'sample2': {
                'mag1': str(Path(multifasta.path / 'sample2/mag1.fasta')),
                'mag2': str(Path(multifasta.path / 'sample2/mag2.fasta'))
            },
        }
        self.assertDictEqual(obs, exp)

        obs = multifasta.sample_dict(relative=True)
        exp = {
            'sample1': {
                'mag1': 'sample1/mag1.fasta',
                'mag2': 'sample1/mag2.fasta',
                'mag3': 'sample1/mag3.fasta'
            },
            'sample2': {
                'mag1': 'sample2/mag1.fasta',
                'mag2': 'sample2/mag2.fasta'
            },
        }
        self.assertDictEqual(obs, exp)

    def test_multifasta_dirfmt_with_dotfile(self):
        dirpath = self.get_data_path('mags/mags-fasta-with-dotfile')
        format = MultiFASTADirectoryFormat(dirpath, mode='r')

        format.validate()

    def test_multibowtie_index_dirfmt(self):
        dirpath = self.get_data_path('bowtie/index-valid')
        format = MultiBowtie2IndexDirFmt(dirpath, mode='r')

        format.validate()

    def test_multibowtie_index_dirfmt_unorganized(self):
        dirpath = self.get_data_path('bowtie/index-unorganized')
        format = MultiBowtie2IndexDirFmt(dirpath, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'should be .* per-sample directories'):
            format.validate()

    def test_multibowtie_dirfmt_with_dotfile(self):
        dirpath = self.get_data_path('bowtie/index-valid-with-dotfile')
        format = MultiBowtie2IndexDirFmt(dirpath, mode='r')

        format.validate()

    def test_contig_seqs_dirfmt(self):
        filepath = self.get_data_path('contigs/')
        shutil.copytree(filepath, self.temp_dir.name, dirs_exist_ok=True)
        ContigSequencesDirFmt(self.temp_dir.name, mode='r').validate()

    def test_contig_seqs_dirfmt_sample_dict(self):
        filepath = self.get_data_path('contigs/')
        shutil.copytree(filepath, self.temp_dir.name, dirs_exist_ok=True)
        contigs = ContigSequencesDirFmt(self.temp_dir.name, mode='r')

        obs = contigs.sample_dict()
        exp = {
            'sample1': str(Path(contigs.path / 'sample1_contigs.fa')),
            'sample2': str(Path(contigs.path / 'sample2_contigs.fa')),
            'sample3': str(Path(contigs.path / 'sample3_contigs.fa'))
        }
        self.assertDictEqual(obs, exp)

        obs = contigs.sample_dict(relative=True)
        exp = {
            'sample1': 'sample1_contigs.fa',
            'sample2': 'sample2_contigs.fa',
            'sample3': 'sample3_contigs.fa'
        }
        self.assertDictEqual(obs, exp)

    @patch('subprocess.run', return_value=Mock(returncode=0))
    def test_bam_dirmt(self, p):
        filepath = self.get_data_path('bowtie/maps-single')
        format = BAMDirFmt(filepath, mode='r')

        format.validate()

    @patch('subprocess.run', return_value=Mock(returncode=3))
    def test_bam_dirmt_invalid(self, p):
        # this patch is not ideal but samtools' installation sometimes can
        # be messed up and the tool returns an error regardless of the invoked
        # command, so let's just assume here that it works as it should
        filepath = self.get_data_path('bowtie/maps-invalid')
        format = BAMDirFmt(filepath, mode='r')

        with self.assertRaisesRegex(
                ValidationError, 'samtools quickcheck -v failed on'):
            format.validate()

    @patch('subprocess.run', return_value=Mock(returncode=0))
    def test_multibam_dirmt(self, p):
        filepath = self.get_data_path('bowtie/maps-multi')
        format = MultiBAMDirFmt(filepath, mode='r')

        format.validate()


if __name__ == "__main__":
    unittest.main()
