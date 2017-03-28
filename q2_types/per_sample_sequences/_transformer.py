# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import warnings
import collections

import skbio
import yaml
import pandas as pd

from ..plugin_setup import plugin
from . import (SingleLanePerSampleSingleEndFastqDirFmt, FastqManifestFormat,
               SingleLanePerSamplePairedEndFastqDirFmt, FastqGzFormat,
               CasavaOneEightSingleLanePerSampleDirFmt, YamlFormat,
               SingleEndFastqManifestPhred33, SingleEndFastqManifestPhred64,
               PairedEndFastqManifestPhred33, PairedEndFastqManifestPhred64)


class PerSampleDNAIterators(dict):
    pass


class PerSamplePairedDNAIterators(dict):
    pass


# Transformers
@plugin.register_transformer
def _1(dirfmt: SingleLanePerSampleSingleEndFastqDirFmt) \
        -> PerSampleDNAIterators:
    result = PerSampleDNAIterators()
    # ensure that dirfmt stays in scope as long as result does
    result.__dirfmt = dirfmt
    fh = iter(dirfmt.manifest.view(FastqManifestFormat).open())
    next(fh)
    for line in fh:
        sample_id, filename, _ = line.split(',')
        filepath = str(dirfmt.path / filename)
        result[sample_id] = skbio.io.read(filepath, format='fastq',
                                          constructor=skbio.DNA)
    return result


@plugin.register_transformer
def _2(dirfmt: SingleLanePerSamplePairedEndFastqDirFmt) \
        -> PerSamplePairedDNAIterators:
    fh = iter(dirfmt.manifest.view(FastqManifestFormat).open())
    next(fh)
    forward_paths = {}
    reverse_paths = {}
    for line in fh:
        sample_id, filename, direction = line.strip().split(',')
        filepath = str(dirfmt.path / filename)
        seqs = skbio.io.read(filepath, format='fastq',
                             constructor=skbio.DNA)

        if direction == 'forward':
            forward_paths[sample_id] = seqs
        else:
            reverse_paths[sample_id] = seqs

    result = PerSamplePairedDNAIterators()
    # ensure that dirfmt stays in scope as long as result does
    result.__dirfmt = dirfmt
    for sample_id in forward_paths:
        result[sample_id] = forward_paths[sample_id], reverse_paths[sample_id]
    return result


def _single_lane_per_sample_fastq_helper(dirfmt, output_cls):
    result = output_cls()
    manifest = FastqManifestFormat()
    manifest_fh = manifest.open()
    manifest_fh.write('sample-id,filename,direction\n')
    directions = ['forward', 'reverse']
    for path, view in dirfmt.sequences.iter_views(FastqGzFormat):

        sample_id, barcode_id, lane_number, read_number, _ = \
            str(path).replace('.fastq.gz', '').rsplit('_', maxsplit=4)
        read_number = int(read_number[1:])
        lane_number = int(lane_number[1:])
        direction = directions[read_number - 1]
        result.sequences.write_data(view, FastqGzFormat, sample_id=sample_id,
                                    barcode_id=barcode_id,
                                    lane_number=lane_number,
                                    read_number=read_number)
        manifest_fh.write('%s,%s,%s\n' % (sample_id, path, direction))

    manifest_fh.close()
    result.manifest.write_data(manifest, FastqManifestFormat)

    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, YamlFormat)

    return result


@plugin.register_transformer
def _3(dirfmt: CasavaOneEightSingleLanePerSampleDirFmt) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    return _single_lane_per_sample_fastq_helper(
        dirfmt, SingleLanePerSampleSingleEndFastqDirFmt)


@plugin.register_transformer
def _4(dirfmt: CasavaOneEightSingleLanePerSampleDirFmt) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    return _single_lane_per_sample_fastq_helper(
        dirfmt, SingleLanePerSamplePairedEndFastqDirFmt)


