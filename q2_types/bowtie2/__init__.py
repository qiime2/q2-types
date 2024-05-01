# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._formats import (Bowtie2IndexFileFormat, Bowtie2IndexDirFmt)
from ._types import Bowtie2Index

from ..plugin_setup import plugin, citations

plugin.register_views(Bowtie2IndexDirFmt,
                      citations=[citations['langmead2012fast']])

__all__ = ['Bowtie2IndexFileFormat', 'Bowtie2IndexDirFmt', 'Bowtie2Index']
