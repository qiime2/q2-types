# ----------------------------------------------------------------------------
# Copyright (c) 2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import warnings

import pandas as pd
import numpy as np

def _partition_kraken2_reports(report, num_partitions):
    partitioned_report = {}
    report_dict = report.file_dict()

    # Make sure we are partitioning on samples if no number of partitions or
    # too many partitions specified and warn if they specified too many
    # partitions
    num_samples = len(report_dict)
    if num_partitions is None:
        num_partitions = num_samples
    elif num_partitions > num_samples:
        warnings.warn("You have requested a number of partitions"
                      f" '{num_partitions}' that is greater than your number"
                      f" of samples '{num_samples}.' Your data will be"
                      f" partitioned by sample into '{num_samples}'"
                      " partitions.")
        num_partitions = num_samples

    df = pd.DataFrame(data=report_dict.values(),
                      index=report_dict.keys(),
                      columns=[ "filepath"])
    partitioned_df = np.array_split(df, num_partitions)

    for i, _df in enumerate(partitioned_df, 1):
        result = type(report)

        # If we have one sample per partition we name the partitions after the
        # samples. Otherwise we number them
        if num_partitions == num_samples:
            partitioned_demux[sample_id] = result
        else:
            partitioned_demux[i] = result

    return partitioned_demux

def _partition_kraken2_outputs():
    # TODO
