# ----------------------------------------------------------------------------
# Copyright (c) 2022-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
from pathlib import Path

from q2_types.kraken2 import Kraken2OutputDirectoryFormat
from qiime2.plugin import model
from qiime2.plugin.testing import TestPluginBase

from q2_types._util import _validate_num_partitions, _validate_mag_ids, \
    FileDictMixin


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


class TestFileDictMixin(TestPluginBase):
    package = "q2_types.tests"

    def setUp(self):
        super().setUp()

        self.TestClass = type(
            f"{model.DirectoryFormat.__name__}With{FileDictMixin.__name__}",
            (FileDictMixin, model.DirectoryFormat),
            {}
        )
        self.TestClass.pathspec = r'.+\.(txt|tsv)$'
        self.TestClass.suffixes = ["_suffix1", "_suffix2"]

    def test_file_dict_mixin_per_sample(self):
        fmt = self.TestClass(self.get_data_path("per_sample"), mode='r')

        obs = fmt.file_dict()
        exp = {
            "sample1": {
                "id1": os.path.join(str(fmt), "sample1", "id1_suffix1.txt"),
            },
            "sample2": {
                "id2": os.path.join(str(fmt), "sample2", "id2_suffix1.txt"),
            },
        }
        self.assertDictEqual(obs, exp)

        obs = fmt.file_dict(relative=True)
        exp = {
            "sample1": {
                "id1": "sample1/id1_suffix1.txt",
            },
            "sample2": {
                "id2": "sample2/id2_suffix1.txt",
            },
        }
        self.assertDictEqual(obs, exp)

    def test_file_dict_mixin_not_per_sample(self):
        fmt = self.TestClass(self.get_data_path("not_per_sample"), mode='r')

        obs = fmt.file_dict()
        exp = {
            "id1": os.path.join(str(fmt), "id1_suffix1.txt"),
            "id2": os.path.join(str(fmt), "id2_suffix2.txt"),
        }
        self.assertDictEqual(obs, exp)

        obs = fmt.file_dict(relative=True)
        exp = {
            "id1": "id1_suffix1.txt",
            "id2": "id2_suffix2.txt",
        }
        self.assertDictEqual(obs, exp)

    def test_file_dict_mixin_kraken_outputs(self):
        fmt = Kraken2OutputDirectoryFormat(
            self.get_data_path("kraken-outputs-mags"), mode='r'
        )

        obs = fmt.file_dict()
        exp = {
            "sample1": {
                "bin1": os.path.join(str(fmt), "sample1", "bin1.output.txt"),
                "bin2": os.path.join(str(fmt), "sample1", "bin2.output.txt"),
            },
            "sample2": {
                "bin3": os.path.join(str(fmt), "sample2", "bin3.output.txt"),
            },
        }
        self.assertDictEqual(obs, exp)

        obs = fmt.file_dict(relative=True)
        exp = {
            "sample1": {
                "bin1": "sample1/bin1.output.txt",
                "bin2": "sample1/bin2.output.txt",
            },
            "sample2": {
                "bin3": "sample2/bin3.output.txt",
            },
        }
        self.assertDictEqual(obs, exp)

    def test_process_path_with_suffix(self):
        # Test when class does have suffixes attribute
        test_class = self.TestClass()
        path = Path(test_class.path / "sample_id_suffix1.txt")

        result_path, result_id = test_class._process_path(
            path,
            relative=True,
        )

        self.assertEqual(result_id, "sample_id")
        self.assertEqual(result_path, "sample_id_suffix1.txt")

    def test_process_path_without_suffix(self):
        # Test when class does not have suffixes attribute
        test_class = self.TestClass()
        delattr(self.TestClass, "suffixes")
        path = Path(test_class.path / "sample_id.txt")

        result_path, result_id = test_class._process_path(
            path,
            relative=True,
        )

        self.assertEqual(result_id, "sample_id")
        self.assertEqual(result_path, "sample_id.txt")

    def test_process_path_absolute(self):
        test_class = self.TestClass()
        path = Path(test_class.path / "sample_id_suffix1.txt")

        result_path, result_id = test_class._process_path(path)

        self.assertEqual(result_id, "sample_id")
        self.assertEqual(result_path, str(path.absolute()))
