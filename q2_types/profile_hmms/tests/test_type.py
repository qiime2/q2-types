# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin.testing import TestPluginBase
from q2_types.profile_hmms._type import (
    ProfileHMM, BaseHmmPressedDirFmt,
    ProteinHmmMultipleProfilesDirectoryFormat,
    DnaHmmMultipleProfilesDirectoryFormat,
    RnaHmmMultipleProfilesDirectoryFormat,
    ProteinHmmDirectoryFormat, DnaHmmDirectoryFormat, RnaHmmDirectoryFormat,
    SingleProtein, SingleDNA, SingleRNA,
    MultipleProtein, MultipleDNA, MultipleRNA,
    PressedProtein, PressedDNA, PressedRNA
)


class TestHMMType(TestPluginBase):
    package = 'q2_types.reference_db.tests'

    def test_hmmer_registration(self):
        self.assertRegisteredSemanticType(ProfileHMM)

    def test_SingleAmino_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[SingleProtein], ProteinHmmDirectoryFormat
        )

    def test_SingleDNA_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[SingleDNA], DnaHmmDirectoryFormat
        )

    def test_SingleRNA_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[SingleRNA], RnaHmmDirectoryFormat
        )

    def test_MultipleAmino_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[MultipleProtein],
            ProteinHmmMultipleProfilesDirectoryFormat
        )

    def test_MultipleDNA_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[MultipleDNA], DnaHmmMultipleProfilesDirectoryFormat
        )

    def test_MultipleRNA_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[MultipleRNA], RnaHmmMultipleProfilesDirectoryFormat
        )

    def test_MultipleAminoPressed_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[PressedProtein], BaseHmmPressedDirFmt
        )

    def test_MultipleDNAPressed_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[PressedDNA], BaseHmmPressedDirFmt
        )

    def test_MultipleRNAPressed_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ProfileHMM[PressedRNA], BaseHmmPressedDirFmt
        )
