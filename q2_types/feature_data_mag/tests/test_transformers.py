# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import glob
import qiime2
import unittest
from itertools import repeat

import pandas as pd
import skbio
from qiime2.plugin.testing import TestPluginBase
from skbio import DNA

from q2_types.feature_data_mag import (
    MAGSequencesDirFmt, MAGIterator, OrthologAnnotationDirFmt
)
from q2_types.feature_data_mag._transformer import (
    _get_filename, _annotations_to_dataframe
)


class TestTransformers(TestPluginBase):
    package = 'q2_types.feature_data_mag.tests'

    def setUp(self):
        super().setUp()
        self.mags_fa = {
            '23c5b64e-3f3e-4688-9862-e9dae4fa0f5b': {
                'k129_5480': 'TTATTTTCAAGATAATGAGCCAATTTAAGCGGTGTCTGGCCG'
                             'CCAAGCTGCACGATCACACCTTTAA'
            },
            '70c5a728-96a6-4eed-b9f9-9a73153c1385': {
                'k129_5112': 'CCCCGGAAAGGGCTGGCGACCGACGATGACCTCGGGAAGCCC'
                             'CAACTCGCGGCCGATGGCGCGTACCTCGTC'
            },
            '7e2a749a-a19a-4b62-8195-0ee601b5fdfb': {
                'k129_6525': 'AAACTCTATCAAGCGTATACCAAAGTGAGTGGTGTATTGATC'
                             'AGTCAGCTCATTATTGAATCGGA',
                'k129_6531': 'TCGGATTTGCCGAATGCTTTTTGTAAGGGCCTTCAATTGATT'
                             'TGGCGATAGCGAGCCCGTATTTACGGT'
            }
        }
        self.mags_fasta = {
            '3b7d53fb-5b60-46c6-8819-aeda065b12e9': {
                'k129_5401': 'CCATTGTATGTCTTTAGGTAGCTCCTCATGTTTGAGGTTCAT'
                             'GTCTTGGATTTTGTTTTCTCCAAAAATC'
            },
            '6232c7e1-8ed7-47c8-9bdb-b94706a26931': {
                'k129_4684': 'TGATACCGACGCGGCACTTGAGTGCGCGCTATCCTTCAAGGA'
                             'AGCCACATGCGTTATTGTTAAACA',
                'k129_5618': 'GTGCTAATCGCACCCTCATGAGCGACACCATTATTCTTTATT'
                             'TTTGAGTCTTCAGCAAAA',
                'k129_5631': 'TCATGATGATCCAAAAGCAGTTGCGGAAGCATCTGGGATAAT'
                             'TACGCGGAGTGGATGTCGCCG',
                'k129_2817': 'GTCGCCAATTAGCAACTATGATGTCTTCTGGAGTACCTTTGG'
                             'TCCAATCATTTGAAATCA'
            },
        }

    @staticmethod
    def mags_to_df(mags):
        df = pd.DataFrame.from_dict(mags, orient='index')
        df = df.astype(str).replace({'nan': None})
        df.index.name = 'Feature ID'
        return df

    @staticmethod
    def create_multi_generator(seqs_dict):
        for k1, v1 in seqs_dict.items():
            yield from zip(
                repeat(k1),
                (DNA(v2, metadata={'id': k2, 'description': ''})
                 for k2, v2 in v1.items())
            )

    @staticmethod
    def read_seqs_into_dict(loc):
        seqs = {}
        for f in sorted(glob.glob(f'{loc}/*')):
            seqs[_get_filename(f)] = {
                seq.metadata['id']: str(seq)
                for seq in skbio.read(f, format='fasta')
            }
        return seqs

    def test_mag_sequences_dir_fmt_to_dataframe(self):
        _, obs = self.transform_format(
            MAGSequencesDirFmt, pd.DataFrame,
            filenames=[
               'mags-fasta/3b7d53fb-5b60-46c6-8819-aeda065b12e9.fasta',
               'mags-fasta/6232c7e1-8ed7-47c8-9bdb-b94706a26931.fasta',
            ]
        )
        exp = self.mags_to_df(self.mags_fasta)
        pd.testing.assert_frame_equal(exp, obs)

    def test_dataframe_to_mag_sequences_dir_fmt(self):
        transformer = self.get_transformer(pd.DataFrame, MAGSequencesDirFmt)
        df = self.mags_to_df(self.mags_fasta)

        obs = transformer(df)
        self.assertIsInstance(obs, MAGSequencesDirFmt)

        obs_seqs = self.read_seqs_into_dict(str(obs))
        self.assertDictEqual(self.mags_fasta, obs_seqs)

    def test_mag_sequences_dir_fmt_to_mag_iterator(self):
        _, obs = self.transform_format(
            MAGSequencesDirFmt, MAGIterator,
            filenames=[
               'mags-fasta/6232c7e1-8ed7-47c8-9bdb-b94706a26931.fasta',
               'mags-fasta/3b7d53fb-5b60-46c6-8819-aeda065b12e9.fasta',
            ]
        )

        exp = self.create_multi_generator(self.mags_fasta)
        for e, o in zip(exp, obs):
            self.assertEqual(e, o)

    def test_mag_iterator_to_mag_sequences_dir_fmt(self):
        transformer = self.get_transformer(MAGIterator, MAGSequencesDirFmt)
        seq_iter = self.create_multi_generator(self.mags_fa)

        obs = transformer(seq_iter)
        self.assertIsInstance(obs, MAGSequencesDirFmt)

        obs_seqs = self.read_seqs_into_dict(str(obs))
        self.assertDictEqual(self.mags_fa, obs_seqs)

    def test_annotations_to_dataframe_samples(self):
        annotations = OrthologAnnotationDirFmt(
            self.get_data_path('ortholog_annotation_samples'),
            mode='r'
        )
        obs = _annotations_to_dataframe(annotations)
        self.assertEqual((11, 22), obs.shape)
        self.assertTrue(obs.columns[0] == "Sample")
        self.assertTrue(obs.index.is_unique)
        self.assertEqual("id", obs.index.name)

    def test_annotations_to_dataframe_mags(self):
        annotations = OrthologAnnotationDirFmt(
            self.get_data_path('ortholog_annotation_mags'),
            mode='r'
        )
        obs = _annotations_to_dataframe(annotations)
        self.assertEqual((11, 22), obs.shape)
        self.assertTrue(obs.columns[0] == "MAG")
        self.assertTrue(obs.index.is_unique)
        self.assertEqual("id", obs.index.name)

    def test_annotations_to_df_transformer(self):
        annotations = OrthologAnnotationDirFmt(
            self.get_data_path('ortholog_annotation_mags'),
            mode='r'
        )
        transformer = self.get_transformer(
            OrthologAnnotationDirFmt, pd.DataFrame
        )

        obs = transformer(annotations)
        self.assertIsInstance(obs, pd.DataFrame)
        self.assertEqual((11, 22), obs.shape)
        self.assertTrue(obs.columns[0] == "MAG")
        self.assertTrue(obs.index.is_unique)
        self.assertEqual("id", obs.index.name)

    def test_annotations_to_metadata_transformer(self):
        annotations = OrthologAnnotationDirFmt(
            self.get_data_path('ortholog_annotation_mags'),
            mode='r'
        )
        transformer = self.get_transformer(
            OrthologAnnotationDirFmt, qiime2.Metadata
        )

        obs = transformer(annotations)
        self.assertIsInstance(obs, qiime2.Metadata)


if __name__ == '__main__':
    unittest.main()
