# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from ._formats import (Bowtie2IndexFileFormat, Bowtie2IndexDirFmt)
from ._types import Bowtie2Index

__all__ = ['Bowtie2IndexFileFormat', 'Bowtie2IndexDirFmt', 'Bowtie2Index']
