# ----------------------------------------------------------------------------
# Copyright (c) 2026, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


def collate_contig_maps(contig_maps: dict) -> dict:
    collated_contig_maps = {}
    for contig_map in contig_maps:
        collated_contig_maps.update(contig_map)

    return collated_contig_maps
