# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import collections.abc
from itertools import zip_longest

import itertools
from ._util import _read_fastq_seqs
from q2_types.per_sample_sequences import FastqGzFormat
from q2_types.multiplexed_sequences import (EMPMultiplexedDirFmt,
                                            EMPSingleEndDirFmt,
                                            EMPPairedEndDirFmt)

import pandas as pd
import biom
import skbio
import qiime2

from ..plugin_setup import plugin
from ..feature_table import BIOMV210Format
from . import (TaxonomyFormat, HeaderlessTSVTaxonomyFormat, TSVTaxonomyFormat,
               DNAFASTAFormat, PairedDNASequencesDirectoryFormat,
               AlignedDNAFASTAFormat, DifferentialFormat, ProteinFASTAFormat,
               AlignedProteinFASTAFormat, RNAFASTAFormat,
               AlignedRNAFASTAFormat, PairedRNASequencesDirectoryFormat,
               BLAST6Format, MixedCaseDNAFASTAFormat, MixedCaseRNAFASTAFormat,
               MixedCaseAlignedDNAFASTAFormat, MixedCaseAlignedRNAFASTAFormat,
               SequenceCharacteristicsFormat)


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
    df = pd.read_csv(filepath, sep='\t', skip_blank_lines=True,
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
            "are duplicated: %s" %
            ', '.join(df.index[df.index.duplicated()].unique()))

    if df.columns.has_duplicates:
        raise ValueError(
            "Taxonomy format column names must be unique. The following "
            "column names are duplicated: %s" %
            ', '.join(df.columns[df.columns.duplicated()].unique()))

    df['Taxon'] = df['Taxon'].str.strip()
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
            "are duplicated: %s" %
            ', '.join(df.index[df.index.duplicated()].unique()))

    if df.columns.has_duplicates:
        raise ValueError(
            "Taxonomy format column names must be unique. The following "
            "column names are duplicated: %s" %
            ', '.join(df.columns[df.columns.duplicated()].unique()))

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


def _biom_to_fasta_format(table: biom.Table):
    metadata = table.metadata(axis='observation')
    ids = table.ids(axis='observation')
    if metadata is None:
        raise TypeError('Table must have observation metadata.')

    supported_sequence_keys = ('sequence', 'Sequence')

    ff = DNAFASTAFormat()
    with open(str(ff), 'w') as fh:
        for header, md_entry in zip(ids, metadata):
            for key in supported_sequence_keys:
                try:
                    sequence = md_entry[key]
                    if sequence is None:
                        continue
                    break

                except KeyError:
                    pass
            else:
                raise ValueError(
                    f'Observation {header} does not have a sequence key in '
                    f'its metadata. Valid keys are {supported_sequence_keys}.'
                )

            fh.write(f'>{header}\n')
            fh.write(f'{sequence}\n')

    return ff


@plugin.register_transformer
def _4(ff: TaxonomyFormat) -> pd.DataFrame:
    return _taxonomy_formats_to_dataframe(str(ff), has_header=None)


@plugin.register_transformer
def _6(ff: TaxonomyFormat) -> pd.Series:
    df = _taxonomy_formats_to_dataframe(str(ff), has_header=None)
    return df.iloc[:, 0]


@plugin.register_transformer
def _28(ff: TaxonomyFormat) -> qiime2.Metadata:
    df = _taxonomy_formats_to_dataframe(str(ff), has_header=None)
    return qiime2.Metadata(df)


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
def _29(ff: TSVTaxonomyFormat) -> qiime2.Metadata:
    df = _taxonomy_formats_to_dataframe(str(ff), has_header=True)
    return qiime2.Metadata(df)


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
    # not using q2_types.feature_table._transformer._parse_biom_table_v210
    # because it strips out metadata
    with ff.open() as fh:
        table = biom.Table.from_hdf5(fh)
    return _biom_to_tsv_taxonomy_format(table)


@plugin.register_transformer
def _30(ff: BIOMV210Format) -> DNAFASTAFormat:
    with ff.open() as fh:
        table = biom.Table.from_hdf5(fh)
    return _biom_to_fasta_format(table)


# common to all FASTA transformers


def _read_from_fasta(path, constructor=skbio.DNA, lowercase=False):
    return skbio.read(path, format='fasta', constructor=constructor,
                      lowercase=lowercase)


