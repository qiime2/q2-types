# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


import functools
import unittest
import os
import io
import shutil
import string

import skbio
import yaml
import pandas as pd
from pandas._testing import assert_frame_equal

from qiime2.plugin import ValidationError
from qiime2.plugin.testing import TestPluginBase

from q2_types.per_sample_sequences import (
    SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt,
    CasavaOneEightSingleLanePerSampleDirFmt,
    CasavaOneEightLanelessPerSampleDirFmt,
    SingleEndFastqManifestPhred33,
    SingleEndFastqManifestPhred64,
    SingleEndFastqManifestPhred33V2,
    SingleEndFastqManifestPhred64V2,
    PairedEndFastqManifestPhred33,
    PairedEndFastqManifestPhred64,
    PairedEndFastqManifestPhred33V2,
    PairedEndFastqManifestPhred64V2,
    FastqAbsolutePathManifestFormat,
    FastqManifestFormat,
    QIIME1DemuxDirFmt,
    FastqGzFormat,
    SampleIdIndexedSingleEndPerSampleDirFmt,
    MultiFASTADirectoryFormat,
    MultiMAGManifestFormat,
    MultiMAGSequencesDirFmt
)
from q2_types.per_sample_sequences._util import (
    _validate_header,
    _validate_single_end_fastq_manifest_directions,
    _validate_paired_end_fastq_manifest_directions,
    _parse_and_validate_manifest
)


_parse_and_validate_manifest_partial = functools.partial(
    _parse_and_validate_manifest,
    abs_manifest_fmt=FastqAbsolutePathManifestFormat,
    manifest_fmt=FastqManifestFormat,
)


