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
    version="0.0.1",
    packages=find_packages(),
    install_requires=['scikit-bio', 'qiime >= 2.0.0', 'pandas',
                      'biom-format >= 2.1.5, < 2.2.0', 'ijson'],
    author="Greg Caporaso",
    author_email="gregcaporaso@gmail.com",
    description="Common QIIME 2 semantic types.",
    license="BSD",
    url="http://www.qiime.org",
    entry_points={
        'qiime.plugins':
        ['q2-types=q2_types.plugin_setup:plugin']
    }
)
