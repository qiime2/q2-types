# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import collections
import gzip
import os
import re
import shutil

import pandas as pd
import qiime2.util
import skbio
import yaml

from qiime2.plugin import ValidationError


# Note: we DI all of the formats into these utils so that we don't wind
# up in circular import mayhem. That is all.


def _parse_sequence_filename(path,
                             parse_lane=True,
                             parse_sample_id_only=False):
    filename = str(path).replace('.fastq.gz', '')

    if parse_sample_id_only:
        # all text before the extension should be treated as the sample id.
        return filename, 'na', 1, 1, 'forward'

    directions = ['forward', 'reverse']
    if parse_lane:
        sample_id, barcode_id, lane_number, read_number, _ = \
            filename.rsplit('_', maxsplit=4)
    else:
        sample_id, barcode_id, read_number, _ = \
            filename.rsplit('_', maxsplit=3)
    read_number = int(read_number[1:])
    lane_number = int(lane_number[1:]) if parse_lane else 1
    direction = directions[read_number - 1]

    return sample_id, barcode_id, lane_number, read_number, direction


def _single_lane_per_sample_fastq_helper(
        dirfmt, output_cls, manifest_fmt, fastq_fmt, yaml_fmt,
        parse_lane=True, parse_sample_id_only=False):
    result = output_cls()
    manifest = manifest_fmt()
    manifest_fh = manifest.open()
    manifest_fh.write('sample-id,filename,direction\n')
    for path, view in dirfmt.sequences.iter_views(fastq_fmt):
        parsed = _parse_sequence_filename(
            path, parse_lane=parse_lane,
            parse_sample_id_only=parse_sample_id_only)
        sample_id, barcode_id, lane_number, read_number, direction = parsed

        result.sequences.write_data(view, fastq_fmt, sample_id=sample_id,
                                    barcode_id=barcode_id,
                                    lane_number=lane_number,
                                    read_number=read_number)

        filepath = result.sequences.path_maker(sample_id=sample_id,
                                               barcode_id=barcode_id,
                                               lane_number=lane_number,
                                               read_number=read_number)
        name = filepath.name

        manifest_fh.write('%s,%s,%s\n' % (sample_id, name, direction))

    manifest_fh.close()
    result.manifest.write_data(manifest, manifest_fmt)

    metadata = yaml_fmt()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, yaml_fmt)

    return result


def _dirfmt_to_casava(dirfmt_in, manifest_fmt, abs_manifest_fmt, fastq_fmt,
                      casava_fmt):
    dirfmt_out = casava_fmt()
    for fastq, _ in dirfmt_in.sequences.iter_views(fastq_fmt):
        from_fp = str(dirfmt_in.path / fastq.name)
        to_fp = str(dirfmt_out.path / fastq.name)
        qiime2.util.duplicate(from_fp, to_fp)
    return dirfmt_out


def _parse_and_validate_manifest(manifest_fh, single_end, absolute,
                                 abs_manifest_fmt, manifest_fmt):
    try:
        manifest = pd.read_csv(manifest_fh, comment='#', header=0,
                               skip_blank_lines=True, dtype=object)
    except Exception as e:
        raise ValueError('There was an issue parsing the manifest '
                         'file as CSV:\n %s' % e)

    expected_header = (abs_manifest_fmt.EXPECTED_HEADER if
                       absolute else manifest_fmt.EXPECTED_HEADER)
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


def _fastq_manifest_helper(fmt, fastq_copy_fn, single_end, se_fmt, pe_fmt,
                           abs_manifest_fmt, manifest_fmt, yaml_fmt):
    direction_to_read_number = {'forward': 1, 'reverse': 2}
    input_manifest = _parse_and_validate_manifest(
        fmt.open(),
        single_end=single_end,
        absolute=True,
        abs_manifest_fmt=abs_manifest_fmt,
        manifest_fmt=manifest_fmt,
    )
    if single_end:
        result = se_fmt()
    else:
        result = pe_fmt()

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

    output_manifest = manifest_fmt()
    output_manifest_df = \
        pd.DataFrame(output_manifest_data,
                     columns=output_manifest.EXPECTED_HEADER)
    output_manifest_df.to_csv(str(output_manifest), index=False)
    result.manifest.write_data(output_manifest, manifest_fmt)

    metadata = yaml_fmt()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, yaml_fmt)

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


