# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path
import unittest

import pandas as pd
import pandas.io.common
import biom
import skbio
import qiime2

from pandas.util.testing import assert_frame_equal, assert_series_equal
from q2_types.feature_table import BIOMV210Format
from q2_types.feature_data import (
    TaxonomyFormat, HeaderlessTSVTaxonomyFormat, TSVTaxonomyFormat,
    DNAFASTAFormat, DNAIterator, PairedDNAIterator,
    PairedDNASequencesDirectoryFormat, AlignedDNAFASTAFormat,
    DifferentialFormat, AlignedDNAIterator
)
from q2_types.feature_data._transformer import (
    _taxonomy_formats_to_dataframe, _dataframe_to_tsv_taxonomy_format)
from qiime2.plugin.testing import TestPluginBase


# NOTE: these tests are fairly high-level and mainly test the transformer
# interfaces for the three taxonomy file formats. More in-depth testing for
# border cases, errors, etc. are in `TestTaxonomyFormatsToDataFrame` and
# `TestDataFrameToTSVTaxonomyFormat` below, which test the lower-level helper
# functions utilized by the transformers.
class TestTaxonomyFormatTransformers(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_taxonomy_format_to_dataframe_with_header(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        exp = pd.DataFrame([['k__Foo; p__Bar', '-1.0'],
                            ['k__Foo; p__Baz', '-42.0']], index=index,
                           columns=['Taxon', 'Confidence'], dtype=object)

        _, obs = self.transform_format(
            TaxonomyFormat, pd.DataFrame,
            filename=os.path.join('taxonomy', '3-column.tsv'))

        assert_frame_equal(obs, exp)

    def test_taxonomy_format_to_dataframe_without_header(self):
        # Bug identified in https://github.com/qiime2/q2-types/issues/107
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        columns = ['Taxon', 'Unnamed Column 1', 'Unnamed Column 2']
        exp = pd.DataFrame([['k__Foo; p__Bar', 'some', 'another'],
                            ['k__Foo; p__Baz', 'column', 'column!']],
                           index=index, columns=columns, dtype=object)

        _, obs = self.transform_format(
            TaxonomyFormat, pd.DataFrame,
            filename=os.path.join('taxonomy', 'headerless.tsv'))

        assert_frame_equal(obs, exp)

    def test_taxonomy_format_to_series_with_header(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        exp = pd.Series(['k__Foo; p__Bar', 'k__Foo; p__Baz'], index=index,
                        name='Taxon', dtype=object)

        _, obs = self.transform_format(
            TaxonomyFormat, pd.Series,
            filename=os.path.join('taxonomy', '3-column.tsv'))

        assert_series_equal(obs, exp)

    def test_taxonomy_format_to_series_without_header(self):
        # Bug identified in https://github.com/qiime2/q2-types/issues/107
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        exp = pd.Series(['k__Foo; p__Bar', 'k__Foo; p__Baz'], index=index,
                        name='Taxon', dtype=object)

        _, obs = self.transform_format(
            TaxonomyFormat, pd.Series,
            filename=os.path.join('taxonomy', 'headerless.tsv'))

        assert_series_equal(obs, exp)

    def test_headerless_tsv_taxonomy_format_to_tsv_taxonomy_format(self):
        exp = (
            'Feature ID\tTaxon\tUnnamed Column 1\tUnnamed Column 2\n'
            'seq1\tk__Foo; p__Bar\tsome\tanother\n'
            'seq2\tk__Foo; p__Baz\tcolumn\tcolumn!\n'
        )

        _, obs = self.transform_format(
            HeaderlessTSVTaxonomyFormat, TSVTaxonomyFormat,
            filename=os.path.join('taxonomy', 'headerless.tsv'))

        with obs.open() as fh:
            self.assertEqual(fh.read(), exp)

    def test_tsv_taxonomy_format_to_dataframe(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        exp = pd.DataFrame([['k__Foo; p__Bar', '-1.0'],
                            ['k__Foo; p__Baz', '-42.0']], index=index,
                           columns=['Taxon', 'Confidence'], dtype=object)

        _, obs = self.transform_format(
            TSVTaxonomyFormat, pd.DataFrame,
            filename=os.path.join('taxonomy', '3-column.tsv'))

        assert_frame_equal(obs, exp)

    def test_tsv_taxonomy_format_to_series(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        exp = pd.Series(['k__Foo; p__Bar', 'k__Foo; p__Baz'], index=index,
                        name='Taxon', dtype=object)

        _, obs = self.transform_format(
            TSVTaxonomyFormat, pd.Series,
            filename=os.path.join('taxonomy', '3-column.tsv'))

        assert_series_equal(obs, exp)

    def test_dataframe_to_tsv_taxonomy_format(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        columns = ['Taxon', 'Foo', 'Bar']
        df = pd.DataFrame([['taxon1', '42', 'foo'], ['taxon2', '43', 'bar']],
                          index=index, columns=columns, dtype=object)
        exp = (
            'Feature ID\tTaxon\tFoo\tBar\n'
            'seq1\ttaxon1\t42\tfoo\n'
            'seq2\ttaxon2\t43\tbar\n'
        )

        transformer = self.get_transformer(pd.DataFrame, TSVTaxonomyFormat)
        obs = transformer(df)

        with obs.open() as fh:
            self.assertEqual(fh.read(), exp)

    def test_series_to_tsv_taxonomy_format(self):
        index = pd.Index(['emrakul', 'peanut'], name='Feature ID',
                         dtype=object)
        series = pd.Series(['taxon1', 'taxon2'],
                           index=index, name='Taxon', dtype=object)
        exp = (
            'Feature ID\tTaxon\n'
            'emrakul\ttaxon1\n'
            'peanut\ttaxon2\n'
        )

        transformer = self.get_transformer(pd.Series, TSVTaxonomyFormat)
        obs = transformer(series)

        with obs.open() as fh:
            self.assertEqual(fh.read(), exp)

    def test_biom_table_to_tsv_taxonomy_format(self):
        filepath = self.get_data_path(
            os.path.join('taxonomy',
                         'feature-table-with-taxonomy-metadata_v210.biom'))
        table = biom.load_table(filepath)

        transformer = self.get_transformer(biom.Table, TSVTaxonomyFormat)
        obs = transformer(table)

        self.assertIsInstance(obs, TSVTaxonomyFormat)
        self.assertEqual(
            obs.path.read_text(),
            'Feature ID\tTaxon\nO0\ta; b\nO1\ta; b\nO2\ta; b\nO3\ta; b\n')

    def test_biom_table_to_tsv_taxonomy_format_no_taxonomy_md(self):
        filepath = self.get_data_path(
            os.path.join('taxonomy',
                         'feature-table-with-taxonomy-metadata_v210.biom'))
        table = biom.load_table(filepath)

        observation_metadata = [dict(taxon=['a', 'b']) for _ in range(4)]
        table = biom.Table(table.matrix_data,
                           observation_ids=table.ids(axis='observation'),
                           sample_ids=table.ids(axis='sample'),
                           observation_metadata=observation_metadata)

        transformer = self.get_transformer(biom.Table, TSVTaxonomyFormat)

        with self.assertRaisesRegex(ValueError,
                                    'O0 does not contain `taxonomy`'):
            transformer(table)

    def test_biom_table_to_tsv_taxonomy_format_missing_md(self):
        filepath = self.get_data_path(
            os.path.join('taxonomy',
                         'feature-table-with-taxonomy-metadata_v210.biom'))
        table = biom.load_table(filepath)

        observation_metadata = [dict(taxonomy=['a', 'b']) for _ in range(4)]
        observation_metadata[2]['taxonomy'] = None  # Wipe out one entry
        table = biom.Table(table.matrix_data,
                           observation_ids=table.ids(axis='observation'),
                           sample_ids=table.ids(axis='sample'),
                           observation_metadata=observation_metadata)

        transformer = self.get_transformer(biom.Table, TSVTaxonomyFormat)

        with self.assertRaisesRegex(TypeError, 'problem preparing.*O2'):
            transformer(table)

    def test_biom_v210_format_to_tsv_taxonomy_format(self):
        filename = os.path.join(
            'taxonomy', 'feature-table-with-taxonomy-metadata_v210.biom')

        _, obs = self.transform_format(BIOMV210Format, TSVTaxonomyFormat,
                                       filename=filename)

        self.assertIsInstance(obs, TSVTaxonomyFormat)
        self.assertEqual(
            obs.path.read_text(),
            'Feature ID\tTaxon\nO0\ta; b\nO1\ta; b\nO2\ta; b\nO3\ta; b\n')

    def test_biom_v210_format_no_md_to_tsv_taxonomy_format(self):
        with self.assertRaisesRegex(TypeError, 'observation metadata'):
            self.transform_format(
                BIOMV210Format, TSVTaxonomyFormat,
                filename=os.path.join('taxonomy', 'feature-table_v210.biom'))

    def test_taxonomy_format_with_header_to_metadata(self):
        _, obs = self.transform_format(TaxonomyFormat, qiime2.Metadata,
                                       os.path.join('taxonomy',
                                                    '3-column.tsv'))

        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        exp_df = pd.DataFrame([['k__Foo; p__Bar', '-1.0'],
                               ['k__Foo; p__Baz', '-42.0']], index=index,
                              columns=['Taxon', 'Confidence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_taxonomy_format_without_header_to_metadata(self):
        _, obs = self.transform_format(TaxonomyFormat, qiime2.Metadata,
                                       os.path.join('taxonomy',
                                                    'headerless.tsv'))

        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        columns = ['Taxon', 'Unnamed Column 1', 'Unnamed Column 2']
        exp_df = pd.DataFrame([['k__Foo; p__Bar', 'some', 'another'],
                               ['k__Foo; p__Baz', 'column', 'column!']],
                              index=index, columns=columns, dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_tsv_taxonomy_format_to_metadata(self):
        _, obs = self.transform_format(TSVTaxonomyFormat, qiime2.Metadata,
                                       os.path.join('taxonomy',
                                                    '3-column.tsv'))

        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        exp_df = pd.DataFrame([['k__Foo; p__Bar', '-1.0'],
                               ['k__Foo; p__Baz', '-42.0']], index=index,
                              columns=['Taxon', 'Confidence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)


# In-depth testing of the `_taxonomy_formats_to_dataframe` helper function,
# which does the heavy lifting for the transformers.
class TestTaxonomyFormatsToDataFrame(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_one_column(self):
        with self.assertRaisesRegex(ValueError, "two columns, found 1"):
            _taxonomy_formats_to_dataframe(
                self.get_data_path(os.path.join('taxonomy', '1-column.tsv')))

    def test_blanks_and_comments(self):
        with self.assertRaises(pandas.io.common.EmptyDataError):
            _taxonomy_formats_to_dataframe(
                self.get_data_path(os.path.join('taxonomy',
                                                'blanks-and-comments')))

    def test_empty(self):
        with self.assertRaises(pandas.io.common.EmptyDataError):
            _taxonomy_formats_to_dataframe(
                self.get_data_path(os.path.join('taxonomy', 'empty')))

    def test_header_only(self):
        with self.assertRaisesRegex(ValueError, 'one row of data'):
            _taxonomy_formats_to_dataframe(
                self.get_data_path(os.path.join('taxonomy',
                                                'header-only.tsv')))

    def test_has_header_with_headerless(self):
        with self.assertRaisesRegex(ValueError, 'requires a header'):
            _taxonomy_formats_to_dataframe(
                self.get_data_path(os.path.join('taxonomy', 'headerless.tsv')),
                has_header=True)

    def test_jagged(self):
        with self.assertRaises(pandas.io.common.CParserError):
            _taxonomy_formats_to_dataframe(
                self.get_data_path(os.path.join('taxonomy', 'jagged.tsv')))

    def test_duplicate_ids(self):
        with self.assertRaisesRegex(ValueError, 'duplicated: SEQUENCE1'):
            _taxonomy_formats_to_dataframe(
                self.get_data_path(os.path.join(
                    'taxonomy', 'duplicate-ids.tsv')))

    def test_duplicate_columns(self):
        with self.assertRaisesRegex(ValueError, 'duplicated: Column1'):
            _taxonomy_formats_to_dataframe(
                self.get_data_path(os.path.join(
                    'taxonomy', 'duplicate-columns.tsv')))

    def test_2_columns(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        exp = pd.DataFrame([['k__Bacteria; p__Proteobacteria'],
                            ['k__Bacteria']], index=index, columns=['Taxon'],
                           dtype=object)

        # has_header=None (default)
        obs = _taxonomy_formats_to_dataframe(
            self.get_data_path(os.path.join('taxonomy', '2-column.tsv')))

        assert_frame_equal(obs, exp)

        # has_header=True
        obs = _taxonomy_formats_to_dataframe(
            self.get_data_path(os.path.join('taxonomy', '2-column.tsv')),
            has_header=True)

        assert_frame_equal(obs, exp)

    def test_3_columns(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        exp = pd.DataFrame([['k__Foo; p__Bar', '-1.0'],
                            ['k__Foo; p__Baz', '-42.0']], index=index,
                           columns=['Taxon', 'Confidence'], dtype=object)

        # has_header=None (default)
        obs = _taxonomy_formats_to_dataframe(
            self.get_data_path(os.path.join('taxonomy', '3-column.tsv')))

        assert_frame_equal(obs, exp)

        # has_header=True
        obs = _taxonomy_formats_to_dataframe(
            self.get_data_path(os.path.join('taxonomy', '3-column.tsv')),
            has_header=True)

        assert_frame_equal(obs, exp)

    def test_valid_but_messy_file(self):
        index = pd.Index(
            ['SEQUENCE1', 'seq2'], name='Feature ID', dtype=object)
        exp = pd.DataFrame([['k__Bar; p__Baz', 'foo'],
                            ['some; taxonomy; for; ya', 'bar baz']],
                           index=index, columns=['Taxon', 'Extra Column'],
                           dtype=object)

        # has_header=None (default)
        obs = _taxonomy_formats_to_dataframe(
            self.get_data_path(os.path.join('taxonomy',
                                            'valid-but-messy.tsv')))

        assert_frame_equal(obs, exp)

        # has_header=True
        obs = _taxonomy_formats_to_dataframe(
            self.get_data_path(os.path.join('taxonomy',
                                            'valid-but-messy.tsv')),
            has_header=True)

        assert_frame_equal(obs, exp)

    def test_headerless(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        columns = ['Taxon', 'Unnamed Column 1', 'Unnamed Column 2']
        exp = pd.DataFrame([['k__Foo; p__Bar', 'some', 'another'],
                            ['k__Foo; p__Baz', 'column', 'column!']],
                           index=index, columns=columns, dtype=object)

        # has_header=None (default)
        obs = _taxonomy_formats_to_dataframe(
            self.get_data_path(os.path.join('taxonomy',
                                            'headerless.tsv')))

        assert_frame_equal(obs, exp)

        # has_header=False
        obs = _taxonomy_formats_to_dataframe(
            self.get_data_path(os.path.join('taxonomy',
                                            'headerless.tsv')),
            has_header=False)

        assert_frame_equal(obs, exp)


# In-depth testing of the `_dataframe_to_tsv_taxonomy_format` helper function,
# which does the heavy lifting for the transformers.
class TestDataFrameToTSVTaxonomyFormat(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_no_rows(self):
        index = pd.Index([], name='Feature ID', dtype=object)
        columns = ['Taxon']
        df = pd.DataFrame([], index=index, columns=columns, dtype=object)

        with self.assertRaisesRegex(ValueError, 'one row of data'):
            _dataframe_to_tsv_taxonomy_format(df)

    def test_no_columns(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        columns = []
        df = pd.DataFrame([[], []], index=index, columns=columns, dtype=object)

        with self.assertRaisesRegex(ValueError, 'one column of data'):
            _dataframe_to_tsv_taxonomy_format(df)

    def test_invalid_index_name(self):
        index = pd.Index(['seq1', 'seq2'], name='Foo', dtype=object)
        columns = ['Taxon']
        df = pd.DataFrame([['abc'], ['def']], index=index, columns=columns,
                          dtype=object)

        with self.assertRaisesRegex(ValueError, "`Feature ID`, found 'Foo'"):
            _dataframe_to_tsv_taxonomy_format(df)

    def test_invalid_taxon_column_name(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        columns = ['Foo']
        df = pd.DataFrame([['abc'], ['def']], index=index, columns=columns,
                          dtype=object)

        with self.assertRaisesRegex(ValueError, "`Taxon`, found 'Foo'"):
            _dataframe_to_tsv_taxonomy_format(df)

    def test_duplicate_ids(self):
        index = pd.Index(['seq1', 'seq2', 'seq1'], name='Feature ID',
                         dtype=object)
        columns = ['Taxon']
        df = pd.DataFrame([['abc'], ['def'], ['ghi']], index=index,
                          columns=columns, dtype=object)

        with self.assertRaisesRegex(ValueError, "duplicated: seq1"):
            _dataframe_to_tsv_taxonomy_format(df)

    def test_duplicate_columns(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        columns = ['Taxon', 'Taxon']
        df = pd.DataFrame([['abc', 'def'], ['ghi', 'jkl']], index=index,
                          columns=columns, dtype=object)

        with self.assertRaisesRegex(ValueError, "duplicated: Taxon"):
            _dataframe_to_tsv_taxonomy_format(df)

    def test_1_column(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        df = pd.DataFrame([['k__Bacteria; p__Proteobacteria'],
                           ['k__Bacteria']], index=index, columns=['Taxon'],
                          dtype=object)
        exp = (
            'Feature ID\tTaxon\n'
            'seq1\tk__Bacteria; p__Proteobacteria\n'
            'seq2\tk__Bacteria\n'
        )

        obs = _dataframe_to_tsv_taxonomy_format(df)

        with obs.open() as fh:
            self.assertEqual(fh.read(), exp)

    def test_2_columns(self):
        index = pd.Index(['seq1', 'seq2'], name='Feature ID', dtype=object)
        df = pd.DataFrame([['k__Bacteria; p__Proteobacteria', '42'],
                           ['k__Bacteria', '43']], index=index,
                          columns=['Taxon', 'Confidence'], dtype=object)
        exp = (
            'Feature ID\tTaxon\tConfidence\n'
            'seq1\tk__Bacteria; p__Proteobacteria\t42\n'
            'seq2\tk__Bacteria\t43\n'
        )

        obs = _dataframe_to_tsv_taxonomy_format(df)

        with obs.open() as fh:
            self.assertEqual(fh.read(), exp)


class TestDNAFASTAFormatTransformers(TestPluginBase):
    package = 'q2_types.feature_data.tests'

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

    def test_aln_dna_fasta_format_to_aln_dna_iterator(self):
        filename = 'aligned-dna-sequences.fasta'
        input, obs = self.transform_format(AlignedDNAFASTAFormat,
                                           AlignedDNAIterator,
                                           filename=filename)

        exp = skbio.read(str(input), format='fasta', constructor=skbio.DNA)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)

    def test_aln_dna_iterator_to_aln_dna_fasta_format(self):
        transformer = self.get_transformer(AlignedDNAIterator,
                                           AlignedDNAFASTAFormat)
        filepath = self.get_data_path('aligned-dna-sequences.fasta')
        generator = skbio.read(filepath, format='fasta', constructor=skbio.DNA)
        input = AlignedDNAIterator(generator)

        obs = transformer(input)
        self.assertIsInstance(obs, AlignedDNAFASTAFormat)
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

    def test_dnafasta_format_to_series(self):
        _, obs = self.transform_format(DNAFASTAFormat, pd.Series,
                                       'dna-sequences.fasta')

        obs = obs.astype(str)

        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'])
        exp = pd.Series(['ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTA'
                         'CGTACGTACGTACGTACGT', 'ACGTACGTACGTACGTACGTAC'
                         'GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACG'
                         'TACGTACGTACGTACGTACGT'], index=index, dtype=object)

        assert_series_equal(exp, obs)

    def test_series_to_dnafasta_format(self):
        transformer = self.get_transformer(pd.Series, DNAFASTAFormat)

        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'])
        input = pd.Series(['ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTA'
                           'CGTACGTACGTACGTACGT', 'ACGTACGTACGTACGTACGTAC'
                           'GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACG'
                           'TACGTACGTACGTACGTACGT'], index=index, dtype=object)

        obs = transformer(input)

        self.assertIsInstance(obs, DNAFASTAFormat)

    def test_dnafasta_format_with_duplicate_ids_to_series(self):
        with self.assertRaisesRegex(ValueError, 'unique.*SEQUENCE1'):
            self.transform_format(DNAFASTAFormat, pd.Series,
                                  'dna-sequences-with-duplicate-ids.fasta')

    def test_dnafasta_format_to_metadata(self):
        _, obs = self.transform_format(DNAFASTAFormat, qiime2.Metadata,
                                       'dna-sequences.fasta')
        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'], name='Feature ID')
        exp_df = pd.DataFrame(['ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTA'
                               'CGTACGTACGTACGTACGT', 'ACGTACGTACGTACGTACGTAC'
                               'GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACG'
                               'TACGTACGTACGTACGTACGT'], index=index,
                              columns=['Sequence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_aligned_dnafasta_format_to_metadata(self):
        _, obs = self.transform_format(AlignedDNAFASTAFormat, qiime2.Metadata,
                                       'aligned-dna-sequences.fasta')
        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'], name='Feature ID')
        exp_df = pd.DataFrame(['------------------------ACGTACGTACGTACGTACGTAC'
                               'GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT',
                               'ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTAC'
                               'GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT'],
                              index=index, columns=['Sequence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)


class TestDifferentialTransformer(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_differential_to_df(self):

        _, obs = self.transform_format(DifferentialFormat, pd.DataFrame,
                                       filename='differentials.tsv')

        # sniff to see if the first 4 feature ids are the same
        exp = ['F0', 'F1', 'F2', 'F3']
        obs = list(obs.index[:4])
        self.assertListEqual(exp, obs)

    def test_df_to_differential(self):
        transformer = self.get_transformer(pd.DataFrame, DifferentialFormat)

        index = pd.Index(['SEQUENCE1', 'SEQUENCE2', 'SEQUENCE3'])
        input = pd.Series([-1.3, 0.1, 1.2], index=index, dtype=float)

        obs = transformer(input)

        self.assertIsInstance(obs, DifferentialFormat)


if __name__ == '__main__':
    unittest.main()
