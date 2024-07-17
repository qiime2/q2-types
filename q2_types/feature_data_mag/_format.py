# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import re

from q2_types.feature_data import DNAFASTAFormat
from qiime2.plugin import model

from ..plugin_setup import plugin


class MAGSequencesDirFmt(model.DirectoryFormat):
    pathspec = (
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-"
        r"[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\.(fa|fasta)$"
    )

    sequences = model.FileCollection(pathspec, format=DNAFASTAFormat)

    @sequences.set_path_maker
    def sequences_path_maker(self, mag_id):
        return r'%s.fasta' % mag_id

    def feature_dict(self, relative=False):
        '''
        Returns a mapping of mag id to filepath for each mag.

        Parameters
        ---------
        relative : bool
            Whether to return filepaths relative to the directory's location.
            Returns absolute filepaths by default.

        Returns
        -------
        dict
            Mapping of feature id -> filepath as described above. Sorted
            alphabetically by key.
        '''
        pattern = re.compile(self.pathspec)
        ids = {}
        for path in self.path.iterdir():
            if not pattern.match(path.name):
                continue

            _id = path.stem
            absolute_path = path.absolute()
            if relative:
                ids[_id] = str(
                    absolute_path.relative_to(self.path.absolute())
                )
            else:
                ids[_id] = str(absolute_path)

        return dict(sorted(ids.items()))


plugin.register_formats(MAGSequencesDirFmt)
