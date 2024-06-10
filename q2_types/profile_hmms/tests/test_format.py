# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin.testing import TestPluginBase
from q2_types.profile_hmms._format import (
    PressedProfileHmmsDirectoryFmt,
    ProteinMultipleProfileHmmFileFmt,
    ProteinSingleProfileHmmFileFmt,
    RnaMultipleProfileHmmFileFmt,
    RnaSingleProfileHmmFileFmt,
    DnaMultipleProfileHmmFileFmt,
    DnaSingleProfileHmmFileFmt
)
from qiime2.plugin import ValidationError


class TestHmmFormats(TestPluginBase):
    package = 'q2_types.profile_hmms.tests'

    def test_PressedProfileHmmsDirectoryFmt_valid(self):
        fmt = PressedProfileHmmsDirectoryFmt(
            self.get_data_path("bacteria"), 'r'
        )
        fmt.validate(level="min")

    def test_ProteinSingleProfileHmmFileFmt_valid(self):
        fmt = ProteinSingleProfileHmmFileFmt(
            self.get_data_path("hmms/amino.hmm"), "r"
        )
        fmt.validate()

    def test_DnaSingleProfileHmmFileFmt_valid(self):
        fmt = DnaSingleProfileHmmFileFmt(
            self.get_data_path("hmms/dna.hmm"), "r",
        )
        fmt.validate()

    def test_RnaSingleProfileHmmFileFmt_valid(self):
        fmt = RnaSingleProfileHmmFileFmt(
            self.get_data_path("hmms/rna.hmm"), "r"
        )
        fmt.validate()

    def test_ProteinSingleProfileHmmFileFmt_invalid_alph(self):
        for typ in ["rna", "dna"]:
            fmt = ProteinSingleProfileHmmFileFmt(
                self.get_data_path(f"hmms/{typ}.hmm"), "r",
            )
            with self.assertRaisesRegex(
                ValidationError, "Found profile with alphabet "
            ):
                fmt.validate()

    def test_DnaSingleProfileHmmFileFmt_invalid_alph(self):
        for typ in ["rna", "amino"]:
            fmt = DnaSingleProfileHmmFileFmt(
                self.get_data_path(f"hmms/{typ}.hmm"), "r"
            )
            with self.assertRaisesRegex(
                ValidationError, "Found profile with alphabet "
            ):
                fmt.validate()

    def test_RnaSingleProfileHmmFileFmt_invalid_alph(self):
        for typ in ["dna", "amino"]:
            fmt = RnaSingleProfileHmmFileFmt(
                self.get_data_path(f"hmms/{typ}.hmm"), "r"
            )
            with self.assertRaisesRegex(
                ValidationError, "Found profile with alphabet "
            ):
                fmt.validate()

    def test_ProteinSingleProfileHmmFileFmt_too_many_profiles(self):
        fmt = ProteinSingleProfileHmmFileFmt(
            self.get_data_path("hmms/4_amino.hmm"), "r"
        )
        with self.assertRaisesRegex(
            ValidationError, "Expected 1 profile, found 4."
        ):
            fmt.validate()

    def test_ProteinMultipleProfileHmmFileFmt_valid(self):
        fmt = ProteinMultipleProfileHmmFileFmt(
            self.get_data_path("hmms/4_amino.hmm"), "r"
        )
        fmt.validate()

    def test_DnaMultipleProfileHmmFileFmt_valid(self):
        fmt = DnaMultipleProfileHmmFileFmt(
            self.get_data_path("hmms/2_dna.hmm"), "r"
        )
        fmt.validate()

    def test_RnaMultipleProfileHmmFileFmt_valid(self):
        fmt = RnaMultipleProfileHmmFileFmt(
            self.get_data_path("hmms/2_rna.hmm"), "r"
        )
        fmt.validate()

    def test_mixed_hmm_profiles_invalid_1(self):
        fmt = ProteinMultipleProfileHmmFileFmt(
            self.get_data_path("hmms/amino_dna.hmm"), 'r'
        )
        with self.assertRaisesRegex(
            ValidationError, "Found profiles with different alphabets."
        ):
            fmt.validate()

    def test_mixed_hmm_profiles_invalid_2(self):
        fmt = DnaMultipleProfileHmmFileFmt(
            self.get_data_path("hmms/rna_dna.hmm"), 'r'
        )
        with self.assertRaisesRegex(
            ValidationError, "Found profiles with different alphabets."
        ):
            fmt.validate()
