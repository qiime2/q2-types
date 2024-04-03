# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from io import StringIO

import uuid

import collections.abc
import glob
import os.path

import qiime2
from itertools import repeat

import pandas as pd
import skbio
from q2_types.feature_data._transformer import _fastaformats_to_series

from . import MAGSequencesDirFmt, OrthologAnnotationDirFmt
from ..plugin_setup import plugin

CONSTRUCTORS = {
    'DNA': skbio.DNA,
    'RNA': skbio.RNA,
    'protein': skbio.Protein
}


def _get_filename(full_path):
    return os.path.splitext(os.path.basename(full_path))[0]


def _series_to_fasta(series, ff, seq_type='DNA'):
    fp = os.path.join(str(ff), f'{series.name}.fasta')
    with open(fp, 'w') as fh:
        for id_, seq in series.iteritems():
            if seq:
                sequence = CONSTRUCTORS[seq_type](seq, metadata={'id': id_})
                skbio.io.write(sequence, format='fasta', into=fh)


def _fastafiles_to_dataframe(ff):
    data = {}
    for fp in sorted(glob.glob(os.path.join(str(ff), '*.fa*'))):
        fname = _get_filename(fp)
        data[fname] = _fastaformats_to_series(fp, constructor=skbio.DNA)
    df = pd.DataFrame.from_dict(data, orient='index')
    df.index.name = 'Feature ID'
    df = df.astype(str).replace({'nan': None})
    return df


@plugin.register_transformer
def _2(ff: MAGSequencesDirFmt) -> pd.DataFrame:
    return _fastafiles_to_dataframe(ff)


@plugin.register_transformer
def _3(df: pd.DataFrame) -> MAGSequencesDirFmt:
    result = MAGSequencesDirFmt()
    df.apply(_series_to_fasta, axis=1, ff=result, seq_type='DNA')
    return result


class MAGIterator(collections.abc.Iterable):
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        yield from self.generator


@plugin.register_transformer
def _4(ff: MAGSequencesDirFmt) -> MAGIterator:
    def _multi_generator(files):
        for fp in files:
            fname = _get_filename(fp)
            fg = skbio.read(fp, format='fasta', constructor=skbio.DNA)
            yield from zip(repeat(fname), fg)

    fps = sorted(glob.glob(os.path.join(str(ff), '*.fa*')))
    return MAGIterator(_multi_generator(fps))


@plugin.register_transformer
def _5(data: MAGIterator) -> MAGSequencesDirFmt:
    result = MAGSequencesDirFmt()
    for fn, seq in data:
        fp = os.path.join(str(result), f'{fn}.fasta')
        with open(fp, 'a') as fin:
            skbio.io.write(seq, format='fasta', into=fin)
    return result


def _is_valid_uuid4(uuid_string: str):
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
def _7(data: OrthologAnnotationDirFmt) -> pd.DataFrame:
    return _annotations_to_dataframe(data)


@plugin.register_transformer
def _7(data: OrthologAnnotationDirFmt) -> qiime2.Metadata:
    annotations = _annotations_to_dataframe(data)
    return qiime2.Metadata(annotations)
