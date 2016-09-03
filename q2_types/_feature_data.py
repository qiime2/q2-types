# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import collections
from itertools import zip_longest

import skbio
import skbio.io
import pandas as pd

import qiime
from qiime.plugin import SemanticType
import qiime.plugin.model as model

from .plugin_setup import plugin


FeatureData = SemanticType('FeatureData', field_names='type')

Taxonomy = SemanticType('Taxonomy', variant_of=FeatureData.field['type'])

Sequence = SemanticType('Sequence', variant_of=FeatureData.field['type'])

PairedEndSequence = SemanticType('PairedEndSequence',
                                 variant_of=FeatureData.field['type'])

AlignedSequence = SemanticType('AlignedSequence',
                               variant_of=FeatureData.field['type'])


class DNAIterator(collections.Iterator):
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        return self.generator

    def __next__(self):
        return next(self.generator)


class PairedDNAIterator(DNAIterator):
    pass


# Formats
class TaxonomyFormat(model.TextFileFormat):
    def sniff(self):
        with self.open() as fh:
            # validate up to 10 data lines (i.e. non-comment lines)
            # recreate behavior of zip(fh, range(10)) accounting for comments
            count = 0
            while count < 10:
                line = fh.readline()
                if line == '':
                    break
                elif line.startswith('#'):
                    continue
                else:
                    cells = line.split('\t')
                    if len(cells) < 2:
                        return False
                    count += 1
            return False if count == 0 else True


class DNAFASTAFormat(model.TextFileFormat):
    def sniff(self):
        filepath = str(self)
        sniffer = skbio.io.io_registry.get_sniffer('fasta')
        if sniffer(filepath)[0]:
            generator = skbio.io.read(filepath, constructor=skbio.DNA,
                                      format='fasta')
            try:
                for seq, _ in zip(generator, range(5)):
                    pass
                return True
            # ValueError raised by skbio if there are invalid DNA chars.
            except ValueError:
                pass
        return False


class AlignedDNAFASTAFormat(model.TextFileFormat):
    def sniff(self):
        filepath = str(self)
        sniffer = skbio.io.io_registry.get_sniffer('fasta')
        if sniffer(filepath)[0]:
            generator = skbio.io.read(filepath, constructor=skbio.DNA,
                                      format='fasta')
            try:
                initial_length = len(next(generator))
                for seq, _ in zip(generator, range(4)):
                    if len(seq) != initial_length:
                        return False
                return True
            # ValueError raised by skbio if there are invalid DNA chars.
            except (StopIteration, ValueError):
                pass
        return False


TaxonomyDirectoryFormat = model.SingleFileDirectoryFormat(
    'TaxonomyDirectoryFormat', 'taxonomy.tsv', TaxonomyFormat)


DNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'DNASequencesDirectoryFormat', 'dna-sequences.fasta', DNAFASTAFormat)


class PairedDNASequencesDirectoryFormat(model.DirectoryFormat):
    left_dna_sequences = model.File('left-dna-sequences.fasta',
                                    format=DNAFASTAFormat)
    right_dna_sequences = model.File('right-dna-sequences.fasta',
                                     format=DNAFASTAFormat)


AlignedDNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'AlignedDNASequencesDirectoryFormat', 'aligned-dna-sequences.fasta',
    AlignedDNAFASTAFormat)


# Transformers
@plugin.register_transformer
def _2(data: pd.DataFrame) -> TaxonomyFormat:
    ff = TaxonomyFormat()
    data.to_csv(str(ff), sep='\t', header=True, index=True)
    return ff


def _read_taxonomy(fp):
    # Using read_csv for access to comment parameter, and set index_col,
    # header, and parse_dates to Series.from_csv default settings for
    # better handling of round-trips.
    #
    # Using `dtype=object` and `set_index` to avoid type casting/inference of
    # any columns or the index.
    df = pd.read_csv(fp, sep='\t', comment='#', header=0,
                     parse_dates=True, skip_blank_lines=True, dtype=object)
    df.set_index(df.columns[0], drop=True, append=False, inplace=True)
    return df


@plugin.register_transformer
def _4(ff: TaxonomyFormat) -> pd.DataFrame:
    return _read_taxonomy(str(ff))


@plugin.register_transformer
def _6(ff: TaxonomyFormat) -> pd.Series:
    data = _read_taxonomy(str(ff))
    return data.iloc[:, 0]


@plugin.register_transformer
def _8(ff: TaxonomyFormat) -> qiime.Metadata:
    data = _read_taxonomy(str(ff))
    return qiime.Metadata(data)


# TODO can this be generalized to any iterable type? See:
#     https://github.com/biocore/scikit-bio/issues/1031#issuecomment-225252290
@plugin.register_transformer
def _9(ff: DNAFASTAFormat) -> DNAIterator:
    generator = skbio.read(str(ff), format='fasta', constructor=skbio.DNA)
    return DNAIterator(generator)


@plugin.register_transformer
def _10(data: DNAIterator) -> DNAFASTAFormat:
    ff = DNAFASTAFormat()
    skbio.io.write(data, format='fasta', into=str(ff))
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

    df.left_dna_sequences.write(ff_left, DNAFASTAFormat)
    df.right_dna_sequences.write(ff_right, DNAFASTAFormat)
    return df


@plugin.register_transformer
def _13(ff: AlignedDNAFASTAFormat) -> skbio.TabularMSA:
    return skbio.TabularMSA.read(str(ff), constructor=skbio.DNA,
                                 format='fasta')


@plugin.register_transformer
def _14(data: skbio.TabularMSA) -> AlignedDNAFASTAFormat:
    ff = AlignedDNAFASTAFormat()
    return data.write(str(ff), format='fasta')


# Registrations
plugin.register_semantic_type(FeatureData)
plugin.register_semantic_type(Taxonomy)
plugin.register_semantic_type(Sequence)
plugin.register_semantic_type(PairedEndSequence)
plugin.register_semantic_type(AlignedSequence)

plugin.register_semantic_type_to_format(
    FeatureData[Taxonomy],
    artifact_format=TaxonomyDirectoryFormat)
plugin.register_semantic_type_to_format(
    FeatureData[Sequence],
    artifact_format=DNASequencesDirectoryFormat)
plugin.register_semantic_type_to_format(
    FeatureData[PairedEndSequence],
    artifact_format=PairedDNASequencesDirectoryFormat)
plugin.register_semantic_type_to_format(
    FeatureData[AlignedSequence],
    artifact_format=AlignedDNASequencesDirectoryFormat)
