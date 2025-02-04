# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import csv

import qiime2.plugin.model as model
from qiime2.plugin import ValidationError


class AlphaDiversityFormat(model.TextFileFormat):
    def _validate_(self, level):
        with self.open() as fh:
            header, records_seen, is_min = None, 0, level == 'min'
            fh_ = csv.reader(fh, delimiter='\t')
            file_ = enumerate(fh_, 1) if is_min else zip(range(1, 11), fh_)
            for i, cells in file_:
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

            # The first non-comment and non-blank row observed will always be
            # the header row, and since we have no requirement on the field
            # names (because they are dynamically defined), so no need to check
            # for the presence (or validity) of a header row at this point.

            if records_seen == 0:
                raise ValidationError('No records found in file, only '
                                      'observed comments, blank lines, and/or '
                                      'a header row.')


AlphaDiversityDirectoryFormat = model.SingleFileDirectoryFormat(
    'AlphaDiversityDirectoryFormat', 'alpha-diversity.tsv',
    AlphaDiversityFormat)
