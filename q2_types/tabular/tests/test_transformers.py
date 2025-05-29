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


class TestDataframeToJsonlTypes(TestPluginBase):
    package = 'q2_types.tabular.tests'

    def setUp(self):
        '''
        Creates a dataframe with a column for each of the recognized dataframe
        types for use in the other tests in this class.
        '''
        super().setUp()

        self.df = pd.DataFrame({
            'integer_column': [1, 2, 3],
            'float_column': [1.0, 2.5, 3.0],
            'string_column': ['i', 'like', 'strings'],
            'datetime_column': pd.to_datetime(
                ['2012-01-01T00:00:00', '17:00:00', '1998-03-14'],
                format='mixed'
            ),
            'timedelta_column': pd.to_timedelta(
                ['P0D5H', 'P420D', 'P7D24H60M60S']
            )
        })

    def test_that_dummy_df_has_intended_types(self):
        '''
        Tests that the columns in the pandas dataframe created in the `setUp`
        have the intended types. (Does not test any plugin behavior.)
        '''
        type_assertion_funcs = {
            'integer': pd.api.types.is_integer_dtype,
            'float': pd.api.types.is_float_dtype,
            'string': pd.api.types.is_string_dtype,
            'datetime': pd.api.types.is_datetime64_dtype,
            'timedelta': pd.api.types.is_timedelta64_dtype,
        }

        for column in self.df.columns:
            column_type = column.removesuffix('_column')

            assert_func = type_assertion_funcs[column_type]
            self.assertTrue(assert_func(self.df[column]))

            for other_column_type in type_assertion_funcs:
                if other_column_type != column_type:
                    assert_not_func = type_assertion_funcs[other_column_type]
                    self.assertFalse(assert_not_func(self.df[column]))

    def test_attrs_written_to_jsonl_header(self):
        '''

        '''
        pass

    def test_missing_attrs_inferred_properly(self):
        '''
        '''
        pass

    def test_type_conversions_from_dataframe_to_jsonl(self):
        pass
