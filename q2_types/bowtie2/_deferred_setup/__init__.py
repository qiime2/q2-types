# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import Citations

from .. import Bowtie2IndexDirFmt
from .. import Bowtie2Index

from ...plugin_setup import plugin

citations = Citations.load('citations.bib', package='q2_types.bowtie2')
plugin.register_views(Bowtie2IndexDirFmt,
                      citations=[citations['langmead2012fast']])

plugin.register_semantic_types(Bowtie2Index)

plugin.register_artifact_class(
    Bowtie2Index,
    directory_format=Bowtie2IndexDirFmt,
    description='An index of sequences for Bowtie 2 to search against.'
)
