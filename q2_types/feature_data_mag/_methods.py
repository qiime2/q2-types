# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os

import numpy as np
from qiime2.util import duplicate

from q2_types._util import _validate_num_partitions, _validate_mag_ids
from q2_types.feature_data_mag import MAGSequencesDirFmt


def partition_feature_data_mags(
    mags: MAGSequencesDirFmt, num_partitions: int = None
) -> MAGSequencesDirFmt:
    """
    Returns a dictionary where each key is either the mag_id or an index, and
    values are the new objects with the mags.
    """
    partitioned_mags = {}
    mags_all = []

    # Get a list where every entry is a tuple representing one MAG
    for mag_id, mag_fp in mags.feature_dict().items():
        mags_all.append((mag_fp, mag_id))

    # Count number of mags and validate the num_partitions
    num_mags = len(mags_all)
    num_partitions = _validate_num_partitions(num_mags, num_partitions, "MAG")
    _validate_mag_ids(num_partitions, num_mags, mags_all)

    # Split list MAGs into n arrays, where n = num_partitions
    arrays_of_mags = np.array_split(mags_all, num_partitions)

    for i, _mag in enumerate(arrays_of_mags, 1):
        result = MAGSequencesDirFmt()

        for mag_fp, mag_id in _mag:
            duplicate(mag_fp, result.path / os.path.basename(mag_fp))

        # If num_partitions == num_mags we will only have gone through one
        # MAG in the above loop and will use its id as a key. Otherwise, we
        # may have gone through multiple MAGs in the above loop and will be
        # using indices for keys
        if num_partitions == num_mags:
            partitioned_mags[mag_id] = result
        else:
            partitioned_mags[i] = result

    return partitioned_mags


def collate_feature_data_mags(mags: MAGSequencesDirFmt) -> MAGSequencesDirFmt:
    collated_mags = MAGSequencesDirFmt()
    for mag in mags:
        for fp in mag.path.iterdir():
            duplicate(fp, collated_mags.path / fp.name)

    return collated_mags
