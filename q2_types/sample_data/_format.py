# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2.plugin.model as model
from qiime2.plugin import ValidationError

from ..plugin_setup import plugin


class AlphaDiversityFormat(model.TextFileFormat):
    def _validate_(self, level):
        with self.open() as fh:
            header = None
            records_seen = 0
            file_ = enumerate(fh) if level == 'min' else zip(range(10), fh)
            for i, line in file_:
                i = i + 1  # For easier reporting
                if line.lstrip(' ') == '\n':
                    continue  # Blank line
                elif line.startswith('#'):
                    continue  # Comment line
                cells = [c.strip() for c in line.rstrip('\n').split('\t')]

                if header is None:
                    if len(cells) < 2:
                        raise ValidationError(
                            'Found header on line %d with the following '
                            'columns: %s (length: %d), expected at least 2 '
                            'columns.' % (i, cells, len(cells)))
                    else:
                        header = cells
                else:
                    if len(cells) != len(header):
                        raise ValidationError(
                            'Line %d has %s cells (%s), expected %s.'
                            % (i, len(cells), cells, len(header)))

                    records_seen += 1

            if header is None:
                raise ValidationError('No header found.')

            if records_seen == 0:
                raise ValidationError('No records found in file, only '
                                      'observed comments, blank lines, and/or '
                                      'a header row.')


AlphaDiversityDirectoryFormat = model.SingleFileDirectoryFormat(
    'AlphaDiversityDirectoryFormat', 'alpha-diversity.tsv',
    AlphaDiversityFormat)


plugin.register_formats(AlphaDiversityFormat, AlphaDiversityDirectoryFormat)
