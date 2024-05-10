# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import collections.abc
import os

import pandas as pd
import skbio
from skbio.io import read

from . import (
    GenesDirectoryFormat, ProteinsDirectoryFormat, GFF3Format, OrthologFileFmt
)
from ..plugin_setup import plugin

CONSTRUCTORS = {
    'DNA': skbio.DNA,
    'RNA': skbio.RNA,
    'protein': skbio.Protein
}


@plugin.register_transformer
def _8(ortholog_file: OrthologFileFmt) -> pd.DataFrame:

    seed_ortholog_column_names = ['qseqid', 'sseqid', 'evalue', 'bitscore',
                                  'qstart', 'qend', 'sstart', 'send', 'pident',
                                  'qcov', 'scov']

    return pd.read_csv(ortholog_file.path, sep="\t",
                       names=seed_ortholog_column_names,
                       header='infer',
                       comment="#"
                       )


def _series_to_fasta(series, ff, seq_type='DNA'):
    fp = os.path.join(ff.path, f'{series.name}.fasta')
    with open(fp, 'w') as fh:
        for id_, seq in series.items():
            if seq:
                sequence = CONSTRUCTORS[seq_type](seq, metadata={'id': id_})
                skbio.io.write(sequence, format='fasta', into=fh)


def _multi_sequences_to_df(seq_iter_view):
    data = {
        os.path.splitext(fp)[0]: pds
        for fp, pds in seq_iter_view
    }
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index.name = 'Genome ID'
    df = df.astype(str).replace({'nan': None})
    return df


@plugin.register_transformer
def _1(dirfmt: GenesDirectoryFormat) -> pd.DataFrame:
    return _multi_sequences_to_df(dirfmt.genes.iter_views(pd.Series))


@plugin.register_transformer
def _2(df: pd.DataFrame) -> GenesDirectoryFormat:
    result = GenesDirectoryFormat()
    df.apply(_series_to_fasta, axis=1, ff=result, seq_type='DNA')
    return result


@plugin.register_transformer
def _3(dirfmt: ProteinsDirectoryFormat) -> pd.DataFrame:
    return _multi_sequences_to_df(dirfmt.proteins.iter_views(pd.Series))


@plugin.register_transformer
def _4(df: pd.DataFrame) -> ProteinsDirectoryFormat:
    result = ProteinsDirectoryFormat()
    df.apply(_series_to_fasta, axis=1, ff=result, seq_type='protein')
    return result


class IntervalMetadataIterator(collections.abc.Iterable):
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        yield from self.generator


@plugin.register_transformer
def _5(fmt: GFF3Format) -> IntervalMetadataIterator:
    generator = read(str(fmt), format='gff3')
    return IntervalMetadataIterator(generator)


@plugin.register_transformer
def _7(data: IntervalMetadataIterator) -> GFF3Format:
    ff = GFF3Format()
    with ff.open() as fh:
        for _id, im in data:
            im.write(fh, format='gff3', seq_id=_id)
    return ff