def _fastaformats_to_series(ff, constructor=skbio.DNA, lowercase=False):
    data = {}
    for sequence in _read_from_fasta(str(ff), constructor,
                                     lowercase=lowercase):
        id_ = sequence.metadata['id']
        # this may no longer do anything b/c of format validation, but leaving
        # here as a safeguard & we may want to examine/address later
        if id_ in data:
            raise ValueError("FASTA format sequence IDs must be unique. The "
                             "following ID was found more than once: %s."
                             % id_)
        data[id_] = sequence
    return pd.Series(data)


def _fastaformats_to_metadata(ff, constructor=skbio.DNA, lowercase=False):
    df = _fastaformats_to_series(ff, constructor,
                                 lowercase=lowercase).to_frame()
    df = df.astype(str)
    df.index.name, df.columns = 'Feature ID', ['Sequence']
    return qiime2.Metadata(df)


def _series_to_fasta_format(ff, data, sequence_type="DNA", lowercase=False):
    with ff.open() as f:
        for id_, seq in data.items():
            if sequence_type == "protein":
                sequence = skbio.Protein(seq, metadata={'id': id_},
                                         lowercase=lowercase)
            elif sequence_type == "DNA":
                sequence = skbio.DNA(seq, metadata={'id': id_},
                                     lowercase=lowercase)
            elif sequence_type == "RNA":
                sequence = skbio.RNA(seq, metadata={'id': id_},
                                     lowercase=lowercase)
            else:
                raise NotImplementedError(
                    "pd.Series can only be converted to DNA or "
                    "protein FASTA format.")
            skbio.io.write(sequence, format='fasta', into=f)


class NucleicAcidIterator(collections.abc.Iterable):
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        yield from self.generator


class DNAIterator(NucleicAcidIterator):
    pass


class PairedDNAIterator(NucleicAcidIterator):
    pass


class AlignedDNAIterator(NucleicAcidIterator):
    pass


class RNAIterator(NucleicAcidIterator):
    pass


class PairedRNAIterator(NucleicAcidIterator):
    pass


class AlignedRNAIterator(NucleicAcidIterator):
    pass


# DNA Transformers
@plugin.register_transformer
def _9(ff: DNAFASTAFormat) -> DNAIterator:
    generator = _read_from_fasta(str(ff), skbio.DNA)
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
    return _fastaformats_to_series(ff, skbio.DNA)


@plugin.register_transformer
def _31(ff: DNAFASTAFormat) -> qiime2.Metadata:
    return _fastaformats_to_metadata(ff, skbio.DNA)


@plugin.register_transformer
def _16(data: pd.Series) -> DNAFASTAFormat:
    ff = DNAFASTAFormat()
    _series_to_fasta_format(ff, data)
    return ff


@plugin.register_transformer
def _18(ff: AlignedDNAFASTAFormat) -> AlignedDNAIterator:
    generator = _read_from_fasta(str(ff), skbio.DNA)
    return AlignedDNAIterator(generator)


@plugin.register_transformer
def _19(data: AlignedDNAIterator) -> AlignedDNAFASTAFormat:
    ff = AlignedDNAFASTAFormat()
    skbio.io.write(iter(data), format='fasta', into=str(ff))
    return ff


@plugin.register_transformer
def _33(ff: AlignedDNAFASTAFormat) -> qiime2.Metadata:
    return _fastaformats_to_metadata(ff, skbio.DNA)


@plugin.register_transformer
def _34(ff: AlignedDNAFASTAFormat) -> pd.Series:
    return _fastaformats_to_series(ff, skbio.DNA)


@plugin.register_transformer
def _35(data: pd.Series) -> AlignedDNAFASTAFormat:
    ff = AlignedDNAFASTAFormat()
    _series_to_fasta_format(ff, data)
    return ff


@plugin.register_transformer
def _36(fmt: AlignedDNAFASTAFormat) -> DNAIterator:
    generator = _read_from_fasta(str(fmt), skbio.DNA)
    return DNAIterator(generator)


# Protein FASTA transformers

class ProteinIterator(collections.abc.Iterable):
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        yield from self.generator


class AlignedProteinIterator(ProteinIterator):
    pass


