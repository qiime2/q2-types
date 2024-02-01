# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2
import pandas as pd
import pandas.testing as pdt
import skbio
import string
import os

import unittest

from q2_types.multiplexed_sequences import (
    MultiplexedFastaQualDirFmt,
    MultiplexedSingleEndBarcodeInSequenceDirFmt,
    # EMPMultiplexedDirFmt,
    ErrorCorrectionDetailsFmt,
    # EMPSingleEndDirFmt,
    # EMPSingleEndCasavaDirFmt,
    # EMPPairedEndDirFmt,
    # EMPPairedEndCasavaDirFmt
)
from q2_types.per_sample_sequences import (
    SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt,
    SingleEndFastqManifestPhred33V2,
    SingleEndFastqManifestPhred64V2,
    PairedEndFastqManifestPhred33V2,
    PairedEndFastqManifestPhred64V2,
    FastqManifestFormat)

from qiime2.plugin.testing import TestPluginBase


class TestMultiplexedSequencesTransformers(TestPluginBase):
    package = 'q2_types.multiplexed_sequences.tests'

    def test_fasta_qual_to_fastq(self):
        _, obs = self.transform_format(
            MultiplexedFastaQualDirFmt,
            target=MultiplexedSingleEndBarcodeInSequenceDirFmt,
            filenames=('reads.fasta', 'reads.qual'))

        sequences = skbio.io.read('%s/forward.fastq.gz' % str(obs),
                                  format='fastq',
                                  variant='illumina1.8')
        sequences = list(sequences)

        self.assertEqual(len(sequences), 3)

        self.assertTrue(str(sequences[0]).startswith('ACAGAGTCGGCTCA'))
        self.assertTrue(str(sequences[0]).endswith('ATGGGCTAGG'))
        self.assertTrue(str(sequences[1]).startswith('ACAGAGTCGGCTCA'))
        self.assertTrue(str(sequences[1]).endswith('CCGGTCGCCA'))
        self.assertTrue(str(sequences[2]).startswith('AGCACGAGCCTACA'))
        self.assertTrue(str(sequences[2]).endswith('GTCTCTTGGG'))

        self.assertEqual(sequences[0].metadata['id'], 'FLP3FBN01ELBSX')
        self.assertEqual(sequences[1].metadata['id'], 'FLP3FBN01EG8AX')
        self.assertEqual(sequences[2].metadata['id'], 'FLP3FBN01EEWKD')

        self.assertEqual(
            list(sequences[0].positional_metadata['quality'][:5]),
            [37, 37, 37, 37, 37])
        self.assertEqual(
            list(sequences[0].positional_metadata['quality'][-5:]),
            [21, 15, 15, 13, 13])
        self.assertEqual(
            list(sequences[1].positional_metadata['quality'][:5]),
            [37, 37, 37, 37, 37])
        self.assertEqual(
            list(sequences[1].positional_metadata['quality'][-5:]),
            [25, 25, 25, 25, 28])
        self.assertEqual(
            list(sequences[2].positional_metadata['quality'][:5]),
            [36, 37, 37, 37, 37])
        self.assertEqual(
            list(sequences[2].positional_metadata['quality'][-5:]),
            [36, 36, 36, 36, 36])