class TestTransformers(TestPluginBase):
    package = "q2_types.per_sample_sequences.tests"

    def test_slpspefdf_to_slpssefdf(self):
        filenames = ('paired_end_data/MANIFEST', 'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz',
                     'paired_end_data/Human-Kneecap_S1_L001_R2_001.fastq.gz')
        input, obs = self.transform_format(
            SingleLanePerSamplePairedEndFastqDirFmt,
            SingleLanePerSampleSingleEndFastqDirFmt, filenames=filenames
        )
        expected = skbio.io.read(
            '%s/Human-Kneecap_S1_L001_R1_001.fastq.gz' % str(input),
            format='fastq', constructor=skbio.DNA
        )
        obs = skbio.io.read(
            '%s/Human-Kneecap_S1_L001_R1_001.fastq.gz' % str(obs),
            format='fastq', constructor=skbio.DNA
        )

        for act, exp in zip(obs, expected):
            self.assertEqual(act, exp)

    def test_slpssefdf_to_qiime1demuxdf(self):
        filenames = ('single-end-two-sample-data1/MANIFEST',
                     'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz',
                     'Human-Armpit_S2_L001_R1_001.fastq.gz')
        input, observed = self.transform_format(
            SingleLanePerSampleSingleEndFastqDirFmt,
            QIIME1DemuxDirFmt, filenames=filenames
        )
        expected1 = list(skbio.io.read(
            '%s/Human-Kneecap_S1_L001_R1_001.fastq.gz' % str(input),
            format='fastq', constructor=skbio.DNA
        ))
        expected2 = list(skbio.io.read(
            '%s/Human-Armpit_S2_L001_R1_001.fastq.gz' % str(input),
            format='fastq', constructor=skbio.DNA
        ))
        expected = \
            list(zip(expected1, ['Human-Kneecap'] * len(expected1))) + \
            list(zip(expected2, ['Human-Armpit'] * len(expected2)))
        observed = skbio.io.read(
            '%s/seqs.fna' % str(observed),
            format='fasta', constructor=skbio.DNA
        )
        observed = list(observed)

        self.assertEqual(len(observed), len(expected))

        for i, obs in enumerate(observed):
            # identifiers are as expected
            self.assertEqual(obs.metadata['id'],
                             '%s_%d' % (expected[i][1], i))
            # sequences are as expected
            self.assertEqual(str(obs), str(expected[i][0]))

    def test_slpssefdf_to_qiime1demuxdf_bad_sample_ids(self):
        filenames = ('single-end-two-sample-data2/MANIFEST',
                     'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz',
                     'Human-Armpit_S2_L001_R1_001.fastq.gz')
        with self.assertRaisesRegex(ValueError,
                                    expected_regex='space.*Human-K'):
            self.transform_format(
                SingleLanePerSampleSingleEndFastqDirFmt,
                QIIME1DemuxDirFmt, filenames=filenames)

        filenames = ('single-end-two-sample-data3/MANIFEST',
                     'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz',
                     'Human-Armpit_S2_L001_R1_001.fastq.gz')
        with self.assertRaisesRegex(ValueError,
                                    expected_regex='space.*Human-A'):
            self.transform_format(
                SingleLanePerSampleSingleEndFastqDirFmt,
                QIIME1DemuxDirFmt, filenames=filenames)

    def test_casava_one_eight_laneless_per_sample_dirfmt_to_slpspefd(self):
        filenames = ('Human-Kneecap_S1_R1_001.fastq.gz',
                     'Human-Armpit_S2_R1_001.fastq.gz')

        input, dirfmt = self.transform_format(
            CasavaOneEightLanelessPerSampleDirFmt,
            SingleLanePerSampleSingleEndFastqDirFmt, filenames=filenames
        )
        expected_filepaths = ['Human-Kneecap_S1_L001_R1_001.fastq.gz',
                              'Human-Armpit_S2_L001_R1_001.fastq.gz']

        for path, view in dirfmt.sequences.iter_views(FastqGzFormat):
            self.assertIn(path.name, expected_filepaths)

        df = dirfmt.manifest.view(pd.DataFrame)
        for name in df['forward']:
            self.assertTrue((dirfmt.path / name).exists())

    def test_casava_one_eight_single_lane_per_sample_dirfmt_to_slpssefdf(self):
        filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',)
        input, obs = self.transform_format(
            CasavaOneEightSingleLanePerSampleDirFmt,
            SingleLanePerSampleSingleEndFastqDirFmt, filenames=filenames
        )

        input = skbio.io.read(
            '%s/Human-Kneecap_S1_L001_R1_001.fastq.gz' % str(input),
            format='fastq', constructor=skbio.DNA
        )
        obs = skbio.io.read(
            '%s/Human-Kneecap_S1_L001_R1_001.fastq.gz' % str(obs),
            format='fastq', constructor=skbio.DNA
        )

        for act, exp in zip(obs, input):
            self.assertEqual(act, exp)

    def test_casava_one_eight_single_lane_per_sample_dirfmt_to_slpspefdf(self):
        filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',)
        input, obs = self.transform_format(
            CasavaOneEightSingleLanePerSampleDirFmt,
            SingleLanePerSampleSingleEndFastqDirFmt, filenames=filenames
        )

        input = skbio.io.read(
            '%s/Human-Kneecap_S1_L001_R1_001.fastq.gz' % str(input),
            format='fastq', constructor=skbio.DNA
        )
        obs = skbio.io.read(
            '%s/Human-Kneecap_S1_L001_R1_001.fastq.gz' % str(obs),
            format='fastq', constructor=skbio.DNA
        )

        for act, exp in zip(obs, input):
            self.assertEqual(act, exp)

    def test_miseq_demux_dirfmt_to_slpssefdf(self):
        input, obs = self.transform_format(
            CasavaOneEightLanelessPerSampleDirFmt,
            SingleLanePerSampleSingleEndFastqDirFmt,
            filenames=('Human-Kneecap_S1_R1_001.fastq.gz',),
        )

        input = skbio.io.read(
            '%s/Human-Kneecap_S1_R1_001.fastq.gz' % str(input),
            format='fastq', constructor=skbio.DNA
        )
        obs = skbio.io.read(
            '%s/Human-Kneecap_S1_L001_R1_001.fastq.gz' % str(obs),
            format='fastq', constructor=skbio.DNA
        )

        for act, exp in zip(obs, input):
            self.assertEqual(act, exp)

    def test_miseq_demux_dirfmt_to_slpspefdf(self):
        input, obs = self.transform_format(
            CasavaOneEightLanelessPerSampleDirFmt,
            SingleLanePerSampleSingleEndFastqDirFmt,
            filenames=('Human-Kneecap_S1_R1_001.fastq.gz',),
        )

        input = skbio.io.read(
            '%s/Human-Kneecap_S1_R1_001.fastq.gz' % str(input),
            format='fastq', constructor=skbio.DNA
        )
        obs = skbio.io.read(
            '%s/Human-Kneecap_S1_L001_R1_001.fastq.gz' % str(obs),
            format='fastq', constructor=skbio.DNA
        )

        for act, exp in zip(obs, input):
            self.assertEqual(act, exp)

    def test_fastqmanifest_single(self):
        _, dirfmt = self.transform_format(
            CasavaOneEightSingleLanePerSampleDirFmt,
            SingleLanePerSampleSingleEndFastqDirFmt,
            filenames=('Human-Kneecap_S1_L001_R1_001.fastq.gz',
                       'Human-Armpit_S2_L001_R1_001.fastq.gz'),
        )

        df = dirfmt.manifest.view(pd.DataFrame)

        self.assertEqual(set(df.index), {'Human-Kneecap', 'Human-Armpit'})
        self.assertEqual(set(df.columns), {'forward'})
        self.assertTrue(os.path.exists(df['forward'].loc['Human-Kneecap']))
        self.assertTrue(os.path.exists(df['forward'].loc['Human-Armpit']))

    def test_fastqmanifest_single_numeric(self):
        _, dirfmt = self.transform_format(
            CasavaOneEightSingleLanePerSampleDirFmt,
            SingleLanePerSampleSingleEndFastqDirFmt,
            filenames=('1_S1_L001_R1_001.fastq.gz',
                       '0.10_S2_L001_R1_001.fastq.gz'),
        )

        df = dirfmt.manifest.view(pd.DataFrame)

        self.assertEqual(set(df.index), {'1', '0.10'})
        self.assertEqual(set(df.columns), {'forward'})
        self.assertTrue(os.path.exists(df['forward'].loc['1']))
        self.assertTrue(os.path.exists(df['forward'].loc['0.10']))

    def test_fastqmanifest_paired(self):
        _, dirfmt = self.transform_format(
            CasavaOneEightSingleLanePerSampleDirFmt,
            SingleLanePerSamplePairedEndFastqDirFmt,
            filenames=(
                'Human-Kneecap_S1_L001_R1_001.fastq.gz',
                'paired_end_data/Human-Kneecap_S1_L001_R2_001.fastq.gz'),
        )

        df = dirfmt.manifest.view(pd.DataFrame)

        self.assertEqual(set(df.index), {'Human-Kneecap'})
        self.assertEqual(set(df.columns), {'forward', 'reverse'})
        self.assertTrue(os.path.exists(df['forward'].loc['Human-Kneecap']))
        self.assertTrue(os.path.exists(df['reverse'].loc['Human-Kneecap']))

    def test_fastqmanifest_paired_numeric(self):
        _, dirfmt = self.transform_format(
            CasavaOneEightSingleLanePerSampleDirFmt,
            SingleLanePerSamplePairedEndFastqDirFmt,
            filenames=(
                '1_S1_L001_R1_001.fastq.gz', '0.10_S2_L001_R1_001.fastq.gz',
                'paired_end_data_numeric/1_S1_L001_R2_001.fastq.gz',
                'paired_end_data_numeric/0.10_S2_L001_R2_001.fastq.gz'),
        )

        df = dirfmt.manifest.view(pd.DataFrame)

        self.assertEqual(set(df.index), {'1', '0.10'})
        self.assertEqual(set(df.columns), {'forward', 'reverse'})
        self.assertTrue(os.path.exists(df['forward'].loc['1']))
        self.assertTrue(os.path.exists(df['reverse'].loc['1']))
        self.assertTrue(os.path.exists(df['forward'].loc['0.10']))
        self.assertTrue(os.path.exists(df['reverse'].loc['0.10']))

    def test_slpssefdf_to_casava_one_eight_single_lane_per_sample_dirfmt(self):
        filenames = ('single-end-two-sample-data1/MANIFEST',
                     'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz',
                     'Human-Armpit_S2_L001_R1_001.fastq.gz')

        input, obs = self.transform_format(
            SingleLanePerSampleSingleEndFastqDirFmt,
            CasavaOneEightSingleLanePerSampleDirFmt, filenames=filenames
        )

        self.assertEqual(input.validate(), None)

        exp_fp = ['Human-Armpit_S2_L001_R1_001.fastq.gz',
                  'Human-Kneecap_S1_L001_R1_001.fastq.gz']
        obs_fp = [str(fp) for fp, _ in obs.sequences.iter_views(FastqGzFormat)]

        self.assertEqual(obs_fp, exp_fp)

    def test_slpspefdf_to_casava_one_eight_single_lane_per_sample_dirfmt(self):
        filenames = ('Human-Kneecap_S1_L001_R1_001.fastq.gz',
                     'paired_end_data/Human-Kneecap_S1_L001_R2_001.fastq.gz',
                     'paired_end_data/MANIFEST',
                     'metadata.yml')
        input, obs = self.transform_format(
            SingleLanePerSamplePairedEndFastqDirFmt,
            CasavaOneEightSingleLanePerSampleDirFmt, filenames=filenames
        )

        self.assertEqual(input.validate(), None)

        exp_fp = ['Human-Kneecap_S1_L001_R1_001.fastq.gz',
                  'Human-Kneecap_S1_L001_R2_001.fastq.gz']
        obs_fp = [str(fp) for fp, _ in obs.sequences.iter_views(FastqGzFormat)]

        self.assertEqual(obs_fp, exp_fp)

    def test_sample_id_indexed_fastq_to_slpssefdf_fmt(self):
        filenames = ('Human-Armpit.fastq.gz',
                     # regardless of how much the file name looks like
                     # Casava, everything before the .fastq.gz should be
                     # treated as the sample id
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz')
        input, obs = self.transform_format(
            SampleIdIndexedSingleEndPerSampleDirFmt,
            SingleLanePerSampleSingleEndFastqDirFmt,
            filenames=filenames
        )

        input.validate()

        exp_fp = ['Human-Armpit_na_L001_R1_001.fastq.gz',
                  'Human-Kneecap_S1_L001_R1_001_na_L001_R1_001.fastq.gz']
        obs_fp = [str(fp) for fp, _ in obs.sequences.iter_views(FastqGzFormat)]
        self.assertEqual(obs_fp, exp_fp)

        manifest_df = obs.manifest.view(pd.DataFrame)
        self.assertEqual(list(manifest_df.index),
                         ['Human-Armpit', 'Human-Kneecap_S1_L001_R1_001'])

    def test_sample_id_indexed_fastq_to_slpssefdf_fmt_bad_fastq(self):
        filenames = ('Human-Armpit.fastq.gz',
                     'invalid-quality.fastq.gz')
        with self.assertRaisesRegex(ValidationError, 'Quality score length'):
            self.transform_format(
                SampleIdIndexedSingleEndPerSampleDirFmt,
                SingleLanePerSampleSingleEndFastqDirFmt,
                filenames=filenames
            )


class TestFastqManifestTransformers(TestPluginBase):
    package = "q2_types.per_sample_sequences.tests"

    def test_single_end_fastq_manifest_phred33_to_slpssefdf(self):
        format_ = SingleEndFastqManifestPhred33
        transformer = self.get_transformer(
            format_,
            SingleLanePerSampleSingleEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz'),
            os.path.join(self.temp_dir.name,
                         'Human-Kneecap_S1_L001_R1_001.fastq.gz'))
        shutil.copy(
            self.get_data_path('Human-Armpit.fastq.gz'),
            os.path.join(self.temp_dir.name, 'Human-Armpit.fastq.gz'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/Human-Kneecap_S1_L001_R1_001.fastq.gz,"
                     "forward\n" % self.temp_dir.name)
            fh.write("sampleXYZ,%s/Human-Armpit.fastq.gz,forward\n"
                     % self.temp_dir.name)

        obs = transformer(format_(manifest_fp, 'r'))

        fastq_pairs = [('Human-Kneecap_S1_L001_R1_001.fastq.gz',
                        'sampleABC_0_L001_R1_001.fastq.gz'),
                       ('Human-Armpit.fastq.gz',
                        'sampleXYZ_1_L001_R1_001.fastq.gz')]
        for input_fastq, obs_fastq in fastq_pairs:
            obs_fh = skbio.io.read(
                os.path.join(str(obs), obs_fastq), compression='gzip',
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )
            exp_fh = skbio.io.read(
                self.get_data_path(input_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )

            for o, e in zip(obs_fh, exp_fh):
                self.assertEqual(o, e)

        obs_metadata = yaml.load(open('%s/metadata.yml' % str(obs)),
                                 Loader=yaml.SafeLoader)
        exp_metadata = yaml.load("{'phred-offset': 33}",
                                 Loader=yaml.SafeLoader)
        self.assertEqual(obs_metadata, exp_metadata)

        obs_manifest = open('%s/MANIFEST' % (str(obs))).read()
        exp_manifest = ("sample-id,filename,direction\n"
                        "sampleABC,sampleABC_0_L001_R1_001.fastq.gz,forward\n"
                        "sampleXYZ,sampleXYZ_1_L001_R1_001.fastq.gz,forward\n")
        self.assertEqual(obs_manifest, exp_manifest)

    def test_single_end_fastq_manifest_phred33_to_slpssefdf_uncompressed(self):
        format_ = SingleEndFastqManifestPhred33
        transformer = self.get_transformer(
            format_,
            SingleLanePerSampleSingleEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq'),
            os.path.join(self.temp_dir.name,
                         'Human-Kneecap_S1_L001_R1_001.fastq'))
        shutil.copy(
            self.get_data_path('Human-Armpit.fastq'),
            os.path.join(self.temp_dir.name, 'Human-Armpit.fastq'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/Human-Kneecap_S1_L001_R1_001.fastq,"
                     "forward\n" % self.temp_dir.name)
            fh.write("sampleXYZ,%s/Human-Armpit.fastq,forward\n"
                     % self.temp_dir.name)

        obs = transformer(format_(manifest_fp, 'r'))

        fastq_pairs = [('Human-Kneecap_S1_L001_R1_001.fastq',
                        'sampleABC_0_L001_R1_001.fastq.gz'),
                       ('Human-Armpit.fastq',
                        'sampleXYZ_1_L001_R1_001.fastq.gz')]
        for input_fastq, obs_fastq in fastq_pairs:
            obs_fh = skbio.io.read(
                os.path.join(str(obs), obs_fastq), compression='gzip',
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )
            exp_fh = skbio.io.read(
                self.get_data_path(input_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )

            for o, e in zip(obs_fh, exp_fh):
                self.assertEqual(o, e)

        obs_metadata = yaml.load(open('%s/metadata.yml' % str(obs)),
                                 Loader=yaml.SafeLoader)
        exp_metadata = yaml.load("{'phred-offset': 33}",
                                 Loader=yaml.SafeLoader)
        self.assertEqual(obs_metadata, exp_metadata)

        obs_manifest = open('%s/MANIFEST' % (str(obs))).read()
        exp_manifest = ("sample-id,filename,direction\n"
                        "sampleABC,sampleABC_0_L001_R1_001.fastq.gz,forward\n"
                        "sampleXYZ,sampleXYZ_1_L001_R1_001.fastq.gz,forward\n")
        self.assertEqual(obs_manifest, exp_manifest)

    def test_single_end_fastq_manifest_phred64_to_slpssefdf(self):
        format_ = SingleEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSampleSingleEndFastqDirFmt)
        shutil.copy(
            self.get_data_path('s1-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's1-phred64.fastq.gz'))
        shutil.copy(
            self.get_data_path('s2-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's2-phred64.fastq.gz'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                     "forward\n" % self.temp_dir.name)
            fh.write("sampleXYZ,%s/s2-phred64.fastq.gz,forward\n" %
                     self.temp_dir.name)

        obs = transformer(format_(manifest_fp, 'r'))

        fastq_pairs = [('s1-phred64.fastq.gz',
                        'sampleABC_0_L001_R1_001.fastq.gz'),
                       ('s2-phred64.fastq.gz',
                        'sampleXYZ_1_L001_R1_001.fastq.gz')]
        for input_fastq, obs_fastq in fastq_pairs:
            obs_fh = skbio.io.read(
                os.path.join(str(obs), obs_fastq), compression='gzip',
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )
            exp_fh = skbio.io.read(
                self.get_data_path(input_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.3'
            )

            for o, e in zip(obs_fh, exp_fh):
                self.assertEqual(o, e)

        obs_metadata = yaml.load(open('%s/metadata.yml' % str(obs)),
                                 Loader=yaml.SafeLoader)
        exp_metadata = yaml.load("{'phred-offset': 33}",
                                 Loader=yaml.SafeLoader)
        self.assertEqual(obs_metadata, exp_metadata)

        obs_manifest = open('%s/MANIFEST' % (str(obs))).read()
        exp_manifest = ("sample-id,filename,direction\n"
                        "sampleABC,sampleABC_0_L001_R1_001.fastq.gz,forward\n"
                        "sampleXYZ,sampleXYZ_1_L001_R1_001.fastq.gz,forward\n")
        self.assertEqual(obs_manifest, exp_manifest)

    def test_single_end_fastq_manifest_phred64_to_slpssefdf_uncompressed(self):
        format_ = SingleEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSampleSingleEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('s1-phred64.fastq'),
            os.path.join(self.temp_dir.name, 's1-phred64.fastq'))
        shutil.copy(
            self.get_data_path('s2-phred64.fastq'),
            os.path.join(self.temp_dir.name, 's2-phred64.fastq'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/s1-phred64.fastq,"
                     "forward\n" % self.temp_dir.name)
            fh.write("sampleXYZ,%s/s2-phred64.fastq,forward\n" %
                     self.temp_dir.name)

        obs = transformer(format_(manifest_fp, 'r'))

        fastq_pairs = [('s1-phred64.fastq',
                        'sampleABC_0_L001_R1_001.fastq.gz'),
                       ('s2-phred64.fastq',
                        'sampleXYZ_1_L001_R1_001.fastq.gz')]
        for input_fastq, obs_fastq in fastq_pairs:
            obs_fh = skbio.io.read(
                os.path.join(str(obs), obs_fastq), compression='gzip',
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )
            exp_fh = skbio.io.read(
                self.get_data_path(input_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.3'
            )

            for o, e in zip(obs_fh, exp_fh):
                self.assertEqual(o, e)

        obs_metadata = yaml.load(open('%s/metadata.yml' % str(obs)),
                                 Loader=yaml.SafeLoader)
        exp_metadata = yaml.load("{'phred-offset': 33}",
                                 Loader=yaml.SafeLoader)
        self.assertEqual(obs_metadata, exp_metadata)

        obs_manifest = open('%s/MANIFEST' % (str(obs))).read()
        exp_manifest = ("sample-id,filename,direction\n"
                        "sampleABC,sampleABC_0_L001_R1_001.fastq.gz,forward\n"
                        "sampleXYZ,sampleXYZ_1_L001_R1_001.fastq.gz,forward\n")
        self.assertEqual(obs_manifest, exp_manifest)

    def test_paired_end_fastq_manifest_phred33_to_slpspefdf(self):
        format_ = PairedEndFastqManifestPhred33
        transformer = self.get_transformer(
            format_,
            SingleLanePerSamplePairedEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz'),
            os.path.join(self.temp_dir.name,
                         'Human-Kneecap_S1_L001_R1_001.fastq.gz'))
        shutil.copy(
            self.get_data_path('Human-Armpit.fastq.gz'),
            os.path.join(self.temp_dir.name, 'Human-Armpit.fastq.gz'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/Human-Kneecap_S1_L001_R1_001.fastq.gz,"
                     "forward\n" % self.temp_dir.name)
            fh.write("sampleABC,%s/Human-Armpit.fastq.gz,reverse\n"
                     % self.temp_dir.name)

        obs = transformer(format_(manifest_fp, 'r'))

        fastq_pairs = [('Human-Kneecap_S1_L001_R1_001.fastq.gz',
                        'sampleABC_0_L001_R1_001.fastq.gz'),
                       ('Human-Armpit.fastq.gz',
                        'sampleABC_1_L001_R2_001.fastq.gz')]
        for input_fastq, obs_fastq in fastq_pairs:
            obs_fh = skbio.io.read(
                os.path.join(str(obs), obs_fastq), compression='gzip',
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )
            exp_fh = skbio.io.read(
                self.get_data_path(input_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )

            for o, e in zip(obs_fh, exp_fh):
                self.assertEqual(o, e)

        obs_metadata = yaml.load(open('%s/metadata.yml' % str(obs)),
                                 Loader=yaml.SafeLoader)
        exp_metadata = yaml.load("{'phred-offset': 33}",
                                 Loader=yaml.SafeLoader)
        self.assertEqual(obs_metadata, exp_metadata)

        obs_manifest = open('%s/MANIFEST' % (str(obs))).read()
        exp_manifest = ("sample-id,filename,direction\n"
                        "sampleABC,sampleABC_0_L001_R1_001.fastq.gz,forward\n"
                        "sampleABC,sampleABC_1_L001_R2_001.fastq.gz,reverse\n")
        self.assertEqual(obs_manifest, exp_manifest)

    def test_paired_end_fastq_manifest_phred33_to_slpspefdf_uncompressed(self):
        format_ = PairedEndFastqManifestPhred33
        transformer = self.get_transformer(
            format_,
            SingleLanePerSamplePairedEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq'),
            os.path.join(self.temp_dir.name,
                         'Human-Kneecap_S1_L001_R1_001.fastq'))
        shutil.copy(
            self.get_data_path('Human-Armpit.fastq'),
            os.path.join(self.temp_dir.name, 'Human-Armpit.fastq'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/Human-Kneecap_S1_L001_R1_001.fastq,"
                     "forward\n" % self.temp_dir.name)
            fh.write("sampleABC,%s/Human-Armpit.fastq,reverse\n"
                     % self.temp_dir.name)

        obs = transformer(format_(manifest_fp, 'r'))

        fastq_pairs = [('Human-Kneecap_S1_L001_R1_001.fastq',
                        'sampleABC_0_L001_R1_001.fastq.gz'),
                       ('Human-Armpit.fastq',
                        'sampleABC_1_L001_R2_001.fastq.gz')]
        for input_fastq, obs_fastq in fastq_pairs:
            obs_fh = skbio.io.read(
                os.path.join(str(obs), obs_fastq), compression='gzip',
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )
            exp_fh = skbio.io.read(
                self.get_data_path(input_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )

            for o, e in zip(obs_fh, exp_fh):
                self.assertEqual(o, e)

        obs_metadata = yaml.load(open('%s/metadata.yml' % str(obs)),
                                 Loader=yaml.SafeLoader)
        exp_metadata = yaml.load("{'phred-offset': 33}",
                                 Loader=yaml.SafeLoader)
        self.assertEqual(obs_metadata, exp_metadata)

        obs_manifest = open('%s/MANIFEST' % (str(obs))).read()
        exp_manifest = ("sample-id,filename,direction\n"
                        "sampleABC,sampleABC_0_L001_R1_001.fastq.gz,forward\n"
                        "sampleABC,sampleABC_1_L001_R2_001.fastq.gz,reverse\n")
        self.assertEqual(obs_manifest, exp_manifest)

    def test_paired_end_fastq_manifest_phred64_to_slpspefdf(self):
        format_ = PairedEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSamplePairedEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('s1-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's1-phred64.fastq.gz'))
        shutil.copy(
            self.get_data_path('s2-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's2-phred64.fastq.gz'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                     "forward\n" % self.temp_dir.name)
            fh.write("sampleABC,%s/s2-phred64.fastq.gz,reverse\n" %
                     self.temp_dir.name)

        obs = transformer(format_(manifest_fp, 'r'))

        fastq_pairs = [('s1-phred64.fastq.gz',
                        'sampleABC_0_L001_R1_001.fastq.gz'),
                       ('s2-phred64.fastq.gz',
                        'sampleABC_1_L001_R2_001.fastq.gz')]
        for input_fastq, obs_fastq in fastq_pairs:
            obs_fh = skbio.io.read(
                os.path.join(str(obs), obs_fastq), compression='gzip',
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )
            exp_fh = skbio.io.read(
                self.get_data_path(input_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.3'
            )

            for o, e in zip(obs_fh, exp_fh):
                self.assertEqual(o, e)

        obs_metadata = yaml.load(open('%s/metadata.yml' % str(obs)),
                                 Loader=yaml.SafeLoader)
        exp_metadata = yaml.load("{'phred-offset': 33}",
                                 Loader=yaml.SafeLoader)
        self.assertEqual(obs_metadata, exp_metadata)

        obs_manifest = open('%s/MANIFEST' % (str(obs))).read()
        exp_manifest = ("sample-id,filename,direction\n"
                        "sampleABC,sampleABC_0_L001_R1_001.fastq.gz,forward\n"
                        "sampleABC,sampleABC_1_L001_R2_001.fastq.gz,reverse\n")
        self.assertEqual(obs_manifest, exp_manifest)

    def test_paired_end_fastq_manifest_phred64_to_slpspefdf_uncompressed(self):
        format_ = PairedEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSamplePairedEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('s1-phred64.fastq'),
            os.path.join(self.temp_dir.name, 's1-phred64.fastq'))
        shutil.copy(
            self.get_data_path('s2-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's2-phred64.fastq'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/s1-phred64.fastq,"
                     "forward\n" % self.temp_dir.name)
            fh.write("sampleABC,%s/s2-phred64.fastq,reverse\n" %
                     self.temp_dir.name)

        obs = transformer(format_(manifest_fp, 'r'))

        fastq_pairs = [('s1-phred64.fastq',
                        'sampleABC_0_L001_R1_001.fastq.gz'),
                       ('s2-phred64.fastq',
                        'sampleABC_1_L001_R2_001.fastq.gz')]
        for input_fastq, obs_fastq in fastq_pairs:
            obs_fh = skbio.io.read(
                os.path.join(str(obs), obs_fastq), compression='gzip',
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )
            exp_fh = skbio.io.read(
                self.get_data_path(input_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.3'
            )

            for o, e in zip(obs_fh, exp_fh):
                self.assertEqual(o, e)

        obs_metadata = yaml.load(open('%s/metadata.yml' % str(obs)),
                                 Loader=yaml.SafeLoader)
        exp_metadata = yaml.load("{'phred-offset': 33}",
                                 Loader=yaml.SafeLoader)
        self.assertEqual(obs_metadata, exp_metadata)

        obs_manifest = open('%s/MANIFEST' % (str(obs))).read()
        exp_manifest = ("sample-id,filename,direction\n"
                        "sampleABC,sampleABC_0_L001_R1_001.fastq.gz,forward\n"
                        "sampleABC,sampleABC_1_L001_R2_001.fastq.gz,reverse\n")
        self.assertEqual(obs_manifest, exp_manifest)

    def test_single_end_fastq_manifest_missing_fastq(self):
        format_ = SingleEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSampleSingleEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('s1-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's1-phred64.fastq.gz'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                     "forward\n" % self.temp_dir.name)
            fh.write("sampleXYZ,%s/s2-phred64.fastq.gz,forward\n" %
                     self.temp_dir.name)

        with self.assertRaisesRegex(FileNotFoundError,
                                    "s2-phred64.fastq.gz"):
            transformer(format_(manifest_fp, 'r'))

    def test_single_end_fastq_manifest_invalid_direction(self):
        format_ = SingleEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSampleSingleEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('s1-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's1-phred64.fastq.gz'))
        shutil.copy(
            self.get_data_path('s2-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's2-phred64.fastq.gz'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                     "middle-out\n" % self.temp_dir.name)
            fh.write("sampleXYZ,%s/s2-phred64.fastq.gz,forward\n" %
                     self.temp_dir.name)

        with self.assertRaisesRegex(ValueError, 'middle-out'):
            transformer(format_(manifest_fp, 'r'))

    def test_single_end_fastq_manifest_too_many_directions(self):
        format_ = SingleEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSampleSingleEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('s1-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's1-phred64.fastq.gz'))
        shutil.copy(
            self.get_data_path('s2-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's2-phred64.fastq.gz'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                     "forward\n" % self.temp_dir.name)
            fh.write("sampleXYZ,%s/s2-phred64.fastq.gz,reverse\n" %
                     self.temp_dir.name)

        with self.assertRaisesRegex(ValueError, "only forward or reverse"):
            transformer(format_(manifest_fp, 'r'))

    def test_paired_end_fastq_manifest_missing_fastq(self):
        format_ = PairedEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSamplePairedEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('s1-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's1-phred64.fastq.gz'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                     "forward\n" % self.temp_dir.name)
            fh.write("sampleABC,%s/s2-phred64.fastq.gz,reverse\n" %
                     self.temp_dir.name)

        with self.assertRaisesRegex(FileNotFoundError,
                                    "s2-phred64.fastq.gz"):
            transformer(format_(manifest_fp, 'r'))

    def test_paired_end_fastq_manifest_invalid_direction(self):
        format_ = PairedEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSamplePairedEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('s1-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's1-phred64.fastq.gz'))
        shutil.copy(
            self.get_data_path('s2-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's2-phred64.fastq.gz'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                     "middle-out\n" % self.temp_dir.name)
            fh.write("sampleABC,%s/s2-phred64.fastq.gz,reverse\n" %
                     self.temp_dir.name)

        with self.assertRaisesRegex(ValueError, 'middle-out'):
            transformer(format_(manifest_fp, 'r'))

    def test_paired_end_fastq_manifest_missing_directions(self):
        format_ = PairedEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSamplePairedEndFastqDirFmt)

        shutil.copy(
            self.get_data_path('s1-phred64.fastq.gz'),
            os.path.join(self.temp_dir.name, 's1-phred64.fastq.gz'))

        manifest_fp = os.path.join(self.temp_dir.name, 'manifest')
        with open(manifest_fp, 'w') as fh:
            fh.write("sample-id,absolute-filepath,direction\n")
            fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                     "forward\n" % self.temp_dir.name)

        with self.assertRaisesRegex(ValueError,
                                    "one time each for each sample"):
            transformer(format_(manifest_fp, 'r'))

    def test_parse_and_validate_manifest_invalid(self):
        manifest = io.StringIO(
            'sample-id,absolute-filepath\n'
            'abc,/hello/world,forward\n')
        with self.assertRaisesRegex(
                ValueError, "Expected.*absolute-filepath.*found "
                            "'sample-id,absolute-filepath'.$"):
            _parse_and_validate_manifest_partial(
                manifest, single_end=True, absolute=True)

        manifest = io.StringIO(
            'sample-id,absolute-filepath,direction\n'
            'abc,/hello/world\n'
            'abc,/hello/world,forward\n')
        with self.assertRaisesRegex(ValueError, 'Empty cells'):
            _parse_and_validate_manifest_partial(
                manifest, single_end=True, absolute=True)

        manifest = io.StringIO(
            'sample-id,absolute-filepath,direction\n'
            'abc,/hello/world,forward\n'
            'xyz,/hello/world,forward,extra-field')
        with self.assertRaisesRegex(ValueError, 'issue parsing the manifest'):
            _parse_and_validate_manifest_partial(
                manifest, single_end=True, absolute=True)

        manifest = io.StringIO(
            'sample-id,absolute-filepath,direction\n'
            'abc,world,forward\n'
            'xyz,world,forward')
        with self.assertRaisesRegex(ValueError,
                                    'absolute but found relative path'):
            _parse_and_validate_manifest_partial(
                manifest, single_end=True, absolute=True)

        manifest = io.StringIO(
            'sample-id,absolute-filepath,direction\n'
            'abc,world,forward\n'
            'abc,world,reverse')
        with self.assertRaisesRegex(ValueError,
                                    'absolute but found relative path'):
            _parse_and_validate_manifest_partial(
                manifest, single_end=False, absolute=True)

        manifest = io.StringIO(
            'sample-id,filename,direction\n'
            'abc,/snap/crackle/pop/world,forward\n'
            'xyz,/snap/crackle/pop/world,forward')
        with self.assertRaisesRegex(ValueError,
                                    'relative but found absolute path'):
            _parse_and_validate_manifest_partial(
                manifest, single_end=True, absolute=False)

        manifest = io.StringIO(
            'sample-id,filename,direction\n'
            'abc,/snap/crackle/pop/world,forward\n'
            'abc,/snap/crackle/pop/world,reverse')
        with self.assertRaisesRegex(ValueError,
                                    'relative but found absolute path'):
            _parse_and_validate_manifest_partial(
                manifest, single_end=False, absolute=False)

    def test_parse_and_validate_manifest_expand_vars(self):
        expected_fp = os.path.join(self.temp_dir.name, 'manifest.txt')
        # touch the file - the valdiator will fail if it doesn't exist
        open(expected_fp, 'w')
        os.environ['TESTENVGWAR'] = self.temp_dir.name
        manifest = io.StringIO(
            'sample-id,absolute-filepath,direction\n'
            'abc,$TESTENVGWAR/manifest.txt,forward')
        manifest = _parse_and_validate_manifest_partial(
            manifest, single_end=True, absolute=True)
        del os.environ['TESTENVGWAR']

        self.assertEqual(manifest.iloc[0]['absolute-filepath'], expected_fp)

    def test_validate_header_valid(self):
        columns = ['sample-id', 'absolute-filepath', 'direction']
        manifest = pd.DataFrame(
            [['abc', '/hello/world', 'forward'],
             ['xyz', '/hello/world', 'forward']],
            columns=columns)
        # should not raise an error
        _validate_header(manifest, expected_header=columns)

    def test_validate_header_invalid(self):
        columns = ['sample-id', 'absolute-filepath', 'direction']
        manifest = pd.DataFrame(
            [['abc', '/hello/world'],
             ['xyz', '/hello/world']],
            columns=['xyz', 'absolute-filepath'])
        with self.assertRaisesRegex(ValueError, 'Expected manifest.*absolute'
                                                '-filepath.*but'):
            _validate_header(manifest, expected_header=columns)

        manifest = pd.DataFrame(
            [['abc', '/hello/world', 'forward'],
             ['xyz', '/hello/world', 'forward']],
            columns=['xyz', 'absolute-filepath', 'direction'])
        with self.assertRaisesRegex(ValueError, 'sample-id.*xyz'):
            _validate_header(manifest, expected_header=columns)

        manifest = pd.DataFrame(
            [['abc', '/hello/world', 'forward'],
             ['xyz', '/hello/world', 'forward']],
            columns=['sample-id', 'xyz', 'direction'])
        with self.assertRaisesRegex(ValueError, 'absolute-filepath.*xyz'):
            _validate_header(manifest, expected_header=columns)

        manifest = pd.DataFrame(
            [['abc', '/hello/world', 'forward'],
             ['xyz', '/hello/world', 'forward']],
            columns=['sample-id', 'absolute-filepath', 'xyz'])
        with self.assertRaisesRegex(ValueError, 'direction.*xyz'):
            _validate_header(manifest, expected_header=columns)

    def test_validate_single_end_fastq_manifest_directions(self):
        manifest = pd.DataFrame(
            [['abc', '/hello/world', 'forward'],
             ['xyz', '/hello/world', 'forward']],
            columns=['sample-id', 'absolute-filepath', 'direction'])
        _validate_single_end_fastq_manifest_directions(manifest)

        manifest = pd.DataFrame(
            [['abc', '/hello/world', 'reverse'],
             ['xyz', '/hello/world', 'reverse']],
            columns=['sample-id', 'absolute-filepath', 'direction'])
        _validate_single_end_fastq_manifest_directions(manifest)

    def test_validate_single_end_fastq_manifest_directions_invalid(self):
        manifest = pd.DataFrame(
            [['abc', '/hello/world', 'forward'],
             ['xyz', '/hello/world', 'reverse']],
            columns=['sample-id', 'absolute-filepath', 'direction'])
        with self.assertRaisesRegex(ValueError, 'can contain only'):
            _validate_single_end_fastq_manifest_directions(manifest)

        manifest = pd.DataFrame(
            [['abc', '/hello/world', 'forward'],
             ['abc', '/hello/world2', 'forward']],
            columns=['sample-id', 'absolute-filepath', 'direction'])
        with self.assertRaisesRegex(ValueError, 'more than once'):
            _validate_single_end_fastq_manifest_directions(manifest)

    def test_validate_paired_end_fastq_manifest_directions(self):
        manifest = pd.DataFrame(
            [['abc', '/hello/world', 'forward'],
             ['abc', '/hello/world', 'reverse'],
             ['xyz', '/hello/world2', 'forward'],
             ['xyz', '/hello/world2', 'reverse']],
            columns=['sample-id', 'absolute-filepath', 'direction'])
        _validate_paired_end_fastq_manifest_directions(manifest)

    def test_validate_paired_end_fastq_manifest_directions_invalid(self):
        manifest = pd.DataFrame(
            [['abc', '/hello/world', 'forward'],
             ['abc', '/hello/world', 'reverse'],
             ['xyz', '/hello/world2', 'reverse']],
            columns=['sample-id', 'absolute-filepath', 'direction'])
        with self.assertRaisesRegex(ValueError, 'reverse but not.*xyz'):
            _validate_paired_end_fastq_manifest_directions(manifest)

        manifest = pd.DataFrame(
            [['abc', '/hello/world', 'forward'],
             ['abc', '/hello/world', 'reverse'],
             ['xyz', '/hello/world2', 'forward']],
            columns=['sample-id', 'absolute-filepath', 'direction'])
        with self.assertRaisesRegex(ValueError, 'forward but not.*xyz'):
            _validate_paired_end_fastq_manifest_directions(manifest)

        manifest = pd.DataFrame(
            [['abc', '/hello/world', 'forward'],
             ['abc', '/hello/world', 'reverse'],
             ['abc', '/hello/world2', 'forward']],
            columns=['sample-id', 'absolute-filepath', 'direction'])
        with self.assertRaisesRegex(ValueError, 'forward read record: abc'):
            _validate_paired_end_fastq_manifest_directions(manifest)

        manifest = pd.DataFrame(
            [['xyz', '/hello/world', 'forward'],
             ['xyz', '/hello/world', 'reverse'],
             ['xyz', '/hello/world2', 'reverse']],
            columns=['sample-id', 'absolute-filepath', 'direction'])
        with self.assertRaisesRegex(ValueError, 'reverse read record: xyz'):
            _validate_paired_end_fastq_manifest_directions(manifest)


# NOTE: we are really only interested in the manifest, since these transformers
# primarily transform the V2 TSV manifests to the (older) CSV manifests. The
# only things asserted here are facts about the manifest and not the actual
# data assets, themselves.
class TestFastqManifestV2Transformers(TestPluginBase):
    package = "q2_types.per_sample_sequences.tests"

    def setUp(self):
        super().setUp()
        self.se_formats = [SingleEndFastqManifestPhred33V2,
                           SingleEndFastqManifestPhred64V2]
        self.pe_formats = [PairedEndFastqManifestPhred33V2,
                           PairedEndFastqManifestPhred64V2]
        self.exp_se_manifest = (
            "sample-id,filename,direction\n"
            "Human-Kneecap,Human-Kneecap_0_L001_R1_001.fastq.gz,forward\n"
            "Peanut-Eyeball,Peanut-Eyeball_1_L001_R1_001.fastq.gz,forward\n")
        self.exp_pe_manifest = (
            "sample-id,filename,direction\n"
            "Human-Kneecap,Human-Kneecap_0_L001_R1_001.fastq.gz,forward\n"
            "Peanut-Eyeball,Peanut-Eyeball_1_L001_R1_001.fastq.gz,forward\n"
            "Human-Kneecap,Human-Kneecap_2_L001_R2_001.fastq.gz,reverse\n"
            "Peanut-Eyeball,Peanut-Eyeball_3_L001_R2_001.fastq.gz,reverse\n")

    def template_manifest(self, filepath, ctx):
        with open(filepath) as fh:
            tmpl = string.Template(fh.read())
        basename = os.path.basename(filepath)
        file_ = os.path.join(self.temp_dir.name, basename)
        with open(file_, 'w') as fh:
            fh.write(tmpl.substitute(**ctx))
        return file_

    def apply_transformation(self, from_fmt, to_fmt, datafile_fp, manifest_fp):
        transformer = self.get_transformer(from_fmt, to_fmt)
        fp = self.get_data_path(datafile_fp)
        manifest = self.template_manifest(
            self.get_data_path(manifest_fp),
            {k: fp for k in ['s1', 's2', 's1f', 's1r', 's2f', 's2r']})
        return transformer(from_fmt(manifest, 'r'))

    def test_single_end_fastq_manifest_phred33_to_slpssefdf(self):
        obs = self.apply_transformation(
            SingleEndFastqManifestPhred33V2,
            SingleLanePerSampleSingleEndFastqDirFmt,
            'Human-Kneecap_S1_L001_R1_001.fastq.gz',
            'absolute_manifests_v2/single-MANIFEST')

        with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
            self.assertEqual(obs_manifest.read(), self.exp_se_manifest)

    def test_single_end_fastq_manifest_phred64_to_slpssefdf(self):
        obs = self.apply_transformation(
            SingleEndFastqManifestPhred64V2,
            SingleLanePerSampleSingleEndFastqDirFmt,
            's1-phred64.fastq.gz',
            'absolute_manifests_v2/single-MANIFEST')

        with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
            self.assertEqual(obs_manifest.read(), self.exp_se_manifest)

    def test_paired_end_fastq_manifest_phred33_to_slpspefdf(self):
        obs = self.apply_transformation(
            PairedEndFastqManifestPhred33V2,
            SingleLanePerSamplePairedEndFastqDirFmt,
            'Human-Kneecap_S1_L001_R1_001.fastq.gz',
            'absolute_manifests_v2/paired-MANIFEST')

        with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
            self.assertEqual(obs_manifest.read(), self.exp_pe_manifest)

    def test_paired_end_fastq_manifest_phred64_to_slpspefdf(self):
        obs = self.apply_transformation(
            PairedEndFastqManifestPhred64V2,
            SingleLanePerSamplePairedEndFastqDirFmt,
            's1-phred64.fastq.gz',
            'absolute_manifests_v2/paired-MANIFEST')

        with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
            self.assertEqual(obs_manifest.read(), self.exp_pe_manifest)


class TestMAGTransformers(TestPluginBase):
    package = "q2_types.per_sample_sequences.tests"

    def setUp(self):
        super().setUp()

    @staticmethod
    def construct_manifest(ext):
        exp_manifest = (
            "sample-id,mag-id,filename\n"
            f"sample1,mag1,sample1/mag1.{ext}\n"
            f"sample1,mag2,sample1/mag2.{ext}\n"
            f"sample1,mag3,sample1/mag3.{ext}\n"
            f"sample2,mag1,sample2/mag1.{ext}\n"
            f"sample2,mag2,sample2/mag2.{ext}\n"
        )
        return exp_manifest

    def apply_transformation(self, from_fmt, to_fmt, datafile_fp):
        transformer = self.get_transformer(from_fmt, to_fmt)
        fp = self.get_data_path(datafile_fp)
        return transformer(from_fmt(fp, 'r'))

    def test_multifile_dirfmt_to_mag_seqs_dirfmt_fa(self):
        obs = self.apply_transformation(
            MultiFASTADirectoryFormat,
            MultiMAGSequencesDirFmt,
            'mags/mags-fa'
        )
        with obs.manifest.view(MultiMAGManifestFormat).open() as obs_manifest:
            self.assertEqual(
                obs_manifest.read(), self.construct_manifest('fasta')
            )

    def test_multifile_dirfmt_to_mag_seqs_dirfmt_fasta(self):
        obs = self.apply_transformation(
            MultiFASTADirectoryFormat,
            MultiMAGSequencesDirFmt,
            'mags/mags-fasta'
        )
        with obs.manifest.view(MultiMAGManifestFormat).open() as obs_manifest:
            self.assertEqual(
                obs_manifest.read(), self.construct_manifest('fasta')
            )

    def test_mag_manifest_to_df(self):
        obs = self.apply_transformation(
            MultiMAGManifestFormat,
            pd.DataFrame,
            'manifests/MANIFEST-mags-fa'
        )
        exp = pd.DataFrame({
            'sample-id': [
                'sample1', 'sample1', 'sample1', 'sample2', 'sample2'
            ],
            'mag-id': ['mag1', 'mag2', 'mag3', 'mag1', 'mag2'],
            'filename': [
                os.path.join(self.get_data_path('manifests'), x)
                for x in [
                    'sample1/mag1.fasta', 'sample1/mag2.fasta',
                    'sample1/mag3.fasta', 'sample2/mag1.fasta',
                    'sample2/mag2.fasta'
                ]
            ]
        })
        exp.set_index(['sample-id', 'mag-id'], inplace=True)

        assert_frame_equal(exp, obs)

    def test_mag_seqs_dirfmt_to_multifile_dirfmt(self):
        obs = self.apply_transformation(
            MultiMAGSequencesDirFmt,
            MultiFASTADirectoryFormat,
            'mags/mags-fa-with-manifest'
        )
        obs.validate()


if __name__ == '__main__':
    unittest.main()
