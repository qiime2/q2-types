# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import collections.abc
from itertools import zip_longest

import pandas as pd
import biom
import skbio

from ..plugin_setup import plugin
from ..feature_table import BIOMV210Format
from . import (TaxonomyFormat, HeaderlessTSVTaxonomyFormat, TSVTaxonomyFormat,
               DNAFASTAFormat, PairedDNASequencesDirectoryFormat,
               AlignedDNAFASTAFormat)


# Taxonomy format transformers

def _taxonomy_formats_to_dataframe(filepath, has_header=None):
    """Read any of the three taxonomy formats into a dataframe.

    Parameters
    ----------
    filepath : str
        The taxonomy-formatted file to be read.
    has_header : bool, optional
        If `None`, autodetect the header: only `Feature ID<tab>Taxon` is
        recognized, optionally followed by other columns. If `True`, the file
        must have the expected header described above otherwise an error is
        raised. If `False`, the file is read without assuming a header.

    Returns
    -------
    pd.DataFrame
        Dataframe containing parsed contents of the taxonomy file. The
        dataframe will have its index name set to `Feature ID` and its first
        column will be `Taxon`, followed by any other columns in the input
        file.

    """
    # Using `dtype=object` and `set_index()` to avoid type casting/inference of
    # any columns or the index.
    df = pd.read_csv(filepath, sep='\t', comment='#', skip_blank_lines=True,
                     header=None, dtype=object)

    if len(df.columns) < 2:
        raise ValueError(
            "Taxonomy format requires at least two columns, found %d."
            % len(df.columns))

    if has_header and not _has_expected_header(df):
        raise ValueError(
            "Taxonomy format requires a header with `Feature ID` and `Taxon` "
            "as the first two columns.")

    if has_header or (has_header is None and _has_expected_header(df)):
        # Make first row the header:
        #     https://stackoverflow.com/a/26147330/3776794
        df.columns = df.iloc[0]
        df.columns.name = None
        df = df.reindex(df.index.drop(0))
    else:
        # No header
        unnamed_columns = ['Unnamed Column %d' % (i + 1)
                           for i in range(len(df.columns[2:]))]
        df.columns = TSVTaxonomyFormat.HEADER + unnamed_columns

    df.set_index(df.columns[0], drop=True, append=False, inplace=True)

    if len(df.index) < 1:
        raise ValueError("Taxonomy format requires at least one row of data.")

    if df.index.has_duplicates:
        raise ValueError(
            "Taxonomy format feature IDs must be unique. The following IDs "
            "are duplicated: %s" % ', '.join(df.index.get_duplicates()))

    if df.columns.has_duplicates:
        raise ValueError(
            "Taxonomy format column names must be unique. The following "
            "column names are duplicated: %s" %
            ', '.join(df.columns.get_duplicates()))

    return df


def _has_expected_header(df):
    return df.iloc[0].tolist()[:2] == TSVTaxonomyFormat.HEADER


def _dataframe_to_tsv_taxonomy_format(df):
    if len(df.index) < 1:
        raise ValueError("Taxonomy format requires at least one row of data.")

    if len(df.columns) < 1:
        raise ValueError(
            "Taxonomy format requires at least one column of data.")

    if df.index.name != 'Feature ID':
        raise ValueError(
            "Taxonomy format requires the dataframe index name to be "
            "`Feature ID`, found %r" % df.index.name)

    if df.columns[0] != 'Taxon':
        raise ValueError(
            "Taxonomy format requires the first column name to be `Taxon`, "
            "found %r" % df.columns[0])

    if df.index.has_duplicates:
        raise ValueError(
            "Taxonomy format feature IDs must be unique. The following IDs "
            "are duplicated: %s" % ', '.join(df.index.get_duplicates()))

    if df.columns.has_duplicates:
        raise ValueError(
            "Taxonomy format column names must be unique. The following "
            "column names are duplicated: %s" %
            ', '.join(df.columns.get_duplicates()))

    ff = TSVTaxonomyFormat()
    df.to_csv(str(ff), sep='\t', header=True, index=True)
    return ff


def _biom_to_tsv_taxonomy_format(table):
    metadata = table.metadata(axis='observation')
    ids = table.ids(axis='observation')
    if metadata is None:
        raise TypeError('Table must have observation metadata.')

    taxonomy = []
    for oid, m in zip(ids, metadata):
        if 'taxonomy' not in m:
            raise ValueError('Observation %s does not contain `taxonomy` '
                             'metadata.' % oid)

        try:
            taxonomy.append('; '.join(m['taxonomy']))
        except Exception as e:
            raise TypeError('There was a problem preparing the taxonomy '
                            'data for Observation %s. Metadata should be '
                            'formatted as a list of strings; received %r.'
                            % (oid, type(m['taxonomy']))) from e

    series = pd.Series(taxonomy, index=ids, name='Taxon')
    series.index.name = 'Feature ID'
    return _dataframe_to_tsv_taxonomy_format(series.to_frame())


@plugin.register_transformer
def _4(ff: TaxonomyFormat) -> pd.DataFrame:
    return _taxonomy_formats_to_dataframe(str(ff), has_header=None)


@plugin.register_transformer
def _6(ff: TaxonomyFormat) -> pd.Series:
    series = _taxonomy_formats_to_dataframe(str(ff), has_header=None)
    return series.iloc[:, 0]


