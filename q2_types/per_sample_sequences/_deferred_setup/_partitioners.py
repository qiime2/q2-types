# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import pandas as pd
import numpy as np
import yaml

import warnings
import os

from q2_types.per_sample_sequences import (
    SingleLanePerSampleSingleEndFastqDirFmt,
    SingleLanePerSamplePairedEndFastqDirFmt,
    FastqManifestFormat, YamlFormat)


from qiime2.util import duplicate


def partition_samples_single(demux: SingleLanePerSampleSingleEndFastqDirFmt,
                             num_partitions: int = None
                             ) -> SingleLanePerSampleSingleEndFastqDirFmt:
    return _partition_helper(demux, num_partitions, paired=False)


def partition_samples_paired(demux: SingleLanePerSamplePairedEndFastqDirFmt,
                             num_partitions: int = None
                             ) -> SingleLanePerSamplePairedEndFastqDirFmt:
    return _partition_helper(demux, num_partitions, paired=True)


def _partition_helper(demux, num_partitions, paired):
    """ Deal with partitioning logic that is largely the same regardless of
        single or paired.
    """
    # Adjust based on if we are in the single or paired end case
    result_class = type(demux)

    partitioned_demux = {}
    df = demux.manifest.view(pd.DataFrame)

    # Make sure we are partitioning on samples if no number of partitions or
    # too many partitions specified and warn if they specified too many
    # partitions
    num_samples = df.shape[0]
    if num_partitions is None:
        num_partitions = num_samples
    elif num_partitions > num_samples:
        warnings.warn("You have requested a number of partitions"
                      f" '{num_partitions}' that is greater than your number"
                      f" of samples '{num_samples}.' Your data will be"
                      f" partitioned by sample into '{num_samples}'"
                      " partitions.")
        num_partitions = num_samples

    partitioned_df = np.array_split(df, num_partitions)
    for i, _df in enumerate(partitioned_df, 1):
        result = result_class()

        manifest_string = ''
        for sample in _df.iterrows():
            sample_id = sample[0]

            manifest_string += _partition_duplicate(
                    sample, sample_id, result, 'forward')
            if paired:
                manifest_string += _partition_duplicate(
                    sample, sample_id, result, 'reverse')

        manifest = _partition_write_manifest(manifest_string, paired)
        result.manifest.write_data(manifest, FastqManifestFormat)
        _write_metadata_yaml(result)

        # If we have one sample per partition we name the partitions after the
        # samples. Otherwise we number them
        if num_partitions == num_samples:
            partitioned_demux[sample_id] = result
        else:
            partitioned_demux[i] = result

    return partitioned_demux


def _partition_duplicate(sample, sample_id, result, direction):
    """ Duplicate the given direction of the sample into the result and return
        the corresponding line for the manifest.
    """
    in_path = sample[1][direction]

    artifact_name = os.path.basename(in_path)
    out_path = os.path.join(result.path, artifact_name)
    duplicate(in_path, out_path)

    return '%s,%s,%s\n' % (sample_id, artifact_name, direction)


def _partition_write_manifest(manifest_string, paired):
    """ Add header to manifest then write to file.
    """
    manifest = FastqManifestFormat()

    header_string = 'sample-id,filename,direction\n'
    if not paired:
        header_string += \
            ('# direction is not meaningful in this file as these\n'
             '# data may be derived from forward, reverse, or \n'
             '# joined reads\n')
    manifest_string = header_string + manifest_string

    with manifest.open() as manifest_fh:
        manifest_fh.write(manifest_string)

    return manifest


def _write_metadata_yaml(dir_fmt):
    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    dir_fmt.metadata.write_data(metadata, YamlFormat)
