# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin.testing import TestPluginBase
from q2_types.profile_hmms._type import (
    ProfileHMM,
    SingleProtein, SingleDNA, SingleRNA,
    MultipleProtein, MultipleDNA, MultipleRNA,
    PressedProtein, PressedDNA, PressedRNA,
    PressedProfileHmmsDirectoryFmt,
    DnaSingleProfileHmmDirectoryFmt,
    DnaMultipleProfileHmmDirectoryFmt,
    RnaSingleProfileHmmDirectoryFmt,
    RnaMultipleProfileHmmDirectoryFmt,
    ProteinSingleProfileHmmDirectoryFmt,
    ProteinMultipleProfileHmmDirectoryFmt
)


class TestHMMType(TestPluginBase):
    package = 'q2_types.reference_db.tests'

    def test_hmmer_registration(self):
        self.assertRegisteredSemanticType(ProfileHMM)

    def test_SingleAmino_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[SingleProtein], ProteinSingleProfileHmmDirectoryFmt
        )

    def test_SingleDNA_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[SingleDNA], DnaSingleProfileHmmDirectoryFmt
        )

    def test_SingleRNA_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[SingleRNA], RnaSingleProfileHmmDirectoryFmt
        )

    def test_MultipleAmino_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[MultipleProtein], ProteinMultipleProfileHmmDirectoryFmt
        )

    def test_MultipleDNA_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[MultipleDNA], DnaMultipleProfileHmmDirectoryFmt
        )

    def test_MultipleRNA_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[MultipleRNA], RnaMultipleProfileHmmDirectoryFmt
        )

    def test_MultipleAminoPressed_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[PressedProtein], PressedProfileHmmsDirectoryFmt
        )

    def test_MultipleDNAPressed_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[PressedDNA], PressedProfileHmmsDirectoryFmt
        )

    def test_MultipleRNAPressed_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[PressedRNA], PressedProfileHmmsDirectoryFmt
        )