# NOTE: we are really only interested in the manifest, since these transformers
# primarily transform the V2 TSV manifests to the (older) CSV manifests. The
# only things asserted here are facts about the manifest and not the actual
# data assets, themselves.
class TestFastqManifestV2Transformers(TestPluginBase):
    package = "q2_types.multiplexed_sequences.tests"

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

    # def test_EMPMultiplexedDirFmt_to_slpssefdf(self):
    #     obs = self.apply_transformation(
    #         EMPMultiplexedDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt,
    #         'Human-Kneecap_S1_L001_R1_001.fastq.gz',
    #         'absolute_manifests_v2/single-MANIFEST')

    #     with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
    #         self.assertEqual(obs_manifest.read(), self.exp_se_manifest)

    # def test_EMPMultiplexedDirFmt_to_slpspefdf(self):
    #     obs = self.apply_transformation(
    #         EMPMultiplexedDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt,
    #         'Human-Kneecap_S1_L001_R1_001.fastq.gz',
    #         'absolute_manifests_v2/paired-MANIFEST')

    #     with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
    #         self.assertEqual(obs_manifest.read(), self.exp_pe_manifest)

    # def test_ErrorCorrectionDetailsFmt_to_slpspefdf(self):
    #     transformer = self.get_transformer(
    #         ErrorCorrectionDetailsFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     obs = transformer(ErrorCorrectionDetailsFmt(
    #         self.get_data_path('error_correction_details.tsv'), 'r'))

    #     exp = pd.read_csv(
    #         self.get_data_path('error_correction_details.tsv'), sep='\t',
    #         index_col=0)
    #     pdt.assert_frame_equal(obs.view(pd.DataFrame), exp)

    # def test_ErrorCorrectionDetailsFmt_to_slpssefdf(self):
    #     transformer = self.get_transformer(
    #         ErrorCorrectionDetailsFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     obs = transformer(ErrorCorrectionDetailsFmt(
    #         self.get_data_path('error_correction_details.tsv'), 'r'))

    #     exp = pd.read_csv(
    #         self.get_data_path('error_correction_details.tsv'), sep='\t',
    #         index_col=0)
    #     pdt.assert_frame_equal(obs.view(pd.DataFrame), exp)

    # def test_ErrorCorrectionDetailsFmt_to_slpssefdf_missing_direction(self):
    #     transformer = self.get_transformer(
    #         ErrorCorrectionDetailsFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'missing.*forward'):
    #         transformer(ErrorCorrectionDetailsFmt(
    #             self.get_data_path('error_correction_details.tsv'), 'r'))

    # def test_ErrorCorrectionDetailsFmt_to_slpspefdf_missing_direction(self):
    #     transformer = self.get_transformer(
    #         ErrorCorrectionDetailsFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'missing.*forward'):
    #         transformer(ErrorCorrectionDetailsFmt(
    #             self.get_data_path('error_correction_details.tsv'), 'r'))

    # def test_ErrorCorrectionDetailsFmt_to_slpspefdf_extra_direction(self):
    #     transformer = self.get_transformer(
    #         ErrorCorrectionDetailsFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'extra.*reverse'):
    #         transformer(ErrorCorrectionDetailsFmt(
    #             self.get_data_path('error_correction_details.tsv'), 'r'))

    # def test_ErrorCorrectionDetailsFmt_to_slpssefdf_extra_direction(self):
    #     transformer = self.get_transformer(
    #         ErrorCorrectionDetailsFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'extra.*reverse'):
    #         transformer(ErrorCorrectionDetailsFmt(
    #             self.get_data_path('error_correction_details.tsv'), 'r'))

    # def test_EMPSingleEndDirFmt_to_slpssefdf(self):
    #     transformer = self.get_transformer(
    #         EMPSingleEndDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     obs = transformer(EMPSingleEndDirFmt(
    #         self.get_data_path('emp-single-end-sequences'), 'r'))

    #     exp = pd.read_csv(
    #         self.get_data_path('emp-single-end-sequences',
    #                            'error_correction_details.tsv'),
    #         sep='\t', index_col=0)
    #     pdt.assert_frame_equal(obs.error_correction_details.view(pd.DataFrame),
    #                            exp)

    #     with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
    #         self.assertEqual(obs_manifest.read(), self.exp_se_manifest)

    # def test_EMPSingleEndDirFmt_to_slpspefdf(self):
    #     transformer = self.get_transformer(
    #         EMPSingleEndDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     obs = transformer(EMPSingleEndDirFmt(
    #         self.get_data_path('emp-single-end-sequences'), 'r'))

    #     exp = pd.read_csv(
    #         self.get_data_path('emp-single-end-sequences',
    #                            'error_correction_details.tsv'),
    #         sep='\t', index_col=0)
    #     pdt.assert_frame_equal(obs.error_correction_details.view(pd.DataFrame),
    #                            exp)

    #     with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
    #         self.assertEqual(obs_manifest.read(), self.exp_pe_manifest)

    # def test_EMPSingleEndDirFmt_to_slpssefdf_missing(self):
    #     transformer = self.get_transformer(
    #         EMPSingleEndDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'missing.*forward'):
    #         transformer(EMPSingleEndDirFmt(
    #             self.get_data_path('emp-single-end-sequences'), 'r'))

    # def test_EMPSingleEndDirFmt_to_slpspefdf_missing(self):
    #     transformer = self.get_transformer(
    #         EMPSingleEndDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'missing.*forward'):
    #         transformer(EMPSingleEndDirFmt(
    #             self.get_data_path('emp-single-end-sequences'), 'r'))

    # def test_EMPSingleEndDirFmt_to_slpspefdf_extra(self):
    #     transformer = self.get_transformer(
    #         EMPSingleEndDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'extra.*reverse'):
    #         transformer(EMPSingleEndDirFmt(
    #             self.get_data_path('emp-single-end-sequences'), 'r'))

    # def test_EMPSingleEndDirFmt_to_slpssefdf_extra(self):
    #     transformer = self.get_transformer(
    #         EMPSingleEndDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'extra.*reverse'):
    #         transformer(EMPSingleEndDirFmt(
    #             self.get_data_path('emp-single-end-sequences'), 'r'))

    # def test_EMPSingleEndCasavaDirFmt_to_slpssefdf(self):
    #     transformer = self.get_transformer(
    #         EMPSingleEndCasavaDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     obs = transformer(EMPSingleEndCasavaDirFmt(
    #         self.get_data_path('emp-single-end-sequences'), 'r'))

    #     exp = pd.read_csv(
    #         self.get_data_path('emp-single-end-sequences',
    #                            'error_correction_details.tsv'),
    #         sep='\t', index_col=0)
    #     pdt.assert_frame_equal(obs.error_correction_details.view(pd.DataFrame),
    #                            exp)

    #     with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
    #         self.assertEqual(obs_manifest.read(), self.exp_se_manifest)

    # def test_EMPSingleEndCasavaDirFmt_to_slpspefdf(self):
    #     transformer = self.get_transformer(
    #         EMPSingleEndCasavaDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     obs = transformer(EMPSingleEndCasavaDirFmt(
    #         self.get_data_path('emp-single-end-sequences'), 'r'))

    #     exp = pd.read_csv(
    #         self.get_data_path('emp-single-end-sequences',
    #                            'error_correction_details.tsv'),
    #         sep='\t', index_col=0)
    #     pdt.assert_frame_equal(obs.error_correction_details.view(pd.DataFrame),
    #                            exp)

    #     with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
    #         self.assertEqual(obs_manifest.read(), self.exp_pe_manifest)

    # def test_EMPSingleEndCasavaDirFmt_to_slpssefdf_missing(self):
    #     transformer = self.get_transformer(
    #         EMPSingleEndCasavaDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'missing.*forward'):
    #         transformer(EMPSingleEndCasavaDirFmt(
    #             self.get_data_path('emp-single-end-sequences'), 'r'))

    # def test_EMPSingleEndCasavaDirFmt_to_slpspefdf_missing(self):
    #     transformer = self.get_transformer(
    #         EMPSingleEndCasavaDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'missing.*forward'):
    #         transformer(EMPSingleEndCasavaDirFmt(
    #             self.get_data_path('emp-single-end-sequences'), 'r'))

    # def test_EMPSingleEndCasavaDirFmt_to_slpspefdf_extra_direction(self):
    #     transformer = self.get_transformer(
    #         EMPSingleEndCasavaDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'extra.*reverse'):
    #         transformer(EMPSingleEndCasavaDirFmt(
    #             self.get_data_path('emp-single-end-sequences'), 'r'))

    # def test_EMPSingleEndCasavaDirFmt_to_slpssefdf_extra_direction(self):
    #     transformer = self.get_transformer(
    #         EMPSingleEndCasavaDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'extra.*reverse'):
    #         transformer(EMPSingleEndCasavaDirFmt(
    #             self.get_data_path('emp-single-end-sequences'), 'r'))

    # def test_EMPPairedEndDirFmt_to_slpssefdf(self):
    #     transformer = self.get_transformer(
    #         EMPPairedEndDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     obs = transformer(EMPPairedEndDirFmt(
    #         self.get_data_path('emp-paired-end-sequences'), 'r'))

    #     exp = pd.read_csv(
    #         self.get_data_path('emp-paired-end-sequences',
    #                            'error_correction_details.tsv'),
    #         sep='\t', index_col=0)
    #     pdt.assert_frame_equal(obs.error_correction_details.view(pd.DataFrame),
    #                            exp)

    #     with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
    #         self.assertEqual(obs_manifest.read(), self.exp_se_manifest)

    # def test_EMPPairedEndDirFmt_to_slpspefdf(self):
    #     transformer = self.get_transformer(
    #         EMPPairedEndDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     obs = transformer(EMPPairedEndDirFmt(
    #         self.get_data_path('emp-paired-end-sequences'), 'r'))

    #     exp = pd.read_csv(
    #         self.get_data_path('emp-paired-end-sequences',
    #                            'error_correction_details.tsv'),
    #         sep='\t', index_col=0)
    #     pdt.assert_frame_equal(obs.error_correction_details.view(pd.DataFrame),
    #                            exp)

    #     with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
    #         self.assertEqual(obs_manifest.read(), self.exp_pe_manifest)

    # def test_EMPPairedEndDirFmt_to_slpssefdf_missing_direction(self):
    #     transformer = self.get_transformer(
    #         EMPPairedEndDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'missing.*forward'):
    #         transformer(EMPPairedEndDirFmt(
    #             self.get_data_path('emp-paired-end-sequences'), 'r'))

    # def test_EMPPairedEndDirFmt_to_slpspefdf_missing_direction(self):
    #     transformer = self.get_transformer(
    #         EMPPairedEndDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'missing.*forward'):
    #         transformer(EMPPairedEndDirFmt(
    #             self.get_data_path('emp-paired-end-sequences'), 'r'))

    # def test_EMPPairedEndDirFmt_to_slpspefdf_extra_direction(self):
    #     transformer = self.get_transformer(
    #         EMPPairedEndDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'extra.*reverse'):
    #         transformer(EMPPairedEndDirFmt(
    #             self.get_data_path('emp-paired-end-sequences'), 'r'))

    # def test_EMPPairedEndDirFmt_to_slpssefdf_extra_direction(self):
    #     transformer = self.get_transformer(
    #         EMPPairedEndDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'extra.*reverse'):
    #         transformer(EMPPairedEndDirFmt(
    #             self.get_data_path('emp-paired-end-sequences'), 'r'))

    # def test_EMPPairedEndCasavaDirFmt_to_slpssefdf(self):
    #     transformer = self.get_transformer(
    #         EMPPairedEndCasavaDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     obs = transformer(EMPPairedEndCasavaDirFmt(
    #         self.get_data_path('emp-paired-end-sequences'), 'r'))

    #     exp = pd.read_csv(
    #         self.get_data_path('emp-paired-end-sequences',
    #                            'error_correction_details.tsv'),
    #         sep='\t', index_col=0)
    #     pdt.assert_frame_equal(obs.error_correction_details.view(pd.DataFrame),
    #                            exp)

    #     with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
    #         self.assertEqual(obs_manifest.read(), self.exp_se_manifest)

    # def test_EMPPairedEndCasavaDirFmt_to_slpspefdf(self):
    #     transformer = self.get_transformer(
    #         EMPPairedEndCasavaDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     obs = transformer(EMPPairedEndCasavaDirFmt(
    #         self.get_data_path('emp-paired-end-sequences'), 'r'))

    #     exp = pd.read_csv(
    #         self.get_data_path('emp-paired-end-sequences',
    #                            'error_correction_details.tsv'),
    #         sep='\t', index_col=0)
    #     pdt.assert_frame_equal(obs.error_correction_details.view(pd.DataFrame),
    #                            exp)

    #     with obs.manifest.view(FastqManifestFormat).open() as obs_manifest:
    #         self.assertEqual(obs_manifest.read(), self.exp_pe_manifest)

    # def test_EMPPairedEndCasavaDirFmt_to_slpssefdf_missing_direction(self):
    #     transformer = self.get_transformer(
    #         EMPPairedEndCasavaDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'missing.*forward'):
    #         transformer(EMPPairedEndCasavaDirFmt(
    #             self.get_data_path('emp-paired-end-sequences'), 'r'))

    # def test_EMPPairedEndCasavaDirFmt_to_slpspefdf_missing_direction(self):
    #     transformer = self.get_transformer(
    #         EMPPairedEndCasavaDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'missing.*forward'):
    #         transformer(EMPPairedEndCasavaDirFmt(
    #             self.get_data_path('emp-paired-end-sequences'), 'r'))

    # def test_EMPPairedEndCasavaDirFmt_to_slpspefdf_extra_direction(self):
    #     transformer = self.get_transformer(
    #         EMPPairedEndCasavaDirFmt,
    #         SingleLanePerSamplePairedEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'extra.*reverse'):
    #         transformer(EMPPairedEndCasavaDirFmt(
    #             self.get_data_path('emp-paired-end-sequences'), 'r'))

    # def test_EMPPairedEndCasavaDirFmt_to_slpssefdf_extra_direction(self):
    #     transformer = self.get_transformer(
    #         EMPPairedEndCasavaDirFmt,
    #         SingleLanePerSampleSingleEndFastqDirFmt)

    #     with self.assertRaisesRegex(ValueError, 'extra.*reverse'):
    #         transformer(EMPPairedEndCasavaDirFmt(
    #             self.get_data_path('emp-paired-end-sequences'), 'r'))

