# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
from qiime2.plugin.testing import TestPluginBase
from q2_types.hmmer import (
    HMM, BaseHmmPressedDirFmt,
    AminoHmmMultipleProfilesDirectoryFormat,
    DnaHmmMultipleProfilesDirectoryFormat,
    RnaHmmMultipleProfilesDirectoryFormat,
    AminoHmmDirectoryFormat, DnaHmmDirectoryFormat, RnaHmmDirectoryFormat,
    SingleAmino, SingleDNA, SingleRNA,
    MultipleAmino, MultipleDNA, MultipleRNA,
    MultipleAminoPressed, MultipleDNAPressed, MultipleRNAPressed
)


class TestHMMType(TestPluginBase):
    package = 'q2_types.reference_db.tests'

    def test_hmmer_registration(self):
        self.assertRegisteredSemanticType(HMM)

    def test_SingleAmino_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            HMM[SingleAmino], AminoHmmDirectoryFormat
        )

    def test_SingleDNA_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            HMM[SingleDNA], DnaHmmDirectoryFormat
        )

    def test_SingleRNA_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            HMM[SingleRNA], RnaHmmDirectoryFormat
        )

    def test_MultipleAmino_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            HMM[MultipleAmino], AminoHmmMultipleProfilesDirectoryFormat
        )

    def test_MultipleDNA_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            HMM[MultipleDNA], DnaHmmMultipleProfilesDirectoryFormat
        )

    def test_MultipleRNA_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            HMM[MultipleRNA], RnaHmmMultipleProfilesDirectoryFormat
        )

    def test_MultipleAminoPressed_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            HMM[MultipleAminoPressed], BaseHmmPressedDirFmt
        )

    def test_MultipleDNAPressed_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            HMM[MultipleDNAPressed], BaseHmmPressedDirFmt
        )

    def test_MultipleRNAPressed_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            HMM[MultipleRNAPressed], BaseHmmPressedDirFmt
        )
