# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin.testing import TestPluginBase

from q2_types.reference_db._format import (
    DiamondDatabaseDirFmt, EggnogRefDirFmt, NCBITaxonomyDirFmt,
    EggnogProteinSequencesDirFmt, HmmerDirFmt
)
from q2_types.reference_db._type import (
    ReferenceDB, Diamond, Eggnog, NCBITaxonomy, EggnogProteinSequences,
    HMMER
)


class TestReferenceType(TestPluginBase):
    package = 'q2_types.reference_db.tests'

    def test_ref_db_registration(self):
        self.assertRegisteredSemanticType(ReferenceDB)

    def test_diamond_registration(self):
        self.assertRegisteredSemanticType(Diamond)

    def test_diamond_semantic_type_registered_to_dmnd_db_dir_fmt(self):
        self.assertSemanticTypeRegisteredToFormat(
                ReferenceDB[Diamond],
                DiamondDatabaseDirFmt)

    def test_eggnog_registration(self):
        self.assertRegisteredSemanticType(Eggnog)

    def test_eggnog_semantic_type_registered_to_eggnog_dir_fmt(self):
        self.assertSemanticTypeRegisteredToFormat(
                ReferenceDB[Eggnog],
                EggnogRefDirFmt)

    def test_ncbi_registration(self):
        self.assertRegisteredSemanticType(NCBITaxonomy)

    def test_ncbi_semantic_type_registered_to_eggnog_dir_fmt(self):
        self.assertSemanticTypeRegisteredToFormat(
                ReferenceDB[NCBITaxonomy],
                NCBITaxonomyDirFmt)

    def test_EggnogProteinSequences_registration(self):
        self.assertRegisteredSemanticType(EggnogProteinSequences)

    def test_EggnogProteinSequences_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
                ReferenceDB[EggnogProteinSequences],
                EggnogProteinSequencesDirFmt)

    def test_hmmer_registration(self):
        self.assertRegisteredSemanticType(HMMER)

    def test_HMMER_semantic_type_registered_to_DirFmt(self):
        self.assertSemanticTypeRegisteredToFormat(
            ReferenceDB[HMMER], HmmerDirFmt
        )
