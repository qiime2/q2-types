# ----------------------------------------------------------------------------
# Copyright (c) 2022-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin.testing import TestPluginBase

from q2_types._util import _validate_num_partitions, _validate_mag_ids


class TestUtil(TestPluginBase):
    package = "q2_types.tests"

    def test_validate_num_partitions_None(self):
        num_partitions = _validate_num_partitions(14, None)
        self.assertEqual(14, num_partitions)

    def test_validate_num_partitions_Warning(self):
        num_partitions = 15
        num_samples = 14
        with self.assertWarnsRegex(
                Warning,
                "You have requested a number of partitions"
                f" '{num_partitions}' that is greater than your number"
                f" of samples '{num_samples}.'"
        ):
            _ = _validate_num_partitions(num_samples, num_partitions)

    def test_validate_num_partitions_valid(self):
        num_partitions = _validate_num_partitions(14, 2)
        self.assertEqual(2, num_partitions)

    def test_validate_mag_ids_valid(self):
        _validate_mag_ids(
            6,
            6,
            [(0, "a"), (0, "b"), (0, "c"), (0, "d"), (0, "e"), (0, "f")]
        )

    def test_validate_mag_ids_invalid(self):
        with self.assertRaisesRegex(ValueError, "MAG IDs are not unique. "):
            _validate_mag_ids(
                6,
                6,
                [(0, "a"), (0, "a"), (0, "c"), (0, "d"), (0, "e"), (0, "f")]
            )
