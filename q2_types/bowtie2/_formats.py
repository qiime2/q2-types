# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import itertools

from qiime2.plugin import model


class Bowtie2IndexFileFormat(model.BinaryFileFormat):
    def _validate_(self, level):
        # It's not clear if there is any way to tell if a Bowtie2 index is
        # correct or not.
        # bowtie2 does have an inspect method — this inspects at the dir level
        # not on the file level.
        # may also want to validate that all files have the same basename
        pass


class Bowtie2IndexDirFmt(model.DirectoryFormat):
    idx1 = model.File(r'.+(?<!\.rev)\.1\.bt2l?', format=Bowtie2IndexFileFormat)
    idx2 = model.File(r'.+(?<!\.rev)\.2\.bt2l?', format=Bowtie2IndexFileFormat)
    ref3 = model.File(r'.+\.3\.bt2l?', format=Bowtie2IndexFileFormat)
    ref4 = model.File(r'.+\.4\.bt2l?', format=Bowtie2IndexFileFormat)
    rev1 = model.File(r'.+\.rev\.1\.bt2l?', format=Bowtie2IndexFileFormat)
    rev2 = model.File(r'.+\.rev\.2\.bt2l?', format=Bowtie2IndexFileFormat)

    def get_basename(self):
        paths = [str(x.relative_to(self.path)) for x in self.path.iterdir()]
        prefix = _get_prefix(paths)
        return prefix[:-1]  # trim trailing '.'


# SO: https://stackoverflow.com/a/6718380/579416
def _get_prefix(strings):
    def all_same(x):
        return all(x[0] == y for y in x)

    char_tuples = zip(*strings)
    prefix_tuples = itertools.takewhile(all_same, char_tuples)
    return ''.join(x[0] for x in prefix_tuples)