@plugin.register_transformer
def _37(ff: ProteinFASTAFormat) -> ProteinIterator:
    generator = _read_from_fasta(str(ff), skbio.Protein)
    return ProteinIterator(generator)


@plugin.register_transformer
def _38(data: ProteinIterator) -> ProteinFASTAFormat:
    ff = ProteinFASTAFormat()
    skbio.io.write(iter(data), format='fasta', into=str(ff))
    return ff


@plugin.register_transformer
def _39(ff: AlignedProteinFASTAFormat) -> skbio.TabularMSA:
    return skbio.TabularMSA.read(str(ff), constructor=skbio.Protein,
                                 format='fasta')


@plugin.register_transformer
def _40(data: skbio.TabularMSA) -> AlignedProteinFASTAFormat:
    ff = AlignedProteinFASTAFormat()
    data.write(str(ff), format='fasta')
    return ff


@plugin.register_transformer
def _41(ff: ProteinFASTAFormat) -> pd.Series:
    return _fastaformats_to_series(ff, skbio.Protein)


@plugin.register_transformer
def _42(ff: ProteinFASTAFormat) -> qiime2.Metadata:
    return _fastaformats_to_metadata(ff, skbio.Protein)


@plugin.register_transformer
def _43(data: pd.Series) -> ProteinFASTAFormat:
    ff = ProteinFASTAFormat()
    _series_to_fasta_format(ff, data, "protein")
    return ff


@plugin.register_transformer
def _44(ff: AlignedProteinFASTAFormat) -> AlignedProteinIterator:
    generator = _read_from_fasta(str(ff), skbio.Protein)
    return AlignedProteinIterator(generator)


@plugin.register_transformer
def _45(data: AlignedProteinIterator) -> AlignedProteinFASTAFormat:
    ff = AlignedProteinFASTAFormat()
    skbio.io.write(iter(data), format='fasta', into=str(ff))
    return ff


@plugin.register_transformer
def _46(ff: AlignedProteinFASTAFormat) -> qiime2.Metadata:
    return _fastaformats_to_metadata(ff, skbio.Protein)


@plugin.register_transformer
def _47(ff: AlignedProteinFASTAFormat) -> pd.Series:
    return _fastaformats_to_series(ff, skbio.Protein)


@plugin.register_transformer
def _48(data: pd.Series) -> AlignedProteinFASTAFormat:
    ff = AlignedProteinFASTAFormat()
    _series_to_fasta_format(ff, data, "protein")
    return ff


@plugin.register_transformer
def _49(fmt: AlignedProteinFASTAFormat) -> ProteinIterator:
    generator = _read_from_fasta(str(fmt), skbio.Protein)
    return ProteinIterator(generator)


# RNA Transformers
@plugin.register_transformer
def _50(ff: RNAFASTAFormat) -> RNAIterator:
    generator = _read_from_fasta(str(ff), constructor=skbio.RNA)
    return RNAIterator(generator)


@plugin.register_transformer
def _51(data: RNAIterator) -> RNAFASTAFormat:
    ff = RNAFASTAFormat()
    skbio.io.write(iter(data), format='fasta', into=str(ff))
    return ff


@plugin.register_transformer
def _52(ff: AlignedRNAFASTAFormat) -> skbio.TabularMSA:
    return skbio.TabularMSA.read(str(ff), constructor=skbio.RNA,
                                 format='fasta')


@plugin.register_transformer
def _53(data: skbio.TabularMSA) -> AlignedRNAFASTAFormat:
    ff = AlignedRNAFASTAFormat()
    data.write(str(ff), format='fasta')
    return ff


@plugin.register_transformer
def _54(ff: RNAFASTAFormat) -> pd.Series:
    return _fastaformats_to_series(ff, constructor=skbio.RNA)


@plugin.register_transformer
def _55(ff: RNAFASTAFormat) -> qiime2.Metadata:
    return _fastaformats_to_metadata(ff, constructor=skbio.RNA)


@plugin.register_transformer
def _56(data: pd.Series) -> RNAFASTAFormat:
    ff = RNAFASTAFormat()
    _series_to_fasta_format(ff, data, sequence_type="RNA")
    return ff


