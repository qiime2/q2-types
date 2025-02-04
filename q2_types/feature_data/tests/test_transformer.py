# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import filecmp
import os.path
import unittest

import pandas as pd
import pandas.errors
from pandas.testing import assert_frame_equal, assert_series_equal
import biom
import skbio

import qiime2
from qiime2.plugin.testing import TestPluginBase

from q2_types.feature_table import BIOMV210Format
from q2_types.feature_data import (
    TaxonomyFormat, HeaderlessTSVTaxonomyFormat, TSVTaxonomyFormat,
    DNAFASTAFormat, DNAIterator, PairedDNAIterator,
    ProteinIterator, AlignedProteinIterator,
    PairedDNASequencesDirectoryFormat, AlignedDNAFASTAFormat,
    DifferentialFormat, AlignedDNAIterator, ProteinFASTAFormat,
    AlignedProteinFASTAFormat, RNAFASTAFormat, AlignedRNAFASTAFormat,
    RNAIterator, AlignedRNAIterator, BLAST6Format, MixedCaseDNAFASTAFormat,
    MixedCaseRNAFASTAFormat, MixedCaseAlignedDNAFASTAFormat,
    MixedCaseAlignedRNAFASTAFormat,
    SequenceCharacteristicsFormat
)
from q2_types.feature_data._deferred_setup._transformers import (
    _taxonomy_formats_to_dataframe, _dataframe_to_tsv_taxonomy_format,
)


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

    def test_tsv_taxonomy_to_metadata_trailing_whitespace_taxon(self):
        _, obs = self.transform_format(TSVTaxonomyFormat, qiime2.Metadata,
                                       os.path.join(
                                           'taxonomy',
                                           'trailing_space_taxon.tsv'))

        index = pd.Index(['seq1'], name='Feature ID', dtype=object)
        exp_df = pd.DataFrame([['k__Foo; p__Bar', '-1.0']], index=index,
                              columns=['Taxon', 'Confidence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_tsv_taxonomy_to_metadata_leading_whitespace_taxon(self):
        _, obs = self.transform_format(TSVTaxonomyFormat, qiime2.Metadata,
                                       os.path.join(
                                           'taxonomy',
                                           'leading_space_taxon.tsv'))

        index = pd.Index(['seq1'], name='Feature ID', dtype=object)
        exp_df = pd.DataFrame([['k__Foo; p__Bar', '-1.0']], index=index,
                              columns=['Taxon', 'Confidence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_tsv_taxonomy_to_metadata_trailing_leading_whitespace_taxon(self):
        _, obs = self.transform_format(TSVTaxonomyFormat, qiime2.Metadata,
                                       os.path.join(
                                           'taxonomy',
                                           'start_end_space_taxon.tsv'))

        index = pd.Index(['seq1'], name='Feature ID', dtype=object)
        exp_df = pd.DataFrame([['k__Foo; p__Bar', '-1.0']], index=index,
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

    def test_blanks(self):
        with self.assertRaises(pandas.errors.EmptyDataError):
            _taxonomy_formats_to_dataframe(
                self.get_data_path(os.path.join('taxonomy',
                                                'blanks')))

    def test_empty(self):
        with self.assertRaises(pandas.errors.EmptyDataError):
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
        with self.assertRaises(pandas.errors.ParserError):
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
            transformer = self.get_transformer(DNAFASTAFormat, pd.Series)
            input = self.get_data_path(
                'dna-sequences-with-duplicate-ids.fasta')
            transformer(input)

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

    def test_aligned_dnafasta_format_to_series(self):
        _, obs = self.transform_format(AlignedDNAFASTAFormat, pd.Series,
                                       'aligned-dna-sequences.fasta')

        obs = obs.astype(str)

        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'])
        exp = pd.Series(['------------------------ACGTACGTACGTACGTACGTAC'
                         'GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT',
                         'ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTAC'
                         'GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT'],
                        index=index, dtype=object)

        assert_series_equal(exp, obs)

    def test_series_to_aligned_dnafasta_format(self):
        transformer = self.get_transformer(pd.Series, AlignedDNAFASTAFormat)

        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'])
        input = pd.Series(['------------------------ACGTACGTACGTACGTACGTAC'
                           'GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT',
                           'ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTAC'
                           'GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT'],
                          index=index, dtype=object)

        obs = transformer(input)

        self.assertIsInstance(obs, AlignedDNAFASTAFormat)

        obs_lines = list(open(str(obs)))
        self.assertEqual(obs_lines[0], '>SEQUENCE1\n')
        self.assertEqual(obs_lines[1],
                         '------------------------ACGTACGTACGTACGTACGTAC'
                         'GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT\n')
        self.assertEqual(obs_lines[2], '>SEQUENCE2\n')
        self.assertEqual(obs_lines[3],
                         'ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTAC'
                         'GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT\n')

    def test_aligned_dna_fasta_format_to_dna_iterator(self):
        input, obs = self.transform_format(
            AlignedDNAFASTAFormat, DNAIterator,
            filename='aligned-dna-sequences.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.DNA)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)

    def test_biom_table_to_dna_fasta_format(self):
        table_fn = 'feature-table-with-sequence-metadata.biom'
        input, obs = self.transform_format(
            BIOMV210Format, DNAFASTAFormat, table_fn
        )

        self.assertIsInstance(obs, DNAFASTAFormat)

        table_fp = self.get_data_path(table_fn)
        table = biom.load_table(table_fp)

        with open(str(obs)) as fh:
            lines = fh.readlines()
            fasta_header = lines[0].strip()
            fasta_sequence = lines[1].strip()
            num_lines = len(lines)

        ids = table.ids(axis='observation')
        # two lines (header & sequence) per feature
        self.assertEqual(len(ids), num_lines / 2)

        first_id = ids[0]
        first_seq = table.metadata(axis='observation')[0]['Sequence']
        self.assertEqual(fasta_header, f'>{first_id}')
        self.assertEqual(fasta_sequence, first_seq)

    def test_biom_table_to_dna_fasta_format_no_md(self):
        table_fp = os.path.join('taxonomy', 'feature-table_v210.biom')
        with self.assertRaisesRegex(TypeError, 'observation metadata'):
            self.transform_format(BIOMV210Format, DNAFASTAFormat, table_fp)

    def test_biom_table_to_dna_fasta_format_no_md_sequence_key(self):
        table_fp = os.path.join(
            'taxonomy', 'feature-table-with-taxonomy-metadata_v210.biom'
        )

        with self.assertRaisesRegex(
            ValueError, 'Observation .* does not have a sequence key.*'
        ):
            self.transform_format(BIOMV210Format, DNAFASTAFormat, table_fp)


class TestRNAFASTAFormatTransformers(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_rna_fasta_format_to_rna_iterator(self):
        input, obs = self.transform_format(RNAFASTAFormat, RNAIterator,
                                           filename='rna-sequences.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.RNA)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)

    def test_rna_iterator_to_rna_fasta_format(self):
        transformer = self.get_transformer(RNAIterator, RNAFASTAFormat)
        filepath = self.get_data_path('rna-sequences.fasta')
        generator = skbio.read(filepath, format='fasta', constructor=skbio.RNA)
        input = RNAIterator(generator)

        obs = transformer(input)
        self.assertIsInstance(obs, RNAFASTAFormat)
        obs = skbio.read(str(obs), format='fasta', constructor=skbio.RNA)

        for act, exp in zip(obs, input):
            self.assertEqual(act, exp)

    def test_aln_rna_fasta_format_to_aln_rna_iterator(self):
        filename = 'aligned-rna-sequences.fasta'
        input, obs = self.transform_format(AlignedRNAFASTAFormat,
                                           AlignedRNAIterator,
                                           filename=filename)

        exp = skbio.read(str(input), format='fasta', constructor=skbio.RNA)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)

    def test_aln_rna_iterator_to_aln_rna_fasta_format(self):
        transformer = self.get_transformer(AlignedRNAIterator,
                                           AlignedRNAFASTAFormat)
        filepath = self.get_data_path('aligned-rna-sequences.fasta')
        generator = skbio.read(filepath, format='fasta', constructor=skbio.RNA)
        input = AlignedRNAIterator(generator)

        obs = transformer(input)
        self.assertIsInstance(obs, AlignedRNAFASTAFormat)
        obs = skbio.read(str(obs), format='fasta', constructor=skbio.RNA)

        for act, exp in zip(obs, input):
            self.assertEqual(act, exp)

    def test_aligned_rna_fasta_format_to_skbio_tabular_msa(self):
        filename = 'aligned-rna-sequences.fasta'
        input, obs = self.transform_format(AlignedRNAFASTAFormat,
                                           skbio.TabularMSA, filename=filename)
        exp = skbio.TabularMSA.read(str(input), constructor=skbio.RNA,
                                    format='fasta')

        for act, exp in zip(obs, exp):
            self.assertEqual(act, exp)

    def test_skbio_tabular_msa_to_aligned_rna_fasta_format(self):
        filepath = self.get_data_path('aligned-rna-sequences.fasta')
        transformer = self.get_transformer(skbio.TabularMSA,
                                           AlignedRNAFASTAFormat)
        input = skbio.TabularMSA.read(filepath, constructor=skbio.RNA,
                                      format='fasta')
        obs = transformer(input)
        obs = skbio.TabularMSA.read(str(obs), constructor=skbio.RNA,
                                    format='fasta')

        for act, exp in zip(obs, input):
            self.assertEqual(act, exp)

    def test_rnafasta_format_to_series(self):
        _, obs = self.transform_format(RNAFASTAFormat, pd.Series,
                                       'rna-sequences.fasta')

        obs = obs.astype(str)

        index = pd.Index(['RNASEQUENCE1', 'RNASEQUENCE2'])
        exp = pd.Series(['ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUA'
                         'CGUACGUACGUACGUACGU', 'ACGUACGUACGUACGUACGUAC'
                         'GUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACG'
                         'UACGUACGUACGUACGUACGU'], index=index, dtype=object)

        assert_series_equal(exp, obs)

    def test_series_to_rnafasta_format(self):
        transformer = self.get_transformer(pd.Series, RNAFASTAFormat)

        index = pd.Index(['RNASEQUENCE1', 'RNASEQUENCE2'])
        input = pd.Series(['ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUA'
                           'CGUACGUACGUACGUACGU', 'ACGUACGUACGUACGUACGUAC'
                           'GUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACG'
                           'UACGUACGUACGUACGUACGU'], index=index, dtype=object)

        obs = transformer(input)

        self.assertIsInstance(obs, RNAFASTAFormat)

    def test_rnafasta_format_with_duplicate_ids_to_series(self):
        with self.assertRaisesRegex(ValueError, 'unique.*RNASEQUENCE1'):
            transformer = self.get_transformer(RNAFASTAFormat, pd.Series)
            input = self.get_data_path(
                'rna-sequences-with-duplicate-ids.fasta')
            transformer(input)

    def test_rnafasta_format_to_metadata(self):
        _, obs = self.transform_format(RNAFASTAFormat, qiime2.Metadata,
                                       'rna-sequences.fasta')
        index = pd.Index(['RNASEQUENCE1', 'RNASEQUENCE2'], name='Feature ID')
        exp_df = pd.DataFrame(['ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUA'
                               'CGUACGUACGUACGUACGU', 'ACGUACGUACGUACGUACGUAC'
                               'GUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACG'
                               'UACGUACGUACGUACGUACGU'], index=index,
                              columns=['Sequence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_aligned_rnafasta_format_to_metadata(self):
        _, obs = self.transform_format(AlignedRNAFASTAFormat, qiime2.Metadata,
                                       'aligned-rna-sequences.fasta')
        index = pd.Index(['RNASEQUENCE1', 'RNASEQUENCE2'], name='Feature ID')
        exp_df = pd.DataFrame(['------------------------ACGUACGUACGUACGUACGUAC'
                               'GUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGU',
                               'ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUAC'
                               'GUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGU'],
                              index=index, columns=['Sequence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_aligned_rnafasta_format_to_series(self):
        _, obs = self.transform_format(AlignedRNAFASTAFormat, pd.Series,
                                       'aligned-rna-sequences.fasta')

        obs = obs.astype(str)

        index = pd.Index(['RNASEQUENCE1', 'RNASEQUENCE2'])
        exp = pd.Series(['------------------------ACGUACGUACGUACGUACGUAC'
                         'GUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGU',
                         'ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUAC'
                         'GUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGU'],
                        index=index, dtype=object)

        assert_series_equal(exp, obs)

    def test_series_to_aligned_rnafasta_format(self):
        transformer = self.get_transformer(pd.Series, AlignedRNAFASTAFormat)

        index = pd.Index(['RNASEQUENCE1', 'RNASEQUENCE2'])
        input = pd.Series(['------------------------ACGUACGUACGUACGUACGUAC'
                           'GUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGU',
                           'ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUAC'
                           'GUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGU'],
                          index=index, dtype=object)

        obs = transformer(input)

        self.assertIsInstance(obs, AlignedRNAFASTAFormat)

        obs_lines = list(open(str(obs)))
        self.assertEqual(obs_lines[0], '>RNASEQUENCE1\n')
        self.assertEqual(obs_lines[1],
                         '------------------------ACGUACGUACGUACGUACGUAC'
                         'GUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGU\n')
        self.assertEqual(obs_lines[2], '>RNASEQUENCE2\n')
        self.assertEqual(obs_lines[3],
                         'ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUAC'
                         'GUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGU\n')

    def test_aligned_rna_fasta_format_to_rna_iterator(self):
        input, obs = self.transform_format(
            AlignedRNAFASTAFormat, RNAIterator,
            filename='aligned-rna-sequences.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.RNA)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)


class TestMixedCaseDNAFASTAFormatTransformers(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_mixed_case_dna_fasta_format_to_dna_iterator(self):
        input, obs = self.transform_format(
                                    MixedCaseDNAFASTAFormat,
                                    DNAIterator,
                                    filename='dna-sequences-mixed-case.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.DNA,
                         lowercase=True)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)

    def test_mixed_case_dna_fasta_format_to_series(self):
        _, obs = self.transform_format(MixedCaseDNAFASTAFormat, pd.Series,
                                       'dna-sequences-mixed-case.fasta')

        obs = obs.astype(str)

        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'])
        exp = pd.Series(['ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTAC'
                         'GTACGTACGTACGT', 'ACGTACGTACGTACGTACGTACGTACGTACGT'
                         'ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTAC'
                         'GTACGT'], index=index, dtype=object)

        assert_series_equal(exp, obs)

    def test_mixed_case_dna_fasta_format_with_duplicate_ids_to_series(self):
        with self.assertRaisesRegex(ValueError, 'unique.*SEQUENCE1'):
            transformer = self.get_transformer(
                        MixedCaseDNAFASTAFormat, pd.Series)
            input = self.get_data_path(
                'dna-sequences-mixed-case-with-duplicate-ids.fasta')
            transformer(input)

    def test_mixed_case_dna_fasta_format_to_metadata(self):
        _, obs = self.transform_format(MixedCaseDNAFASTAFormat,
                                       qiime2.Metadata,
                                       'dna-sequences-mixed-case.fasta')
        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'], name='Feature ID')
        exp_df = pd.DataFrame(['ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTA'
                               'CGTACGTACGTACGTACGT', 'ACGTACGTACGTACGTACGTAC'
                               'GTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACG'
                               'TACGTACGTACGTACGTACGT'], index=index,
                              columns=['Sequence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_mixed_case_dna_format_to_dna_format(self):
        input, obs = self.transform_format(
                                    MixedCaseDNAFASTAFormat,
                                    DNAFASTAFormat,
                                    filename='dna-sequences-mixed-case.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.DNA,
                         lowercase=True)
        transformer = self.get_transformer(DNAIterator, DNAFASTAFormat)
        exp = transformer(exp)

        self.assertIsInstance(obs, DNAFASTAFormat)
        self.assertEqual(
            obs.path.read_text(),
            exp.path.read_text())


class TestMixedCaseRNAFASTAFormatTransformers(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_mixed_case_rna_fasta_format_to_rna_iterator(self):
        input, obs = self.transform_format(
                                    MixedCaseRNAFASTAFormat,
                                    RNAIterator,
                                    filename='rna-sequences-mixed-case.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.RNA,
                         lowercase=True)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)

    def test_mixed_case_rna_fasta_format_to_series(self):
        _, obs = self.transform_format(MixedCaseRNAFASTAFormat, pd.Series,
                                       'rna-sequences-mixed-case.fasta')

        obs = obs.astype(str)

        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'])
        exp = pd.Series(['ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUAC'
                         'GUACGUACGUACGU', 'ACGUACGUACGUACGUACGUACGUACGUACGU'
                         'ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUAC'
                         'GUACGU'], index=index, dtype=object)

        assert_series_equal(exp, obs)

    def test_mixed_case_rna_fasta_format_with_duplicate_ids_to_series(self):
        with self.assertRaisesRegex(ValueError, 'unique.*SEQUENCE1'):
            transformer = self.get_transformer(
                        MixedCaseRNAFASTAFormat, pd.Series)
            input = self.get_data_path(
                'rna-sequences-mixed-case-with-duplicate-ids.fasta')
            transformer(input)

    def test_mixed_case_rna_fasta_format_to_metadata(self):
        _, obs = self.transform_format(MixedCaseRNAFASTAFormat,
                                       qiime2.Metadata,
                                       'rna-sequences-mixed-case.fasta')
        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'], name='Feature ID')
        exp_df = pd.DataFrame(['ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUA'
                               'CGUACGUACGUACGUACGU', 'ACGUACGUACGUACGUACGUAC'
                               'GUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACG'
                               'UACGUACGUACGUACGUACGU'], index=index,
                              columns=['Sequence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_mixed_case_rna_format_to_rna_format(self):
        input, obs = self.transform_format(
                                    MixedCaseRNAFASTAFormat,
                                    RNAFASTAFormat,
                                    filename='rna-sequences-mixed-case.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.RNA,
                         lowercase=True)
        transformer = self.get_transformer(RNAIterator, RNAFASTAFormat)
        exp = transformer(exp)

        self.assertIsInstance(obs, RNAFASTAFormat)
        self.assertEqual(
            obs.path.read_text(),
            exp.path.read_text())


class TestMixedCaseAlignedDNAFASTAFormatTransformers(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_mixed_case_aln_dna_fasta_format_to_aln_dna_iterator(self):
        input, obs = self.transform_format(
                            MixedCaseAlignedDNAFASTAFormat,
                            AlignedDNAIterator,
                            filename='aligned-dna-sequences-mixed-case.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.DNA,
                         lowercase=True)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)

    def test_mixed_case_aln_dna_fasta_format_to_series(self):
        _, obs = self.transform_format(
                        MixedCaseAlignedDNAFASTAFormat,
                        pd.Series, 'aligned-dna-sequences-mixed-case.fasta')

        obs = obs.astype(str)

        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'])
        exp = pd.Series(['------------------------ACGTACGTACGTACGTACGTACGTAC'
                         'GTACGTACGTACGTACGTACGTACGTACGTACGTACGT', 'ACGTACGT'
                         'ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTAC'
                         'GTACGTACGTACGTACGTACGTACGTACGT'], index=index,
                        dtype=object)

        assert_series_equal(exp, obs)

    def test_mixed_case_aln_dna_fasta_format_w_duplicate_ids_to_series(self):
        with self.assertRaisesRegex(ValueError, 'unique.*SEQUENCE1'):
            transformer = self.get_transformer(
                        MixedCaseAlignedDNAFASTAFormat, pd.Series)
            input = self.get_data_path(
                'dna-sequences-mixed-case-with-duplicate-ids.fasta')
            transformer(input)

    def test_mixed_case_aln_dna_fasta_format_to_metadata(self):
        _, obs = self.transform_format(
                        MixedCaseAlignedDNAFASTAFormat,
                        qiime2.Metadata,
                        'aligned-dna-sequences-mixed-case.fasta')
        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'], name='Feature ID')
        exp_df = pd.DataFrame(['------------------------ACGTACGTACGTACGTACGT'
                               'ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT',
                               'ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT'
                               'ACGTACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT'],
                              index=index, columns=['Sequence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_mixed_case_aln_dna_format_to_aln_dna_format(self):
        input, obs = self.transform_format(
                            MixedCaseAlignedDNAFASTAFormat,
                            AlignedDNAFASTAFormat,
                            filename='aligned-dna-sequences-mixed-case.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.DNA,
                         lowercase=True)
        transformer = self.get_transformer(AlignedDNAIterator,
                                           AlignedDNAFASTAFormat)
        exp = transformer(exp)

        self.assertIsInstance(obs, AlignedDNAFASTAFormat)
        self.assertEqual(
            obs.path.read_text(),
            exp.path.read_text())


class TestMixedCaseAlignedRNAFASTAFormatTransformers(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_mixed_case_aln_rna_fasta_format_to_aln_rna_iterator(self):
        input, obs = self.transform_format(
                            MixedCaseAlignedRNAFASTAFormat,
                            AlignedRNAIterator,
                            filename='aligned-rna-sequences-mixed-case.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.RNA,
                         lowercase=True)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)

    def test_mixed_case_aln_rna_fasta_format_to_series(self):
        _, obs = self.transform_format(
                        MixedCaseAlignedRNAFASTAFormat,
                        pd.Series, 'aligned-rna-sequences-mixed-case.fasta')

        obs = obs.astype(str)

        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'])
        exp = pd.Series(['------------------------ACGUACGUACGUACGUACGUACGUAC'
                         'GUACGUACGUACGUACGUACGUACGUACGUACGUACGU', 'ACGUACGU'
                         'ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUAC'
                         'GUACGUACGUACGUACGUACGUACGUACGU'], index=index,
                        dtype=object)

        assert_series_equal(exp, obs)

    def test_mixed_case_aln_rna_fasta_format_w_duplicate_ids_to_series(self):
        with self.assertRaisesRegex(ValueError, 'unique.*SEQUENCE1'):
            transformer = self.get_transformer(
                MixedCaseAlignedRNAFASTAFormat, pd.Series)
            input = self.get_data_path(
                'rna-sequences-mixed-case-with-duplicate-ids.fasta')
            transformer(input)

    def test_mixed_case_aln_rna_fasta_format_to_metadata(self):
        _, obs = self.transform_format(
                        MixedCaseAlignedRNAFASTAFormat,
                        qiime2.Metadata,
                        'aligned-rna-sequences-mixed-case.fasta')
        index = pd.Index(['SEQUENCE1', 'SEQUENCE2'], name='Feature ID')
        exp_df = pd.DataFrame(['------------------------ACGUACGUACGUACGUACGU'
                               'ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGU',
                               'ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGU'
                               'ACGUACGUACGUACGUACGUACGUACGUACGUACGUACGUACGU'],
                              index=index, columns=['Sequence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_mixed_case_aln_rna_format_to_aln_rna_format(self):
        input, obs = self.transform_format(
                            MixedCaseAlignedRNAFASTAFormat,
                            AlignedRNAFASTAFormat,
                            filename='aligned-rna-sequences-mixed-case.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.RNA,
                         lowercase=True)
        transformer = self.get_transformer(AlignedRNAIterator,
                                           AlignedRNAFASTAFormat)
        exp = transformer(exp)

        self.assertIsInstance(obs, AlignedRNAFASTAFormat)
        self.assertEqual(
            obs.path.read_text(),
            exp.path.read_text())


class TestDifferentialTransformer(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_differential_to_df(self):

        _, obs = self.transform_format(DifferentialFormat, pd.DataFrame,
                                       filename='differentials.tsv')

        # sniff to see if the first 4 feature ids are the same
        exp = ['F0', 'F1', 'F2', 'F3']
        obs = list(obs.index[:4])
        self.assertListEqual(exp, obs)

    def test_differential_to_md(self):

        _, obs = self.transform_format(DifferentialFormat, qiime2.Metadata,
                                       filename='differentials.tsv')
        obs = obs.to_dataframe()
        # sniff to see if the first 4 feature ids are the same
        exp = ['F0', 'F1', 'F2', 'F3']
        obs = list(obs.index[:4])
        self.assertListEqual(exp, obs)

    def test_df_to_differential(self):
        transformer = self.get_transformer(pd.DataFrame, DifferentialFormat)

        index = pd.Index(['SEQUENCE1', 'SEQUENCE2', 'SEQUENCE3'])
        index.name = 'featureid'
        input = pd.DataFrame(
            [-1.3, 0.1, 1.2], index=index, columns=['differential'],
            dtype=float)

        obs = transformer(input)

        self.assertIsInstance(obs, DifferentialFormat)


class TestProteinFASTAFormatTransformers(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_protein_fasta_format_to_protein_iterator(self):
        input, obs = self.transform_format(ProteinFASTAFormat, ProteinIterator,
                                           filename='protein-sequences.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.Protein)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)

    def test_protein_iterator_to_protein_fasta_format(self):
        transformer = self.get_transformer(
            ProteinIterator, ProteinFASTAFormat)
        filepath = self.get_data_path('protein-sequences.fasta')
        generator = skbio.read(
            filepath, format='fasta', constructor=skbio.Protein)
        input = ProteinIterator(generator)

        obs = transformer(input)
        self.assertIsInstance(obs, ProteinFASTAFormat)
        obs = skbio.read(str(obs), format='fasta', constructor=skbio.Protein)

        for act, exp in zip(obs, input):
            self.assertEqual(act, exp)

    def test_aln_protein_fasta_format_to_aln_protein_iterator(self):
        filename = 'aligned-protein-sequences.fasta'
        input, obs = self.transform_format(AlignedProteinFASTAFormat,
                                           AlignedProteinIterator,
                                           filename=filename)

        exp = skbio.read(str(input), format='fasta', constructor=skbio.Protein)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)

    def test_aln_protein_iterator_to_aln_protein_fasta_format(self):
        transformer = self.get_transformer(AlignedProteinIterator,
                                           AlignedProteinFASTAFormat)
        filepath = self.get_data_path('aligned-protein-sequences.fasta')
        generator = skbio.read(
            filepath, format='fasta', constructor=skbio.Protein)
        input = AlignedProteinIterator(generator)

        obs = transformer(input)
        self.assertIsInstance(obs, AlignedProteinFASTAFormat)
        obs = skbio.read(str(obs), format='fasta', constructor=skbio.Protein)

        for act, exp in zip(obs, input):
            self.assertEqual(act, exp)

    def test_aligned_protein_fasta_format_to_skbio_tabular_msa(self):
        filename = 'aligned-protein-sequences.fasta'
        input, obs = self.transform_format(AlignedProteinFASTAFormat,
                                           skbio.TabularMSA, filename=filename)
        exp = skbio.TabularMSA.read(str(input), constructor=skbio.Protein,
                                    format='fasta')

        for act, exp in zip(obs, exp):
            self.assertEqual(act, exp)

    def test_skbio_tabular_msa_to_aligned_protein_fasta_format(self):
        filepath = self.get_data_path('aligned-protein-sequences.fasta')
        transformer = self.get_transformer(skbio.TabularMSA,
                                           AlignedProteinFASTAFormat)
        input = skbio.TabularMSA.read(filepath, constructor=skbio.Protein,
                                      format='fasta')
        obs = transformer(input)
        obs = skbio.TabularMSA.read(str(obs), constructor=skbio.Protein,
                                    format='fasta')

        for act, exp in zip(obs, input):
            self.assertEqual(act, exp)

    def test_proteinfasta_format_to_series(self):
        _, obs = self.transform_format(ProteinFASTAFormat, pd.Series,
                                       'protein-sequences.fasta')

        obs = obs.astype(str)

        index = pd.Index(['sequence1', 'sequence2', 'sequence3'])
        exp = pd.Series(['MTTRDLTAAQFNETIQSSDMVLVDYWASWCGPCRAFAPTFAESSEK'
                         'HPDVVHAKVDTEAERELAAAAQIR',
                         'MVKQIESKTAFQEALDAAGDKLVVVDFSATWCGPCKMIKPFFHSLS'
                         'EKYSNVIFLEVDVDDCQDVASECEVKCMPTFQFFKKGQKVGEFSGAN*',
                         'TEPDZNZWKRUZQYTWUYKSWUQFPUNHMDBGHFDZ'
                         'SPIYKCZHQXLCEBYJREOAUJVDLIRPEGPOGMEJ'
                         'ZQQRHCFQXUPZLDWDGOXTOQTCIQDD*'],
                        index=index, dtype=object)

        assert_series_equal(exp, obs)

    def test_series_to_proteinfasta_format(self):
        transformer = self.get_transformer(pd.Series, ProteinFASTAFormat)

        index = pd.Index(['sequence1', 'sequence2', 'sequence3'])
        input = pd.Series(['MTTRDLTAAQFNETIQSSDMVLVDYWASWCGPCRAFAPTFAESSEK'
                           'HPDVVHAKVDTEAERELAAAAQIR',
                           'MVKQIESKTAFQEALDAAGDKLVVVDFSATWCGPCKMIKPFFHSLS'
                           'EKYSNVIFLEVDVDDCQDVASECEVKCMPTFQFFKKGQKVGEFSGAN*',
                           'TEPDZNZWKRUZQYTWUYKSWUQFPUNHMDBGHFDZ'
                           'SPIYKCZHQXLCEBYJREOAUJVDLIRPEGPOGMEJ'
                           'ZQQRHCFQXUPZLDWDGOXTOQTCIQDD*'],
                          index=index, dtype=object)

        obs = transformer(input)

        self.assertIsInstance(obs, ProteinFASTAFormat)

    def test_proteinfasta_format_with_duplicate_ids_to_series(self):
        with self.assertRaisesRegex(ValueError, 'unique.*sequence1'):
            transformer = self.get_transformer(ProteinFASTAFormat, pd.Series)
            input = self.get_data_path('protein-sequences-duplicate-ids.fasta')
            transformer(input)

    def test_proteinfasta_format_to_metadata(self):
        _, obs = self.transform_format(ProteinFASTAFormat, qiime2.Metadata,
                                       'protein-sequences.fasta')
        index = pd.Index(
            ['sequence1', 'sequence2', 'sequence3'], name='Feature ID'
        )
        exp_df = pd.DataFrame(['MTTRDLTAAQFNETIQSSDMVLVDYWASWCGPCRA'
                               'FAPTFAESSEKHPDVVHAKVDTEAERELAAAAQIR',
                               'MVKQIESKTAFQEALDAAGDKLVVVDFSATWCGPC'
                               'KMIKPFFHSLSEKYSNVIFLEVDVDDCQDVASECE'
                               'VKCMPTFQFFKKGQKVGEFSGAN*',
                               'TEPDZNZWKRUZQYTWUYKSWUQFPUNHMDBGHFDZ'
                               'SPIYKCZHQXLCEBYJREOAUJVDLIRPEGPOGMEJ'
                               'ZQQRHCFQXUPZLDWDGOXTOQTCIQDD*'],
                              index=index, columns=['Sequence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_aligned_proteinfasta_format_to_metadata(self):
        _, obs = self.transform_format(AlignedProteinFASTAFormat,
                                       qiime2.Metadata,
                                       'aligned-protein-sequences.fasta')
        index = pd.Index(
            ['sequence1', 'sequence2', 'sequence3'], name='Feature ID'
        )
        exp_df = pd.DataFrame(['------------------------VDFSATWCGPC'
                               'KMIKPFFHSLSEKYSNVIFLEVDVDDCQDVASECE'
                               'VKCMPTFQFFKKGQKVGEFSGAN',
                               'MVKQIESKTAFQEALDAAGDKLVVVDFSATWCGPC'
                               'KMIKPFFHSLSEKYSNVIFLEVDVDDCQDVASECE'
                               'VKCMPTFQ-------VGEFSGAN',
                               'MVKQIESKTAFQJALDAAGDKLVVVDFSATWCGPC'
                               'KMIKPFFHSLSEKYSNUIFLEVDVDDCQD'
                               'VASECEVKCMPTFO-------VGEFSGAN'],
                              index=index, columns=['Sequence'], dtype=object)
        exp = qiime2.Metadata(exp_df)

        self.assertEqual(exp, obs)

    def test_aligned_proteinfasta_format_to_series(self):
        _, obs = self.transform_format(AlignedProteinFASTAFormat, pd.Series,
                                       'aligned-protein-sequences.fasta')

        obs = obs.astype(str)

        index = pd.Index(['sequence1', 'sequence2', 'sequence3'])
        exp = pd.Series(['------------------------VDFSATWCGPC'
                         'KMIKPFFHSLSEKYSNVIFLEVDVDDCQDVASECE'
                         'VKCMPTFQFFKKGQKVGEFSGAN',
                         'MVKQIESKTAFQEALDAAGDKLVVVDFSATWCGPC'
                         'KMIKPFFHSLSEKYSNVIFLEVDVDDCQDVASECE'
                         'VKCMPTFQ-------VGEFSGAN',
                         'MVKQIESKTAFQJALDAAGDKLVVVDFSATWCGPC'
                         'KMIKPFFHSLSEKYSNUIFLEVDVDDCQD'
                         'VASECEVKCMPTFO-------VGEFSGAN'],
                        index=index, dtype=object)

        assert_series_equal(exp, obs)

    def test_series_to_aligned_proteinfasta_format(self):
        transformer = self.get_transformer(
            pd.Series, AlignedProteinFASTAFormat)

        index = pd.Index(['sequence1', 'sequence2', 'sequence3'])
        input = pd.Series(['------------------------VDFSATWCGPC'
                           'KMIKPFFHSLSEKYSNVIFLEVDVDDCQDVASECE'
                           'VKCMPTFQFFKKGQKVGEFSGAN',
                           'MVKQIESKTAFQEALDAAGDKLVVVDFSATWCGPC'
                           'KMIKPFFHSLSEKYSNVIFLEVDVDDCQDVASECE'
                           'VKCMPTFQ-------VGEFSGAN',
                           'MVKQIESKTAFQJALDAAGDKLVVVDFSATWCGPC'
                           'KMIKPFFHSLSEKYSNUIFLEVDVDDCQD'
                           'VASECEVKCMPTFO-------VGEFSGAN'],
                          index=index, dtype=object)

        obs = transformer(input)

        self.assertIsInstance(obs, AlignedProteinFASTAFormat)

        obs_lines = list(open(str(obs)))
        self.assertEqual(obs_lines[0], '>sequence1\n')
        self.assertEqual(obs_lines[1],
                         '------------------------VDFSATWCGPC'
                         'KMIKPFFHSLSEKYSNVIFLEVDVDDCQDVASECE'
                         'VKCMPTFQFFKKGQKVGEFSGAN\n')
        self.assertEqual(obs_lines[2], '>sequence2\n')
        self.assertEqual(obs_lines[3],
                         'MVKQIESKTAFQEALDAAGDKLVVVDFSATWCGPC'
                         'KMIKPFFHSLSEKYSNVIFLEVDVDDCQDVASECE'
                         'VKCMPTFQ-------VGEFSGAN\n')
        self.assertEqual(obs_lines[4], '>sequence3\n')
        self.assertEqual(obs_lines[5],
                         'MVKQIESKTAFQJALDAAGDKLVVVDFSATWCGPC'
                         'KMIKPFFHSLSEKYSNUIFLEVDVDDCQD'
                         'VASECEVKCMPTFO-------VGEFSGAN\n')

    def test_aligned_protein_fasta_format_to_protein_iterator(self):
        input, obs = self.transform_format(
            AlignedProteinFASTAFormat, ProteinIterator,
            filename='aligned-protein-sequences.fasta')

        exp = skbio.read(str(input), format='fasta', constructor=skbio.Protein)

        for observed, expected in zip(obs, exp):
            self.assertEqual(observed, expected)


class TestBLAST6Transformer(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_blast6_to_df(self):

        _, obs = self.transform_format(BLAST6Format, pd.DataFrame,
                                       filename='blast6.tsv')
        self.assertEqual(obs.shape[0], 2)
        self.assertListEqual(obs.columns.tolist(), [
            'qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen',
            'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore'])
        self.assertListEqual(obs['pident'].tolist(), [100.0, 99.38])
        self.assertListEqual(obs['mismatch'].tolist(), [0.0, 1.0])
        self.assertListEqual(obs['bitscore'].tolist(), [330.0, 329.0])

    def test_df_to_blast6(self):
        transformer = self.get_transformer(pd.DataFrame, BLAST6Format)

        columns = [
            'qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen',
            'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore']
        data = [
            ['moaC', 'gi|15800534|ref|NP_286546.1|', 100.0, 161.0, 0.0, 0.0,
                1.0, 161.0, 1.0, 161.0, 2e-114, 330.0],
            ['moaC', 'gi|170768970|ref|ZP_02903423.1|', 99.38, 161.0, 1.0,
                0.0, 1.0, 161.0, 1.0, 161.0, 8e-114, 329.0]]
        input = pd.DataFrame(data=data, columns=columns)
        obs = transformer(input)
        self.assertIsInstance(obs, BLAST6Format)

    def test_blast6_to_metadata(self):

        _, obs = self.transform_format(BLAST6Format, qiime2.Metadata,
                                       filename='blast6.tsv')
        # we already validated the DataFrame transformer above, so just use
        # that as a reference point for this test, but re-cast the index as str
        _, exp = self.transform_format(BLAST6Format, pd.DataFrame,
                                       filename='blast6.tsv')
        exp.index = pd.Index(exp.index.astype(str), name='id')
        assert_frame_equal(obs.to_dataframe(), exp)


class TestSequenceCharacteristicsTransformer(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def setUp(self):
        super().setUp()
        self.exp_file = self.get_data_path(
            'sequence_characteristics_length.tsv')
        self.exp_df = pd.DataFrame({'length': [876, 54]},
                                   index=pd.Index([1, 2], name='id'))

    def test_df_to_sequence_characteristics_format(self):
        transformer = self.get_transformer(pd.DataFrame,
                                           SequenceCharacteristicsFormat)
        obs = transformer(self.exp_df)

        self.assertIsInstance(obs, SequenceCharacteristicsFormat)
        assert filecmp.cmp(self.exp_file, obs.path)

    def test_sequence_characteristics_format_to_df(self):
        transformer = self.get_transformer(SequenceCharacteristicsFormat,
                                           pd.DataFrame)
        format = SequenceCharacteristicsFormat(self.exp_file, mode='r')
        obs = transformer(format)

        assert_frame_equal(self.exp_df, obs)

    def test_sequence_characteristics_format_to_metadata(self):
        transformer = self.get_transformer(SequenceCharacteristicsFormat,
                                           qiime2.Metadata)
        format = SequenceCharacteristicsFormat(self.exp_file, mode='r')
        obs = transformer(format)

        self.exp_df.index = pd.Index(self.exp_df.index.astype(str))
        self.exp_df['length'] = self.exp_df['length'].astype('float64')

        assert_frame_equal(obs.to_dataframe(), self.exp_df)


if __name__ == '__main__':
    unittest.main()