@plugin.register_transformer
def _20(ff: HeaderlessTSVTaxonomyFormat) -> TSVTaxonomyFormat:
    return _dataframe_to_tsv_taxonomy_format(
        _taxonomy_formats_to_dataframe(str(ff), has_header=False))


@plugin.register_transformer
def _22(ff: TSVTaxonomyFormat) -> pd.DataFrame:
    return _taxonomy_formats_to_dataframe(str(ff), has_header=True)


@plugin.register_transformer
def _23(ff: TSVTaxonomyFormat) -> pd.Series:
    df = _taxonomy_formats_to_dataframe(str(ff), has_header=True)
    return df.iloc[:, 0]


@plugin.register_transformer
def _24(df: pd.DataFrame) -> TSVTaxonomyFormat:
    return _dataframe_to_tsv_taxonomy_format(df)


@plugin.register_transformer
def _25(series: pd.Series) -> TSVTaxonomyFormat:
    return _dataframe_to_tsv_taxonomy_format(series.to_frame())


@plugin.register_transformer
def _26(data: biom.Table) -> TSVTaxonomyFormat:
    return _biom_to_tsv_taxonomy_format(data)


@plugin.register_transformer
def _27(ff: BIOMV210Format) -> TSVTaxonomyFormat:
    # skip _parse_biom_table_v210 because it strips out metadata
    with ff.open() as fh:
        table = biom.Table.from_hdf5(fh)
    return _biom_to_tsv_taxonomy_format(table)


# DNA FASTA transformers

class DNAIterator(collections.abc.Iterable):
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        yield from self.generator


class PairedDNAIterator(DNAIterator):
    pass


class AlignedDNAIterator(DNAIterator):
    pass


def _read_dna_fasta(path):
    return skbio.read(path, format='fasta', constructor=skbio.DNA)


@plugin.register_transformer
def _9(ff: DNAFASTAFormat) -> DNAIterator:
    generator = _read_dna_fasta(str(ff))
    return DNAIterator(generator)


@plugin.register_transformer
def _10(data: DNAIterator) -> DNAFASTAFormat:
    ff = DNAFASTAFormat()
    skbio.io.write(iter(data), format='fasta', into=str(ff))
    return ff


@plugin.register_transformer
def _11(df: PairedDNASequencesDirectoryFormat) -> PairedDNAIterator:
    left = df.left_dna_sequences.view(DNAIterator)
    right = df.right_dna_sequences.view(DNAIterator)

    def read_seqs():
        for lseq, rseq in zip_longest(left, right):
            if rseq is None:
                raise ValueError('more left sequences than right sequences')
            if lseq is None:
                raise ValueError('more right sequences than left sequences')
            if rseq.metadata['id'] != lseq.metadata['id']:
                raise ValueError(lseq.metadata['id'] + ' and ' +
                                 rseq.metadata['id'] + ' differ')
            yield lseq, rseq

    return PairedDNAIterator(read_seqs())


@plugin.register_transformer
def _12(data: PairedDNAIterator) -> PairedDNASequencesDirectoryFormat:
    df = PairedDNASequencesDirectoryFormat()
    ff_left = DNAFASTAFormat()
    ff_right = DNAFASTAFormat()

    with ff_left.open() as lfile, ff_right.open() as rfile:
        for lseq, rseq in data:
            if rseq.metadata['id'] != lseq.metadata['id']:
                raise ValueError(lseq.metadata['id'] + ' and ' +
                                 rseq.metadata['id'] + ' differ')
            skbio.io.write(lseq, format='fasta', into=lfile)
            skbio.io.write(rseq, format='fasta', into=rfile)

    df.left_dna_sequences.write_data(ff_left, DNAFASTAFormat)
    df.right_dna_sequences.write_data(ff_right, DNAFASTAFormat)
    return df


@plugin.register_transformer
def _13(ff: AlignedDNAFASTAFormat) -> skbio.TabularMSA:
    return skbio.TabularMSA.read(str(ff), constructor=skbio.DNA,
                                 format='fasta')


@plugin.register_transformer
def _14(data: skbio.TabularMSA) -> AlignedDNAFASTAFormat:
    ff = AlignedDNAFASTAFormat()
    data.write(str(ff), format='fasta')
    return ff


@plugin.register_transformer
def _15(ff: DNAFASTAFormat) -> pd.Series:
    data = {}
    for sequence in _read_dna_fasta(str(ff)):
        data[sequence.metadata['id']] = sequence
    return pd.Series(data)


@plugin.register_transformer
def _16(data: pd.Series) -> DNAFASTAFormat:
    ff = DNAFASTAFormat()
    with ff.open() as f:
        for sequence in data:
            skbio.io.write(sequence, format='fasta', into=f)
    return ff


@plugin.register_transformer
def _18(ff: AlignedDNAFASTAFormat) -> AlignedDNAIterator:
    generator = _read_dna_fasta(str(ff))
    return AlignedDNAIterator(generator)


@plugin.register_transformer
def _19(data: AlignedDNAIterator) -> AlignedDNAFASTAFormat:
    ff = AlignedDNAFASTAFormat()
    skbio.io.write(iter(data), format='fasta', into=str(ff))
    return ff
