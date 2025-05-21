# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd

from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin.util import transform
import qiime2.metadata

from q2_types.tabular.formats import (
    TabularDataResourceDirFmt, TableJSONLFileFormat,
)


class TestTransformers(TestPluginBase):
    package = 'q2_types.tabular.tests'

    def test_empty_tabular_data_resource_to_dataframe(self):
        _, obs = self.transform_format(TabularDataResourceDirFmt,
                                       pd.DataFrame,
                                       filename='empty_data_dist')

        exp = pd.DataFrame(columns=['id', 'measure', 'group', 'subject'])

        pd.testing.assert_frame_equal(obs, exp, check_dtype=False)

    def test_empty_table_jsonl_to_dataframe(self):
        _, obs = self.transform_format(TableJSONLFileFormat,
                                       pd.DataFrame,
                                       filename='empty_data_dist.table.jsonl')

        exp = pd.DataFrame(columns=['id', 'measure', 'group', 'subject'])

        pd.testing.assert_frame_equal(obs, exp, check_dtype=False)

    def _assert_jsonl_roundtrip(self, path):
        exp, df = self.transform_format(TableJSONLFileFormat,
                                        pd.DataFrame,
                                        filename=path)
        res = transform(df, to_type=TableJSONLFileFormat)

        exp.validate()
        res.validate()

        with exp.open() as fh:
            expected = fh.read()
        with res.open() as fh:
            result = fh.read()

        self.assertEqual(result, expected)

    def test_jsonl_roundtrip_empty(self):
        self._assert_jsonl_roundtrip('empty_data_dist.table.jsonl')

    def test_jsonl_roundtrip_refdist(self):
        self._assert_jsonl_roundtrip('faithpd_refdist.table.jsonl')

    def test_jsonl_roundtrip_timedist(self):
        self._assert_jsonl_roundtrip('faithpd_timedist.table.jsonl')

    def test_jsonl_to_metadata(self):
        _, obs = self.transform_format(TableJSONLFileFormat, qiime2.Metadata,
                                       'faithpd_refdist.table.jsonl')
        _, exp = self.transform_format(TableJSONLFileFormat, pd.DataFrame,
                                       'faithpd_refdist.table.jsonl')
        exp = exp.set_index('id')
        pd.testing.assert_frame_equal(obs.to_dataframe(), exp)
