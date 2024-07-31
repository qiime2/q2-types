
import pandas as pd
from qiime2.plugin import ValidationError
from qiime2.plugin.testing import TestPluginBase

from q2_types.feature_data._deferred_setup._validators import (
    validate_seq_char_len)


class TestTypes(TestPluginBase):
    package = 'q2_types.feature_data.tests'

    def test_validate_sequence_characteristics_length(self):
        data = self._setup_df()
        validate_seq_char_len(data, None)

    def test_validate_sequence_characteristics_length_no_length_column(self):
        data = self._setup_df()
        data.drop(columns=['length'], inplace=True)
        self._assert_validation_error(data, 'Column "length" has to exist in '
                                            'the file.')

    def test_validate_sequence_characteristics_length_not_numerical(self):
        data = self._setup_df()
        data.loc[1, 'length'] = 'a'
        self._assert_validation_error(data, 'Values in column "length" have '
                                            'to be numerical.')

    def test_validate_sequence_characteristics_length_empty_values(self):
        data = self._setup_df()
        data.loc[1, 'length'] = None
        self._assert_validation_error(data, 'Column "length" cannot contain '
                                            'empty (NaN) values.')

    def test_validate_sequence_characteristics_length_negative_values(self):
        data = self._setup_df()
        data.loc[1, 'length'] = -1
        self._assert_validation_error(data, 'Column "length" cannot contain '
                                            'negative values.')

    def _setup_df(self):
        data_path = self.get_data_path('sequence_characteristics_length.tsv')
        return pd.read_csv(data_path, sep="\t", index_col=0)

    def _assert_validation_error(self, data, error_message):
        with self.assertRaises(ValidationError) as context:
            validate_seq_char_len(data, None)
        self.assertEqual(str(context.exception), error_message)
