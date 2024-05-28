# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import re
import gzip
import itertools
import warnings
from typing import List

import qiime2.plugin.model as model
from qiime2.plugin import ValidationError

# These classes and their helper functions are located in this module to avoid
# circular imports.


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


class FastqGzFormat(model.BinaryFileFormat):
    """
    A gzipped fastq file.

    """

    def _check_n_records(self, n=None):
        with gzip.open(str(self), mode='rt', encoding='ascii') as fh:
            zipper = itertools.zip_longest(*[fh] * 4)
            if n is None:
                file_ = enumerate(zipper)
            else:
                file_ = zip(range(1, n), zipper)
            for i, record in file_:
                header, seq, sep, qual = record

                if not header.startswith('@'):
                    raise ValidationError('Header on line %d is not FASTQ, '
                                          'records may be misaligned' %
                                          (i * 4 + 1))

                if seq is None or seq == '\n':
                    raise ValidationError('Missing sequence for record '
                                          'beginning on line %d'
                                          % (i * 4 + 1))
                elif not seq.isupper():
                    raise ValidationError('Lowercase case sequence on line %d'
                                          % (i * 4 + 2))

                if sep is None:
                    raise ValidationError('Missing separator for record '
                                          'beginning on line %d'
                                          % (i * 4 + 1))
                elif not sep.startswith('+'):
                    raise ValidationError('Invalid separator on line %d'
                                          % (i * 4 + 3))

                if qual is None:
                    raise ValidationError('Missing quality for record '
                                          'beginning on line %d'
                                          % (i * 4 + 1))
                elif len(qual) != len(seq):
                    raise ValidationError('Quality score length doesn\'t '
                                          'match sequence length for record '
                                          'beginning on line %d'
                                          % (i * 4 + 1))

    def _validate_(self, level):
        with self.open() as fh:
            if fh.peek(2)[:2] != b'\x1f\x8b':
                raise ValidationError('File is uncompressed')

        record_count_map = {'min': 5, 'max': None}
        self._check_n_records(record_count_map[level])


def _validate_num_partitions(
        num_samples: int, num_partitions: int, sample_type: str = "sample"
) -> int:

    if num_partitions is None:
        return num_samples
    elif num_partitions > num_samples:
        warnings.warn(
            "You have requested a number of partitions "
            f"'{num_partitions}' that is greater than your number "
            f"of {sample_type}s '{num_samples}.' Your data will be "
            f"partitioned by {sample_type} into '{num_samples}' "
            "partitions."
        )
        return num_samples
    else:
        return num_partitions


def _validate_mag_ids(
    num_partitions: int, num_mags: int, mags_all: List[tuple]
):
    # If num_partitions == num_mags and MAG ids are not unique
    # the output will be missing these duplicated-id MAGs.
    # While this is technically impossible since
    # MAGs should have unique IDs by construction, it could still happen that a
    # used imports MAGs with non-unique IDs. In such case this test would be
    # useful.

    if num_partitions == num_mags:
        mag_ids = [mag_id[1] for mag_id in mags_all]
        duplicates = [
            mag_id for mag_id in mag_ids if mag_ids.count(mag_id) > 1
        ]
        if len(duplicates) > 0:
            raise ValueError(
                "MAG IDs are not unique. "
                "They must be unique in order to output all partitions "
                "correctly. Printing duplicate MAG IDs: "
                f"{set(duplicates)}"
            )