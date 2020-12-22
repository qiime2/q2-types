# ----------------------------------------------------------------------------
# Copyright (c) 2016-2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import itertools
import re

import qiime2.plugin.model as model
import skbio
from qiime2.plugin import ValidationError
import qiime2

from ..plugin_setup import plugin


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


class DNAFASTAFormat(model.TextFileFormat):
    def _validate_(self, level):
        FASTADNAValidator = re.compile(r'[ACGTURYKMSWBDHVN]+\r?\n?')
        ValidationSet = frozenset(('A', 'C', 'G', 'T', 'U', 'R', 'Y', 'K', 'M',
                                   'S', 'W', 'B', 'D', 'H', 'V', 'N'))

        _validate_DNAFASTAFormats(self, FASTADNAValidator, ValidationSet,
                                  level)


DNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'DNASequencesDirectoryFormat', 'dna-sequences.fasta', DNAFASTAFormat)


class PairedDNASequencesDirectoryFormat(model.DirectoryFormat):
    left_dna_sequences = model.File('left-dna-sequences.fasta',
                                    format=DNAFASTAFormat)
    right_dna_sequences = model.File('right-dna-sequences.fasta',
                                     format=DNAFASTAFormat)


class AlignedDNAFASTAFormat(model.TextFileFormat):
    def _validate_(self, level):
        FASTADNAValidator = re.compile(r'[ACGTURYKMSWBDHVN.-]+\r?\n?')
        ValidationSet = frozenset(('A', 'C', 'G', 'T', 'U', 'R', 'Y', 'K', 'M',
                                   'S', 'W', 'B', 'D', 'H', 'V', 'N', '.',
                                   '-'))

        _validate_DNAFASTAFormats(self, FASTADNAValidator, ValidationSet,
                                  level, True)


AlignedDNASequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'AlignedDNASequencesDirectoryFormat', 'aligned-dna-sequences.fasta',
    AlignedDNAFASTAFormat)


def _validate_DNAFASTAFormats(fmt, FASTADNAValidator, ValidationSet, level,
                              aligned=False):
    last_line_was_ID = False
    ids = {}

    seq_len = 0
    prev_seq_len = 0
    prev_seq_start_line = 0

    level_map = {'min': 100, 'max': float('inf')}
    max_lines = level_map[level]

    with fmt.path.open('rb') as fh:
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
                if line_number >= max_lines:
                    return
                line = line.decode('utf-8-sig')

                if line.startswith('>'):
                    if seq_len == 0:
                        seq_len = prev_seq_len

                    if aligned:
                        _validate_line_lengths(seq_len, prev_seq_len,
                                               prev_seq_start_line)

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

                elif re.fullmatch(FASTADNAValidator, line):
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
                                "characters for a DNA sequence).")

        except UnicodeDecodeError as e:
            raise ValidationError(f'utf-8 cannot decode byte on line '
                                  f'{line_number}') from e

    if aligned:
        _validate_line_lengths(seq_len, prev_seq_len, prev_seq_start_line)


def _validate_line_lengths(seq_len, prev_seq_len, prev_seq_start_line):
    if prev_seq_len != seq_len:
        raise ValidationError('The sequence starting on line '
                              f'{prev_seq_start_line} was length '
                              f'{prev_seq_len}. All previous sequences were '
                              f'length {seq_len}. All sequences must be the '
                              'same length for AlignedDNAFASTAFormat.')


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


class ProteinFASTAFormat(model.TextFileFormat):
    def _validate_(self, level):
        record_count_map = {'min': 5, 'max': None}
        self._validate(record_count_map[level])

    def _validate(self, n_records=None):
        # read in using skbio and iterate over the contents -
        # ValueErrors will be raised for wrong records
        generator = self._read_protein_fasta(str(self))
        if n_records is not None:
            generator = itertools.islice(generator, n_records)
        [x for x in generator]

    def _read_protein_fasta(self, path):
        return skbio.read(path, format='fasta', constructor=skbio.Protein)


ProteinSequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'ProteinSequencesDirectoryFormat',
    'protein-sequences.fasta',
    ProteinFASTAFormat)


class AlignedProteinFASTAFormat(model.TextFileFormat):
    def _validate_(self, level):
        record_count_map = {'min': 5, 'max': None}
        self._validate(record_count_map[level])

    def _validate(self, n_records=None):
        # read in using skbio and iterate over the contents -
        # ValueErrors will be raised for wrong records
        generator = self._read_protein_alignment_fasta(str(self))
        if n_records is not None:
            generator = itertools.islice(generator, n_records)
        [x for x in generator]

    def _read_protein_fasta(self, path):
        return skbio.read(path, format='fasta',
                          constructor=skbio.Protein, into=skbio.TabularMSA)


AlignedProteinSequencesDirectoryFormat = model.SingleFileDirectoryFormat(
    'AlignedProteinSequencesDirectoryFormat',
    'aligned-protein-sequences.fasta',
    AlignedProteinFASTAFormat)


plugin.register_formats(
    TSVTaxonomyFormat, TSVTaxonomyDirectoryFormat,
    HeaderlessTSVTaxonomyFormat, HeaderlessTSVTaxonomyDirectoryFormat,
    TaxonomyFormat, TaxonomyDirectoryFormat, DNAFASTAFormat,
    DNASequencesDirectoryFormat, PairedDNASequencesDirectoryFormat,
    AlignedDNAFASTAFormat, AlignedDNASequencesDirectoryFormat,
    DifferentialFormat, DifferentialDirectoryFormat, ProteinFASTAFormat,
    AlignedProteinFASTAFormat, ProteinSequencesDirectoryFormat,
    AlignedProteinSequencesDirectoryFormat,
)
