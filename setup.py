# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import setup, find_packages

setup(
    name="q2-types",
    # TODO stop duplicating version string
    version="0.0.7.dev0",
    packages=find_packages(),
    install_requires=['scikit-bio', 'qiime >= 2.0.6', 'pandas',
                      'biom-format >= 2.1.5, < 2.2.0', 'ijson',
                      'h5py'],
    author="Greg Caporaso",
    author_email="gregcaporaso@gmail.com",
    description="Common QIIME 2 semantic types.",
    license='BSD-3-Clause',
    url="http://www.qiime.org",
    entry_points={
        'qiime.plugins':
        ['q2-types=q2_types.plugin_setup:plugin']
    },
    package_data={
        'q2_types.tests': ['data/*'],
        'q2_types.distance_matrix.tests': ['data/*'],
        'q2_types.feature_data.tests': ['data/*'],
        'q2_types.feature_table.tests': ['data/*'],
        'q2_types.ordination.tests': ['data/*'],
        'q2_types.per_sample_sequences.tests': ['data/*',
                                                'data/paired_end_data/*',
                                                'data/single_end_data/*'],
        'q2_types.reference_features.tests': ['data/*'],
        'q2_types.sample_data.tests': ['data/*'],
        'q2_types.tree.tests': ['data/*']
    }
)
