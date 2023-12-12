# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest

from qiime2.core.exceptions import ValidationError
from qiime2.plugin.testing import TestPluginBase

from .._format import MAGtoContigsFormat


class TestFormats(TestPluginBase):
    package = "q2_types.feature_map.tests"

    def test_mag_to_contigs_valid_min(self):
        fp = self.get_data_path("mag-to-contigs-valid.json")
        fmt = MAGtoContigsFormat(fp, mode="r")
        fmt.validate(level="min")

    def test_mag_to_contigs_valid_max(self):
        fp = self.get_data_path("mag-to-contigs-valid.json")
        fmt = MAGtoContigsFormat(fp, mode="r")
        fmt.validate(level="max")

    def test_mag_to_contigs_has_invalid_ids(self):
        fp = self.get_data_path("mag-to-contigs-invalid-ids.json")
        fmt = MAGtoContigsFormat(fp, mode="r")
        with self.assertRaisesRegex(
            ValidationError, 'Found "6232c7e1", which is invalid.'
        ):
            fmt.validate(level="max")

    def test_mag_to_contigs_has_invalid_values(self):
        fp = self.get_data_path("mag-to-contigs-invalid-values.json")
        fmt = MAGtoContigsFormat(fp, mode="r")
        with self.assertRaisesRegex(
            ValidationError,
            'Found "<class \'str\'>" for MAG '
            '"6232c7e1-8ed7-47c8-9bdb-b94706a26931".',
        ):
            fmt.validate(level="max")

    def test_mag_to_contigs_has_no_contigs(self):
        fp = self.get_data_path("mag-to-contigs-empty-list.json")
        fmt = MAGtoContigsFormat(fp, mode="r")
        with self.assertRaisesRegex(
            ValidationError,
            'MAG "6232c7e1-8ed7-47c8-9bdb-b94706a26931" is empty.',
        ):
            fmt.validate(level="max")


if __name__ == "__main__":
    unittest.main()
