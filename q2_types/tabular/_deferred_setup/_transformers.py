# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd
import frictionless as fls
import json

import qiime2.metadata

from ..formats import TableJSONLFileFormat

from .. import (NDJSONFileFormat,
                DataResourceSchemaFileFormat,
                TabularDataResourceDirFmt)

from ...plugin_setup import plugin


def table_jsonl_header(df: pd.DataFrame) -> str:
    header = {}
    header['doctype'] = dict(
        name='table.jsonl', format='application/x-json-lines', version='1.0')
    header['direction'] = 'row'
    header['style'] = 'key:value'

    fields = []
    for name in df.columns:
        attrs = df[name].attrs.copy()
        title = attrs.pop('title', '')
        description = attrs.pop('description', '')
        type = attrs.pop('type', None)
        missing = attrs.pop('missing', False)
        extra = attrs.pop('extra', None)
        if extra is None:
            extra = attrs
        fields.append(dict(
            name=name, type=type, missing=missing, title=title,
            description=description, extra=extra))

    header['fields'] = fields
    header['index'] = []
    header['title'] = df.attrs.get('title', '')
    header['description'] = df.attrs.get('description', '')
    header['extra'] = df.attrs.get('extra', {})

    # prevent whitespace after comma and colon
    return json.dumps(header, separators=(',', ':'))


@plugin.register_transformer
def table_jsonl_to_df(ff: TableJSONLFileFormat) -> pd.DataFrame:
    with ff.open() as fh:
        header = json.loads(next(fh))
        df = pd.read_json(fh, lines=True, orient='records')
        if df.empty:
            df = pd.DataFrame(columns=[
                spec['name'] for spec in header['fields']])

    # The order of these steps matters.

    # 1. set order of columns
    df = df[[spec['name'] for spec in header['fields']]]

    # 2. update types
    for spec in header['fields']:
        col = spec['name']
        if spec['type'] == 'integer':
            df[col] = df[col].astype('int64')
        elif spec['type'] == 'number':
            df[col] = df[col].astype('float64')
        elif spec['type'] == 'datetime':
            df[col] = pd.to_datetime(df[col], format='iso8601')
        elif spec['type'] == 'date':
            df[col] = pd.to_datetime(df[col], format='iso8601')
        elif spec['type'] == 'time':
            df[col] = pd.to_datetime(df[col], format='mixed').dt.time
        elif spec['type'] == 'duration':
            df[col] = pd.to_timedelta(df[col])

    # 3. set index
    if len(header['index']) > 0:
        df = df.set_index(header['index'], drop=False)

    # 4. add metadata to columns
    for spec in header['fields']:
        df[spec['name']].attrs.update(spec)

    # 5. add metadata to table
    attrs = dict(title=header['title'], description=header['description'])
    df.attrs.update(attrs)

    return df


@plugin.register_transformer
def df_to_table_jsonl(obj: pd.DataFrame) -> TableJSONLFileFormat:
    header = table_jsonl_header(obj)

    ff = TableJSONLFileFormat()
    with ff.open() as fh:
        fh.write(header)
        fh.write('\n')
        if not obj.empty:
            obj.to_json(fh, orient='records', lines=True, date_format='iso')

    return ff


@plugin.register_transformer
def _1(obj: pd.DataFrame) -> NDJSONFileFormat:
    ff = NDJSONFileFormat()
    obj.to_json(str(ff), lines=True, orient='records')
    return ff


@plugin.register_transformer
def _2(obj: DataResourceSchemaFileFormat) -> fls.Resource:
    return fls.Resource(str(obj))


@plugin.register_transformer
def _3(df: TabularDataResourceDirFmt) -> pd.DataFrame:
    path = df.data.view(NDJSONFileFormat)
    data = pd.read_json(str(path), lines=True)
    resource = df.metadata.view(fls.Resource)

    if data.empty:
        data = pd.DataFrame(
            columns=[c.name for c in resource.schema.fields])

    for field in resource.schema.fields:
        data[field.name].attrs = field.to_dict()

    return data


@plugin.register_transformer
def _4(obj: pd.DataFrame) -> TabularDataResourceDirFmt:
    metadata_obj = []

    for col in obj.columns:
        series = obj[col]
        dtype = series.convert_dtypes().dtype
        metadata = series.attrs.copy()

        if pd.api.types.is_float_dtype(dtype):
            schema_dtype = 'number'
        elif pd.api.types.is_integer_dtype(dtype):
            schema_dtype = 'integer'
        else:
            schema_dtype = 'string'

        metadata['name'] = col
        metadata['type'] = schema_dtype

        metadata_obj.append(metadata)

    metadata_dict = {'schema': {'fields': metadata_obj}, **obj.attrs}
    metadata_dict['format'] = 'ndjson'
    metadata_dict['path'] = 'data.ndjson'
    metadata_dict['name'] = 'data'

    dir_fmt = TabularDataResourceDirFmt()

    dir_fmt.data.write_data(obj, pd.DataFrame)
    with open(dir_fmt.path / 'dataresource.json', 'w') as fh:
        fh.write(json.dumps(metadata_dict, indent=4))

    return dir_fmt


@plugin.register_transformer
def _5(ff: TableJSONLFileFormat) -> qiime2.Metadata:
    with ff.open() as fh:
        header = json.loads(next(fh))
        df = pd.read_json(fh, lines=True, orient='records')
        if df.empty:
            df = pd.DataFrame(columns=[
                spec['name'] for spec in header['fields']])

    # The order of these steps matters.

    # 1. set order of columns
    df = df[[spec['name'] for spec in header['fields']]]

    # 2. update types
    for spec in header['fields']:
        col = spec['name']
        if spec['type'] == 'integer':
            df[col] = df[col].astype('int64')
        elif spec['type'] == 'number':
            df[col] = df[col].astype('float64')
        elif spec['type'] == 'datetime':
            df[col] = pd.to_datetime(df[col], format='iso8601')
        elif spec['type'] == 'date':
            df[col] = pd.to_datetime(df[col], format='iso8601')
        elif spec['type'] == 'time':
            df[col] = pd.to_datetime(df[col], format='mixed').dt.time
        elif spec['type'] == 'duration':
            df[col] = pd.to_timedelta(df[col])

    # 3. set index
    if len(header['index']) > 0:
        df = df.set_index(header['index'], drop=False)
    else:
        df = df.set_index('id', drop=False)

    # 4. add metadata to columns
    for spec in header['fields']:
        df[spec['name']].attrs.update(spec)

    # 5. add metadata to table
    attrs = dict(title=header['title'], description=header['description'])
    df.attrs.update(attrs)
    if 'id' in df.columns:
        df.drop('id', axis=1, inplace=True)

    return qiime2.Metadata(df)
