# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest
import tempfile
import os
import shutil

import skbio
import yaml

from q2_types.per_sample_sequences import (
    PerSampleDNAIterators, PerSamplePairedDNAIterators,
    SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt,
    CasavaOneEightSingleLanePerSampleDirFmt,
    SingleEndFastqManifestPhred33,
    SingleEndFastqManifestPhred64,
    PairedEndFastqManifestPhred33,
    PairedEndFastqManifestPhred64,
)
from qiime2.plugin.testing import TestPluginBase


class TestTransformers(TestPluginBase):
    package = "q2_types.per_sample_sequences.tests"

    def test_slpssefdf_to_per_sample_dna_iterators(self):
        filenames = ('single_end_data/MANIFEST', 'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz')
        input, obs = self.transform_format(
            SingleLanePerSampleSingleEndFastqDirFmt, PerSampleDNAIterators,
            filenames=filenames
        )

        obs = obs['Human-Kneecap']
        sk = skbio.io.read(
            '%s/Human-Kneecap_S1_L001_R1_001.fastq.gz' % str(input),
            format='fastq', constructor=skbio.DNA
        )

        for act, exp in zip(obs, sk):
            self.assertEqual(act, exp)

    def test_slpspefdf_to_per_sample_paired_dna_iterators(self):
        filenames = ('paired_end_data/MANIFEST', 'metadata.yml',
                     'Human-Kneecap_S1_L001_R1_001.fastq.gz',
                     'paired_end_data/Human-Kneecap_S1_L001_R2_001.fastq.gz')
        input, obs = self.transform_format(
            SingleLanePerSamplePairedEndFastqDirFmt,
            PerSamplePairedDNAIterators, filenames=filenames
        )

        obs = obs['Human-Kneecap']
        sk1 = skbio.io.read(
            '%s/Human-Kneecap_S1_L001_R1_001.fastq.gz' % str(input),
            format='fastq', constructor=skbio.DNA
        )
        sk2 = skbio.io.read(
            '%s/Human-Kneecap_S1_L001_R2_001.fastq.gz' % str(input),
            format='fastq', constructor=skbio.DNA
        )
        expected = sk1, sk2

        for act, exp in zip(obs, expected):
            for seq1, seq2 in zip(act, exp):
                self.assertEqual(seq1, seq2)

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
            SingleLanePerSamplePairedEndFastqDirFmt, filenames=filenames
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


    def test_single_end_fastq_manifest_phred33_to_slpssefdf(self):
        format_ = SingleEndFastqManifestPhred33
        transformer = self.get_transformer(
            format_,
            SingleLanePerSampleSingleEndFastqDirFmt)

        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz'),
                os.path.join(tmpdir, 'Human-Kneecap_S1_L001_R1_001.fastq.gz'))
            shutil.copy(
                self.get_data_path('Human-Armpit.fastq.gz'),
                os.path.join(tmpdir, 'Human-Armpit.fastq.gz'))

            manifest_fp = os.path.join(tmpdir, 'manifest')
            with open(manifest_fp, 'w') as fh:
                fh.write("sample-id,filename,direction\n")
                fh.write("sampleABC,%s/Human-Kneecap_S1_L001_R1_001.fastq.gz,"
                         "forward\n" % tmpdir)
                fh.write("sampleXYZ,%s/Human-Armpit.fastq.gz,forward\n" % tmpdir)

            obs = transformer(format_(manifest_fp, 'r'))

        fastq_pairs = [('Human-Kneecap_S1_L001_R1_001.fastq.gz',
                        'sampleABC_0_L001_R1_001.fastq.gz'),
                       ('Human-Armpit.fastq.gz',
                        'sampleXYZ_1_L001_R1_001.fastq.gz')]
        for input_fastq, obs_fastq in fastq_pairs:
            obs_fh = skbio.io.read(
                os.path.join(str(obs), obs_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )
            exp_fh = skbio.io.read(
                self.get_data_path(input_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )

            for o, e in zip(obs_fh, exp_fh):
                self.assertEqual(o, e)

        obs_metadata = yaml.load(open('%s/metadata.yml' % str(obs)))
        exp_metadata = yaml.load("{'phred-offset': 33}")
        self.assertEqual(obs_metadata, exp_metadata)

        obs_manifest = open('%s/MANIFEST' % (str(obs))).read()
        exp_manifest=("sample-id,filename,direction\n"
                      "sampleABC,sampleABC_0_L001_R1_001.fastq.gz,forward\n"
                      "sampleXYZ,sampleXYZ_1_L001_R1_001.fastq.gz,forward\n")
        self.assertEqual(obs_manifest, exp_manifest)

    def test_single_end_fastq_manifest_phred64_to_slpssefdf(self):
        format_ = SingleEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSampleSingleEndFastqDirFmt)

        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                self.get_data_path('s1-phred64.fastq.gz'),
                os.path.join(tmpdir, 's1-phred64.fastq.gz'))
            shutil.copy(
                self.get_data_path('s2-phred64.fastq.gz'),
                os.path.join(tmpdir, 's2-phred64.fastq.gz'))

            manifest_fp = os.path.join(tmpdir, 'manifest')
            with open(manifest_fp, 'w') as fh:
                fh.write("sample-id,filename,direction\n")
                fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                         "forward\n" % tmpdir)
                fh.write("sampleXYZ,%s/s2-phred64.fastq.gz,forward\n" % tmpdir)

            obs = transformer(format_(manifest_fp, 'r'))

        fastq_pairs = [('s1-phred64.fastq.gz',
                        'sampleABC_0_L001_R1_001.fastq.gz'),
                       ('s2-phred64.fastq.gz',
                        'sampleXYZ_1_L001_R1_001.fastq.gz')]
        for input_fastq, obs_fastq in fastq_pairs:
            obs_fh = skbio.io.read(
                os.path.join(str(obs), obs_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )
            exp_fh = skbio.io.read(
                self.get_data_path(input_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.3'
            )

            for o, e in zip(obs_fh, exp_fh):
                self.assertEqual(o, e)

        obs_metadata = yaml.load(open('%s/metadata.yml' % str(obs)))
        exp_metadata = yaml.load("{'phred-offset': 33}")
        self.assertEqual(obs_metadata, exp_metadata)

        obs_manifest = open('%s/MANIFEST' % (str(obs))).read()
        exp_manifest=("sample-id,filename,direction\n"
                      "sampleABC,sampleABC_0_L001_R1_001.fastq.gz,forward\n"
                      "sampleXYZ,sampleXYZ_1_L001_R1_001.fastq.gz,forward\n")
        self.assertEqual(obs_manifest, exp_manifest)

    def test_paired_end_fastq_manifest_phred33_to_slpspefdf(self):
        format_ = PairedEndFastqManifestPhred33
        transformer = self.get_transformer(
            format_,
            SingleLanePerSamplePairedEndFastqDirFmt)

        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                self.get_data_path('Human-Kneecap_S1_L001_R1_001.fastq.gz'),
                os.path.join(tmpdir, 'Human-Kneecap_S1_L001_R1_001.fastq.gz'))
            shutil.copy(
                self.get_data_path('Human-Armpit.fastq.gz'),
                os.path.join(tmpdir, 'Human-Armpit.fastq.gz'))

            manifest_fp = os.path.join(tmpdir, 'manifest')
            with open(manifest_fp, 'w') as fh:
                fh.write("sample-id,filename,direction\n")
                fh.write("sampleABC,%s/Human-Kneecap_S1_L001_R1_001.fastq.gz,"
                         "forward\n" % tmpdir)
                fh.write("sampleABC,%s/Human-Armpit.fastq.gz,reverse\n" % tmpdir)

            obs = transformer(format_(manifest_fp, 'r'))

        fastq_pairs = [('Human-Kneecap_S1_L001_R1_001.fastq.gz',
                        'sampleABC_0_L001_R1_001.fastq.gz'),
                       ('Human-Armpit.fastq.gz',
                        'sampleABC_1_L001_R2_001.fastq.gz')]
        for input_fastq, obs_fastq in fastq_pairs:
            obs_fh = skbio.io.read(
                os.path.join(str(obs), obs_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )
            exp_fh = skbio.io.read(
                self.get_data_path(input_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )

            for o, e in zip(obs_fh, exp_fh):
                self.assertEqual(o, e)

        obs_metadata = yaml.load(open('%s/metadata.yml' % str(obs)))
        exp_metadata = yaml.load("{'phred-offset': 33}")
        self.assertEqual(obs_metadata, exp_metadata)

        obs_manifest = open('%s/MANIFEST' % (str(obs))).read()
        exp_manifest=("sample-id,filename,direction\n"
                      "sampleABC,sampleABC_0_L001_R1_001.fastq.gz,forward\n"
                      "sampleABC,sampleABC_1_L001_R2_001.fastq.gz,reverse\n")
        self.assertEqual(obs_manifest, exp_manifest)

    def test_paired_end_fastq_manifest_phred64_to_slpspefdf(self):
        format_ = PairedEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSamplePairedEndFastqDirFmt)

        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                self.get_data_path('s1-phred64.fastq.gz'),
                os.path.join(tmpdir, 's1-phred64.fastq.gz'))
            shutil.copy(
                self.get_data_path('s2-phred64.fastq.gz'),
                os.path.join(tmpdir, 's2-phred64.fastq.gz'))

            manifest_fp = os.path.join(tmpdir, 'manifest')
            with open(manifest_fp, 'w') as fh:
                fh.write("sample-id,filename,direction\n")
                fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                         "forward\n" % tmpdir)
                fh.write("sampleABC,%s/s2-phred64.fastq.gz,reverse\n" % tmpdir)

            obs = transformer(format_(manifest_fp, 'r'))

        fastq_pairs = [('s1-phred64.fastq.gz',
                        'sampleABC_0_L001_R1_001.fastq.gz'),
                       ('s2-phred64.fastq.gz',
                        'sampleABC_1_L001_R2_001.fastq.gz')]
        for input_fastq, obs_fastq in fastq_pairs:
            obs_fh = skbio.io.read(
                os.path.join(str(obs), obs_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.8'
            )
            exp_fh = skbio.io.read(
                self.get_data_path(input_fastq),
                format='fastq', constructor=skbio.DNA, variant='illumina1.3'
            )

            for o, e in zip(obs_fh, exp_fh):
                self.assertEqual(o, e)

        obs_metadata = yaml.load(open('%s/metadata.yml' % str(obs)))
        exp_metadata = yaml.load("{'phred-offset': 33}")
        self.assertEqual(obs_metadata, exp_metadata)

        obs_manifest = open('%s/MANIFEST' % (str(obs))).read()
        exp_manifest=("sample-id,filename,direction\n"
                      "sampleABC,sampleABC_0_L001_R1_001.fastq.gz,forward\n"
                      "sampleABC,sampleABC_1_L001_R2_001.fastq.gz,reverse\n")
        self.assertEqual(obs_manifest, exp_manifest)

    def test_single_end_fastq_manifest_invalid(self):
        format_ = SingleEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSampleSingleEndFastqDirFmt)

        # file specified in manifest doesn't exist
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                self.get_data_path('s1-phred64.fastq.gz'),
                os.path.join(tmpdir, 's1-phred64.fastq.gz'))

            manifest_fp = os.path.join(tmpdir, 'manifest')
            with open(manifest_fp, 'w') as fh:
                fh.write("sample-id,filename,direction\n")
                fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                         "forward\n" % tmpdir)
                fh.write("sampleXYZ,%s/s2-phred64.fastq.gz,forward\n" % tmpdir)

            with self.assertRaisesRegex(FileNotFoundError,
                                        "s2-phred64.fastq.gz"):
                transformer(format_(manifest_fp, 'r'))

        # invalid direction in manifest
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                self.get_data_path('s1-phred64.fastq.gz'),
                os.path.join(tmpdir, 's1-phred64.fastq.gz'))
            shutil.copy(
                self.get_data_path('s2-phred64.fastq.gz'),
                os.path.join(tmpdir, 's2-phred64.fastq.gz'))

            manifest_fp = os.path.join(tmpdir, 'manifest')
            with open(manifest_fp, 'w') as fh:
                fh.write("sample-id,filename,direction\n")
                fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                         "middle-out\n" % tmpdir)
                fh.write("sampleXYZ,%s/s2-phred64.fastq.gz,forward\n" % tmpdir)

            with self.assertRaisesRegex(ValueError, 'middle-out'):
                transformer(format_(manifest_fp, 'r'))

        # different directions in single-end manifest
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                self.get_data_path('s1-phred64.fastq.gz'),
                os.path.join(tmpdir, 's1-phred64.fastq.gz'))
            shutil.copy(
                self.get_data_path('s2-phred64.fastq.gz'),
                os.path.join(tmpdir, 's2-phred64.fastq.gz'))

            manifest_fp = os.path.join(tmpdir, 'manifest')
            with open(manifest_fp, 'w') as fh:
                fh.write("sample-id,filename,direction\n")
                fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                         "forward\n" % tmpdir)
                fh.write("sampleXYZ,%s/s2-phred64.fastq.gz,reverse\n" % tmpdir)

            with self.assertRaisesRegex(ValueError, "only forward or reverse"):
                transformer(format_(manifest_fp, 'r'))

    def test_paired_end_fastq_manifest_invalid(self):
        format_ = PairedEndFastqManifestPhred64
        transformer = self.get_transformer(
            format_,
            SingleLanePerSamplePairedEndFastqDirFmt)

        # file specified in manifest doesn't exist
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                self.get_data_path('s1-phred64.fastq.gz'),
                os.path.join(tmpdir, 's1-phred64.fastq.gz'))

            manifest_fp = os.path.join(tmpdir, 'manifest')
            with open(manifest_fp, 'w') as fh:
                fh.write("sample-id,filename,direction\n")
                fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                         "forward\n" % tmpdir)
                fh.write("sampleABC,%s/s2-phred64.fastq.gz,reverse\n" % tmpdir)

            with self.assertRaisesRegex(FileNotFoundError,
                                        "s2-phred64.fastq.gz"):
                transformer(format_(manifest_fp, 'r'))

        # invalid direction in manifest
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                self.get_data_path('s1-phred64.fastq.gz'),
                os.path.join(tmpdir, 's1-phred64.fastq.gz'))
            shutil.copy(
                self.get_data_path('s2-phred64.fastq.gz'),
                os.path.join(tmpdir, 's2-phred64.fastq.gz'))

            manifest_fp = os.path.join(tmpdir, 'manifest')
            with open(manifest_fp, 'w') as fh:
                fh.write("sample-id,filename,direction\n")
                fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                         "middle-out\n" % tmpdir)
                fh.write("sampleABC,%s/s2-phred64.fastq.gz,reverse\n" % tmpdir)

            with self.assertRaisesRegex(ValueError, 'middle-out'):
                transformer(format_(manifest_fp, 'r'))

        # missing directions in single-end manifest
        with tempfile.TemporaryDirectory() as tmpdir:
            shutil.copy(
                self.get_data_path('s1-phred64.fastq.gz'),
                os.path.join(tmpdir, 's1-phred64.fastq.gz'))

            manifest_fp = os.path.join(tmpdir, 'manifest')
            with open(manifest_fp, 'w') as fh:
                fh.write("sample-id,filename,direction\n")
                fh.write("sampleABC,%s/s1-phred64.fastq.gz,"
                         "forward\n" % tmpdir)

            with self.assertRaisesRegex(ValueError,
                                        "one time each for each sample"):
                transformer(format_(manifest_fp, 'r'))

if __name__ == '__main__':
    unittest.main()
