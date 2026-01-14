# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import warnings
import pandas as pd

from qiime2.plugin import Properties, ValidationError

from .. import FeatureData, SequenceCharacteristics, Taxonomy

from ...plugin_setup import plugin

from q2_types.feature_data._deferred_setup._transformers import (
    _taxonomy_formats_to_dataframe
)
from q2_types.feature_data import TSVTaxonomyFormat

from qiime2.core.exceptions import RachisWarning


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


@plugin.register_validator(FeatureData[Taxonomy])
def _check_single_taxon(data: TSVTaxonomyFormat, level):
    taxon_df = _taxonomy_formats_to_dataframe(str(data))

    max_depth = 0
    for taxon in taxon_df['Taxon']:
        if taxon.count(';') > max_depth:
            max_depth = taxon.count(';')
    if max_depth == 0:
        warnings.warn(
            'Importing taxonomy with taxonomic depth of one.',
            RachisWarning
        )


@plugin.register_validator(FeatureData[Taxonomy])
def _check_trailing_semicolon(data: TSVTaxonomyFormat, level):
    taxon_df = _taxonomy_formats_to_dataframe(str(data))

    for taxon in taxon_df['Taxon']:
        if taxon.rstrip().endswith(';'):
            warnings.warn(
                'Importing taxonomy with a trailing semicolon.',
                RachisWarning
            )
