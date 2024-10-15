# ----------------------------------------------------------------------------
# Copyright (c) 2022-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
from pathlib import Path

from qiime2.plugin import model
from qiime2.plugin.testing import TestPluginBase

from q2_types._util import _validate_num_partitions, _validate_mag_ids, \
    FileDictMixin, _process_path


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

    def test_file_dict_mixin(self):
        TestClass = type(
            f"{model.DirectoryFormat.__name__}With{FileDictMixin.__name__}",
            (FileDictMixin, model.DirectoryFormat),
            {}
        )
        fmt = TestClass(self.get_data_path("per_sample"), mode='r')

        obs = fmt.file_dict(suffixes=["_suffix"])
        exp = {
            "sample1": {
                "id1": os.path.join(str(fmt), "sample1", "id1_suffix.txt"),
            },
            "sample2": {
                "": os.path.join(str(fmt), "sample2", "suffix.txt"),
            },
        }
        self.assertDictEqual(obs, exp)

        obs = fmt.file_dict(suffixes=["_suffix"], relative=True)
        exp = {
            "sample1": {
                "id1": "sample1/id1_suffix.txt",
            },
            "sample2": {
                "": "sample2/suffix.txt",
            },
        }
        self.assertDictEqual(obs, exp)

    def test_genes_dirfmt_genome_dict(self):
        TestClass = type(
            f"{model.DirectoryFormat.__name__}With{FileDictMixin.__name__}",
            (FileDictMixin, model.DirectoryFormat),
            {}
        )
        fmt = TestClass(self.get_data_path("not_per_sample"), mode='r')

        obs = fmt.file_dict(suffixes=["_suffix1", "_suffix2"])
        exp = {
            "id1": os.path.join(str(fmt), "id1_suffix1.txt"),
            "id2": os.path.join(str(fmt), "id2_suffix2.txt"),
        }
        self.assertDictEqual(obs, exp)

        obs = fmt.file_dict(
            suffixes=["_suffix1", "_suffix2"],
            relative=True
        )
        exp = {
            "id1": "id1_suffix1.txt",
            "id2": "id2_suffix2.txt",
        }
        self.assertDictEqual(obs, exp)


class TestProcessPath(TestPluginBase):
    package = "q2_types.tests"

    def setUp(self):
        super().setUp()
        self.dir_fmt = model.DirectoryFormat()

    def test_process_path_with_suffix(self):
        # Test when the file name ends with a given suffix
        path = Path(self.dir_fmt.path / "sample_id_suffix1.txt")
        suffixes = ["_suffix1", "_suffix2"]

        result_path, result_id = _process_path(
            path,
            relative=True,
            dir_format=self.dir_fmt,
            suffixes=suffixes
        )

        self.assertEqual(result_id, "sample_id")
        self.assertEqual(result_path, "sample_id_suffix1.txt")

    def test_process_path_without_suffix(self):
        # Test when no suffix matches the file name
        path = Path(self.dir_fmt.path / "sample_id.txt")
        suffixes = ["_suffix1", "_suffix2"]

        result_path, result_id = _process_path(
            path,
            relative=True,
            dir_format=self.dir_fmt,
            suffixes=suffixes
        )

        self.assertEqual(result_id, "sample_id")
        self.assertEqual(result_path, "sample_id.txt")

    def test_process_path_absolute(self):
        # Test when the relative flag is False (absolute path is returned)
        path = Path(self.dir_fmt.path / "sample_id_suffix2.txt")
        suffixes = ["_suffix1", "_suffix2"]

        result_path, result_id = _process_path(
            path,
            relative=False,
            dir_format=self.dir_fmt,
            suffixes=suffixes
        )

        self.assertEqual(result_id, "sample_id")
        self.assertEqual(result_path, str(path.absolute()))

    def test_process_path_only_suffix(self):
        # Test when the file name consists only of the suffix
        path = Path(self.dir_fmt.path / "suffix1.txt")
        suffixes = ["_suffix1", "_suffix2"]

        result_path, result_id = _process_path(
            path,
            relative=True,
            dir_format=self.dir_fmt,
            suffixes=suffixes
        )

        self.assertEqual(result_id, "")
        self.assertEqual(result_path, "suffix1.txt")