# start tests to keep


class TestErrorCorrectionDetailsFmtTransformers(TestPluginBase):
    package = 'q2_types.multiplexed_sequences.tests'

    def setUp(self):
        super().setUp()

        self.df = pd.DataFrame([
                ['s1', 'seq-1',  'AAC', 'AAA', 2.],
                ['s1', 'seq-4',  'ACA', 'AAA', 20.],
                ['s2', 'seq-5',  'CCA', 'CCC', 1.],
                ['s3', 'seq-50', 'GGT', 'GGG', 1.],
            ],
            columns=['sample', 'barcode-sequence-id', 'barcode-uncorrected',
                     'barcode-corrected', 'barcode-errors'],
            index=pd.Index(['record-1', 'record-2', 'record-3', 'record-4'],
                           name='id'))

        self.serialized = (
            'id\tsample\tbarcode-sequence-id\tbarcode-uncorrected\t'
            'barcode-corrected\tbarcode-errors\n'
            '#q2:types\tcategorical\tcategorical\tcategorical\tcategorical\t'
            'numeric\n'
            'record-1\ts1\tseq-1\tAAC\tAAA\t2\n'
            'record-2\ts1\tseq-4\tACA\tAAA\t20\n'
            'record-3\ts2\tseq-5\tCCA\tCCC\t1\n'
            'record-4\ts3\tseq-50\tGGT\tGGG\t1\n'
        )

    def test_df_to_error_correction_details_fmt(self):
        transformer = self.get_transformer(
            pd.DataFrame, ErrorCorrectionDetailsFmt)
        obs = transformer(self.df)

        with obs.open() as obs:
            self.assertEqual(obs.read(), self.serialized)

    def test_error_correction_details_fmt_to_df(self):
        transformer = self.get_transformer(
            ErrorCorrectionDetailsFmt, pd.DataFrame)
        ff = ErrorCorrectionDetailsFmt()
        with ff.open() as fh:
            fh.write(self.serialized)
        obs = transformer(ff)

        pdt.assert_frame_equal(obs, self.df)

    def test_error_correction_details_fmt_to_metadata(self):
        transformer = self.get_transformer(
            ErrorCorrectionDetailsFmt, qiime2.Metadata)
        ff = ErrorCorrectionDetailsFmt()
        with ff.open() as fh:
            fh.write(self.serialized)
        obs = transformer(ff)

        self.assertEqual(obs, qiime2.Metadata(self.df))


if __name__ == '__main__':
    unittest.main()