def _manifest_v2_to_v1(fmt, manifest_fmt):
    df = qiime2.Metadata.load(str(fmt)).to_dataframe()
    # Drop unneccessary metadata columns
    df = df[list(fmt.METADATA_COLUMNS.keys())]
    denormalized_dfs = []
    for column, direction in fmt.METADATA_COLUMNS.items():
        denormalized_df = df[[column]]
        original_index_name = denormalized_df.index.name
        denormalized_df.reset_index(drop=False, inplace=True)
        denormalized_df.rename(columns={
            original_index_name: 'sample-id',
            column: 'absolute-filepath'
        }, inplace=True)
        denormalized_df['direction'] = direction
        denormalized_dfs.append(denormalized_df)
    old_fmt = manifest_fmt()
    pd.concat(denormalized_dfs, axis=0).to_csv(str(old_fmt), index=False)
    return old_fmt


def _manifest_to_df(ff, base_dir):
    manifest = pd.read_csv(str(ff), header=0, comment='#', dtype=str)
    manifest.filename = manifest.filename.apply(
        lambda f: os.path.join(base_dir, f))

    df = manifest.pivot(index='sample-id', columns='direction',
                        values='filename')
    df.columns.name = None
    return df


def _parse_mag_filename(path):
    filename = re.sub(r'\.(fa|fasta)$', '', str(path))
    sample_id, mag_id = filename.rsplit('/', maxsplit=2)
    return sample_id, mag_id


# TODO: should there be any metadata written as well?
def _mag_manifest_helper(dirfmt, output_cls, manifest_fmt,
                         fastq_fmt):
    result = output_cls()
    manifest = manifest_fmt()
    manifest_fh = manifest.open()
    manifest_fh.write('sample-id,mag-id,filename\n')
    for path, view in dirfmt.sequences.iter_views(fastq_fmt):
        sample_id, mag_id = _parse_mag_filename(path)
        result.sequences.write_data(view, fastq_fmt,
                                    sample_id=sample_id,
                                    mag_id=mag_id)

        filepath = result.sequences.path_maker(sample_id=sample_id,
                                               mag_id=mag_id)
        name = f"{filepath.parent.name}/{filepath.name}"

        manifest_fh.write('%s,%s,%s\n' % (sample_id, mag_id, name))

    manifest_fh.close()
    result.manifest.write_data(manifest, manifest_fmt)

    return result


def validate_paired_ends_equal_record_count(file_fwd: str, file_rev: str):
    """
    Ensures that the number of lines in the `file_fwd` and `file_rev` fastq
    files match.

    Parameters
    ----------
    file_fwd : str
        The absolute path to the forward read file.
    file_rev : str
        The absolute path to the reverse read file.

    Raises
    ------
    ValidationError
        If the line counts of the forward and reverse read files are not equal.
    """
    def count_lines(file):
        num_lines = 0
        with gzip.open(file, 'rb') as f:
            while block := f.read(1024 * 1024):
                num_lines = num_lines + block.count(b'\n')
        return num_lines

    fwd_count = count_lines(file_fwd)
    rev_count = count_lines(file_rev)

    if fwd_count != rev_count:
        raise ValidationError(
            f'A pair of paired-end files were found not to have the same '
            f'number of records. {file_fwd} has {fwd_count} records. '
            f'{file_rev} has {rev_count} records.'
        )


# def _bowtie2_fmt_helper(dirfmt, output_cls, bowtie_fmt):
#     result = output_cls()
#     for path, view in dirfmt.sequences.iter_views(bowtie_fmt):
#         sample_id, mag_id = _parse_mag_filename(path)
#         result.sequences.write_data(view, bowtie_fmt,
#                                     sample_id=sample_id,
#                                     mag_id=mag_id)
#
#         filepath = result.sequences.path_maker(sample_id=sample_id,
#                                                mag_id=mag_id)
#         name = f"{filepath.parent.name}/{filepath.name}"
#
#         manifest_fh.write('%s,%s,%s\n' % (sample_id, mag_id, name))
#
#     manifest_fh.close()
#     result.manifest.write_data(manifest, manifest_fmt)
#
#     return result
