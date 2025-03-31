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
from qiime2.core.type import (
    Int, Range, Collection, List, TypeMatch, Properties
)

import q2_types
from q2_types import __version__

from q2_types.feature_data_mag import MAG
import q2_types.kraken2
from q2_types.per_sample_sequences import (MAGs,
                                           JoinedSequencesWithQuality,
                                           SequencesWithQuality,
                                           PairedEndSequencesWithQuality)
from q2_types.feature_data import FeatureData
from q2_types.genome_data import Orthologs, GenomeData, NOG, Loci
from q2_types.genome_data._methods import collate_loci
from q2_types.sample_data import SampleData
from q2_types.kraken2 import Kraken2Reports, Kraken2Outputs


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
demux_param_descriptions = {
    'demux_description': 'The demultiplexed sequences to partition.',
    'num_partitions': 'The number of partitions to split the'
                      ' demultiplexed sequences into. Defaults to'
                      ' partitioning into individual samples.',
    'partitioned_demux': 'The partitioned demultiplexed sequences.',
    'name': 'Split demultiplexed sequence data into partitions.'
}

T = qiime2.plugin.TypeMatch([SequencesWithQuality, JoinedSequencesWithQuality])
plugin.methods.register_function(
    function=q2_types.per_sample_sequences.partition_samples_single,
    inputs={'demux': SampleData[T]},
    parameters={'num_partitions': Int % Range(1, None)},
    outputs=[
        ('partitioned_demux', Collection[SampleData[T]]),
    ],
    input_descriptions={
        'demux': demux_param_descriptions['demux_description']
    },
    parameter_descriptions={
        'num_partitions':  demux_param_descriptions['num_partitions']
    },
    output_descriptions={
        'partitioned_demux': demux_param_descriptions['partitioned_demux']
    },
    name=demux_param_descriptions['name'],
    description=('Partition demultiplexed single end or joined '
                 'sequences into individual samples or the number of '
                 'partitions specified.'),
)

plugin.methods.register_function(
    function=q2_types.per_sample_sequences.partition_samples_paired,
    inputs={'demux': SampleData[PairedEndSequencesWithQuality]},
    parameters={'num_partitions': Int % Range(1, None)},
    outputs=[
        ('partitioned_demux',
         Collection[SampleData[PairedEndSequencesWithQuality]]),
    ],
    input_descriptions={
        'demux': demux_param_descriptions['demux_description']
    },
    parameter_descriptions={
        'num_partitions': demux_param_descriptions['num_partitions']
    },
    output_descriptions={
        'partitioned_demux': demux_param_descriptions['partitioned_demux']
    },
    name=demux_param_descriptions['name'],
    description=('Partition demultiplexed paired end sequences into '
                 'individual samples or the number of partitions specified.'),
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

plugin.methods.register_function(
    function=collate_loci,
    inputs={"loci": List[GenomeData[Loci]]},
    parameters={},
    outputs={"collated_loci": GenomeData[Loci]},
    input_descriptions={"loci": "A collection of loci to be collated."},
    name="Collate loci",
    description="Takes a collection of GenomeData[Loci]'s "
                "and collates them into a single artifact.",
)

KRAKEN2_REPORTS = TypeMatch([
    SampleData[Kraken2Reports % Properties('reads')],
    SampleData[Kraken2Reports % Properties('contigs')],
    SampleData[Kraken2Reports % Properties('mags')],
    FeatureData[Kraken2Reports % Properties('mags')],
])
plugin.methods.register_function(
    function=q2_types.kraken2.collate_kraken2_reports,
    inputs={
        'kraken2_reports': List[KRAKEN2_REPORTS],
    },
    parameters={},
    outputs={
        'collated_kraken2_reports': KRAKEN2_REPORTS
    },
    input_descriptions={
        'kraken2_reports': 'The kraken2 reports to collate.'
    },
    parameter_descriptions={},
    output_descriptions={
        'collated_kraken2_reports': 'The collated kraken2 reports.'
    },
    name="Collate kraken2 reports.",
    description=""
)

KRAKEN2_OUTPUTS = TypeMatch([
    SampleData[Kraken2Outputs % Properties('reads')],
    SampleData[Kraken2Outputs % Properties('contigs')],
    SampleData[Kraken2Outputs % Properties('mags')],
    FeatureData[Kraken2Outputs % Properties('mags')],
])
plugin.methods.register_function(
    function=q2_types.kraken2.collate_kraken2_outputs,
    inputs={
        'kraken2_outputs': List[KRAKEN2_OUTPUTS],
    },
    parameters={},
    outputs={
        'collated_kraken2_outputs': KRAKEN2_OUTPUTS
    },
    input_descriptions={
        'kraken2_outputs': 'The kraken2 outputs to collate.'
    },
    parameter_descriptions={},
    output_descriptions={
        'collated_kraken2_outputs': 'The collated kraken2 outputs.'
    },
    name="Collate kraken2 outputs.",
    description=""
)

KRAKEN2_REPORTS = TypeMatch([
    SampleData[Kraken2Reports % Properties('reads')],
    SampleData[Kraken2Reports % Properties('contigs')],
    SampleData[Kraken2Reports % Properties('mags')],
    FeatureData[Kraken2Reports % Properties('mags')],
])
plugin.methods.register_function(
    function=q2_types.kraken2.partition_kraken2_reports,
    inputs={
        'reports': KRAKEN2_REPORTS,
    },
    parameters={
        'num_partitions': Int % Range(1, None),
    },
    outputs={
        'partitioned_reports': Collection[KRAKEN2_REPORTS]
    },
    input_descriptions={
        'reports': 'The kraken2 reports to partition.'
    },
    parameter_descriptions={
        'num_partitions': (
            'The desired number of partitions. Defaults to one partition per '
            'sample.'
        ),
    },
    output_descriptions={
        'partitioned_reports': 'The partitioned kraken2 reports.'
    },
    name="Partition kraken2 reports.",
    description=""
)

KRAKEN2_OUTPUTS = TypeMatch([
    SampleData[Kraken2Outputs % Properties('reads')],
    SampleData[Kraken2Outputs % Properties('contigs')],
    SampleData[Kraken2Outputs % Properties('mags')],
    FeatureData[Kraken2Outputs % Properties('mags')],
])
plugin.methods.register_function(
    function=q2_types.kraken2.partition_kraken2_outputs,
    inputs={
        'outputs': KRAKEN2_OUTPUTS,
    },
    parameters={
        'num_partitions': Int % Range(1, None),
    },
    outputs={
        'partitioned_outputs': Collection[KRAKEN2_OUTPUTS]
    },
    input_descriptions={
        'outputs': 'The kraken2 outputs to partition.'
    },
    parameter_descriptions={
        'num_partitions': (
            'The desired number of partitions. Defaults to one partition per '
            'sample.'
        ),
    },
    output_descriptions={
        'partitioned_outputs': 'The partitioned kraken2 outputs.'
    },
    name="Partition kraken2 outputs.",
    description=""
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
importlib.import_module('q2_types.tabular._deferred_setup')
