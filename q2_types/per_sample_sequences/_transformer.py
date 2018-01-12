# ----------------------------------------------------------------------------
# Copyright (c) 2016-2018, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import re
import os
import gzip
import shutil
import warnings
import collections

import skbio
import yaml
import pandas as pd
import qiime2.util

from ..plugin_setup import plugin
from . import (SingleLanePerSampleSingleEndFastqDirFmt, FastqManifestFormat,
               FastqAbsolutePathManifestFormat, FastqGzFormat,
               SingleLanePerSamplePairedEndFastqDirFmt, YamlFormat,
               CasavaOneEightSingleLanePerSampleDirFmt,
               CasavaOneEightLanelessPerSampleDirFmt,
               SingleEndFastqManifestPhred33, SingleEndFastqManifestPhred64,
               PairedEndFastqManifestPhred33, PairedEndFastqManifestPhred64,
               QIIME1DemuxDirFmt)


def _single_lane_per_sample_fastq_helper(dirfmt, output_cls, parse_lane=True):
    result = output_cls()
    manifest = FastqManifestFormat()
    manifest_fh = manifest.open()
    manifest_fh.write('sample-id,filename,direction\n')
    directions = ['forward', 'reverse']
    for path, view in dirfmt.sequences.iter_views(FastqGzFormat):
        filename = str(path).replace('.fastq.gz', '')
        if parse_lane:
            sample_id, barcode_id, lane_number, read_number, _ = \
                filename.rsplit('_', maxsplit=4)
        else:
            sample_id, barcode_id, read_number, _ = \
                filename.rsplit('_', maxsplit=3)
        read_number = int(read_number[1:])
        lane_number = int(lane_number[1:]) if parse_lane else 1
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
def _10(dirfmt: CasavaOneEightLanelessPerSampleDirFmt) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    return _single_lane_per_sample_fastq_helper(
        dirfmt, SingleLanePerSampleSingleEndFastqDirFmt, parse_lane=False)


@plugin.register_transformer
def _11(dirfmt: CasavaOneEightLanelessPerSampleDirFmt) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    return _single_lane_per_sample_fastq_helper(
        dirfmt, SingleLanePerSamplePairedEndFastqDirFmt, parse_lane=False)


@plugin.register_transformer
def _5(dirfmt: SingleLanePerSamplePairedEndFastqDirFmt) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    with dirfmt.manifest.view(FastqManifestFormat).open() as fh:
        input_manifest = _parse_and_validate_manifest(fh, single_end=False,
                                                      absolute=False)

    output_manifest = FastqManifestFormat()
    output_df = input_manifest[input_manifest.direction == 'forward']
    with output_manifest.open() as fh:
        output_df.to_csv(fh, index=False)

    result = SingleLanePerSampleSingleEndFastqDirFmt()
    result.manifest.write_data(output_manifest, FastqManifestFormat)
    for _, _, filename, _ in output_df.itertuples():
        qiime2.util.duplicate(str(dirfmt.path / filename),
                              str(result.path / filename))

    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, YamlFormat)

    return result


def _parse_and_validate_manifest(manifest_fh, single_end, absolute):
    try:
        manifest = pd.read_csv(manifest_fh, comment='#', header=0,
                               skip_blank_lines=True, dtype=object)
    except Exception as e:
        raise ValueError('There was an issue parsing the manifest '
                         'file as CSV:\n %s' % e)

    expected_header = (FastqAbsolutePathManifestFormat.EXPECTED_HEADER if
                       absolute else FastqManifestFormat.EXPECTED_HEADER)
    _validate_header(manifest, expected_header)

    for idx in manifest.index:
        record = manifest.loc[idx]
        if record.isnull().any():
            raise ValueError('Empty cells are not supported in '
                             'manifest files. Found one or more '
                             'empty cells in this record: %s'
                             % ','.join(map(str, record)))
        record[expected_header[1]] = \
            os.path.expandvars(record[expected_header[1]])
        path = record[expected_header[1]]
        if absolute:
            if not os.path.isabs(path):
                raise ValueError('All paths provided in manifest must be '
                                 'absolute but found relative path: %s' % path)
        else:
            if os.path.isabs(path):
                raise ValueError('All paths provided in manifest must be '
                                 'relative but found absolute path: %s' % path)
            path = os.path.join(os.path.dirname(manifest_fh.name), path)
        if not os.path.exists(path):
            raise FileNotFoundError(
                'A path specified in the manifest does not exist '
                'or is not accessible: '
                '%s' % path)

    if single_end:
        _validate_single_end_fastq_manifest_directions(manifest)
    else:
        _validate_paired_end_fastq_manifest_directions(manifest)

    return manifest


