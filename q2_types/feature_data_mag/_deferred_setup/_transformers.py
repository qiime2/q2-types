# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import glob
import os.path

from itertools import repeat

import pandas as pd
import skbio
from q2_types._util import fasta_to_series

from .. import MAGSequencesDirFmt, MAGIterator
from ...plugin_setup import plugin

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
        for id_, seq in series.items():
            if seq:
                sequence = CONSTRUCTORS[seq_type](seq, metadata={'id': id_})
                skbio.io.write(sequence, format='fasta', into=fh)


def _fastafiles_to_dataframe(ff):
    data = {}
    for fp in sorted(glob.glob(os.path.join(str(ff), '*.fa*'))):
        fname = _get_filename(fp)
        data[fname] = fasta_to_series(fp, constructor=skbio.DNA)
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
