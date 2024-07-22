# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import setup, find_packages

import versioneer

setup(
    name="q2-types",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    author="Greg Caporaso",
    author_email="gregcaporaso@gmail.com",
    description="Common QIIME 2 semantic types.",
    license='BSD-3-Clause',
    url="https://qiime2.org",
    entry_points={
        'qiime2.plugins':
        ['q2-types=q2_types.plugin_setup:plugin']
    },
    package_data={
        'q2_types': ['citations.bib'],
        'q2_types.tests': ['data/*'],
        'q2_types.bowtie2': ['citations.bib'],
        'q2_types.distance_matrix.tests': ['data/*'],
        'q2_types.feature_data.tests': ['data/*',
                                        'data/taxonomy/*',
                                        'data/emp_multiplexed/*',
                                        'data/emp_multiplexed_single_end/*'],
        'q2_types.feature_map.tests': ['data/*'],
        'q2_types.feature_table.tests': ['data/*'],
        'q2_types.metadata.tests': ['data/*'],
        'q2_types.multiplexed_sequences.tests': [
            'data/*',
            'data/absolute_manifests_v2/*'
            ],
        'q2_types.ordination.tests': ['data/*'],
        'q2_types.per_sample_sequences.tests':
            ['data/*',
             'data/paired_end_data/*',
             'data/paired_end_data_numeric/*',
             'data/single_end_data/*',
             'data/absolute_manifests/*',
             'data/absolute_manifests_v2/*',
             'data/relative_manifests/*',
             'data/qiime1-demux-format/*',
             'data/single-end-two-sample-data1/*',
             'data/single-end-two-sample-data2/*',
             'data/single-end-two-sample-data3/*',
             'data/mags/*/*', 'data/mags/*/*/*',
             'data/manifests/*', 'data/contigs/*',
             'data/diamond_hit/*',
             'data/bowtie/*/*',
             'data/bowtie/*/*/*/*',
             'data/bowtie/*/*/*',
             'data/error_correction_details/*'],
        'q2_types.sample_data.tests': ['data/*'],
        'q2_types.tree.tests': ['data/*'],
        'q2_types.feature_data_mag.tests':
            ['data/*', 'data/*/*',
             'data/mags-fa/*', 'data/mags-fasta/*'],
        'q2_types.genome_data.tests':
            ['data/*',
             'data/genes/*',
             'data/loci-invalid/*',
             'data/loci/*',
             'data/genome-sequences/*',
             'data/ortholog/*',
             'data/ortholog-annotation-extra/*',
             'data/ortholog-annotation-mags/*',
             'data/ortholog-annotation-samples/*',
             'data/ortholog-annotation/*',
             'data/proteins/*',
             ],
        'q2_types.kraken2.tests': [
            'data/*',
            'data/kraken2-db/*',
            'data/bracken-db/*',
            'data/outputs-single/*',
            'data/outputs-reads/*/*',
            'data/outputs-contigs/*',
            'data/outputs-mags/*/*',
            'data/reports-single/*',
            'data/reports-reads/*/*',
            'data/reports-mags/*/*',
            'data/db-reports/**/*'
        ],
        'q2_types.kaiju.tests':
            ['data/*', 'data/db-valid/*'],
        'q2_types.reference_db.tests':
            ['data/*', 'data/*/*', 'data/*/*/*'],
        'q2_types.profile_hmms.tests':
            ['data/*', 'data/*/*']
    },
    zip_safe=False,
)
