# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import unittest

from qiime2.core.exceptions import ValidationError
from qiime2.plugin.testing import TestPluginBase

from q2_types.genome_data import (
    GenesDirectoryFormat, ProteinsDirectoryFormat, GFF3Format,
    LociDirectoryFormat, SeedOrthologDirFmt, OrthologFileFmt,
    OrthologAnnotationDirFmt, GenomeSequencesDirectoryFormat,
)


class TestFormats(TestPluginBase):
    package = 'q2_types.genome_data.tests'

    def test_ortholog_file_fmt(self):
        dirpath = self.get_data_path(
                'partitioned_orthologs/ortholog_1/1.emapper.seed_orthologs')
        fmt_obj = OrthologFileFmt(dirpath, mode='r')

        fmt_obj.validate()

    def test_seed_ortholog_dir_fmt_collection_file_name(self):
        dirpath = self.get_data_path('partitioned_orthologs/ortholog_1')
        fmt_obj = SeedOrthologDirFmt(dirpath, mode='r')

        for relpath, obj in fmt_obj.seed_orthologs.iter_views(OrthologFileFmt):
            obs = str(obj).split("/")[-1].split("/")[-1]

        exp = "1.emapper.seed_orthologs"

        self.assertEqual(obs, exp)

    def test_seed_ortholog_dir_fmt_good_validate(self):
        dirpath = self.get_data_path('partitioned_orthologs/ortholog_1')

        fmt_obj = SeedOrthologDirFmt(dirpath, mode='r')

        fmt_obj.validate()

    def test_seed_ortholog_dir_fmt_collection(self):
        dirpath = self.get_data_path('partitioned_orthologs/ortholog_1')
        fmt = SeedOrthologDirFmt(dirpath, mode='r')

        for relpath, obj in fmt.seed_orthologs.iter_views(OrthologFileFmt):
            self.assertIsInstance(obj=obj, cls=OrthologFileFmt)
            obj.validate()

    def test_genes_dirfmt_fa_with_suffix(self):
        dirpath = self.get_data_path('genes')
        fmt = GenesDirectoryFormat(dirpath, mode='r')

        fmt.validate()

    def test_proteins_dirfmt_fa_with_suffix(self):
        dirpath = self.get_data_path('proteins')
        fmt = ProteinsDirectoryFormat(dirpath, mode='r')

        fmt.validate()

    def test_gff_format_positive_with_suffix(self):
        filepath = self.get_data_path('loci/loci1.gff')
        fmt = GFF3Format(filepath, mode='r')

        fmt.validate()

    def test_loci_dirfmt_with_suffix(self):
        dirpath = self.get_data_path('loci')
        fmt = LociDirectoryFormat(dirpath, mode='r')

        fmt.validate()

    def test_genome_sequences_dirfmt(self):
        dirpath = self.get_data_path('genome-sequences')
        fmt = GenomeSequencesDirectoryFormat(dirpath, mode='r')

        fmt.validate()

    def test_gff_format_wrong_version(self):
        filepath = self.get_data_path('loci-invalid/loci-wrong-version.gff')
        with self.assertRaisesRegex(
                ValidationError, 'Invalid GFF format version: 2.'):
            GFF3Format(filepath, mode='r').validate()

    def test_gff_format_no_version(self):
        filepath = self.get_data_path('loci-invalid/loci-no-version.gff')
        with self.assertRaisesRegex(
                ValidationError, '"gff-version" directive is missing'):
            GFF3Format(filepath, mode='r').validate()

    def test_gff_format_empty_directive(self):
        filepath = self.get_data_path('loci-invalid/loci-directive-empty.gff')
        with self.assertRaisesRegex(
                ValidationError, 'directive entry on line 1 is incomplete.'):
            GFF3Format(filepath, mode='r').validate()

    def test_gff_format_lines_nonequal(self):
        filepath = self.get_data_path('loci-invalid/loci-lines-unequal.gff')
        with self.assertRaisesRegex(
                ValidationError, 'line 9 has an incorrect number of elements'):
            GFF3Format(filepath, mode='r').validate()

    def test_gff_format_empty_feature(self):
        filepath = self.get_data_path('loci-invalid/loci-empty-feature.gff')
        with self.assertRaisesRegex(
                ValidationError, r'empty feature found on line 9'):
            GFF3Format(filepath, mode='r').validate()

    def test_gff_format_invalid_char(self):
        filepath = self.get_data_path('loci-invalid/loci-invalid-char.gff')
        with self.assertRaisesRegex(
                ValidationError, r'unescaped ">". The ID on line 10 '
                                 r'was ">AL123456.3"'):
            GFF3Format(filepath, mode='r').validate()

    def test_gff_format_invalid_start_stop(self):
        filepath = self.get_data_path('loci-invalid/loci-invalid-start.gff')
        with self.assertRaisesRegex(
                ValidationError, 'position on line 9 is bigger than stop'):
            GFF3Format(filepath, mode='r').validate()

    def test_gff_format_negative_position(self):
        filepath = self.get_data_path('loci-invalid/loci-negative-start.gff')
        with self.assertRaisesRegex(
                ValidationError, 'positions on line 8 is incorrect'):
            GFF3Format(filepath, mode='r').validate()

    def test_gff_format_invalid_strand(self):
        filepath = self.get_data_path('loci-invalid/loci-invalid-strand.gff')
        with self.assertRaisesRegex(
                ValidationError, 'feature on line 10 is not one '
                                 'of the allowed'):
            GFF3Format(filepath, mode='r').validate()

    def test_gff_format_invalid_phase(self):
        filepath = self.get_data_path('loci-invalid/loci-invalid-phase.gff')
        with self.assertRaisesRegex(
                ValidationError, 'The phase on line 10 was 8.'):
            GFF3Format(filepath, mode='r').validate()

    def test_ortholog_annotation_dir_fmt_passing(self):
        dirpath = self.get_data_path('ortholog-annotation')
        fmt_obj = OrthologAnnotationDirFmt(dirpath, mode='r')
        fmt_obj.validate()

    def test_ortholog_annotation_dir_fmt_fails_extra_file(self):
        dirpath = self.get_data_path('ortholog-annotation-extra')
        fmt_obj = OrthologAnnotationDirFmt(dirpath, mode='r')

        with self.assertRaisesRegex(ValidationError, "Unrecognized file"):
            fmt_obj.validate()

    def test_ortholog_annotations_annot_dict(self):
        annotations = OrthologAnnotationDirFmt(
            self.get_data_path('ortholog-annotation-samples'), mode='r'
        )

        obs = annotations.annotation_dict()
        exp = {
            'test_output1':
                str(annotations.path / 'test_output1.emapper.annotations'),
            'test_output2':
                str(annotations.path / 'test_output2.emapper.annotations')
        }
        self.assertDictEqual(obs, exp)

        obs = annotations.annotation_dict(relative=True)
        exp = {
            'test_output1': 'test_output1.emapper.annotations',
            'test_output2': 'test_output2.emapper.annotations'
        }
        self.assertDictEqual(obs, exp)


if __name__ == '__main__':
    unittest.main()
