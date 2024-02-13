# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import re


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
