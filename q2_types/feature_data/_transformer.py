# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import collections
from itertools import zip_longest

import pandas as pd
import skbio
import qiime

from ..plugin_setup import plugin
from . import (TaxonomyFormat, DNAFASTAFormat,
               PairedDNASequencesDirectoryFormat, AlignedDNAFASTAFormat)


class DNAIterator(collections.Iterator):
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        return self.generator

    def __next__(self):
        return next(self.generator)


class PairedDNAIterator(DNAIterator):
    pass


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
