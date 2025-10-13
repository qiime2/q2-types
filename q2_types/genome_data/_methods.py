# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import glob
import os
import shutil
import warnings
from typing import Union
from warnings import warn

import numpy as np
import skbio
from qiime2.util import duplicate

from q2_types._util import _collate_helper
from q2_types.feature_data import DNAIterator, DNAFASTAFormat
from q2_types.genome_data import (
    SeedOrthologDirFmt, OrthologAnnotationDirFmt, LociDirectoryFormat,
    GenomeSequencesDirectoryFormat, GenesDirectoryFormat,
    ProteinsDirectoryFormat
)


def collate_loci(loci: LociDirectoryFormat) -> LociDirectoryFormat:
    return _collate_helper(dir_fmts=loci)


def collate_ortholog_annotations(
    ortholog_annotations: OrthologAnnotationDirFmt
) -> OrthologAnnotationDirFmt:
    return _collate_helper(dir_fmts=ortholog_annotations)


def collate_genes(
        genes: GenesDirectoryFormat
) -> GenesDirectoryFormat:
    return _collate_helper(dir_fmts=genes)


def collate_proteins(
        proteins: ProteinsDirectoryFormat
) -> ProteinsDirectoryFormat:
    return _collate_helper(dir_fmts=proteins)


def collate_orthologs(orthologs: SeedOrthologDirFmt) -> SeedOrthologDirFmt:
    result = SeedOrthologDirFmt()

    for ortholog in orthologs:
        for fp in ortholog.path.iterdir():
            duplicate(fp, result.path / os.path.basename(fp))

    return result


def partition_orthologs(
        orthologs: SeedOrthologDirFmt, num_partitions: int = None
) -> SeedOrthologDirFmt:
    """
    Returns a dictionary where each key is either the sample_id and
    values are the new objects with the orthologs.
    """
    partitioned_orthologs = {}

    # TODO: this logic should move to the format itself
    orthologs = glob.glob(os.path.join(str(orthologs), "*.seed_orthologs"))
    names = [
        os.path.basename(x).replace(".emapper.seed_orthologs", "")
        for x in orthologs
    ]
    orthologs = list(zip(names, orthologs))

    num_samples = len(orthologs)
    if num_partitions is None:
        num_partitions = num_samples
    elif num_partitions > num_samples:
        warnings.warn(
            "You have requested a number of partitions"
            f" '{num_partitions}' that is greater than your number"
            f" of samples '{num_samples}.' Your data will be"
            f" partitioned by sample into '{num_samples}'"
            " partitions."
        )
        num_partitions = num_samples

    orthologs = np.array_split(orthologs, num_partitions)
    for i, samples in enumerate(orthologs, 1):
        result = SeedOrthologDirFmt()

        for sample_id, sample_fp in samples:
            duplicate(sample_fp, result.path / os.path.basename(sample_fp))

        # If num_partitions == num_samples we will only have gone through one
        # sample in the above loop and will use its id as a key. Otherwise we
        # may have gone through multiple samples in the above loop and will be
        # using indices for keys
        if num_partitions == num_samples:
            partitioned_orthologs[sample_id] = result
        else:
            partitioned_orthologs[i] = result

    return partitioned_orthologs


def collate_genomes(
    genomes: Union[DNAFASTAFormat, GenomeSequencesDirectoryFormat],
    on_duplicates: str = "warn",
) -> GenomeSequencesDirectoryFormat:
    genomes_dir = GenomeSequencesDirectoryFormat()
    error_on_duplicates = True if on_duplicates == "error" else False
    ids = set()
    duplicate_ids = set()
    msg = "Duplicate sequence files were found for the following IDs: {}."
    if isinstance(genomes[0], DNAFASTAFormat):
        for genome_file in genomes:
            for genome in genome_file.view(DNAIterator):
                fn = genome.metadata["id"]
                if fn not in ids:
                    with open(os.path.join(genomes_dir.path, fn + ".fasta"),
                              "w") as f:
                        skbio.io.write(genome, format="fasta", into=f)
                    ids.add(fn)
                else:
                    duplicate_ids.add(fn)
                    if error_on_duplicates:
                        raise ValueError(msg.format(", ".join(duplicate_ids)))

    else:
        for genome in genomes:
            for fp in genome.path.iterdir():
                fn = os.path.basename(fp)
                if fn not in ids:
                    shutil.copyfile(
                        fp,
                        os.path.join(genomes_dir.path, fn),
                    )
                    ids.add(fn)
                else:
                    duplicate_ids.add(fn)
                    if error_on_duplicates:
                        raise ValueError(msg.format(", ".join(duplicate_ids)))

    if duplicate_ids:
        warn(
            msg.format(", ".join(sorted(duplicate_ids)))
            + " The latest occurrence will overwrite all previous "
            "occurrences for each corresponding ID."
        )

    return genomes_dir