@plugin.register_transformer
def _5(dirfmt: SingleLanePerSamplePairedEndFastqDirFmt) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    result = SingleLanePerSampleSingleEndFastqDirFmt()
    manifest = FastqManifestFormat()

    with manifest.open() as manifest_fh:
        with dirfmt.manifest.view(FastqManifestFormat).open() as fh:
            iterator = iter(fh)
            manifest_fh.write(next(iterator))  # header line
            for line in iterator:
                _, relpath, direction = line.rstrip().split(',')
                if direction == 'forward':
                    manifest_fh.write(line)
                    os.link(str(dirfmt.path / relpath),
                            str(result.path / relpath))

    result.manifest.write_data(manifest, FastqManifestFormat)

    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, YamlFormat)

    return result


def _parse_and_validate_manifest(manifest_fh, single_end):
    try:
        manifest = pd.read_csv(manifest_fh, comment='#', header=0,
                               skip_blank_lines=True, dtype=object)
    except pd.io.common.CParserError as e:
        raise ValueError('All records in manifest must contain '
                         'exactly three comma-separated fields, but it '
                         'that appears at least one record contains more. '
                         'Original error message:\n %s' % str(e))

    _validate_header(manifest)

    for idx in manifest.index:
        record = manifest.loc[idx]
        if record.isnull().any():
            raise ValueError('All records in manifest must contain '
                             'exactly three comma-separated fields, but at '
                             'least one contains fewer. The data in that '
                             'record is: %s' % ','.join(map(str, record)))
        record['absolute-filepath'] = \
            os.path.expandvars(record['absolute-filepath'])
        _validate_path(record['absolute-filepath'])
        _validate_direction(record['direction'])

    if single_end:
        _validate_single_end_fastq_manifest_directions(manifest)
    else:
        _validate_paired_end_fastq_manifest_directions(manifest)

    return manifest


def _get_fastq_fn(sample_id, barcode_id, direction):
    direction_to_read_number = {'forward': 1, 'reverse': 2}
    return '%s_%d_L001_R%d_001.fastq.gz' % \
           (sample_id, barcode_id,
            direction_to_read_number[direction])


def _write_phred64_to_phred33(phred64_path, phred33_path):
    with open(phred64_path, 'rb') as phred64_fh, \
         open(phred33_path, 'wb') as phred33_fh:
        for seq in skbio.io.read(phred64_fh, format='fastq',
                                 variant='illumina1.3'):
            skbio.io.write(seq, into=phred33_fh,
                           format='fastq',
                           variant='illumina1.8',
                           compression='gzip')


def _validate_header(manifest):
    header = manifest.columns
    if len(header) != 3:
        raise ValueError('manifest header must contain exactly three columns.')
    expected_header = ['sample-id', 'absolute-filepath', 'direction']
    for i, is_correct in enumerate(header == expected_header):
        if not is_correct:
            raise ValueError('Expected manifest header column "%s" but '
                             'observed "%s".'
                             % (expected_header[i], header[i]))


def _validate_path(path):
    if not os.path.isabs(path):
        raise ValueError('All paths provided in manifest must be absolute '
                         'but observed: %s' % path)
    if not os.path.exists(path):
        raise FileNotFoundError(
            'A path specified in the manifest does not exist: '
            '%s' % path)


def _validate_direction(direction):
    if direction not in {'forward', 'reverse'}:
        raise ValueError('Direction can only be "forward" or '
                         '"reverse", but observed: %s' % direction)


def _duplicated_ids(sample_ids):
    counts = collections.Counter(sample_ids).most_common()
    if len(counts) == 0 or counts[0][1] == 1:
        # if there were no sample ids provided, or the most frequent sample id
        # was only observed once, there are no duplicates
        return []
    else:
        return [e[0] for e in counts if e[1] > 1]


def _validate_single_end_fastq_manifest_directions(manifest):
    directions = set(manifest['direction'])
    if len(directions) > 1:
        raise ValueError('Manifest for single-end reads can '
                         'contain only forward or reverse reads '
                         'but the following directions were observed: %s'
                         % ', '.join(directions))

    duplicated_ids = _duplicated_ids(manifest['sample-id'])
    if len(duplicated_ids) > 0:
        raise ValueError('Each sample id can only appear one time in a '
                         'manifest for single-end reads, but the following '
                         'sample ids were observed more than once: '
                         '%s' % ', '.join(duplicated_ids))


