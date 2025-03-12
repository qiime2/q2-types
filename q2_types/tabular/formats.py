# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import ValidationError, model

from frictionless import validate


class TableJSONLFileFormat(model.TextFileFormat):
    def _validate_(self, level):
        with self.open() as fh:
            assert fh.read(33)[:33] == '{"doctype":{"name":"table.jsonl",'


TableJSONLDirFmt = model.SingleFileDirectoryFormat(
    'TableJSONLDirFmt', 'data.table.jsonl', TableJSONLFileFormat)


class NDJSONFileFormat(model.TextFileFormat):
    """Format for newline-delimited (ND) JSON file."""
    def _validate_(self, level):
        pass


class DataResourceSchemaFileFormat(model.TextFileFormat):
    """
    Format for data resource schema.
    """
    def _validate_(self, level):
        pass


class TabularDataResourceDirFmt(model.DirectoryFormat):
    data = model.File('data.ndjson', format=NDJSONFileFormat)
    metadata = model.File('dataresource.json',
                          format=DataResourceSchemaFileFormat)

    def _validate_(self, level='min'):
        try:
            validate(str(self.path/'dataresource.json'))
        except ValidationError:
            raise model.ValidationError(
                'The dataresource does not completely describe'
                ' the data.ndjson file')
