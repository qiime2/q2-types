# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import collections
import itertools


FastqHeader = collections.namedtuple('FastqHeader', ['id', 'description'])


def _trim_id(id):
    return id.rsplit('/', 1)[0]


def _trim_description(desc):
    # The first number of ':' separated description is the read number
    if ':' in desc:
        desc = desc.split(':', 1)[1]
    return desc.rsplit('/', 1)[0]


def _record_to_fastq_header(record):
    tokens = record[0][1:].split(' ', maxsplit=1)
    if len(tokens) == 1:
        id, = tokens
        description = None
    else:
        id, description = tokens

    return FastqHeader(id=id, description=description)


class BarcodeSequenceFastqIterator(collections.abc.Iterable):
    def __init__(self, barcode_generator, sequence_generator,
                 ignore_description_mismatch=False):
        self.barcode_generator = barcode_generator
        self.sequence_generator = sequence_generator
        self.ignore_description_mismatch = ignore_description_mismatch

    def __iter__(self):
        # Adapted from q2-types
        for barcode_record, sequence_record in itertools.zip_longest(
                self.barcode_generator, self.sequence_generator):
            if barcode_record is None:
                raise ValueError('More sequences were provided than barcodes.')
            if sequence_record is None:
                raise ValueError('More barcodes were provided than sequences.')
            # The id or description fields may end with "/read-number", which
            # will differ between the sequence and barcode reads. Confirm that
            # they are identical up until the last /
            barcode_header = _record_to_fastq_header(barcode_record)
            sequence_header = _record_to_fastq_header(sequence_record)

            # confirm that the id fields are equal
            if _trim_id(barcode_header.id) != \
               _trim_id(sequence_header.id):
                raise ValueError(
                    'Mismatched sequence ids: %s and %s' %
                    (_trim_id(barcode_header.id),
                     _trim_id(sequence_header.id)))

            if not self.ignore_description_mismatch:
                # if a description field is present, confirm that they're equal
                if barcode_header.description is None and \
                   sequence_header.description is None:
                    pass
                elif barcode_header.description is None:
                    raise ValueError(
                        'Barcode header lines do not contain description '
                        'fields but sequence header lines do.')
                elif sequence_header.description is None:
                    raise ValueError(
                        'Sequence header lines do not contain description '
                        'fields but barcode header lines do.')
                elif _trim_description(barcode_header.description) != \
                        _trim_description(sequence_header.description):
                    raise ValueError(
                        'Mismatched sequence descriptions: %s and %s' %
                        (_trim_description(barcode_header.description),
                         _trim_description(sequence_header.description)))

            yield barcode_record, sequence_record


class BarcodePairedSequenceFastqIterator(collections.abc.Iterable):
    def __init__(self, barcode_generator, forward_generator,
                 reverse_generator, ignore_description_mismatch=False):
        self.barcode_generator = barcode_generator
        self.forward_generator = forward_generator
        self.reverse_generator = reverse_generator
        self.ignore_description_mismatch = ignore_description_mismatch

    def __iter__(self):
        # Adapted from q2-types
        for barcode_record, forward_record, reverse_record \
                in itertools.zip_longest(self.barcode_generator,
                                         self.forward_generator,
                                         self.reverse_generator):
            if barcode_record is None:
                raise ValueError('More sequences were provided than barcodes.')
            if forward_record is None:
                raise ValueError('More barcodes were provided than '
                                 'forward-sequences.')
            elif reverse_record is None:
                raise ValueError('More barcodes were provided than '
                                 'reverse-sequences.')
            # The id or description fields may end with "/read-number", which
            # will differ between the sequence and barcode reads. Confirm that
            # they are identical up until the last /
            barcode_header = _record_to_fastq_header(barcode_record)
            forward_header = _record_to_fastq_header(forward_record)
            reverse_header = _record_to_fastq_header(reverse_record)

            # confirm that the id fields are equal
            if not (_trim_id(barcode_header.id) ==
                    _trim_id(forward_header.id) ==
                    _trim_id(reverse_header.id)):
                raise ValueError(
                    'Mismatched sequence ids: %s, %s, and %s' %
                    (_trim_id(barcode_header.id),
                     _trim_id(forward_header.id),
                     _trim_id(reverse_header.id)))

            if not self.ignore_description_mismatch:
                # if a description field is present, confirm that they're equal
                if barcode_header.description is None and \
                   forward_header.description is None and \
                   reverse_header.description is None:
                    pass
                elif barcode_header.description is None:
                    raise ValueError(
                        'Barcode header lines do not contain description '
                        'fields but sequence header lines do.')
                elif forward_header.description is None:
                    raise ValueError(
                        'Forward-read header lines do not contain description '
                        'fields but barcode header lines do.')
                elif reverse_header.description is None:
                    raise ValueError(
                        'Reverse-read header lines do not contain description '
                        'fields but barcode header lines do.')
                elif not (_trim_description(barcode_header.description) ==
                          _trim_description(forward_header.description) ==
                          _trim_description(reverse_header.description)):
                    raise ValueError(
                        'Mismatched sequence descriptions: %s, %s, and %s' %
                        (_trim_description(barcode_header.description),
                         _trim_description(forward_header.description),
                         _trim_description(reverse_header.description)))

            yield barcode_record, forward_record, reverse_record
