# ----------------------------------------------------------------------------
# Copyright (c) 2016-2022, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType
from . import Bowtie2IndexDirFmt
from ..plugin_setup import plugin


# Technically there is a bit more to this, for instance the ref sequences may
# or may not be present in an index, or may be the only thing in an index,
# but let's not worry about that just yet.
Bowtie2Index = SemanticType('Bowtie2Index')

plugin.register_semantic_types(Bowtie2Index)
plugin.register_artifact_class(Bowtie2Index, Bowtie2IndexDirFmt)
