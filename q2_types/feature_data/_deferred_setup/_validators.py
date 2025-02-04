# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd

from qiime2.plugin import Properties, ValidationError

from .. import FeatureData, SequenceCharacteristics

from ...plugin_setup import plugin


@plugin.register_validator(FeatureData[SequenceCharacteristics %
                                       Properties("length")])
def validate_seq_char_len(data: pd.DataFrame, level):
    """
    Semantic validator that validates a numerical column called 'length',
    which cannot contain empty or negative values, for the
    FeatureData[SequenceCharacteristics] type with property "length".
    """
    if 'length' not in data.columns:
        raise ValidationError('Column "length" has to exist in the file.')

    if data['length'].isnull().any():
        raise ValidationError('Column "length" cannot contain empty (NaN) '
                              'values.')

    if not pd.api.types.is_numeric_dtype(data['length']):
        raise ValidationError('Values in column "length" have to be '
                              'numerical.')

    if not (data['length'] > 0).all():
        raise ValidationError('Column "length" cannot contain negative '
                              'values.')
