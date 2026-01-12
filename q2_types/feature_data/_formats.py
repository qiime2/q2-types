# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import re

import pandas as pd
import skbio

import qiime2.plugin.model as model
from qiime2.plugin import ValidationError
import qiime2


class TaxonomyFormat(model.TextFileFormat):
    """Legacy format for any 2+ column TSV file, with or without a header.

    This format has been superseded by taxonomy file formats explicitly with
    and without headers, `TSVTaxonomyFormat` and `HeaderlessTSVTaxonomyFormat`,
    respectively.

    This format remains in place for backwards-compatibility. Transformers are
    intentionally not hooked up to transform this format into the canonical
    .qza format (`TSVTaxonomyFormat`) to prevent users from importing data in
    this format. Transformers will remain in place to transform this format
    into in-memory Python objects (e.g. `pd.Series`) so that existing .qza
    files can still be loaded and processed.

    The only header recognized by this format is:

        Feature ID<tab>Taxon

    Optionally followed by other arbitrary columns.

    If this header isn't present, the format is assumed to be headerless.

    This format supports comment lines starting with #, and blank lines.

    """

    def sniff(self):
        with self.open() as fh:
            count = 0
            while count < 10:
                line = fh.readline()

                if line == '':
                    # EOF
                    break
                elif line.lstrip(' ') == '\n':
                    # Blank line
                    continue
                else:
                    cells = line.split('\t')
                    if len(cells) < 2:
                        return False
                    count += 1

            return False if count == 0 else True


TaxonomyDirectoryFormat = model.SingleFileDirectoryFormat(
    'TaxonomyDirectoryFormat', 'taxonomy.tsv', TaxonomyFormat)


class HeaderlessTSVTaxonomyFormat(TaxonomyFormat):
    """Format for a 2+ column TSV file without a header.

    This format supports comment lines starting with #, and blank lines.

    """
    pass


HeaderlessTSVTaxonomyDirectoryFormat = model.SingleFileDirectoryFormat(
    'HeaderlessTSVTaxonomyDirectoryFormat', 'taxonomy.tsv',
    HeaderlessTSVTaxonomyFormat)


class TSVTaxonomyFormat(model.TextFileFormat):
    """Format for a 2+ column TSV file with an expected minimal header.

    The only header recognized by this format is:

        Feature ID<tab>Taxon

    Optionally followed by other arbitrary columns.

    This format supports blank lines. The expected header must be the first
    non-blank line. In addition to the header, there must be at least one line
    of data.

    """
    HEADER = ['Feature ID', 'Taxon']

    def _check_n_records(self, n=None):
        with self.open() as fh:
            data_line_count = 0
            header = None

            file_ = enumerate(fh) if n is None else zip(range(n), fh)

            for i, line in file_:
                # Tracks line number for error reporting
                i = i + 1

                if line.lstrip(' ') == '\n':
                    # Blank line
                    continue

                cells = line.strip('\n').split('\t')

                if header is None:
                    if cells[:2] != self.HEADER:
                        raise ValidationError(
                            '%s must be the first two header values. The '
                            'first two header values provided are: %s (on '
                            'line %s).' % (self.HEADER, cells[:2], i))
                    header = cells
                else:
                    if len(cells) != len(header):
                        raise ValidationError(
                            'Number of values on line %s are not the same as '
                            'number of header values. Found %s values '
                            '(%s), expected %s.' % (i, len(cells), cells,
                                                    len(self.HEADER)))

                    data_line_count += 1

            if data_line_count == 0:
                raise ValidationError('No taxonomy records found, only blank '
                                      'lines and/or a header row.')

    def _validate_(self, level):
        self._check_n_records(n={'min': 10, 'max': None}[level])


TSVTaxonomyDirectoryFormat = model.SingleFileDirectoryFormat(
    'TSVTaxonomyDirectoryFormat', 'taxonomy.tsv', TSVTaxonomyFormat)


def _construct_validator_from_alphabet(alphabet_str):
    if alphabet_str:
        Validator = re.compile(fr'[{alphabet_str}]+\r?\n?')
        ValidationSet = frozenset(alphabet_str)
    else:
        Validator, ValidationSet = None, None
    return Validator, ValidationSet


