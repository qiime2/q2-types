# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import uuid
from io import StringIO

import pandas as pd
import qiime2
import skbio
from skbio.io import read

from .. import (
    GenesDirectoryFormat, ProteinsDirectoryFormat, GFF3Format,
    OrthologFileFmt, OrthologAnnotationDirFmt, IntervalMetadataIterator
)
from ...plugin_setup import plugin

CONSTRUCTORS = {
    'DNA': skbio.DNA,
    'RNA': skbio.RNA,
    'protein': skbio.Protein
}


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


def _is_valid_uuid4(uuid_string: str):
    """
    Check if a given string is a valid UUID version 4.

    This function checks if the provided string is a valid UUID version 4.
    The only purpose of doing that here is to identify whether provided
    string was a MAG ID (UUID4) or a sample ID. For that reason, we don't
    print any statements or raise any exceptions.

    Parameters:
    uuid_string (str): The string to check for UUID version 4 validity.

    Returns:
    bool: True if the string is a valid UUID version 4, False otherwise.
    """
    try:
        uuid_obj = uuid.UUID(uuid_string, version=4)
    except ValueError:
        return False

    return str(uuid_obj) == uuid_string


def _reshuffle_columns(df: pd.DataFrame):
    if 'MAG' in df.columns:
        col = 'MAG'
    elif 'Sample' in df.columns:
        col = 'Sample'
    else:
        return df

    cols = df.columns.tolist()
    cols.remove(col)
    cols.insert(0, col)
    df = df[cols]
    return df


def _annotations_to_dataframe(
        data: OrthologAnnotationDirFmt
) -> pd.DataFrame:
    annotations = data.annotation_dict()
    dfs = []
    for _id, path in annotations.items():
        # we need to ignore the ## comments at
        # the beginning and end of the file
        with open(path, 'r') as f:
            lines = [line for line in f if not line.startswith('##')]

        df = pd.read_csv(StringIO('\n'.join(lines)), sep='\t', index_col=0)
        if _is_valid_uuid4(_id):
            df['MAG'] = _id
        else:
            df['Sample'] = _id

        dfs.append(df)

    df = pd.concat(dfs)

    # to satisfy QIIME2's particular requirements
    df.reset_index(drop=False, inplace=True)
    df.index = df.index.astype(str)
    df.index.rename('id', inplace=True)

    # reshuffle columns for nicer display
    df = _reshuffle_columns(df)

    return df


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


@plugin.register_transformer
def _9(data: OrthologAnnotationDirFmt) -> pd.DataFrame:
    return _annotations_to_dataframe(data)


@plugin.register_transformer
def _10(data: OrthologAnnotationDirFmt) -> qiime2.Metadata:
    annotations = _annotations_to_dataframe(data)
    return qiime2.Metadata(annotations)
