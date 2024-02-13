# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from pathlib import Path
import shutil
import unittest

from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin import ValidationError

from q2_types.feature_data_mag._format import (
        MAGSequencesDirFmt, OrthologAnnotationDirFmt,
        )


class TestFormats(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_mag_dirfmt_fa(self):
        dirpath = self.get_data_path('mags-fa')
        format = MAGSequencesDirFmt(dirpath, mode='r')

        format.validate()

    def test_mag_dirfmt_fasta(self):
        dirpath = self.get_data_path('mags-fasta')
        format = MAGSequencesDirFmt(dirpath, mode='r')

        format.validate()

    def test_mag_dirfmt_feature_dict(self):
        dirpath = self.get_data_path('mags-fasta')
        shutil.copytree(dirpath, self.temp_dir.name, dirs_exist_ok=True)
        mags = MAGSequencesDirFmt(self.temp_dir.name, mode='r')

        # non-mags should not be collected
        with open(Path(self.temp_dir.name) / 'not-a-mag.fasta', 'w') as fh:
            fh.write('not a mag')

        obs = mags.feature_dict()
        exp = {
            '3b7d53fb-5b60-46c6-8819-aeda065b12e9':
                str(mags.path / '3b7d53fb-5b60-46c6-8819-aeda065b12e9.fasta'),
            '6232c7e1-8ed7-47c8-9bdb-b94706a26931':
                str(mags.path / '6232c7e1-8ed7-47c8-9bdb-b94706a26931.fasta'),
        }
        self.assertEqual(obs, exp)

        obs = mags.feature_dict(relative=True)
        exp = {
            '3b7d53fb-5b60-46c6-8819-aeda065b12e9':
                '3b7d53fb-5b60-46c6-8819-aeda065b12e9.fasta',
            '6232c7e1-8ed7-47c8-9bdb-b94706a26931':
                '6232c7e1-8ed7-47c8-9bdb-b94706a26931.fasta',
        }
        self.assertEqual(obs, exp)

    def test_ortholog_annotation_dir_fmt_passing(self):
        dirpath = self.get_data_path('good_ortholog_annotation')
        fmt_obj = OrthologAnnotationDirFmt(dirpath, mode='r')
        fmt_obj.validate()

    def test_ortholog_annotation_dir_fmt_fails_extra_file(self):
        dirpath = self.get_data_path('ortholog_annotation_extra')
        fmt_obj = OrthologAnnotationDirFmt(dirpath, mode='r')

        with self.assertRaisesRegex(ValidationError, "Unrecognized file"):
            fmt_obj.validate()


if __name__ == '__main__':
    unittest.main()
