# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import importlib

import pandas as pd

import qiime2.plugin
from qiime2.core.type import Int, Range, Collection, List

import q2_types
from q2_types import __version__

from q2_types.feature_data_mag import MAG
from q2_types.per_sample_sequences import MAGs
from q2_types.feature_data import FeatureData
from q2_types.genome_data import Orthologs, GenomeData, NOG
from q2_types.sample_data import SampleData


citations = qiime2.plugin.Citations.load('citations.bib', package='q2_types')
plugin = qiime2.plugin.Plugin(
    name='types',
    version=__version__,
    website='https://github.com/qiime2/q2-types',
    package='q2_types',
    description=('This QIIME 2 plugin defines semantic types and '
                 'transformers supporting microbiome analysis.'),
    short_description='Plugin defining types for microbiome analysis.'
)

plugin.register_views(pd.Series, pd.DataFrame,
                      citations=[citations['mckinney-proc-scipy-2010']])


plugin.methods.register_function(
    function=q2_types.per_sample_sequences.partition_sample_data_mags,
    inputs={"mags": SampleData[MAGs]},
    parameters={"num_partitions": Int % Range(1, None)},
    outputs={"partitioned_mags": Collection[SampleData[MAGs]]},
    input_descriptions={"mags": "The MAGs to partition."},
    parameter_descriptions={
        "num_partitions": "The number of partitions to split the MAGs"
        " into. Defaults to partitioning into individual"
        " MAGs."
    },
    name="Partition MAGs",
    description="Partition a SampleData[MAGs] artifact into smaller "
                "artifacts containing subsets of the MAGs",
)

plugin.methods.register_function(
    function=q2_types.genome_data.partition_orthologs,
    inputs={"orthologs": SampleData[Orthologs]},
    parameters={"num_partitions": Int % Range(1, None)},
    outputs={"partitioned_orthologs": Collection[SampleData[Orthologs]]},
    input_descriptions={"orthologs": "The orthologs to partition."},
    parameter_descriptions={
        "num_partitions": "The number of partitions to split the MAGs"
        " into. Defaults to partitioning into individual"
        " MAGs."
    },
    name="Partition orthologs",
    description="Partition a SampleData[BLAST6] artifact into smaller "
                "artifacts containing subsets of the BLAST6 reports.",
)

plugin.methods.register_function(
    function=q2_types.per_sample_sequences.collate_sample_data_mags,
    inputs={"mags": List[SampleData[MAGs]]},
    parameters={},
    outputs={"collated_mags": SampleData[MAGs]},
    input_descriptions={"mags": "A collection of MAGs to be collated."},
    name="Collate MAGs",
    description="Takes a collection of SampleData[MAGs]'s "
                "and collates them into a single artifact.",
)

plugin.methods.register_function(
    function=q2_types.feature_data_mag.partition_feature_data_mags,
    inputs={"mags": FeatureData[MAG]},
    parameters={"num_partitions": Int % Range(1, None)},
    outputs={"partitioned_mags": Collection[FeatureData[MAG]]},
    input_descriptions={"mags": "MAGs to partition."},
    parameter_descriptions={
        "num_partitions": "The number of partitions to split the MAGs"
        " into. Defaults to partitioning into individual"
        " MAGs."
    },
    name="Partition MAGs",
    description="Partition a FeatureData[MAG] artifact into smaller "
                "artifacts containing subsets of the MAGs",
)

plugin.methods.register_function(
    function=q2_types.feature_data_mag.collate_feature_data_mags,
    inputs={"mags": List[FeatureData[MAG]]},
    parameters={},
    outputs={"collated_mags": FeatureData[MAG]},
    input_descriptions={"mags": "A collection of MAGs to be collated."},
    name="Collate MAGs",
    description="Takes a collection of FeatureData[MAG]'s "
                "and collates them into a single artifact.",
)

plugin.methods.register_function(
    function=q2_types.genome_data.collate_orthologs,
    inputs={"orthologs": List[SampleData[Orthologs]]},
    parameters={},
    outputs={"collated_orthologs": SampleData[Orthologs]},
    input_descriptions={"orthologs": "Orthologs to collate"},
    parameter_descriptions={},
    name="Collate orthologs",
    description="Takes a collection SampleData[BLAST6] artifacts "
                "and collates them into a single artifact.",
)

plugin.methods.register_function(
    function=q2_types.genome_data.collate_ortholog_annotations,
    inputs={'ortholog_annotations': List[GenomeData[NOG]]},
    parameters={},
    outputs=[('collated_annotations', GenomeData[NOG])],
    input_descriptions={
        'ortholog_annotations': "Collection of ortholog annotations."
    },
    output_descriptions={
        'collated_annotations': "Collated ortholog annotations."
    },
    name='Collate ortholog annotations.',
    description="Takes a collection of GenomeData[NOG]'s "
                "and collates them into a single artifact.",
)

importlib.import_module('q2_types.bowtie2._deferred_setup')
importlib.import_module('q2_types.distance_matrix._deferred_setup')
importlib.import_module('q2_types.feature_data._deferred_setup')
importlib.import_module('q2_types.feature_data_mag._deferred_setup')
importlib.import_module('q2_types.feature_map._deferred_setup')
importlib.import_module('q2_types.feature_table._deferred_setup')
importlib.import_module('q2_types.genome_data._deferred_setup')
importlib.import_module('q2_types.kaiju._deferred_setup')
importlib.import_module('q2_types.kraken2._deferred_setup')
importlib.import_module('q2_types.metadata._deferred_setup')
importlib.import_module('q2_types.multiplexed_sequences._deferred_setup')
importlib.import_module('q2_types.ordination._deferred_setup')
importlib.import_module('q2_types.per_sample_sequences._deferred_setup')
importlib.import_module('q2_types.profile_hmms._deferred_setup')
importlib.import_module('q2_types.reference_db._deferred_setup')
importlib.import_module('q2_types.sample_data._deferred_setup')
importlib.import_module('q2_types.tree._deferred_setup')