@plugin.register_transformer
def _57(ff: AlignedRNAFASTAFormat) -> AlignedRNAIterator:
    generator = _read_from_fasta(str(ff), constructor=skbio.RNA)
    return AlignedRNAIterator(generator)


@plugin.register_transformer
def _58(data: AlignedRNAIterator) -> AlignedRNAFASTAFormat:
    ff = AlignedRNAFASTAFormat()
    skbio.io.write(iter(data), format='fasta', into=str(ff))
    return ff


@plugin.register_transformer
def _59(ff: AlignedRNAFASTAFormat) -> qiime2.Metadata:
    return _fastaformats_to_metadata(ff, constructor=skbio.RNA)


@plugin.register_transformer
def _60(ff: AlignedRNAFASTAFormat) -> pd.Series:
    return _fastaformats_to_series(ff, constructor=skbio.RNA)


@plugin.register_transformer
def _61(data: pd.Series) -> AlignedRNAFASTAFormat:
    ff = AlignedRNAFASTAFormat()
    _series_to_fasta_format(ff, data, sequence_type="RNA")
    return ff


@plugin.register_transformer
def _62(fmt: AlignedRNAFASTAFormat) -> RNAIterator:
    generator = _read_from_fasta(str(fmt), constructor=skbio.RNA)
    return RNAIterator(generator)


@plugin.register_transformer
def _63(df: PairedRNASequencesDirectoryFormat) -> PairedRNAIterator:
    left = df.left_rna_sequences.view(RNAIterator)
    right = df.right_rna_sequences.view(RNAIterator)

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

    return PairedRNAIterator(read_seqs())


@plugin.register_transformer
def _64(data: PairedRNAIterator) -> PairedRNASequencesDirectoryFormat:
    df = PairedRNASequencesDirectoryFormat()
    ff_left = RNAFASTAFormat()
    ff_right = RNAFASTAFormat()

    with ff_left.open() as lfile, ff_right.open() as rfile:
        for lseq, rseq in data:
            if rseq.metadata['id'] != lseq.metadata['id']:
                raise ValueError(lseq.metadata['id'] + ' and ' +
                                 rseq.metadata['id'] + ' differ')
            skbio.io.write(lseq, format='fasta', into=lfile)
            skbio.io.write(rseq, format='fasta', into=rfile)

    df.left_rna_sequences.write_data(ff_left, RNAFASTAFormat)
    df.right_rna_sequences.write_data(ff_right, RNAFASTAFormat)
    return df


# Barcode Sequence Fastq Iterators

FastqHeader = collections.namedtuple('FastqHeader', ['id', 'description'])


def _trim_id(id):
    return id.rsplit('/', 1)[0]


def _trim_description(desc):
    # The first number of ':' seperated description is the read number
    if ':' in desc:
        desc = desc.split(':', 1)[1]
    return desc.rsplit('/', 1)[0]


def _record_to_fastq_header(record):
    tokens = record[0][1:].split(' ', maxsplit=1)
    if len(tokens) == 1:
        id, = tokens
        description = None
    else:
        id, description = tokens

    return FastqHeader(id=id, description=description)


class BarcodeSequenceFastqIterator(collections.abc.Iterable):
    def __init__(self, barcode_generator, sequence_generator,
                 ignore_description_mismatch=False):
        self.barcode_generator = barcode_generator
        self.sequence_generator = sequence_generator
        self.ignore_description_mismatch = ignore_description_mismatch

    def __iter__(self):
        # Adapted from q2-types
        for barcode_record, sequence_record in itertools.zip_longest(
                self.barcode_generator, self.sequence_generator):
            if barcode_record is None:
                raise ValueError('More sequences were provided than barcodes.')
            if sequence_record is None:
                raise ValueError('More barcodes were provided than sequences.')
            # The id or description fields may end with "/read-number", which
            # will differ between the sequence and barcode reads. Confirm that
            # they are identical up until the last /
            barcode_header = _record_to_fastq_header(barcode_record)
            sequence_header = _record_to_fastq_header(sequence_record)

            # confirm that the id fields are equal
            if _trim_id(barcode_header.id) != \
               _trim_id(sequence_header.id):
                raise ValueError(
                    'Mismatched sequence ids: %s and %s' %
                    (_trim_id(barcode_header.id),
                     _trim_id(sequence_header.id)))

            if not self.ignore_description_mismatch:
                # if a description field is present, confirm that they're equal
                if barcode_header.description is None and \
                   sequence_header.description is None:
                    pass
                elif barcode_header.description is None:
                    raise ValueError(
                        'Barcode header lines do not contain description '
                        'fields but sequence header lines do.')
                elif sequence_header.description is None:
                    raise ValueError(
                        'Sequence header lines do not contain description '
                        'fields but barcode header lines do.')
                elif _trim_description(barcode_header.description) != \
                        _trim_description(sequence_header.description):
                    raise ValueError(
                        'Mismatched sequence descriptions: %s and %s' %
                        (_trim_description(barcode_header.description),
                         _trim_description(sequence_header.description)))

            yield barcode_record, sequence_record
