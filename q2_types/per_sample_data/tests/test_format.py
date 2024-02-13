# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
from pathlib import Path
import shutil
import string
import unittest
from unittest.mock import patch, Mock

from qiime2.core.exceptions import ValidationError
from qiime2.plugin.testing import TestPluginBase

from q2_types.per_sample_data._format import (
    MultiFASTADirectoryFormat, MultiMAGManifestFormat,
    ContigSequencesDirFmt, MultiBowtie2IndexDirFmt, BAMDirFmt, MultiBAMDirFmt
)


class TestMultiMAGManifestFormat(TestPluginBase):
    package = 'q2_types.per_sample_data.tests'

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


class TestFormats(TestPluginBase):
    package = 'q2_types.per_sample_data.tests'

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
        self.assertEqual(obs, exp)

        obs = contigs.sample_dict(relative=True)
        exp = {
            'sample1': 'sample1_contigs.fa',
            'sample2': 'sample2_contigs.fa',
            'sample3': 'sample3_contigs.fa'
        }
        self.assertEqual(obs, exp)

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


if __name__ == '__main__':
    unittest.main()
