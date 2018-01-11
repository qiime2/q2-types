# ----------------------------------------------------------------------------
# Copyright (c) 2016-2018, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2.plugin.model as model

from ..plugin_setup import plugin


class AlphaDiversityFormat(model.TextFileFormat):
    def sniff(self):
        with self.open() as fh:
            for line, _ in zip(fh, range(10)):
                cells = line.split('\t')
                if len(cells) != 2:
                    return False
            return True


AlphaDiversityDirectoryFormat = model.SingleFileDirectoryFormat(
    'AlphaDiversityDirectoryFormat', 'alpha-diversity.tsv',
    AlphaDiversityFormat)


plugin.register_formats(AlphaDiversityFormat, AlphaDiversityDirectoryFormat)
