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
from q2_types.hmmer._format import (
    HmmIdmapFileFmt, BaseHmmPressedDirFmt, AminoHmmFileFmt, DnaHmmFileFmt,
    # RnaHmmFileFmt
)
from qiime2.plugin import ValidationError


class TestHmmFormats(TestPluginBase):
    package = 'q2_types.hmmer.tests'

    def test_HmmIdmapFileFmt_valid(self):
        fmt = HmmIdmapFileFmt(
            self.get_data_path("bacteria/bacteria.hmm.idmap"), 'r'
        )
        fmt.validate()

    def test_HmmIdmapFileFmt_invalid_idmap_1(self):
        fmt = HmmIdmapFileFmt(
            self.get_data_path("invalid_idmaps/1.hmm.idmap"), 'r'
        )
        with self.assertRaisesRegex(
            ValidationError,
            "Expected index and an alphanumeric code separated "
            "by a single space."
        ):
            fmt.validate(level="min")

    def test_HmmIdmapFileFmt_invalid_idmap_2(self):
        fmt = HmmIdmapFileFmt(
            self.get_data_path("invalid_idmaps/2.hmm.idmap"), 'r'
        )
        with self.assertRaisesRegex(
            ValidationError,
            "Expected index and an alphanumeric code separated "
            "by a single space."
        ):
            fmt.validate(level="min")

    def test_HmmIdmapFileFmt_invalid_idmap_3(self):
        fmt = HmmIdmapFileFmt(
            self.get_data_path("invalid_idmaps/3.hmm.idmap"), 'r'
        )
        with self.assertRaisesRegex(
            ValidationError,
            'Expected index'
        ):
            fmt.validate(level="min")

    def test_HmmIdmapFileFmt_invalid_idmap_4(self):
        fmt = HmmIdmapFileFmt(
            self.get_data_path("invalid_idmaps/4.hmm.idmap"), 'r'
        )
        with self.assertRaisesRegex(
            ValidationError,
            "Expected index and an alphanumeric code separated "
            "by a single space."
        ):
            fmt.validate(level="min")

    def test_BaseHmmPressedDirFmt_missing_hmm(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(
                self.get_data_path("bacteria"), tmp, dirs_exist_ok=True
            )
            os.remove(f"{tmp}/bacteria.hmm.h3f")
            fmt = BaseHmmPressedDirFmt(tmp, 'r')
            with self.assertRaisesRegex(
                ValidationError, "Missing one or more files"
            ):
                fmt.validate(level="min")

    def test_BaseHmmPressedDirFmt_missing_idmap_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(
                self.get_data_path("bacteria"), tmp, dirs_exist_ok=True
            )
            os.remove(f"{tmp}/bacteria.hmm.idmap")
            fmt = BaseHmmPressedDirFmt(tmp, 'r')
            fmt.validate(level="min")

    def test_BaseHmmPressedDirFmt_valid(self):
        fmt = BaseHmmPressedDirFmt(self.get_data_path("bacteria"), 'r')
        fmt.validate(level="min")

    def test_AminoHmmFileFmt_valid(self):
        fmt = AminoHmmFileFmt(self.get_data_path("hmms/amino.hmm"), "r")
        fmt.validate()

    def test_DnaHmmFileFmt_valid(self):
        fmt = DnaHmmFileFmt(self.get_data_path("hmms/dna.hmm"), "r")
        fmt.validate()

    # def test_RnaHmmFileFmt_valid(self):
    #     fmt = RnaHmmFileFmt(self.get_data_path("hmms/rna.hmm"), "r")
    #     fmt.validate()
