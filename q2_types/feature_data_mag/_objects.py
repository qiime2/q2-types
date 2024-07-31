# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import collections.abc


class MAGIterator(collections.abc.Iterable):
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        yield from self.generator
