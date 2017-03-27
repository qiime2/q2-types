# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import gzip

import skbio
import yaml

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

@plugin.register_transformer
def _6(fmt: SingleEndFastqManifestPhred33) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    result = SingleLanePerSampleSingleEndFastqDirFmt()
    manifest = FastqManifestFormat()
    with manifest.open() as manifest_fh:
        with fmt.open() as fh:
            iterator = iter(fh)
            manifest_fh.write(next(iterator))  # header line
            for barcode_id, line in enumerate(iterator):
                sample_id, path, direction = line.rstrip().split(',')
                abspath = os.path.abspath(path)
                if not os.path.exists(abspath):
                    raise FileNotFoundError(
                        'A path specified in the manifest does not exist: '
                        '%s' % path)
                if direction == 'forward':
                    manifest_fh.write(line)
                    result_path = '%s_%s_L001_R1_001.fastq.gz' % \
                        (sample_id, barcode_id)
                    os.link(str(abspath), str(result.path / result_path))

    result.manifest.write_data(manifest, FastqManifestFormat)

    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, YamlFormat)

    return result

@plugin.register_transformer
def _7(fmt: SingleEndFastqManifestPhred64) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    result = SingleLanePerSampleSingleEndFastqDirFmt()
    manifest = FastqManifestFormat()
    with manifest.open() as manifest_fh:
        with fmt.open() as fh:
            iterator = iter(fh)
            manifest_fh.write(next(iterator))  # header line
            for barcode_id, line in enumerate(iterator):
                sample_id, path, direction = line.rstrip().split(',')
                abspath = os.path.abspath(path)
                if not os.path.exists(abspath):
                    raise FileNotFoundError(
                        'A path specified in the manifest does not exist: '
                        '%s' % path)
                if direction == 'forward':
                    manifest_fh.write(line)
                    result_path = '%s_%s_L001_R1_001.fastq.gz' % \
                        (sample_id, barcode_id)
                    out_path = str(result.path / result_path)
                    # convert PHRED 64 to PHRED 33
                    with open(out_path, 'wb') as out_file:
                        for seq in skbio.io.read(path, format='fastq',
                                                 variant='illumina1.3'):
                            skbio.io.write(seq, into=out_file,
                                           format='fastq',
                                           variant='illumina1.8',
                                           compression='gzip')

    result.manifest.write_data(manifest, FastqManifestFormat)

    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, YamlFormat)

    return result

@plugin.register_transformer
def _8(fmt: PairedEndFastqManifestPhred33) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    result = SingleLanePerSamplePairedEndFastqDirFmt()
    manifest = FastqManifestFormat()
    with manifest.open() as manifest_fh:
        with fmt.open() as fh:
            iterator = iter(fh)
            manifest_fh.write(next(iterator))  # header line
            for barcode_id, line in enumerate(iterator):
                sample_id, path, direction = line.rstrip().split(',')
                abspath = os.path.abspath(path)
                if not os.path.exists(abspath):
                    raise FileNotFoundError(
                        'A path specified in the manifest does not exist: '
                        '%s' % path)
                if direction == 'forward':
                    manifest_fh.write(line)
                    result_path = '%s_%s_L001_R1_001.fastq.gz' % \
                        (sample_id, barcode_id)
                elif direction == 'reverse':
                    manifest_fh.write(line)
                    result_path = '%s_%s_L001_R2_001.fastq.gz' % \
                        (sample_id, barcode_id)
                else:
                    raise ValueError('Read direction must be "forward" or '
                                     '"reverse" in manifest, but received: '
                                     '%s' % direction)
                os.link(str(abspath), str(result.path / result_path))

    result.manifest.write_data(manifest, FastqManifestFormat)

    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, YamlFormat)

    return result

@plugin.register_transformer
def _9(fmt: PairedEndFastqManifestPhred64) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    result = SingleLanePerSamplePairedEndFastqDirFmt()
    manifest = FastqManifestFormat()
    with manifest.open() as manifest_fh:
        with fmt.open() as fh:
            iterator = iter(fh)
            manifest_fh.write(next(iterator))  # header line
            for barcode_id, line in enumerate(iterator):
                sample_id, path, direction = line.rstrip().split(',')
                abspath = os.path.abspath(path)
                if not os.path.exists(abspath):
                    raise FileNotFoundError(
                        'A path specified in the manifest does not exist: '
                        '%s' % path)
                if direction == 'forward':
                    manifest_fh.write(line)
                    result_path = '%s_%s_L001_R1_001.fastq.gz' % \
                        (sample_id, barcode_id)
                elif direction == 'reverse':
                    manifest_fh.write(line)
                    result_path = '%s_%s_L001_R2_001.fastq.gz' % \
                        (sample_id, barcode_id)
                else:
                    raise ValueError('Read direction must be "forward" or '
                                     '"reverse" in manifest, but received: '
                                     '%s' % direction)

                out_path = str(result.path / result_path)
                # convert PHRED 64 to PHRED 33
                with open(out_path, 'wb') as out_file:
                    for seq in skbio.io.read(path, format='fastq',
                                             variant='illumina1.3'):
                        skbio.io.write(seq, into=out_file,
                                       format='fastq',
                                       variant='illumina1.8',
                                       compression='gzip')

    result.manifest.write_data(manifest, FastqManifestFormat)

    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, YamlFormat)

    return result
