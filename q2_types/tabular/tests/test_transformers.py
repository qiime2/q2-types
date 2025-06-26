# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import json

import pandas as pd
from pandas.testing import assert_series_equal, assert_frame_equal

from qiime2.plugin.testing import TestPluginBase
from qiime2.plugin.util import transform
import qiime2.metadata

from q2_types.tabular.formats import (
    TabularDataResourceDirFmt, TableJSONLFileFormat,
)
from q2_types.tabular._deferred_setup._transformers import (
    _copy_dataframe_with_attrs
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

        obs = obs.to_dataframe()
        obs.index = obs.index.astype('string')
        obs['group'] = obs['group'].astype('string')

        pd.testing.assert_frame_equal(obs, exp)


class TestDataframeToJsonlTypeHandling(TestPluginBase):
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

    def get_header_field(self, header: dict, name: str) -> dict:
        for field in header['fields']:
            if field['name'] == name:
                return field

        raise ValueError(f'The {name} field was not found in the header.')

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
        Tests that dataframe column attrs are written to the jsonl header
        properly.
        '''
        self.df['integer_column'].attrs['type'] = 'integer'
        self.df['float_column'].attrs['type'] = 'number'
        self.df['string_column'].attrs['type'] = 'string'
        self.df['datetime_column'].attrs['type'] = 'datetime'
        self.df['timedelta_column'].attrs['type'] = 'duration'

        jsonl = transform(self.df, to_type=TableJSONLFileFormat)

        with open(jsonl.path, 'r') as fh:
            header_line = fh.readline()
            header_dict = json.loads(header_line)

        for column in self.df.columns:
            field = self.get_header_field(header_dict, column)
            self.assertEqual(field['type'], self.df[column].attrs['type'])

    def test_invalid_attr_type_errors(self):
        '''
        Tests that columns with invalid type attrs produce an error.
        '''
        self.df['integer_column'].attrs['type'] = 'datetime'

        with self.assertRaisesRegex(
            ValueError,
            r'.*type integer can not be converted.*datetime.*'
        ):
            transform(self.df, to_type=TableJSONLFileFormat)

    def test_missing_attrs_inferred_properly(self):
        '''
        Tests that dataframe columns that do not have attrs have their type
        properly inferred and written to the jsonl header.
        '''
        column_to_jsonl_type = {
            'integer_column': 'integer',
            'float_column': 'number',
            'string_column': 'string',
            'datetime_column': 'datetime',
            'timedelta_column': 'duration',
        }

        jsonl = transform(self.df, to_type=TableJSONLFileFormat)

        with open(jsonl.path, 'r') as fh:
            header_line = fh.readline()
            header_dict = json.loads(header_line)

        for column in self.df.columns:
            field = self.get_header_field(header_dict, column)
            self.assertEqual(field['type'], column_to_jsonl_type[column])

    def test_invalid_dataframe_column_type_errors(self):
        '''
        Tests that a column of a type that is not in the set of supported
        data types produces an error.
        '''
        self.df['float_column'] = self.df['float_column'].astype('category')

        with self.assertRaisesRegex(
            ValueError,
            r'.*type of the float_column column was not detected as any of.*'
        ):
            transform(self.df, to_type=TableJSONLFileFormat)

    def assert_proper_type_conversion(
        self,
        df: pd.DataFrame,
        column: str,
        expected_column: pd.Series
    ):
        '''
        Transforms a dataframe to and back from the jsonl format then asserts
        that a column of interest is stored as expected.
        '''
        jsonl = transform(df, to_type=TableJSONLFileFormat)
        round_trip_df = transform(jsonl, to_type=pd.DataFrame)

        expected_column.name = column
        assert_series_equal(round_trip_df[column], expected_column)

    def test_integer_type_conversions(self):
        '''
        Tests that a column of the integer type can be converted to the number
        and string types.
        '''
        self.df['integer_column'].attrs['type'] = 'number'
        self.assert_proper_type_conversion(
            self.df,
            'integer_column',
            pd.Series([1.0, 2.0, 3.0], dtype='float64')
        )

        self.df['integer_column'].attrs['type'] = 'string'
        self.assert_proper_type_conversion(
            self.df,
            'integer_column',
            pd.Series(['1', '2', '3'], dtype='string')
        )

    def test_float_type_conversions(self):
        '''
        Tests that a column of the float type can be converted to the number
        type.
        '''
        self.df['float_column'].attrs['type'] = 'string'
        self.assert_proper_type_conversion(
            self.df,
            'float_column',
            pd.Series(['1.0', '2.5', '3.0'], dtype='string')
        )

    def test_string_type_conversions(self):
        '''
        Tests that columns of the string type can be converted to the datetime,
        date, time, and duration types, whether in the corresponding formats
        or not.
        '''
        df = pd.DataFrame({
            'datetime': ['2025-06-02T13:00:00'],
            'date': ['2025-06-02'],
            'time': ['13:00:00'],
            'duration': ['P7D7H7M7S'],
        })

        # immediately corresponding formats
        df['datetime'].attrs['type'] = 'datetime'
        self.assert_proper_type_conversion(
            df,
            'datetime',
            pd.Series(
                [pd.to_datetime('2025-06-02T13:00:00')],
                dtype='datetime64[ns]'
            )
        )

        df['date'].attrs['type'] = 'date'
        self.assert_proper_type_conversion(
            df,
            'date',
            pd.Series(
                pd.to_datetime(['2025-06-02T00:00:00']),
                dtype='datetime64[ns]'
            )
        )

        df['time'].attrs['type'] = 'time'
        self.assert_proper_type_conversion(
            df,
            'time',
            pd.to_datetime(pd.Series(['13:00:00'])).dt.time
        )

        df['duration'].attrs['type'] = 'duration'
        self.assert_proper_type_conversion(
            df,
            'duration',
            pd.Series(pd.to_timedelta(['P7D7H7M7S']), dtype='timedelta64[ns]')
        )

        # non immediately corresponding formats
        # NOTE: not all possible conversions are enumerated here
        df['datetime'].attrs['type'] = 'time'
        self.assert_proper_type_conversion(
            df,
            'datetime',
            pd.to_datetime(pd.Series(['13:00:00'])).dt.time
        )

        df['date'].attrs['type'] = 'datetime'
        self.assert_proper_type_conversion(
            df,
            'date',
            pd.Series(
                pd.to_datetime(['2025-06-02T00:00:00']), dtype='datetime64[ns]'
            )
        )

        df['time'].attrs['type'] = 'datetime'
        self.assert_proper_type_conversion(
            df,
            'time',
            pd.Series(
                pd.to_datetime(['13:00:00']), dtype='datetime64[ns]'
            )
        )

    def test_datetime_type_conversions(self):
        '''
        Tests that a column of the datetime type can be converted to the
        date and time types.
        '''
        self.df['datetime_column'].attrs['type'] = 'date'
        self.assert_proper_type_conversion(
            self.df,
            'datetime_column',
            pd.Series(
                pd.to_datetime([
                    '2012-01-01T00:00:00', '00:00:00', '1998-03-14T00:00:00'
                ], format='mixed'),
                dtype='datetime64[ns]'
            )
        )

        self.df['datetime_column'].attrs['type'] = 'time'
        self.assert_proper_type_conversion(
            self.df,
            'datetime_column',
            pd.to_datetime(
                pd.Series(['00:00:00', '17:00:00', '00:00:00'])
            ).dt.time
        )

    def test_boolean_type_round_trips(self):
        '''
        Tests that columns of the dtype bool are successfully round-tripped,
        whether the type is annotated in the attrs, or inferred. Note that
        the boolean type is not tested alongside the other types because
        it is not convertable to any other types and no other types convert to
        it.
        '''
        df = pd.DataFrame({
            'bool': [True, False],
            'crip': [False, True],
        })
        df['bool'].attrs['type'] = 'boolean'

        jsonl = transform(df, to_type=TableJSONLFileFormat)
        round_trip_df = transform(jsonl, to_type=pd.DataFrame)

        assert_frame_equal(df, round_trip_df)

    def test_copy_dataframe_with_attrs(self):
        '''
        Tests that the `_copy_dataframe_with_attrs` function accurately
        copies a dataframe and its column and dataframe-level attributes, and
        that it preserves these attributes in the copied-from dataframe.
        '''
        self.df.attrs = {'yay': 'attrs'}
        self.df['integer_column'].attrs = {'key': 'value'}
        self.df['string_column'].attrs = {'oompa': 'loompa'}

        copied_df = _copy_dataframe_with_attrs(self.df)

        assert_frame_equal(copied_df, self.df)

        self.assertEqual(copied_df.attrs, {'yay': 'attrs'})
        self.assertEqual(copied_df['integer_column'].attrs, {'key': 'value'})
        self.assertEqual(copied_df['string_column'].attrs, {'oompa': 'loompa'})

        self.assertEqual(self.df.attrs, {'yay': 'attrs'})
        self.assertEqual(self.df['integer_column'].attrs, {'key': 'value'})
        self.assertEqual(self.df['string_column'].attrs, {'oompa': 'loompa'})

    def test_json_representations(self):
        '''
        Tests that the json representations of various data types are as
        they are expected to be.
        '''
        self.df['boolean_column'] = [True, False, True]

        jsonl = transform(self.df, to_type=TableJSONLFileFormat)
        with open(str(jsonl)) as fh:
            json_content = fh.read()

        self.assertIn('"integer_column":1', json_content)
        self.assertIn('"float_column":1.0', json_content)
        self.assertIn('"string_column":"strings"', json_content)
        self.assertIn('"boolean_column":true', json_content)
        self.assertIn(
            '"datetime_column":"2012-01-01T00:00:00.000"', json_content
        )
        self.assertIn(
            '"datetime_column":"1998-03-14T00:00:00.000"', json_content
        )
        self.assertIn('"timedelta_column":"P420DT0H0M0S"', json_content)

        # datetime to date
        self.df['datetime_column'].attrs['type'] = 'date'
        jsonl = transform(self.df, to_type=TableJSONLFileFormat)
        with open(str(jsonl)) as fh:
            json_content = fh.read()

        self.assertIn('"datetime_column":"1998-03-14"', json_content)

        # datetime to time
        self.df['datetime_column'].attrs['type'] = 'time'
        jsonl = transform(self.df, to_type=TableJSONLFileFormat)
        with open(str(jsonl)) as fh:
            json_content = fh.read()

        self.assertIn('"datetime_column":"17:00:00"', json_content)
