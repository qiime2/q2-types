# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json

import biom
import pandas as pd
import qiime

from . import BIOMV1Format, BIOMV210Format
from ..plugin_setup import plugin


def _get_generated_by():
    return 'qiime %s' % qiime.__version__


@plugin.register_transformer
def _1(data: biom.Table) -> BIOMV1Format:
    # TODO: issue a warning about limited support for this format
    ff = BIOMV1Format()
    with ff.open() as fh:
        fh.write(data.to_json(generated_by=_get_generated_by()))
    return ff


def _parse_biom_table_v100(ff):
    with ff.open() as fh:
        return biom.Table.from_json(json.load(fh))


def _parse_biom_table_v210(ff):
    with ff.open() as fh:
        return biom.Table.from_hdf5(fh)


@plugin.register_transformer
def _2(ff: BIOMV1Format) -> biom.Table:
    return _parse_biom_table_v100(ff)


# Note: this is an old TODO and should be revisited with the new view system.
# TODO: this always returns a pd.DataFrame of floats due to how biom loads
# tables, and we don't know what the dtype of the DataFrame should be. It would
# be nice to have support for a semantic-type override that specifies further
# transformations (e.g. converting from floats to ints or bools as
# appropriate).
@plugin.register_transformer
def _3(ff: BIOMV1Format) -> pd.DataFrame:
    table = _parse_biom_table_v100(ff)
    return _table_to_dataframe(table)


def _table_to_dataframe(table: biom.Table) -> pd.DataFrame:
    array = table.matrix_data.toarray().T
    sample_ids = table.ids(axis='sample')
    feature_ids = table.ids(axis='observation')
    return pd.DataFrame(array, index=sample_ids, columns=feature_ids)


@plugin.register_transformer
def _4(ff: BIOMV210Format) -> pd.DataFrame:
    table = _parse_biom_table_v210(ff)
    return _table_to_dataframe(table)


@plugin.register_transformer
def _5(ff: BIOMV210Format) -> biom.Table:
    return _parse_biom_table_v210(ff)


@plugin.register_transformer
def _6(data: biom.Table) -> BIOMV210Format:
    ff = BIOMV210Format()
    with ff.open() as fh:
        data.to_hdf5(fh, generated_by=_get_generated_by())
    return ff
