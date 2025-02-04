# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json

import biom
import pandas as pd
import qiime2

from .. import BIOMV100Format, BIOMV210Format
from ...plugin_setup import plugin

# NOTE: In the readers and writers for BIOM v1 and v2 below, metadata must be
# ignored on both axes because BIOM v1 and v2 are incompatible with certain
# types of metadata. We need to support both versions of the format and
# converting between them (e.g. to support existing QIIME 1 data). We can
# ignore metadata because it is represented as different types in QIIME 2, and
# thus is stored in separate artifacts. `biom.Table` does not have an API to
# delete/unset metadata on its axes, so we construct a new `biom.Table` object
# from the existing table's matrix data and axis IDs (see `_drop_axis_metadata`
# below). This workaround should be fairly efficient because the matrix data
# and axis IDs aren't copied; only a new `biom.Table` reference is created and
# some ID indexing operations are performed.
#
# TODO: Revisit this workaround when `biom.Table` supports deletion of
# metadata: https://github.com/biocore/biom-format/issues/708


def _drop_axis_metadata(table):
    return biom.Table(table.matrix_data,
                      observation_ids=table.ids(axis='observation'),
                      sample_ids=table.ids(axis='sample'))


def _get_generated_by():
    return 'qiime2 %s' % qiime2.__version__


def _parse_biom_table_v100(ff):
    with ff.open() as fh:
        table = biom.Table.from_json(json.load(fh))
        return _drop_axis_metadata(table)


def _parse_biom_table_v210(ff):
    with ff.open() as fh:
        table = biom.Table.from_hdf5(fh)
        return _drop_axis_metadata(table)


def _table_to_dataframe(table: biom.Table) -> pd.DataFrame:
    array = table.matrix_data.toarray().T
    sample_ids = table.ids(axis='sample')
    feature_ids = table.ids(axis='observation')
    return pd.DataFrame(array, index=sample_ids, columns=feature_ids)


def _table_to_metadata(table: biom.Table) -> qiime2.Metadata:
    table = _table_to_dataframe(table)
    table.index.name = 'id'
    return qiime2.Metadata(table)


def _table_to_v210(data):
    ff = BIOMV210Format()
    with ff.open() as fh:
        data.to_hdf5(fh, generated_by=_get_generated_by())
    return ff


def _dataframe_to_table(df):
    if df.index.inferred_type != 'string':
        raise TypeError("Please provide a DataFrame with a string-based Index")
    return biom.Table(df.T.values, observation_ids=df.columns,
                      sample_ids=df.index)


@plugin.register_transformer
def _2(ff: BIOMV100Format) -> biom.Table:
    return _parse_biom_table_v100(ff)


# Note: this is an old TODO and should be revisited with the new view system.
# TODO: this always returns a pd.DataFrame of floats due to how biom loads
# tables, and we don't know what the dtype of the DataFrame should be. It would
# be nice to have support for a semantic-type override that specifies further
# transformations (e.g. converting from floats to ints or bools as
# appropriate).
@plugin.register_transformer
def _3(ff: BIOMV100Format) -> pd.DataFrame:
    table = _parse_biom_table_v100(ff)
    return _table_to_dataframe(table)


@plugin.register_transformer
def _4(ff: BIOMV210Format) -> pd.DataFrame:
    table = _parse_biom_table_v210(ff)
    return _table_to_dataframe(table)


@plugin.register_transformer
def _5(ff: BIOMV210Format) -> biom.Table:
    return _parse_biom_table_v210(ff)


@plugin.register_transformer
def _6(data: biom.Table) -> BIOMV210Format:
    data = _drop_axis_metadata(data)
    return _table_to_v210(data)


@plugin.register_transformer
def _7(data: biom.Table) -> pd.DataFrame:
    return _table_to_dataframe(data)


@plugin.register_transformer
def _8(ff: BIOMV100Format) -> BIOMV210Format:
    data = _parse_biom_table_v100(ff)
    return _table_to_v210(data)


@plugin.register_transformer
def _9(df: pd.DataFrame) -> biom.Table:
    return _dataframe_to_table(df)


@plugin.register_transformer
def _10(df: pd.DataFrame) -> BIOMV210Format:
    return _table_to_v210(_dataframe_to_table(df))


@plugin.register_transformer
def _12(data: biom.Table) -> qiime2.Metadata:
    return _table_to_metadata(data)


@plugin.register_transformer
def _13(ff: BIOMV100Format) -> qiime2.Metadata:
    table = _parse_biom_table_v100(ff)
    return _table_to_metadata(table)


@plugin.register_transformer
def _14(ff: BIOMV210Format) -> qiime2.Metadata:
    table = _parse_biom_table_v210(ff)
    return _table_to_metadata(table)
