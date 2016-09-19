# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import skbio
import yaml
import gzip

from ..plugin_setup import plugin
from . import (SingleLanePerSampleSingleEndFastqDirFmt, FastqManifestFormat,
               SingleLanePerSamplePairedEndFastqDirFmt, FastqGzFormat,
               CasavaOneEightSingleLanePerSampleDirFmt, YamlFormat,
               QIIME1DemultiplexedFastqDirFmt, QIIME1FastqManifestFormat)


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
        result[sample_id] = skbio.io.read(
            filepath, format='fastq', constructor=skbio.DNA,
            phred_offset=33, verify=False)
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
                             constructor=skbio.DNA,
                             phred_offset=33, verify=False)

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
def _5(dirfmt: QIIME1DemultiplexedFastqDirFmt)\
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    result = SingleLanePerSampleSingleEndFastqDirFmt()

    out_manifest = FastqManifestFormat()
    out_manifest_fh = out_manifest.open()
    out_manifest_fh.write('sample-id,filename,direction\n')

    # keep track of what samples and corresponding read directions have
    # been observed, to ensure that we only have one read direction per
    # sample across the input fastq files
    observed_sample_reads = {}
    directions = ['forward', 'reverse']
    in_manifest = iter(dirfmt.manifest.view(QIIME1FastqManifestFormat).open())
    next(in_manifest)

    for line in in_manifest:
        if line.startswith('#'):
            continue
        filename, read_number, lane_number, phred_offset = \
            line.strip().split(',')
        read_number = int(read_number)
        lane_number = int(lane_number)
        phred_offset = int(phred_offset)
        in_fastq_filepath = str(dirfmt.path / filename)
        data = {}
        for seq in skbio.io.read(in_fastq_filepath,
                                 constructor=skbio.DNA,
                                 format='fastq',
                                 verify=False,
                                 phred_offset=phred_offset):

            sample_id = seq.metadata['id'].split('_')[0]

            if (sample_id, read_number) in observed_sample_reads:
                raise ValueError(
                    'Read %d data was observed for sample %s in at least two '
                    'fastq files. Each sample can be present in a maximum of '
                    'one read 1 file and one read 2 file. The offending fastq '
                    'files are %s and %s.' % (
                        read_number, sample_id, in_fastq_filepath,
                        observed_sample_reads[(sample_id, read_number)]))

            # skbio can't currently write to a gzip file handle, so this is a
            # hack to do that.
            # this transformer will always write with phred offset = 33
            fastq_lines = ''.join(
                seq.write([], format='fastq', phred_offset=33))
            fastq_lines = fastq_lines.encode('ascii')

            if sample_id in data:
                data[sample_id][1].write(fastq_lines)
            else:
                barcode_id = len(data) + 1
                path = result.sequences.path_maker(sample_id=sample_id,
                                                   barcode_id=barcode_id,
                                                   lane_number=lane_number,
                                                   read_number=read_number)
                fh = gzip.open(str(path), mode='w')
                fh.write(fastq_lines)
                data[sample_id] = (path, fh)

        # write output manifest lines
        for sample_id, (path, fh) in data.items():
            observed_sample_reads[(sample_id, read_number)] = in_fastq_filepath
            fh.close()
            direction = directions[read_number - 1]
            out_manifest_fh.write('%s,%s,%s\n' %
                                  (sample_id, path.name, direction))

    out_manifest_fh.close()
    result.manifest.write_data(out_manifest, FastqManifestFormat)

    # this transformer will always write with phred offset = 33
    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, YamlFormat)

    return result
