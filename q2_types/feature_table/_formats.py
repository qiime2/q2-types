# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import ijson
import h5py

import qiime2.plugin.model as model


class BIOMV100Format(model.TextFileFormat):
    top_level_keys = {
        'id', 'format', 'format_url', 'type', 'generated_by',
        'date', 'rows', 'columns', 'matrix_type', 'matrix_element_type',
        'shape', 'data', 'comment'
    }

    def sniff(self):
        # Can't self.open(mode='rb'), so we defer to the backing pathlib object
        with self.path.open(mode='rb') as fh:
            try:
                parser = ijson.parse(fh)
                for prefix, event, value in parser:
                    if (prefix, event) == ('', 'map_key'):
                        # `format_url` seems pretty unique to BIOM 1.0.
                        if value == 'format_url':
                            return True
                        elif value not in self.top_level_keys:
                            return False
            except (ijson.JSONError, UnicodeDecodeError):
                pass
            return False


class BIOMV210Format(model.BinaryFileFormat):
    # minimum requirements as described by
    # http://biom-format.org/documentation/format_versions/biom-2.1.html
    groups = {'sample',
              'sample/matrix',
              'sample/metadata',
              'sample/group-metadata',
              'observation',
              'observation/matrix',
              'observation/metadata',
              'observation/group-metadata'}
    datasets = {'sample/ids',
                'sample/matrix/data',
                'sample/matrix/indptr',
                'sample/matrix/indices',
                'observation/ids',
                'observation/matrix/data',
                'observation/matrix/indptr',
                'observation/matrix/indices'}
    attrs = {'id',
             'type',
             'format-url',
             'format-version',
             'generated-by',
             'creation-date',
             'shape',
             'nnz'}

    def open(self):
        return h5py.File(str(self), mode=self._mode)

    def sniff(self):
        try:
            # Always sniff in read-only mode. If opened in 'w' mode,
            # h5py will truncate the file, effectively destroying
            # the table's contents
            with h5py.File(str(self), mode='r') as fh:
                for grp in self.groups:
                    if grp not in fh:
                        return False
                for ds in self.datasets:
                    if ds not in fh:
                        return False
                for attr in self.attrs:
                    if attr not in fh.attrs:
                        return False
                return True
        except Exception:
            return False


BIOMV100DirFmt = model.SingleFileDirectoryFormat('BIOMV100DirFmt',
                                                 'feature-table.biom',
                                                 BIOMV100Format)
BIOMV210DirFmt = model.SingleFileDirectoryFormat('BIOMV210DirFmt',
                                                 'feature-table.biom',
                                                 BIOMV210Format)