# Barcode Sequence Fastq Transformers


@plugin.register_transformer
def _65(dirfmt: EMPSingleEndDirFmt) -> BarcodeSequenceFastqIterator:
    barcode_generator = _read_fastq_seqs(
        str(dirfmt.barcodes.view(FastqGzFormat)))
    sequence_generator = _read_fastq_seqs(
        str(dirfmt.sequences.view(FastqGzFormat)))
    result = BarcodeSequenceFastqIterator(barcode_generator,
                                          sequence_generator)
    # ensure that dirfmt stays in scope as long as result does so these
    # generators will work.
    result.__dirfmt = dirfmt
    return result


# TODO: remove this when names are aliased
@plugin.register_transformer
def _65_legacy(dirfmt: EMPMultiplexedDirFmt) -> BarcodeSequenceFastqIterator:
    return _65(dirfmt)


@plugin.register_transformer
def _67(dirfmt: EMPPairedEndDirFmt) -> BarcodeSequenceFastqIterator:
    barcode_generator = _read_fastq_seqs(
        str(dirfmt.barcodes.view(FastqGzFormat)))
    sequence_generator = _read_fastq_seqs(
        str(dirfmt.forward.view(FastqGzFormat)))
    result = BarcodeSequenceFastqIterator(barcode_generator,
                                          sequence_generator)
    # ensure that dirfmt stays in scope as long as result does so these
    # generators will work.
    result.__dirfmt = dirfmt
    return result


class BarcodePairedSequenceFastqIterator(collections.abc.Iterable):
    def __init__(self, barcode_generator, forward_generator,
                 reverse_generator, ignore_description_mismatch=False):
        self.barcode_generator = barcode_generator
        self.forward_generator = forward_generator
        self.reverse_generator = reverse_generator
        self.ignore_description_mismatch = ignore_description_mismatch

    def __iter__(self):
        # Adapted from q2-types
        for barcode_record, forward_record, reverse_record \
                in itertools.zip_longest(self.barcode_generator,
                                         self.forward_generator,
                                         self.reverse_generator):
            if barcode_record is None:
                raise ValueError('More sequences were provided than barcodes.')
            if forward_record is None:
                raise ValueError('More barcodes were provided than '
                                 'forward-sequences.')
            elif reverse_record is None:
                raise ValueError('More barcodes were provided than '
                                 'reverse-sequences.')
            # The id or description fields may end with "/read-number", which
            # will differ between the sequence and barcode reads. Confirm that
            # they are identical up until the last /
            barcode_header = _record_to_fastq_header(barcode_record)
            forward_header = _record_to_fastq_header(forward_record)
            reverse_header = _record_to_fastq_header(reverse_record)

            # confirm that the id fields are equal
            if not (_trim_id(barcode_header.id) ==
                    _trim_id(forward_header.id) ==
                    _trim_id(reverse_header.id)):
                raise ValueError(
                    'Mismatched sequence ids: %s, %s, and %s' %
                    (_trim_id(barcode_header.id),
                     _trim_id(forward_header.id),
                     _trim_id(reverse_header.id)))

            if not self.ignore_description_mismatch:
                # if a description field is present, confirm that they're equal
                if barcode_header.description is None and \
                   forward_header.description is None and \
                   reverse_header.description is None:
                    pass
                elif barcode_header.description is None:
                    raise ValueError(
                        'Barcode header lines do not contain description '
                        'fields but sequence header lines do.')
                elif forward_header.description is None:
                    raise ValueError(
                        'Forward-read header lines do not contain description '
                        'fields but barcode header lines do.')
                elif reverse_header.description is None:
                    raise ValueError(
                        'Reverse-read header lines do not contain description '
                        'fields but barcode header lines do.')
                elif not (_trim_description(barcode_header.description) ==
                          _trim_description(forward_header.description) ==
                          _trim_description(reverse_header.description)):
                    raise ValueError(
                        'Mismatched sequence descriptions: %s, %s, and %s' %
                        (_trim_description(barcode_header.description),
                         _trim_description(forward_header.description),
                         _trim_description(reverse_header.description)))

            yield barcode_record, forward_record, reverse_record


