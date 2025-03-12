# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import re

import qiime2.plugin.model as model
from qiime2.plugin import ValidationError

from q2_types._util import FileDictMixin
from q2_types.feature_data import DNAFASTAFormat, ProteinFASTAFormat


class OrthologFileFmt(model.TextFileFormat):
    def _validate_(self, level):
        pass


class GenesDirectoryFormat(model.DirectoryFormat, FileDictMixin):
    pathspec = r'.+\.(fa|fna|fasta)$'
    genes = model.FileCollection(pathspec, format=DNAFASTAFormat)

    @genes.set_path_maker
    def genes_path_maker(self, genome_id):
        return '%s.fasta' % genome_id


class ProteinsDirectoryFormat(model.DirectoryFormat, FileDictMixin):
    pathspec = r'.+\.(fa|faa|fasta)$'
    proteins = model.FileCollection(pathspec, format=ProteinFASTAFormat)

    @proteins.set_path_maker
    def proteins_path_maker(self, genome_id):
        return '%s.fasta' % genome_id


class GFF3Format(model.TextFileFormat):
    """
    Generic Feature Format Version 3 (GFF3) spec:
    https://github.com/The-Sequence-Ontology/Specifications/blob/master/gff3.md
    NCBI modifications to the above:
    https://www.ncbi.nlm.nih.gov/datasets/docs/reference-docs/file-formats/about-ncbi-gff3/
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.directives = {}
        self.directives_unofficial = {}

    def _update_directives(self, line, line_number):
        directive = line[2:].split(maxsplit=1)
        if len(directive) <= 1:
            raise ValidationError(
                f'GFF directive entry on line {line_number} is incomplete.'
            )
        elif line.startswith('##'):
            self.directives.update({directive[0]: directive[1]})
        elif line.startswith('#!'):
            self.directives_unofficial.update({directive[0]: directive[1]})

    def _validate_directives(self) -> bool:
        if 'gff-version' not in self.directives.keys():
            raise ValidationError(
                '"gff-version" directive is missing from the file headers.'
            )
        if not self.directives['gff-version'].startswith('3'):
            raise ValidationError(
                f'Invalid GFF format version: '
                f'{self.directives["gff-version"]}. Only version 3 '
                f'is supported.'
            )
        return True

    @staticmethod
    def _validate_feature_line(line, line_number):
        line_elements = line.split('\t')
        line_len = len(line_elements)
        if line_len != 9:
            raise ValidationError(
                f'The entry on line {line_number} '
                f'has an incorrect number of elements. All '
                f'entries need to have 9 elements in a valid '
                f'GFF3 file.'
            )

        # 1: seqid, 2: source, 3: type, 4: start, 5:stop,
        # 6: score, 7:strand, 8:phase, 9:attributes
        if any([True for x in line_elements
                if x in {"", " "}]):
            raise ValidationError(
                f'An empty feature found on line '
                f'{line_number}. Empty features should be '
                f'denoted with a ".".'
            )

        if str(line_elements[0]).startswith('>'):
            raise ValidationError(
                'Landmark IDs must not start with an unescaped'
                f' ">". The ID on line {line_number} was '
                f'"{line_elements[0]}".'
            )

        if int(line_elements[3]) > int(line_elements[4]):
            raise ValidationError(
                f'Start position on line {line_number} '
                f'is bigger than stop position.'
            )

        if any([int(line_elements[3]) <= 0,
                int(line_elements[4]) <= 0]):
            raise ValidationError(
                'Coordinates should be expressed as '
                f'positive,  1-based integers. At least '
                f'one of the positions on line {line_number} '
                f'is incorrect.'
            )

        if str(line_elements[6]) not in ['+', '-', '?', '.']:
            raise ValidationError(
                f'Strand of the feature on line {line_number} '
                f'is not one of the allowed symbols (+-.?).'
            )

        if str(line_elements[2]) == 'CDS' and \
                str(line_elements[7]) not in ['0', '1', '2']:
            raise ValidationError(
                'Features of type CDS require the phase to '
                'be one of: 0, 1, 3. The phase on line '
                f'{line_number} was {line_elements[7]}.'
            )

    def _validate_(self, level):
        level_map = {'min': 100, 'max': float('inf')}
        max_lines = level_map[level]

        directives_validated = False

        with self.path.open('rb') as fh:
            try:
                for line_number, line in enumerate(fh, 1):
                    line = line.strip()
                    if line_number >= max_lines:
                        return
                    line = line.decode('utf-8-sig')

                    if line.startswith(("##", "#!")) and not self.directives:
                        self._update_directives(line, line_number)
                    elif line.startswith('#'):
                        continue
                    else:
                        if not directives_validated:
                            directives_validated = self._validate_directives()
                        self._validate_feature_line(line, line_number)

            except UnicodeDecodeError as e:
                raise ValidationError(f'utf-8 cannot decode byte on line '
                                      f'{line_number}') from e


class LociDirectoryFormat(model.DirectoryFormat, FileDictMixin):
    pathspec = r'.+\.gff$'
    loci = model.FileCollection(pathspec, format=GFF3Format)

    @loci.set_path_maker
    def loci_path_maker(self, genome_id):
        return '%s.gff' % genome_id


class GenomeSequencesDirectoryFormat(model.DirectoryFormat, FileDictMixin):
    pathspec = r'.+\.(fasta|fa)$'
    genomes = model.FileCollection(pathspec, format=DNAFASTAFormat)

    @genomes.set_path_maker
    def genomes_path_maker(self, genome_id):
        return '%s.fasta' % genome_id


class SeedOrthologDirFmt(model.DirectoryFormat):
    seed_orthologs = model.FileCollection(r'.*\..*\.seed_orthologs',
                                          format=OrthologFileFmt,
                                          optional=False)

    @seed_orthologs.set_path_maker
    def seed_ortholog_pathmaker(self, sample_name):
        return str(sample_name.split(sep=".")[0] + ".seed_orthologs")


class OrthologAnnotationDirFmt(model.DirectoryFormat):
    pathspec = r'.+\.annotations'
    annotations = model.FileCollection(pathspec, format=OrthologFileFmt)

    @annotations.set_path_maker
    def annotations_path_maker(self, file_name):
        return file_name.split(sep="_")[0]

    def annotation_dict(self, relative=False) -> dict:
        ids = {}
        for path in self.path.iterdir():
            if re.compile(self.pathspec).match(path.name):
                _id = re.sub('.emapper$', '', path.stem)
                absolute_path = path.absolute()
                if relative:
                    ids[_id] = str(
                        absolute_path.relative_to(self.path.absolute())
                    )
                else:
                    ids[_id] = str(absolute_path)

        return dict(sorted(ids.items()))
