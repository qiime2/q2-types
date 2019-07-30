# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import h5py
import biom

import qiime2.plugin.model as model

from ..plugin_setup import plugin, citations


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
            with self.open() as fh:
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


BIOMV210DirFmt = model.SingleFileDirectoryFormat('BIOMV210DirFmt',
                                                 'feature-table.biom',
                                                 BIOMV210Format)

plugin.register_views(BIOMV210Format, BIOMV210DirFmt, biom.Table,
                      citations=[citations['mcdonald2012biological']])
