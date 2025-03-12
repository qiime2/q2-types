# ----------------------------------------------------------------------------
# Copyright (c) 2022-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pandas as pd

from qiime2.plugin import ValidationError
from .. import (Dist1D, Ordered, Unordered, NestedOrdered,
                NestedUnordered, Matched, Independent)
from ...plugin_setup import plugin


@plugin.register_validator(Dist1D[Ordered | Unordered,
                           Matched | Independent])
def validate_all_dist_columns_present(data: pd.DataFrame, level):
    req_cols = ['id', 'measure', 'group']
    for col in req_cols:
        if col not in data.columns:
            raise ValidationError(f'"{col}" not found in distribution.')


@plugin.register_validator(Dist1D[Ordered | Unordered, Matched])
def validate_unique_subjects_within_group(data: pd.DataFrame, level):
    if 'subject' not in data.columns:
        raise ValidationError('"subject" not found in distribution.')

    for group_id, group_df in data.groupby('group'):
        if group_df['subject'].duplicated().any():
            dupes = list(group_df['subject'][group_df['subject'].duplicated()])
            raise ValidationError(
                'Unique subject found more than once within an individual'
                ' group. Group(s) where duplicated subject was found:'
                f' [{group_id}] Duplicated subjects: {dupes}')


@plugin.register_validator(Dist1D[NestedOrdered | NestedUnordered,
                           Matched | Independent])
def validate_all_nesteddist_columns_present(data: pd.DataFrame, level):
    req_cols = ['id', 'measure', 'group', 'class', "level"]
    for col in req_cols:
        if col not in data.columns:
            raise ValidationError(f'"{col}" not found in distribution.')
