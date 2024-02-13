# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
import unittest

import pandas as pd
from pandas._testing import assert_frame_equal
from qiime2.plugin.testing import TestPluginBase

from q2_types.per_sample_data._format import (
    MultiFASTADirectoryFormat,
    MultiMAGSequencesDirFmt, MultiMAGManifestFormat
)


class TestTransformers(TestPluginBase):
    package = "q2_types.per_sample_data.tests"

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


if __name__ == '__main__':
    unittest.main()
