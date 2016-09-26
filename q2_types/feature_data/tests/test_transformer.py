# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import shutil

import pandas as pd
import qiime
import skbio

from pandas.util.testing import assert_frame_equal, assert_series_equal
from q2_types.feature_data import (
    TaxonomyFormat, DNAFASTAFormat, DNAIterator, PairedDNAIterator,
    PairedDNASequencesDirectoryFormat, AlignedDNAFASTAFormat
)
from qiime.plugin.testing import TestPluginBase


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

        # capture the return value of the transformer and mimic _read_taxonomy
        obs = transformer(input)

        self.assertIsInstance(obs, TaxonomyFormat)

    def _init_taxonomy_tests(self, dest):
        transformer = self.get_transformer(TaxonomyFormat, dest)
        filepath = self.get_data_path('taxonomy.tsv')
        format = TaxonomyFormat(filepath, mode='r')

        return transformer, format

    def test_taxonomy_format_to_pd_dataframe(self):
        transformer, format = self._init_taxonomy_tests(pd.DataFrame)
        obs = transformer(format)

        exp = pd.read_csv(self.get_data_path('taxonomy.tsv'), sep='\t',
                          comment='#', header=0, parse_dates=True,
                          skip_blank_lines=True, dtype=object)
        exp.set_index(exp.columns[0], drop=True, append=False, inplace=True)

        self.assertIsInstance(obs, pd.DataFrame)
        assert_frame_equal(obs, exp)

    def test_taxonomy_format_to_pd_series(self):
        transformer, format = self._init_taxonomy_tests(pd.Series)
        obs = transformer(format)

        exp = pd.read_csv(self.get_data_path('taxonomy.tsv'), sep='\t',
                          comment='#', header=0, parse_dates=True,
                          skip_blank_lines=True, dtype=object)
        exp.set_index(exp.columns[0], drop=True, append=False, inplace=True)
        exp = exp.iloc[:, 0]

        self.assertIsInstance(obs, pd.Series)
        assert_series_equal(obs, exp)

    def test_taxonomy_format_to_qiime_metadata(self):
        transformer, format = self._init_taxonomy_tests(qiime.Metadata)
        obs = transformer(format)

        df = pd.read_csv(self.get_data_path('taxonomy.tsv'), sep='\t',
                         comment='#', header=0, parse_dates=True,
                         skip_blank_lines=True, dtype=object)
        df.set_index(df.columns[0], drop=True, append=False, inplace=True)
        exp = qiime.Metadata(df)

        self.assertIsInstance(obs, qiime.Metadata)
        assert_frame_equal(obs.to_dataframe(), exp.to_dataframe())

    # Test DNA Sequence Transformers
    def test_dna_fasta_format_to_dna_iterator(self):
        transformer = self.get_transformer(DNAFASTAFormat, DNAIterator)
        filepath = self.get_data_path('dna-sequences.fasta')
        format = DNAFASTAFormat(filepath, mode='r')

        obs = transformer(format)

        exp = skbio.read(filepath, format='fasta', constructor=skbio.DNA)
        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)
        self.assertIsInstance(obs, DNAIterator)

    def test_dna_iterator_to_dna_fasta_format(self):
        transformer = self.get_transformer(DNAIterator, DNAFASTAFormat)
        filepath = self.get_data_path('dna-sequences.fasta')
        generator = skbio.read(filepath, format='fasta', constructor=skbio.DNA)
        format = DNAIterator(generator)

        obs = transformer(format)

        self.assertIsInstance(obs, DNAFASTAFormat)

    def test_pair_dna_sequences_directory_format_to_pair_dna_iterator(self):
        transformer = self.get_transformer(PairedDNASequencesDirectoryFormat,
                                           PairedDNAIterator)
        filepath = self.get_data_path('dna-sequences.fasta')
        temp_dir = self.temp_dir.name
        l_seq = os.path.join(temp_dir, 'left-dna-sequences.fasta')
        r_seq = os.path.join(temp_dir, 'right-dna-sequences.fasta')

        shutil.copy(filepath, l_seq)
        shutil.copy(filepath, r_seq)
        format = PairedDNASequencesDirectoryFormat(temp_dir, mode='r')

        obs = transformer(format)

        exp_left = skbio.read(l_seq, format='fasta', constructor=skbio.DNA)
        exp_right = skbio.read(r_seq, format='fasta', constructor=skbio.DNA)
        for observed, expected in zip(obs, zip(exp_left, exp_right)):
            self.assertEqual(observed, expected)
        self.assertIsInstance(obs, PairedDNAIterator)

    def test_pair_dna_iterator_to_pair_dna_sequences_directory_format(self):
        transformer = self.get_transformer(PairedDNAIterator,
                                           PairedDNASequencesDirectoryFormat)
        filepath = self.get_data_path('dna-sequences.fasta')
        temp_dir = self.temp_dir.name
        l_seq = os.path.join(temp_dir, 'left-dna-sequences.fasta')
        r_seq = os.path.join(temp_dir, 'right-dna-sequences.fasta')

        shutil.copy(filepath, l_seq)
        shutil.copy(filepath, r_seq)

        left = skbio.read(l_seq, format='fasta', constructor=skbio.DNA)
        right = skbio.read(r_seq, format='fasta', constructor=skbio.DNA)
        generator = zip(left, right)
        format = PairedDNAIterator(generator)

        obs = transformer(format)

        self.assertIsInstance(obs, PairedDNASequencesDirectoryFormat)

    def test_aligned_dna_fasta_format_to_skbio_tabular_msa(self):
        transformer = self.get_transformer(AlignedDNAFASTAFormat,
                                           skbio.TabularMSA)
        filepath = self.get_data_path('aligned-dna-sequences.fasta')
        format = AlignedDNAFASTAFormat(filepath, mode='r')
        obs = transformer(format)

        self.assertIsInstance(obs, skbio.TabularMSA)

    def test_skbio_tabular_msa_to_aligned_dna_fasta_format(self):
        transformer = self.get_transformer(skbio.TabularMSA,
                                           AlignedDNAFASTAFormat)
        filepath = self.get_data_path('aligned-dna-sequences.fasta')
        input = skbio.TabularMSA.read(filepath, constructor=skbio.DNA,
                                      format='fasta')
        obs = transformer(input)

        self.assertIsInstance(obs, AlignedDNAFASTAFormat)
