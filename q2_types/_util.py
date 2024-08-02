# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import gzip
import itertools
import warnings
from typing import List

import skbio
import pandas as pd

import qiime2.plugin.model as model
from qiime2.plugin import ValidationError


def read_from_fasta(path, constructor=skbio.DNA, lowercase=False):
    return skbio.read(path, format='fasta', constructor=constructor,
                      lowercase=lowercase)


def fasta_to_series(ff, constructor=skbio.DNA, lowercase=False):
    data = {}
    for sequence in read_from_fasta(str(ff), constructor,
                                    lowercase=lowercase):
        id_ = sequence.metadata['id']
        # this may no longer do anything b/c of format validation, but leaving
        # here as a safeguard & we may want to examine/address later
        # relevant PR associated with this change:
        # https://github.com/qiime2/q2-types/pull/335
        if id_ in data:
            raise ValueError("FASTA format sequence IDs must be unique. The "
                             "following ID was found more than once: %s."
                             % id_)
        data[id_] = sequence
    return pd.Series(data)


# These classes and their helper functions are located in this module to avoid
# circular imports.
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
