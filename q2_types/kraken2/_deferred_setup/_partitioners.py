# ----------------------------------------------------------------------------
# Copyright (c) 2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import os
import warnings

import pandas as pd
import numpy as np

from qiime2.util import duplicate

from q2_types.kraken2 import (Kraken2ReportDirectoryFormat,
                              Kraken2OutputDirectoryFormat)


def _partition_kraken2_results(
    result: Kraken2ReportDirectoryFormat | Kraken2OutputDirectoryFormat,
    num_partitions: int
) -> dict[
    str | int, Kraken2ReportDirectoryFormat | Kraken2OutputDirectoryFormat
]:
    partitioned_result = {}
    result_dict = result.file_dict()
    result_class = type(result)

    # Make sure we are partitioning on samples if no number of partitions or
    # too many partitions specified and warn if they specified too many
    # partitions
    num_samples = len(result_dict)
    if num_partitions is None:
        num_partitions = num_samples
    elif num_partitions > num_samples:
        warnings.warn("You have requested a number of partitions"
                      f" '{num_partitions}' that is greater than your number"
                      f" of samples '{num_samples}.' Your data will be"
                      f" partitioned by sample into '{num_samples}'"
                      " partitions.")
        num_partitions = num_samples

    df = pd.DataFrame(data=result_dict.values(),
                      index=result_dict.keys(),
                      columns=["filepath"])

    partitioned_df = np.array_split(df, num_partitions)

    for i, _df in enumerate(partitioned_df, 1):
        result = result_class()

        for sample_id, _ in _df.iterrows():
            in_path = _df.loc[sample_id, "filepath"]
            filename = os.path.basename(in_path)
            out_path = os.path.join(result.path, filename)
            duplicate(in_path, out_path)

        if num_partitions == num_samples:
            partitioned_result[sample_id] = result
        else:
            partitioned_result[i] = result

    return partitioned_result
