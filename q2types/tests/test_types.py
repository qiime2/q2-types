# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import glob
import os.path
import tempfile
import unittest

import q2types
from qiime.sdk import Artifact


class TypesTests(unittest.TestCase):

    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'data')

    def test_load_save(self):
        # confirm that for every example artifact in the repository,
        # the artifact can be loaded and a new artifact saved and reloaded
        artifact_fps = glob.glob(os.path.join(self.data_dir, '*qtf'))
        for artifact_fp in artifact_fps:
            # load example artifact
            a = Artifact(artifact_fp)
            with tempfile.NamedTemporaryFile(suffix='.qtf') as f:
                # save loaded artifact
                a.save(a.data, a.type, a.provenance, f.name)
                # reload saved artifact
                Artifact(f.name)

    def test_all_types_represented(self):
        # confirm that all types defined in this repository have at lease one
        # example artifact
        all_types = set(q2types.__all__)
        artifact_fps = glob.glob(os.path.join(self.data_dir, '*qtf'))
        for artifact_fp in artifact_fps:
            a = Artifact(artifact_fp)
            for type_imports in a.type().get_imports():
                type_name = type_imports[0]
                if type_name in all_types:
                    all_types.remove(type_name)
        self.assertEqual(len(all_types), 0,
                         "Example artifact not included for type(s): %s"
                         % ', '.join(all_types))


if __name__ == "__main__":
    unittest.main()
