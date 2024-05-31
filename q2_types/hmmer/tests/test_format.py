# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import tempfile
import shutil
import os
from qiime2.plugin.testing import TestPluginBase
from q2_types.hmmer._format import HmmIdmapFileFmt
from qiime2.plugin import ValidationError


class TestRefFormats(TestPluginBase):
    package = 'q2_types.hmm.tests'

    def test_HmmerDirFmt_valid(self):
        fmt = ...(self.get_data_path("hmmer/bacteria"), 'r')
        fmt.validate()

    def test_HmmerDirFmt_invalid_idmap_1(self):
        fmt = HmmIdmapFileFmt(self.get_data_path(
            "hmmer/invalid_idmaps/1.hmm.idmap"), 'r'
        )
        with self.assertRaisesRegex(
            ValidationError,
            "Expected index and an alphanumeric code separated "
            "by a single space."
        ):
            fmt.validate(level="min")

    def test_HmmerDirFmt_invalid_idmap_2(self):
        fmt = HmmIdmapFileFmt(self.get_data_path(
            "hmmer/invalid_idmaps/2.hmm.idmap"), 'r'
        )
        with self.assertRaisesRegex(
            ValidationError,
            "Expected index and an alphanumeric code separated "
            "by a single space."
        ):
            fmt.validate(level="min")

    def test_HmmerDirFmt_invalid_idmap_3(self):
        fmt = HmmIdmapFileFmt(self.get_data_path(
            "hmmer/invalid_idmaps/3.hmm.idmap"), 'r'
        )
        with self.assertRaisesRegex(
            ValidationError,
            'Expected index'
        ):
            fmt.validate(level="min")

    def test_HmmerDirFmt_invalid_idmap_4(self):
        fmt = HmmIdmapFileFmt(self.get_data_path(
            "hmmer/invalid_idmaps/4.hmm.idmap"), 'r'
        )
        with self.assertRaisesRegex(
            ValidationError,
            "Expected index and an alphanumeric code separated "
            "by a single space."
        ):
            fmt.validate(level="min")

    def test_HmmerDirFmt_missing_hmm(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(
                self.get_data_path("hmmer/bacteria"), tmp, dirs_exist_ok=True
            )
            os.remove(f"{tmp}/bacteria.hmm.h3f")
            fmt = ...(tmp, 'r')
            with self.assertRaisesRegex(
                ValidationError, "Missing one or more files"
            ):
                fmt.validate(level="min")

    def test_HmmerDirFmt_missing_fa(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(
                self.get_data_path("hmmer/bacteria"), tmp, dirs_exist_ok=True
            )
            for file in ["a", "b", "b2"]:
                os.remove(f"{tmp}/{file}.fa")
            fmt = ...(tmp, 'r')
            with self.assertRaisesRegex(
                ValidationError, "Missing one or more files"
            ):
                fmt.validate(level="min")
