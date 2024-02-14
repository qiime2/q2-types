# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import pandas as pd
import skbio.io
from qiime2.plugin.testing import TestPluginBase

from q2_types.genome_data import (
    GenesDirectoryFormat, ProteinsDirectoryFormat, GFF3Format,
    IntervalMetadataIterator
)


class TestTransformers(TestPluginBase):
    package = 'q2_types.genome_data.tests'

    def setUp(self):
        super().setUp()
        self.genes = {
            'genes1': {
                'gene1': 'GGCAGATTCCCCCTAGACCCGCCCGCACCATGGTCAGGCATGCCCCTCC'
                         'TCATCGCTGGGCACAGCCCAGAGGGTATAAACAGTGCTGGAGGC',
                'gene2': 'CCACTGCACTCACCGCACCCGGCCAATTTTTGTGTTTTTAGTAGAGACT'
                         'AAATACCATATAGTGAACACCTAAGACGGGGGGCCTTGG',
                'gene3': 'GCACCCGGCCAATTTTTGTGTTTTTAGTAGAGAAGATTCCCCCTAGACC'
                         'CGCCCGCTATAGTGAACACCTAAGAACTGGAGG'
            },
            'genes2': {
                'gene11': 'ATGGTCAGGCATGCCCCTCCTCATCGCTGGGCGGCAGATTCCCCCTAG'
                          'ACCCGCCCGCACCACAGCCCAGAGGGTATAAACAGTGCTGGAGGC',
                'gene12': 'AATACCATATAGTGAACACCTAACCACTGCACTCACCGCACCCGGCCA'
                          'ATTTTTGTGTTTTTAGTAGAGACTAGACGGGGGGCCTTGG'
            }
        }
        self.proteins = {
            'proteins1': {
                'k129_5480_1': 'MPKRTDISSICIIGAGPIVIGQACEFDYSGAQACKALKEEGYR'
                               'VVLINSNPATIMTDPNMADATYIEPITP',
                'k129_5480_2': 'MQKIPLTKQGHTDLEAELKDLKHRQRPAVIAAISEAREHGDLS'
                               'ENAEYHAAREQQSFIEGRIEQVEAILSLAEIIDPAK'
            },
            'proteins2': {
                'k129_5112_1': 'MTEQTETSQRPVLVVDFGAQYAQLIARRVREAGVYSELVPHTA'
                               'TAEEIAAKDPIGIILSGGPSSVYEPGAPTLDPAVFDLGVP',
                'k129_5112_2': 'MPREPKPSSFPAIRGALTFYQVASIITGVMLLLLLAEMILKYS'
                               'PLHVELFAGGSGGFLWFAPVLVG'
            }
        }

    @staticmethod
    def seqs_to_df(seqs):
        df = pd.DataFrame.from_dict(seqs, orient='index')
        df = df.astype(str).replace({'nan': None})
        df.index.name = 'Genome ID'
        return df

    def test_genes_to_dataframe(self):
        _, obs = self.transform_format(GenesDirectoryFormat, pd.DataFrame,
                                       filenames=[
                                           'genes-with-suffix/genes1.fa',
                                           'genes-with-suffix/genes2.fa'
                                       ])
        exp = self.seqs_to_df(self.genes)
        pd.testing.assert_frame_equal(exp, obs)

    def test_dataframe_to_genes(self):
        transformer = self.get_transformer(pd.DataFrame, GenesDirectoryFormat)
        df = self.seqs_to_df(self.genes)

        obs = transformer(df)
        self.assertIsInstance(obs, GenesDirectoryFormat)

    def test_proteins_to_dataframe(self):
        _, obs = self.transform_format(
            ProteinsDirectoryFormat,
            pd.DataFrame,
            filenames=[
                'proteins-with-suffix/proteins1.faa',
                'proteins-with-suffix/proteins2.faa'
            ])
        exp = self.seqs_to_df(self.proteins)
        pd.testing.assert_frame_equal(exp, obs)

    def test_dataframe_to_proteins(self):
        transformer = self.get_transformer(
            pd.DataFrame, ProteinsDirectoryFormat)
        df = self.seqs_to_df(self.proteins)

        obs = transformer(df)
        self.assertIsInstance(obs, ProteinsDirectoryFormat)

    def test_gff_to_interval_metadata_iterator(self):
        input, obs = self.transform_format(
            GFF3Format,
            IntervalMetadataIterator,
            filename='loci-with-suffix/loci1.gff')
        exp = skbio.io.read(str(input), format='gff3')

        for o, e in zip(obs, exp):
            self.assertEqual(o, e)

    def test_interval_metadata_iterator_to_gff(self):
        transformer = self.get_transformer(IntervalMetadataIterator,
                                           GFF3Format)
        filepath = self.get_data_path('loci-with-suffix/loci1.gff')
        generator = skbio.io.read(filepath, format='gff3')
        input = IntervalMetadataIterator(generator)

        obs = transformer(input)
        self.assertIsInstance(obs, GFF3Format)
        obs = skbio.io.read(str(obs), format='gff3')

        for o, e in zip(obs, input):
            self.assertEqual(o, e)


if __name__ == '__main__':
    unittest.main()
