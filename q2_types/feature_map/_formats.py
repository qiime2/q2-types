# ----------------------------------------------------------------------------
# Copyright (c) 2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json
from uuid import UUID

from qiime2.plugin import model, ValidationError


class MAGtoContigsFormat(model.TextFileFormat):
    def _validate_(self, level):
        with self.path.open("r") as fh:
            data = json.load(fh)

            level_map = {"min": 1, "max": len(data)}
            max_entries = level_map[level]

            # assert keys are proper UUIDs and dict values are lists
            # with at least one contig
            for _id, contigs in list(data.items())[:max_entries]:
                try:
                    UUID(_id, version=4)
                except ValueError:
                    raise ValidationError(
                        "MAG IDs must be valid UUID version 4 sequences. "
                        f'Found "{_id}", which is invalid.'
                    )

                if not isinstance(contigs, list):
                    raise ValidationError(
                        "Values corresponding to MAG IDs must be lists of "
                        f'contigs. Found "{type(contigs)}" for MAG "{_id}".'
                    )

                if len(contigs) == 0:
                    raise ValidationError(
                        "Only non-empty MAGs are allowed. The list of "
                        f'contigs for MAG "{_id}" is empty.'
                    )


MAGtoContigsDirFmt = model.SingleFileDirectoryFormat(
    "MAGtoContigsDirFmt", "mag-to-contigs.json", MAGtoContigsFormat
)


class FeatureMapFormat(model.TextFileFormat):
    def _validate_(self, level):
        level_map = {"min": 1, "max": float("inf")}

        feature_map = {}
        with self.path.open("r") as fh:
            for i, line in enumerate(fh):
                if i > level_map[level]:
                    break

                try:
                    data = json.loads(line)
                except json.decoder.JSONDecodeError:
                    raise ValidationError(f"Invalid JSONL file: {self.path}")

                feature_id = data["name"]
                members = data["members"]

                if feature_id in feature_map:
                    raise ValidationError(
                        f"Duplicate feature ID: {feature_id}"
                    )

                if not isinstance(members, list):
                    raise ValidationError(
                        f"Values corresponding to feature IDs must be lists "
                        f"of member features. Found {type(members)} for "
                        f"feature '{feature_id}'."
                    )

                if len(members) == 0:
                    raise ValidationError(
                        "Only non-empty feature members are allowed. The "
                        f"list of members for feature '{feature_id}' "
                        "is empty."
                    )

                feature_map[feature_id] = members


FeatureMapDirFmt = model.SingleFileDirectoryFormat(
    "FeatureMapDirFmt",
    "feature-map.json",
    FeatureMapFormat
)