def _validate_paired_end_fastq_manifest_directions(manifest):
    forward_direction_sample_ids = []
    reverse_direction_sample_ids = []

    for _, sample_id, _, direction in manifest.itertuples():
        if direction == 'forward':
            forward_direction_sample_ids.append(sample_id)
        elif direction == 'reverse':
            reverse_direction_sample_ids.append(sample_id)
        else:
            raise ValueError('Directions can only be "forward" and '
                             '"reverse", but observed: %s' % direction)

    duplicated_ids_forward = _duplicated_ids(forward_direction_sample_ids)
    if len(duplicated_ids_forward) > 0:
        raise ValueError('Each sample id can have only one forward read '
                         'record in a paired-end read manifest, but the '
                         'following sample ids were associated with more '
                         'than one forward read record: '
                         '%s' % ', '.join(duplicated_ids_forward))

    duplicated_ids_reverse = _duplicated_ids(reverse_direction_sample_ids)
    if len(duplicated_ids_reverse) > 0:
        raise ValueError('Each sample id can have only one reverse read '
                         'record in a paired-end read manifest, but the '
                         'following sample ids were associated with more '
                         'than one reverse read record: '
                         '%s' % ', '.join(duplicated_ids_reverse))

    if sorted(forward_direction_sample_ids) != \
       sorted(reverse_direction_sample_ids):

        forward_but_no_reverse = set(forward_direction_sample_ids) - \
            set(reverse_direction_sample_ids)

        reverse_but_no_forward = set(reverse_direction_sample_ids) - \
            set(forward_direction_sample_ids)

        if len(forward_but_no_reverse) > 0:
            raise ValueError('Forward and reverse reads must be provided '
                             'exactly one time each for each sample. The '
                             'following samples had forward but not '
                             'reverse read fastq files: %s'
                             % ', '.join(forward_but_no_reverse))
        else:
            raise ValueError('Forward and reverse reads must be provided '
                             'exactly one time each for each sample. The '
                             'following samples had reverse but not '
                             'forward read fastq files: %s'
                             % ', '.join(reverse_but_no_forward))


def _fastq_manifest_helper(fmt, fastq_copy_fn, single_end):
    input_manifest = _parse_and_validate_manifest(fmt.open(),
                                                  single_end=single_end)
    if single_end:
        result = SingleLanePerSampleSingleEndFastqDirFmt()
    else:
        result = SingleLanePerSamplePairedEndFastqDirFmt()

    output_manifest_data = []
    for idx, sample_id, input_fastq_fp, direction in \
            input_manifest.itertuples():
        output_fastq_fn = \
            _get_fastq_fn(sample_id, idx, direction)
        output_manifest_data.append([sample_id, output_fastq_fn, direction])
        output_fastq_fp = str(result.path / output_fastq_fn)
        fastq_copy_fn(input_fastq_fp, output_fastq_fp)

    output_manifest = FastqManifestFormat()
    output_manifest_df = pd.DataFrame(
        output_manifest_data, columns=['sample-id', 'filename', 'direction'])
    output_manifest_df.to_csv(str(output_manifest), index=False)
    result.manifest.write_data(output_manifest, FastqManifestFormat)

    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, YamlFormat)

    return result


_phred64_warning = ('Importing of PHRED 64 data is slow as it is converted '
                    'internally to PHRED 33. Working with the imported data '
                    'will not be slower than working with PHRED 33 data.')


@plugin.register_transformer
def _6(fmt: SingleEndFastqManifestPhred33) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    return _fastq_manifest_helper(fmt, os.link, single_end=True)


@plugin.register_transformer
def _7(fmt: SingleEndFastqManifestPhred64) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    warnings.warn(_phred64_warning)
    return _fastq_manifest_helper(fmt, _write_phred64_to_phred33,
                                  single_end=True)


@plugin.register_transformer
def _8(fmt: PairedEndFastqManifestPhred33) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    return _fastq_manifest_helper(fmt, os.link, single_end=False)


@plugin.register_transformer
def _9(fmt: PairedEndFastqManifestPhred64) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    warnings.warn(_phred64_warning)
    return _fastq_manifest_helper(fmt, _write_phred64_to_phred33,
                                  single_end=False)