@plugin.register_transformer
def _68(dirfmt: EMPPairedEndDirFmt) -> BarcodePairedSequenceFastqIterator:
    barcode_generator = _read_fastq_seqs(
        str(dirfmt.barcodes.view(FastqGzFormat)))
    forward_generator = _read_fastq_seqs(
        str(dirfmt.forward.view(FastqGzFormat)))
    reverse_generator = _read_fastq_seqs(
        str(dirfmt.reverse.view(FastqGzFormat)))
    result = BarcodePairedSequenceFastqIterator(barcode_generator,
                                                forward_generator,
                                                reverse_generator)
    # ensure that dirfmt stays in scope as long as result does so these
    # generators will work.
    result.__dirfmt = dirfmt
    return result


# Mixed Case Transformers
# NOTE:
# These are mainly for reading in mixed case data and converting to another
# format (i.e. `MixedCaseDNAFASTAFormat` to `DNAIterator` or `DNAFASTAFormat`).
# We'd have to make a new `skbio.sequence.GrammaredSequence` class to enable
# proper iterator, reader, writer functionality for mixed case types. That is
# skbio.DNA|RNA|Protein enforce IUPAC characters (i.e. capital letters).

@plugin.register_transformer
def _69(fmt: MixedCaseDNAFASTAFormat) -> DNAIterator:
    generator = _read_from_fasta(str(fmt), constructor=skbio.DNA,
                                 lowercase=True)
    return DNAIterator(generator)


@plugin.register_transformer
def _70(ff: MixedCaseDNAFASTAFormat) -> pd.Series:
    return _fastaformats_to_series(ff, constructor=skbio.DNA,
                                   lowercase=True)


@plugin.register_transformer
def _71(ff: MixedCaseDNAFASTAFormat) -> qiime2.Metadata:
    return _fastaformats_to_metadata(ff, constructor=skbio.DNA,
                                     lowercase=True)


@plugin.register_transformer
def _72(ff: MixedCaseDNAFASTAFormat) -> DNAFASTAFormat:
    generator = _read_from_fasta(str(ff), constructor=skbio.DNA,
                                 lowercase=True)
    data = DNAIterator(generator)
    dff = DNAFASTAFormat()
    skbio.io.write(iter(data), format='fasta', into=str(dff))
    return dff


@plugin.register_transformer
def _73(fmt: MixedCaseRNAFASTAFormat) -> RNAIterator:
    generator = _read_from_fasta(str(fmt), constructor=skbio.RNA,
                                 lowercase=True)
    return RNAIterator(generator)


@plugin.register_transformer
def _74(ff: MixedCaseRNAFASTAFormat) -> pd.Series:
    return _fastaformats_to_series(ff, constructor=skbio.RNA,
                                   lowercase=True)


@plugin.register_transformer
def _75(ff: MixedCaseRNAFASTAFormat) -> qiime2.Metadata:
    return _fastaformats_to_metadata(ff, constructor=skbio.RNA,
                                     lowercase=True)


@plugin.register_transformer
def _76(ff: MixedCaseRNAFASTAFormat) -> RNAFASTAFormat:
    generator = _read_from_fasta(str(ff), constructor=skbio.RNA,
                                 lowercase=True)
    data = RNAIterator(generator)
    dff = RNAFASTAFormat()
    skbio.io.write(iter(data), format='fasta', into=str(dff))
    return dff


@plugin.register_transformer
def _77(fmt: MixedCaseAlignedDNAFASTAFormat) -> AlignedDNAIterator:
    generator = _read_from_fasta(str(fmt), constructor=skbio.DNA,
                                 lowercase=True)
    return AlignedDNAIterator(generator)


