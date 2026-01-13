# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json

from .. import MAGtoContigsFormat, FeatureMapFormat

from ...plugin_setup import plugin


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


@plugin.register_transformer
def _3(fp: FeatureMapFormat) -> dict:
    data = {}
    with fp.open() as fh:
        for line in fh:
            feature = json.loads(line)
            data[feature["name"]] = feature["members"]
    return data


@plugin.register_transformer
def _4(data: dict) -> FeatureMapFormat:
    fp = FeatureMapFormat()
    with fp.open() as fh:
        for k, v in data.items():
            fh.write(json.dumps({"name": k, "members": v}) + "\n")
    return fp
