# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import pandas as pd
import qiime2
import skbio

from pandas.util.testing import assert_frame_equal, assert_series_equal
from q2_types.feature_data import (
    TaxonomyFormat, DNAFASTAFormat, DNAIterator, PairedDNAIterator,
    PairedDNASequencesDirectoryFormat, AlignedDNAFASTAFormat
)
from qiime2.plugin.testing import TestPluginBase


class TestTranfomers(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    # Test TaxonomyFormat Transformers
    def test_pd_dataframe_to_taxonomy_format(self):
        filepath = self.get_data_path('taxonomy.tsv')
        transformer = self.get_transformer(pd.DataFrame, TaxonomyFormat)
        # mimic _read_taxonomy from _transformer.py
        input = pd.read_csv(filepath, sep='\t', comment='#', header=0,
                            parse_dates=True, skip_blank_lines=True,
                            dtype=object)
        input.set_index(input.columns[0], drop=True, append=False,
                        inplace=True)

        obs = transformer(input)
        obs = pd.read_csv(str(obs), sep='\t',
                          comment='#', header=0, parse_dates=True,
                          skip_blank_lines=True, dtype=object)
        obs.set_index(obs.columns[0], drop=True, append=False, inplace=True)

        exp = input
        assert_frame_equal(obs, exp)

    def test_taxonomy_format_to_pd_dataframe(self):
        input, obs = self.transform_format(TaxonomyFormat, pd.DataFrame,
                                           filename='taxonomy.tsv')

        exp = pd.read_csv(str(input), sep='\t',
                          comment='#', header=0, parse_dates=True,
                          skip_blank_lines=True, dtype=object)
        exp.set_index(exp.columns[0], drop=True, append=False, inplace=True)

        assert_frame_equal(obs, exp)

    def test_taxonomy_format_to_pd_series(self):
        input, obs = self.transform_format(TaxonomyFormat, pd.Series,
                                           filename='taxonomy.tsv')

        exp = pd.read_csv(str(input), sep='\t',
                          comment='#', header=0, parse_dates=True,
                          skip_blank_lines=True, dtype=object)
        exp.set_index(exp.columns[0], drop=True, append=False, inplace=True)
        exp = exp.iloc[:, 0]

        assert_series_equal(obs, exp)

    def test_taxonomy_format_to_qiime_metadata(self):
        input, obs = self.transform_format(TaxonomyFormat, qiime2.Metadata,
                                           filename='taxonomy.tsv')

        df = pd.read_csv(str(input), sep='\t',
                         comment='#', header=0, parse_dates=True,
                         skip_blank_lines=True, dtype=object)
        df.set_index(df.columns[0], drop=True, append=False, inplace=True)
        exp = qiime2.Metadata(df)

        assert_frame_equal(obs.to_dataframe(), exp.to_dataframe())

    # Test DNA Sequence Transformers
    def test_dna_fasta_format_to_dna_iterator(self):
        input, obs = self.transform_format(DNAFASTAFormat, DNAIterator,
                                           filename='dna-sequences.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.DNA)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)

    def test_dna_iterator_to_dna_fasta_format(self):
        transformer = self.get_transformer(DNAIterator, DNAFASTAFormat)
        filepath = self.get_data_path('dna-sequences.fasta')
        generator = skbio.read(filepath, format='fasta', constructor=skbio.DNA)
        input = DNAIterator(generator)

        obs = transformer(input)
        self.assertIsInstance(obs, DNAFASTAFormat)
        obs = skbio.read(str(obs), format='fasta', constructor=skbio.DNA)

        for act, exp in zip(obs, input):
            self.assertEqual(act, exp)

    def test_pair_dna_sequences_directory_format_to_pair_dna_iterator(self):
        filenames = ('left-dna-sequences.fasta', 'right-dna-sequences.fasta')
        input, obs = self.transform_format(PairedDNASequencesDirectoryFormat,
                                           PairedDNAIterator,
                                           filenames=filenames)

        exp_left = skbio.read(self.get_data_path(filenames[0]),
                              format='fasta', constructor=skbio.DNA)
        exp_right = skbio.read(self.get_data_path(filenames[1]),
                               format='fasta', constructor=skbio.DNA)
        for act, exp in zip(obs, zip(exp_left, exp_right)):
            self.assertEqual(act, exp)
        self.assertIsInstance(obs, PairedDNAIterator)

    def test_pair_dna_iterator_to_pair_dna_sequences_directory_format(self):
        transformer = self.get_transformer(PairedDNAIterator,
                                           PairedDNASequencesDirectoryFormat)

        l_seqs = skbio.read(self.get_data_path('left-dna-sequences.fasta'),
                            format='fasta', constructor=skbio.DNA)
        r_seqs = skbio.read(self.get_data_path('right-dna-sequences.fasta'),
                            format='fasta', constructor=skbio.DNA)
        input = PairedDNAIterator(zip(l_seqs, r_seqs))

        obs = transformer(input)
        obs_l = skbio.read('%s/left-dna-sequences.fasta' % str(obs),
                           format='fasta', constructor=skbio.DNA)
        obs_r = skbio.read('%s/right-dna-sequences.fasta' % str(obs),
                           format='fasta', constructor=skbio.DNA)

        for act, exp in zip(zip(obs_l, obs_r), zip(l_seqs, r_seqs)):
            self.assertEqual(act, exp)
        self.assertIsInstance(obs, PairedDNASequencesDirectoryFormat)

    def test_aligned_dna_fasta_format_to_skbio_tabular_msa(self):
        filename = 'aligned-dna-sequences.fasta'
        input, obs = self.transform_format(AlignedDNAFASTAFormat,
                                           skbio.TabularMSA, filename=filename)
        exp = skbio.TabularMSA.read(str(input), constructor=skbio.DNA,
                                    format='fasta')

        for act, exp in zip(obs, exp):
            self.assertEqual(act, exp)

    def test_skbio_tabular_msa_to_aligned_dna_fasta_format(self):
        filepath = self.get_data_path('aligned-dna-sequences.fasta')
        transformer = self.get_transformer(skbio.TabularMSA,
                                           AlignedDNAFASTAFormat)
        input = skbio.TabularMSA.read(filepath, constructor=skbio.DNA,
                                      format='fasta')
        obs = transformer(input)
        obs = skbio.TabularMSA.read(str(obs), constructor=skbio.DNA,
                                    format='fasta')

        for act, exp in zip(obs, input):
            self.assertEqual(act, exp)


if __name__ == '__main__':
    unittest.main()