class FASTAFormat(model.TextFileFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aligned = False
        self.alphabet = None

    def _validate_(self, level):
        FASTAValidator, ValidationSet = _construct_validator_from_alphabet(
            self.alphabet)
        self._validate_FASTA(level, FASTAValidator, ValidationSet)

    def _validate_line_lengths(
            self, seq_len, prev_seq_len, prev_seq_start_line):
        if prev_seq_len != seq_len:
            raise ValidationError('The sequence starting on line '
                                  f'{prev_seq_start_line} was length '
                                  f'{prev_seq_len}. All previous sequences '
                                  f'were length {seq_len}. All sequences must '
                                  'be the same length for AlignedFASTAFormat.')

    def _validate_FASTA(self, level, FASTAValidator=None, ValidationSet=None):
        last_line_was_ID = False
        ids = {}

        seq_len = 0
        prev_seq_len = 0
        prev_seq_start_line = 0

        level_map = {'min': 100, 'max': float('inf')}
        max_lines = level_map[level]

        with self.path.open('rb') as fh:
            try:
                first = fh.read(6)
                if first[:3] == b'\xEF\xBB\xBF':
                    first = first[3:]

                # Empty files should validate
                if first.strip() == b'':
                    return

                if first[0] != ord(b'>'):
                    raise ValidationError("First line of file is not a valid "
                                          "description. Descriptions must "
                                          "start with '>'")
                fh.seek(0)

                for line_number, line in enumerate(fh, 1):
                    line = line.strip()
                    if line_number >= max_lines:
                        return
                    line = line.decode('utf-8-sig')

                    if line.startswith('>'):
                        if FASTAValidator and ValidationSet:
                            if seq_len == 0:
                                seq_len = prev_seq_len

                            if self.aligned:
                                self._validate_line_lengths(
                                    seq_len, prev_seq_len, prev_seq_start_line)

                            prev_seq_len = 0
                            prev_seq_start_line = 0

                        if last_line_was_ID:
                            raise ValidationError('Multiple consecutive '
                                                  'descriptions starting on '
                                                  f'line {line_number-1!r}')

                        line = line.split()

                        if line[0] == '>':
                            if len(line) == 1:
                                raise ValidationError(
                                    f'Description on line {line_number} is '
                                    'missing an ID.')
                            else:
                                raise ValidationError(
                                    f'ID on line {line_number} starts with a '
                                    'space. IDs may not start with spaces')

                        if line[0] in ids:
                            raise ValidationError(
                                f'ID on line {line_number} is a duplicate of '
                                f'another ID on line {ids[line[0]]}.')

                        ids[line[0]] = line_number
                        last_line_was_ID = True

                    elif FASTAValidator and ValidationSet:
                        if re.fullmatch(FASTAValidator, line):
                            if prev_seq_start_line == 0:
                                prev_seq_start_line = line_number

                            prev_seq_len += len(line)
                            last_line_was_ID = False

                        else:
                            for position, character in enumerate(line):
                                if character not in ValidationSet:
                                    raise ValidationError(
                                        f"Invalid character '{character}' at "
                                        f"position {position} on line "
                                        f"{line_number} (does not match IUPAC "
                                        "characters for this sequence type). "
                                        "Allowed characters are "
                                        f"{self.alphabet}.")

                    else:
                        last_line_was_ID = False

            except UnicodeDecodeError as e:
                raise ValidationError(f'utf-8 cannot decode byte on line '
                                      f'{line_number}') from e

        if self.aligned:
            self._validate_line_lengths(
                seq_len, prev_seq_len, prev_seq_start_line)


class DNAFASTAFormat(FASTAFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alphabet = "ACGTRYKMSWBDHVN"


class AlignedFASTAFormatMixin:
    def _turn_into_alignment(self):
        self.aligned = True
        self.alphabet = self.alphabet + ".-"

    def _validate_line_lengths(
            self, seq_len, prev_seq_len, prev_seq_start_line):
        if prev_seq_len != seq_len:
            raise ValidationError('The sequence starting on line '
                                  f'{prev_seq_start_line} was length '
                                  f'{prev_seq_len}. All previous sequences '
                                  f'were length {seq_len}. All sequences must '
                                  'be the same length for AlignedFASTAFormat.')


DNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'DNASequencesDirectoryFormat', 'dna-sequences.fasta', DNAFASTAFormat)


class MixedCaseDNAFASTAFormat(DNAFASTAFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alphabet = self.alphabet + self.alphabet.lower()


MixedCaseDNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'MixedCaseDNASequencesDirectoryFormat', 'dna-sequences.fasta',
    MixedCaseDNAFASTAFormat)


class RNAFASTAFormat(FASTAFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alphabet = "ACGURYKMSWBDHVN"


RNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'RNASequencesDirectoryFormat', 'rna-sequences.fasta', RNAFASTAFormat)


class MixedCaseRNAFASTAFormat(RNAFASTAFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alphabet = self.alphabet + self.alphabet.lower()


MixedCaseRNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'MixedCaseRNASequencesDirectoryFormat', 'rna-sequences.fasta',
    MixedCaseRNAFASTAFormat)


class PairedDNASequencesDirectoryFormat(model.DirectoryFormat):
    left_dna_sequences = model.File('left-dna-sequences.fasta',
                                    format=DNAFASTAFormat)
    right_dna_sequences = model.File('right-dna-sequences.fasta',
                                     format=DNAFASTAFormat)


class PairedRNASequencesDirectoryFormat(model.DirectoryFormat):
    left_rna_sequences = model.File('left-rna-sequences.fasta',
                                    format=RNAFASTAFormat)
    right_rna_sequences = model.File('right-rna-sequences.fasta',
                                     format=RNAFASTAFormat)


class AlignedDNAFASTAFormat(AlignedFASTAFormatMixin, DNAFASTAFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super()._turn_into_alignment()


AlignedDNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'AlignedDNASequencesDirectoryFormat', 'aligned-dna-sequences.fasta',
    AlignedDNAFASTAFormat)


class MixedCaseAlignedDNAFASTAFormat(AlignedFASTAFormatMixin,
                                     MixedCaseDNAFASTAFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super()._turn_into_alignment()


MixedCaseAlignedDNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'MixedCaseAlignedDNASequencesDirectoryFormat',
    'aligned-dna-sequences.fasta', MixedCaseAlignedDNAFASTAFormat)


class AlignedRNAFASTAFormat(AlignedFASTAFormatMixin, RNAFASTAFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super()._turn_into_alignment()


AlignedRNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'AlignedRNASequencesDirectoryFormat', 'aligned-rna-sequences.fasta',
    AlignedRNAFASTAFormat)


class MixedCaseAlignedRNAFASTAFormat(AlignedFASTAFormatMixin,
                                     MixedCaseRNAFASTAFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super()._turn_into_alignment()


MixedCaseAlignedRNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'MixedCaseAlignedRNASequencesDirectoryFormat',
    'aligned-rna-sequences.fasta', MixedCaseAlignedRNAFASTAFormat)


class DifferentialFormat(model.TextFileFormat):
    def validate(self, *args):
        try:
            md = qiime2.Metadata.load(str(self))
        except qiime2.metadata.MetadataFileError as md_exc:
            raise ValidationError(md_exc) from md_exc

        if md.column_count == 0:
            raise ValidationError('Format must contain at least 1 column')

        filtered_md = md.filter_columns(column_type='numeric')
        if filtered_md.column_count != md.column_count:
            raise ValidationError('Must only contain numeric values.')


DifferentialDirectoryFormat = model.SingleFileDirectoryFormat(
    'DifferentialDirectoryFormat', 'differentials.tsv', DifferentialFormat)


class ProteinFASTAFormat(FASTAFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ*"


ProteinSequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'ProteinSequencesDirectoryFormat',
    'protein-sequences.fasta',
    ProteinFASTAFormat)


class MixedCaseProteinFASTAFormat(ProteinFASTAFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lower_case = "abcdefghijklmnopqrstuvwxyz"
        self.alphabet = self.alphabet + lower_case


MixedCaseProteinSequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'MixedCaseProteinSequencesDirectoryFormat',
    'protein-sequences.fasta',
    MixedCaseProteinFASTAFormat)


class AlignedProteinFASTAFormat(AlignedFASTAFormatMixin, ProteinFASTAFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super()._turn_into_alignment()


AlignedProteinSequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'AlignedProteinSequencesDirectoryFormat',
    'aligned-protein-sequences.fasta',
    AlignedProteinFASTAFormat)


class MixedCaseAlignedProteinFASTAFormat(
    AlignedFASTAFormatMixin, MixedCaseProteinFASTAFormat
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super()._turn_into_alignment()


MixedCaseAlignedProteinSequencesDirectoryFormat = (
    model.SingleFileDirectoryFormat(
        'MixedCaseAlignedProteinSequencesDirectoryFormat',
        'aligned-protein-sequences.fasta',
        MixedCaseAlignedProteinFASTAFormat
    )
)


class BLAST6Format(model.TextFileFormat):
    def validate(self, *args):
        try:
            _ = skbio.read(str(self), format='blast+6', into=pd.DataFrame,
                           default_columns=True)
        except pd.errors.EmptyDataError:
            raise ValidationError('BLAST6 file is empty.')
        except ValueError:
            raise ValidationError('Invalid BLAST6 format.')


BLAST6DirectoryFormat = model.SingleFileDirectoryFormat(
    'BLAST6DirectoryFormat', 'blast6.tsv', BLAST6Format)


class SequenceCharacteristicsFormat(model.TextFileFormat):
    """
    Format for a TSV file with information about sequences like length of a
    feature. The first column contains feature identifiers and is followed by
    other optional columns.

    The file cannot be empty and must have at least two columns.

    Validation for additional columns can be added with a semantic validator
    tied to a property. For example the "validate_seq_char_len" validator for
    "FeatureData[SequenceCharacteristics % Properties("length")]"
    adds validation for a numerical column called "length".
    """

    def validate(self, n_records=None):
        try:
            data = pd.read_csv(str(self), sep='\t', index_col=0)
        except pd.errors.EmptyDataError:
            raise ValidationError('File cannot be empty.')

        if not data.columns.any():
            raise ValidationError('File needs to have at least two columns.')


SequenceCharacteristicsDirectoryFormat = model.SingleFileDirectoryFormat(
    "SequenceCharacteristicsDirectoryFormat",
    "sequence_characteristics.tsv", SequenceCharacteristicsFormat
)
