# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
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
        'q2_types.distance_matrix.tests': ['data/*'],
        'q2_types.feature_data.tests': ['data/*', 'data/taxonomy/*'],
        'q2_types.feature_table.tests': ['data/*'],
        'q2_types.multiplexed_sequences.tests': ['data/*'],
        'q2_types.ordination.tests': ['data/*'],
        'q2_types.per_sample_sequences.tests':
            ['data/*',
             'data/paired_end_data/*',
             'data/single_end_data/*',
             'data/absolute_manifests/*',
             'data/absolute_manifests_v2/*',
             'data/relative_manifests/*',
             'data/qiime1-demux-format/*',
             'data/single-end-two-sample-data1/*',
             'data/single-end-two-sample-data2/*',
             'data/single-end-two-sample-data3/*'],
        'q2_types.sample_data.tests': ['data/*'],
        'q2_types.tree.tests': ['data/*']
    },
    zip_safe=False,
)
