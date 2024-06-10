# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin.testing import TestPluginBase
from q2_types.profile_hmms._format import (
    BaseHmmPressedDirFmt,
    ProteinHmmFileFmt, DnaHmmFileFmt, RnaHmmFileFmt,
    ProteinHmmMultipleProfilesFileFmt,
    DnaHmmMultipleProfilesFileFmt,
    RnaHmmMultipleProfilesFileFmt
)
from qiime2.plugin import ValidationError


class TestHmmFormats(TestPluginBase):
    package = 'q2_types.hmmer.tests'

    def test_BaseHmmPressedDirFmt_valid(self):
        fmt = BaseHmmPressedDirFmt(self.get_data_path("bacteria"), 'r')
        fmt.validate(level="min")

    def test_AminoHmmFileFmt_valid(self):
        fmt = ProteinHmmFileFmt(self.get_data_path("hmms/amino.hmm"), "r")
        fmt.validate()

    def test_DnaHmmFileFmt_valid(self):
        fmt = DnaHmmFileFmt(self.get_data_path("hmms/dna.hmm"), "r")
        fmt.validate()

    def test_RnaHmmFileFmt_valid(self):
        fmt = RnaHmmFileFmt(self.get_data_path("hmms/rna.hmm"), "r")
        fmt.validate()

    def test_AminoHmmFileFmt_invalid_alph(self):
        for typ in ["rna", "dna"]:
            fmt = ProteinHmmFileFmt(self.get_data_path(f"hmms/{typ}.hmm"), "r")
            with self.assertRaisesRegex(
                ValidationError, "Found profile with alphabet "
            ):
                fmt.validate()

    def test_DnaHmmFileFmt_invalid_alph(self):
        for typ in ["rna", "amino"]:
            fmt = DnaHmmFileFmt(self.get_data_path(f"hmms/{typ}.hmm"), "r")
            with self.assertRaisesRegex(
                ValidationError, "Found profile with alphabet "
            ):
                fmt.validate()

    def test_RnaHmmFileFmt_invalid_alph(self):
        for typ in ["dna", "amino"]:
            fmt = RnaHmmFileFmt(self.get_data_path(f"hmms/{typ}.hmm"), "r")
            with self.assertRaisesRegex(
                ValidationError, "Found profile with alphabet "
            ):
                fmt.validate()

    def test_AminoHmmFileFmt_too_many_profiles(self):
        fmt = ProteinHmmFileFmt(self.get_data_path("hmms/4_amino.hmm"), "r")
        with self.assertRaisesRegex(
            ValidationError, "Expected 1 profile, found 4."
        ):
            fmt.validate()

    def test_AminoHmmMultipleProfilesFileFmt_valid(self):
        fmt = ProteinHmmMultipleProfilesFileFmt(
            self.get_data_path("hmms/4_amino.hmm"), 'r'
        )
        fmt.validate()

    def test_DnaHmmMultipleProfilesFileFmt_valid(self):
        fmt = DnaHmmMultipleProfilesFileFmt(
            self.get_data_path("hmms/2_dna.hmm"), "r"
        )
        fmt.validate()

    def test_RnaHmmMultipleProfilesFileFmt_valid(self):
        fmt = RnaHmmMultipleProfilesFileFmt(
            self.get_data_path("hmms/2_rna.hmm"), "r"
        )
        fmt.validate()

    def test_mixed_hmm_profiles_invalid_1(self):
        fmt = ProteinHmmMultipleProfilesFileFmt(
            self.get_data_path("hmms/amino_dna.hmm"), 'r'
        )
        with self.assertRaisesRegex(
            ValidationError, "Found profiles with different alphabets."
        ):
            fmt.validate()

    def test_mixed_hmm_profiles_invalid_2(self):
        fmt = DnaHmmMultipleProfilesFileFmt(
            self.get_data_path("hmms/rna_dna.hmm"), 'r'
        )
        with self.assertRaisesRegex(
            ValidationError, "Found profiles with different alphabets."
        ):
            fmt.validate()