def _validate_header(manifest, expected_header):
    header = manifest.columns.tolist()
    if header != expected_header:
        raise ValueError('Expected manifest header %r but '
                         'found %r.'
                         % (','.join(expected_header), ','.join(header)))


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
    if not directions.issubset({'forward', 'reverse'}):
        raise ValueError('Directions can only be "forward" or '
                         '"reverse", but observed: %s'
                         % ', '.join(directions))
    if len(directions) > 1:
        raise ValueError('Manifest for single-end reads can '
                         'contain only forward or reverse reads, '
                         'but not both. The following directions were '
                         'observed: %s' % ', '.join(directions))
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
            raise ValueError('Directions can only be "forward" or '
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

        if len(forward_but_no_reverse) > 0:
            raise ValueError('Forward and reverse reads must be provided '
                             'exactly one time each for each sample. The '
                             'following samples had forward but not '
                             'reverse read fastq files: %s'
                             % ', '.join(forward_but_no_reverse))
        else:
            reverse_but_no_forward = set(reverse_direction_sample_ids) - \
              set(forward_direction_sample_ids)
            raise ValueError('Forward and reverse reads must be provided '
                             'exactly one time each for each sample. The '
                             'following samples had reverse but not '
                             'forward read fastq files: %s'
                             % ', '.join(reverse_but_no_forward))


def _copy_with_compression(src, dst):
    with open(src, 'rb') as src_fh:
        if src_fh.read(2)[:2] != b'\x1f\x8b':
            src_fh.seek(0)
            # SO: http://stackoverflow.com/a/27069578/579416
            # shutil.copyfileobj will pick a pretty good chunksize for us
            with gzip.open(dst, 'wb') as dst_fh:
                shutil.copyfileobj(src_fh, dst_fh)
                return

    qiime2.util.duplicate(src, dst)


def _fastq_manifest_helper(fmt, fastq_copy_fn, single_end):
    direction_to_read_number = {'forward': 1, 'reverse': 2}
    input_manifest = _parse_and_validate_manifest(fmt.open(),
                                                  single_end=single_end,
                                                  absolute=True)
    if single_end:
        result = SingleLanePerSampleSingleEndFastqDirFmt()
    else:
        result = SingleLanePerSamplePairedEndFastqDirFmt()

    output_manifest_data = []
    for idx, sample_id, input_fastq_fp, direction in \
            input_manifest.itertuples():
        read_number = direction_to_read_number[direction]
        output_fastq_fp = \
            result.sequences.path_maker(sample_id=sample_id,
                                        # the remaining values aren't used
                                        # internally by QIIME, so their values
                                        # aren't very important
                                        barcode_id=idx,
                                        lane_number=1,
                                        read_number=read_number)
        output_manifest_data.append(
            [sample_id, output_fastq_fp.name, direction])
        fastq_copy_fn(input_fastq_fp, str(output_fastq_fp))

    output_manifest = FastqManifestFormat()
    output_manifest_df = \
        pd.DataFrame(output_manifest_data,
                     columns=output_manifest.EXPECTED_HEADER)
    output_manifest_df.to_csv(str(output_manifest), index=False)
    result.manifest.write_data(output_manifest, FastqManifestFormat)

    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, YamlFormat)

    return result


_phred64_warning = ('Importing of PHRED 64 data is slow as it is converted '
                    'internally to PHRED 33. Working with the imported data '
                    'will not be slower than working with PHRED 33 data.')


def _write_phred64_to_phred33(phred64_path, phred33_path):
    with open(phred64_path, 'rb') as phred64_fh, \
         open(phred33_path, 'wb') as phred33_fh:
        for seq in skbio.io.read(phred64_fh, format='fastq',
                                 variant='illumina1.3'):
            skbio.io.write(seq, into=phred33_fh,
                           format='fastq',
                           variant='illumina1.8',
                           compression='gzip')


@plugin.register_transformer
def _6(fmt: SingleEndFastqManifestPhred33) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    return _fastq_manifest_helper(fmt, _copy_with_compression, single_end=True)


@plugin.register_transformer
def _7(fmt: SingleEndFastqManifestPhred64) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    warnings.warn(_phred64_warning)
    return _fastq_manifest_helper(fmt, _write_phred64_to_phred33,
                                  single_end=True)


@plugin.register_transformer
def _8(fmt: PairedEndFastqManifestPhred33) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    return _fastq_manifest_helper(fmt, _copy_with_compression,
                                  single_end=False)


@plugin.register_transformer
def _9(fmt: PairedEndFastqManifestPhred64) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    warnings.warn(_phred64_warning)
    return _fastq_manifest_helper(fmt, _write_phred64_to_phred33,
                                  single_end=False)


@plugin.register_transformer
def _12(dirfmt: SingleLanePerSampleSingleEndFastqDirFmt) \
        -> QIIME1DemuxDirFmt:
    with dirfmt.manifest.view(FastqManifestFormat).open() as fh:
        input_manifest = _parse_and_validate_manifest(fh, single_end=True,
                                                      absolute=False)

    result = QIIME1DemuxDirFmt()
    fp = str(result.path / 'seqs.fna')
    with open(fp, 'w') as fh:
        i = 0
        for r in input_manifest.iterrows():
            sample_id = r[1]['sample-id']
            filename = r[1]['filename']
            if re.search("\s", sample_id) is not None:
                raise ValueError(
                    "Whitespace was found in the ID for sample %s. Sample "
                    "IDs with whitespace are incompatible with FASTA."
                    % sample_id)
            fq_reader = skbio.io.read('%s/%s' % (str(dirfmt), filename),
                                      format='fastq', constructor=skbio.DNA,
                                      phred_offset=33, verify=False)
            for seq in fq_reader:
                seq.metadata['id'] = '%s_%d' % (sample_id, i)
                seq.write(fh)
                i += 1

    return result
