# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
import shutil

import numpy as np
import pandas as pd
from qiime2.util import duplicate

from q2_types._util import _validate_num_partitions
from q2_types.per_sample_sequences import MultiMAGSequencesDirFmt


def partition_sample_data_mags(
    mags: MultiMAGSequencesDirFmt, num_partitions: int = None
) -> MultiMAGSequencesDirFmt:
    """
    Returns a dictionary where each key is either the mag_id or an index, and
    values are the new objects with the mags.
    """
    partitioned_mags = {}
    mags_all = [{k: v} for k, v in mags.sample_dict().items()]

    num_partitions = _validate_num_partitions(
        len(mags_all), num_partitions, "sample"
    )

    arrays_of_mags = np.array_split(mags_all, num_partitions)

    for i, samples in enumerate(arrays_of_mags, 1):
        result = MultiMAGSequencesDirFmt()
        all_samples = set(k for d in samples for k in d.keys())
        manifest = pd.read_csv(mags.path / "MANIFEST", index_col=None)
        manifest = manifest[manifest["sample-id"].isin(all_samples)]
        manifest.to_csv(result.path / "MANIFEST", index=False)

        for sample_dict in samples:
            for sample_id, mag_dict in sample_dict.items():
                for mag_id, mag_fp in mag_dict.items():
                    os.makedirs(result.path / sample_id, exist_ok=True)
                    duplicate(
                        mag_fp,
                        result.path / sample_id / os.path.basename(mag_fp)
                    )

        # If num_partitions == num_samples we will only have gone through one
        # sample in the above loop and will use its id as a key. Otherwise we
        # may have gone through multiple MAGs in the above loop and will be
        # using indices for keys
        if num_partitions == len(mags_all):
            partitioned_mags[sample_id] = result
        else:
            partitioned_mags[i] = result

    return partitioned_mags


def collate_sample_data_mags(
    mags: MultiMAGSequencesDirFmt
) -> MultiMAGSequencesDirFmt:
    collated_mags = MultiMAGSequencesDirFmt()

    # For every partition
    for mag in mags:

        # For every sample in the partition
        for file_or_dir in mag.path.iterdir():

            if file_or_dir.is_dir():
                sample = file_or_dir
                os.makedirs(collated_mags.path / sample.name, exist_ok=True)

                # For every mag in the sample
                for mag in sample.iterdir():
                    duplicate(
                        mag, collated_mags.path / sample.name / mag.name
                    )

            # If it's a file, it should be the manifest
            else:
                manifest = file_or_dir
                # If it's the first manifest, copy it over
                if not (collated_mags.path / manifest.name).exists():
                    shutil.copy(manifest, collated_mags.path / manifest.name)
                else:
                    # Append entries (except header) to the existing manifest
                    with (
                        open(manifest, 'r') as src,
                        open(collated_mags.path / manifest.name, 'a') as dest
                    ):
                        next(src)  # Skip header
                        for line in src:
                            dest.write(line)

    return collated_mags