@plugin.register_transformer
def _78(ff: MixedCaseAlignedDNAFASTAFormat) -> pd.Series:
    return _fastaformats_to_series(ff, constructor=skbio.DNA,
                                   lowercase=True)


@plugin.register_transformer
def _79(ff: MixedCaseAlignedDNAFASTAFormat) -> qiime2.Metadata:
    return _fastaformats_to_metadata(ff, constructor=skbio.DNA,
                                     lowercase=True)


@plugin.register_transformer
def _80(ff: MixedCaseAlignedDNAFASTAFormat) -> AlignedDNAFASTAFormat:
    generator = _read_from_fasta(str(ff), constructor=skbio.DNA,
                                 lowercase=True)
    data = AlignedDNAIterator(generator)
    dff = AlignedDNAFASTAFormat()
    skbio.io.write(iter(data), format='fasta', into=str(dff))
    return dff


@plugin.register_transformer
def _81(fmt: MixedCaseAlignedRNAFASTAFormat) -> AlignedRNAIterator:
    generator = _read_from_fasta(str(fmt), constructor=skbio.RNA,
                                 lowercase=True)
    return AlignedRNAIterator(generator)


@plugin.register_transformer
def _82(ff: MixedCaseAlignedRNAFASTAFormat) -> pd.Series:
    return _fastaformats_to_series(ff, constructor=skbio.RNA,
                                   lowercase=True)


@plugin.register_transformer
def _83(ff: MixedCaseAlignedRNAFASTAFormat) -> qiime2.Metadata:
    return _fastaformats_to_metadata(ff, constructor=skbio.RNA,
                                     lowercase=True)


@plugin.register_transformer
def _84(ff: MixedCaseAlignedRNAFASTAFormat) -> AlignedRNAFASTAFormat:
    generator = _read_from_fasta(str(ff), constructor=skbio.RNA,
                                 lowercase=True)
    data = AlignedRNAIterator(generator)
    dff = AlignedRNAFASTAFormat()
    skbio.io.write(iter(data), format='fasta', into=str(dff))
    return dff


# differential types
@plugin.register_transformer
def _85(ff: DifferentialFormat) -> pd.DataFrame:
    return qiime2.Metadata.load(str(ff)).to_dataframe()


@plugin.register_transformer
def _86(ff: DifferentialFormat) -> qiime2.Metadata:
    return qiime2.Metadata.load(str(ff))


@plugin.register_transformer
def _87(data: pd.DataFrame) -> DifferentialFormat:
    ff = DifferentialFormat()
    qiime2.Metadata(data).save(str(ff))
    return ff


# blast types
@plugin.register_transformer
def _88(ff: BLAST6Format) -> pd.DataFrame:
    return skbio.read(str(ff), format='blast+6', into=pd.DataFrame,
                      default_columns=True)


@plugin.register_transformer
def _89(data: pd.DataFrame) -> BLAST6Format:
    ff = BLAST6Format()
    data.to_csv(str(ff), sep='\t', header=False, index=False)
    return ff


@plugin.register_transformer
def _90(ff: BLAST6Format) -> qiime2.Metadata:
    data = skbio.read(
        str(ff), format='blast+6', into=pd.DataFrame, default_columns=True)
    # Metadata cannot have repeat index names, nor a multiindex, so we use the
    # default int index but cast to a str and give it a name.
    data.index = pd.Index(data.index.astype(str), name='id')
    return qiime2.Metadata(data)


@plugin.register_transformer
def _228(ff: SequenceCharacteristicsFormat) -> pd.DataFrame:
    return pd.read_csv(str(ff), sep='\t', index_col=0)


@plugin.register_transformer
def _229(data: pd.DataFrame) -> SequenceCharacteristicsFormat:
    ff = SequenceCharacteristicsFormat()
    data.to_csv(str(ff), sep='\t')
    return ff


@plugin.register_transformer
def _230(ff: SequenceCharacteristicsFormat) -> qiime2.Metadata:
    df = pd.read_csv(str(ff), sep='\t', index_col=0)
    df.index = pd.Index(df.index.astype(str), name='id')
    return qiime2.Metadata(df)
