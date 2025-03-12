# ----------------------------------------------------------------------------
# Copyright (c) 2024, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest

import pandas as pd

from qiime2.plugin import ValidationError

from q2_types.tabular._deferred_setup._validators import (
    validate_all_dist_columns_present,
    validate_unique_subjects_within_group,
)


class TestValidators(unittest.TestCase):
    def test_validators_missing_columns_in_dist(self):
        with self.assertRaisesRegex(ValidationError, '"group" not found'
                                    ' in distribution.'):
            df = pd.DataFrame({
                'id': ['S340445', 'S892825', 'S460691'],
                'measure': [7.662921088, 8.431734297, 8.513263823]
            })
            validate_all_dist_columns_present(df, level=min)

    def test_validators_unique_subjects_not_duplicated_per_group(self):
        with self.assertRaisesRegex(ValidationError, 'Unique subject found'
                                    ' more than once within an individual'
                                    ' group.*0.*P26'):
            df = pd.DataFrame({
                'id': ['S116625', 'S813956'],
                'measure': [7.662921088, 8.431734297],
                'group': [0, 0],
                'subject': ['P26', 'P26']
            })
            validate_unique_subjects_within_group(df, level=min)
