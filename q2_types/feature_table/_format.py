# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import ijson

import qiime.plugin.model as model


class BIOMV1Format(model.TextFileFormat):
    top_level_keys = {
        'id', 'format', 'format_url', 'type', 'generated_by',
        'date', 'rows', 'columns', 'matrix_type', 'matrix_element_type',
        'shape', 'data', 'comment'
    }

    def sniff(self):
        with self.open() as fh:
            try:
                parser = ijson.parse(fh)
                for prefix, event, value in parser:
                    if (prefix, event) == ('', 'map_key'):
                        # `format_url` seems pretty unique to BIOM 1.0.
                        if value == 'format_url':
                            return True
                        elif value not in self.top_level_keys:
                            return False
            except ijson.JSONError:
                pass
            return False


FeatureTableDirectoryFormat = model.SingleFileDirectoryFormat(
    'FeatureTableDirectoryFormat', 'feature-table.biom', BIOMV1Format)
