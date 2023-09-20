# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json

from . import MAGtoContigsFormat

from ..plugin_setup import plugin


@plugin.register_transformer
def _1(fp: MAGtoContigsFormat) -> dict:
    with fp.open() as fh:
        data = json.load(fh)
    return data


@plugin.register_transformer
def _2(data: dict) -> MAGtoContigsFormat:
    fp = MAGtoContigsFormat()
    with fp.open() as fh:
        json.dump(data, fh)
    return fp
