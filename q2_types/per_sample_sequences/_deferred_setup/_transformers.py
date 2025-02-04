# ----------------------------------------------------------------------------
# Copyright (c) 2016-2025, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import shutil
import functools
import re
import warnings
import skbio
import yaml
import pandas as pd

import qiime2.util

from q2_types.feature_data import DNAFASTAFormat

from .. import (
    SingleLanePerSampleSingleEndFastqDirFmt,
    FastqAbsolutePathManifestFormat,
    FastqManifestFormat,
    FastqGzFormat,
    SingleLanePerSamplePairedEndFastqDirFmt,
    YamlFormat,
    CasavaOneEightSingleLanePerSampleDirFmt,
    CasavaOneEightLanelessPerSampleDirFmt,
    SingleEndFastqManifestPhred33,
    SingleEndFastqManifestPhred64,
    PairedEndFastqManifestPhred33,
    PairedEndFastqManifestPhred64,
    SingleEndFastqManifestPhred33V2,
    SingleEndFastqManifestPhred64V2,
    PairedEndFastqManifestPhred33V2,
    PairedEndFastqManifestPhred64V2,
    QIIME1DemuxDirFmt,
    SampleIdIndexedSingleEndPerSampleDirFmt,
    MultiMAGManifestFormat,
    MultiMAGSequencesDirFmt,
    MultiFASTADirectoryFormat
)
from .._util import (
    _single_lane_per_sample_fastq_helper,
    _dirfmt_to_casava,
    _parse_and_validate_manifest,
    _copy_with_compression,
    _fastq_manifest_helper,
    _phred64_warning,
    _write_phred64_to_phred33,
    _manifest_v2_to_v1,
    _manifest_to_df,
    _mag_manifest_helper
)

from ...plugin_setup import plugin

# Partially apply the helpers here, to cut down on boilerplate.

_fastq_manifest_helper_partial = functools.partial(
    _fastq_manifest_helper,
    se_fmt=SingleLanePerSampleSingleEndFastqDirFmt,
    pe_fmt=SingleLanePerSamplePairedEndFastqDirFmt,
    abs_manifest_fmt=FastqAbsolutePathManifestFormat,
    manifest_fmt=FastqManifestFormat,
    yaml_fmt=YamlFormat,
)

_parse_and_validate_manifest_partial = functools.partial(
    _parse_and_validate_manifest,
    abs_manifest_fmt=FastqAbsolutePathManifestFormat,
    manifest_fmt=FastqManifestFormat,
)


_single_lane_per_sample_fastq_helper_partial = functools.partial(
    _single_lane_per_sample_fastq_helper,
    manifest_fmt=FastqManifestFormat,
    fastq_fmt=FastqGzFormat,
    yaml_fmt=YamlFormat,
)

_dirfmt_to_casava_partial = functools.partial(
    _dirfmt_to_casava,
    manifest_fmt=FastqManifestFormat,
    abs_manifest_fmt=FastqAbsolutePathManifestFormat,
    fastq_fmt=FastqGzFormat,
    casava_fmt=CasavaOneEightSingleLanePerSampleDirFmt,
)


@plugin.register_transformer
def _1(dirfmt: CasavaOneEightSingleLanePerSampleDirFmt) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    return _single_lane_per_sample_fastq_helper_partial(
        dirfmt, SingleLanePerSampleSingleEndFastqDirFmt)


@plugin.register_transformer
def _2(dirfmt_in: SingleLanePerSampleSingleEndFastqDirFmt) \
        -> CasavaOneEightSingleLanePerSampleDirFmt:
    return _dirfmt_to_casava_partial(dirfmt_in)


@plugin.register_transformer
def _3(dirfmt: CasavaOneEightSingleLanePerSampleDirFmt) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    return _single_lane_per_sample_fastq_helper_partial(
        dirfmt, SingleLanePerSamplePairedEndFastqDirFmt)


@plugin.register_transformer
def _4(dirfmt_in: SingleLanePerSamplePairedEndFastqDirFmt) \
        -> CasavaOneEightSingleLanePerSampleDirFmt:
    return _dirfmt_to_casava_partial(dirfmt_in)


@plugin.register_transformer
def _5(dirfmt: CasavaOneEightLanelessPerSampleDirFmt) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    return _single_lane_per_sample_fastq_helper_partial(
        dirfmt, SingleLanePerSampleSingleEndFastqDirFmt, parse_lane=False)


@plugin.register_transformer
def _6(dirfmt: CasavaOneEightLanelessPerSampleDirFmt) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    return _single_lane_per_sample_fastq_helper_partial(
        dirfmt, SingleLanePerSamplePairedEndFastqDirFmt, parse_lane=False)


@plugin.register_transformer
def _7(dirfmt: SingleLanePerSamplePairedEndFastqDirFmt) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    with dirfmt.manifest.view(FastqManifestFormat).open() as fh:
        input_manifest = _parse_and_validate_manifest_partial(
            fh, single_end=False, absolute=False)

    output_manifest = FastqManifestFormat()
    output_df = input_manifest[input_manifest.direction == 'forward']
    with output_manifest.open() as fh:
        output_df.to_csv(fh, index=False)

    result = SingleLanePerSampleSingleEndFastqDirFmt()
    result.manifest.write_data(output_manifest, FastqManifestFormat)
    for _, _, filename, _ in output_df.itertuples():
        qiime2.util.duplicate(str(dirfmt.path / filename),
                              str(result.path / filename))

    metadata = YamlFormat()
    metadata.path.write_text(yaml.dump({'phred-offset': 33}))
    result.metadata.write_data(metadata, YamlFormat)

    return result


@plugin.register_transformer
def _8(fmt: SingleEndFastqManifestPhred33) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    return _fastq_manifest_helper_partial(fmt, _copy_with_compression,
                                          single_end=True)


@plugin.register_transformer
def _9(fmt: SingleEndFastqManifestPhred64) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    warnings.warn(_phred64_warning)
    return _fastq_manifest_helper_partial(fmt, _write_phred64_to_phred33,
                                          single_end=True)


@plugin.register_transformer
def _10(fmt: PairedEndFastqManifestPhred33) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    return _fastq_manifest_helper_partial(fmt, _copy_with_compression,
                                          single_end=False)


@plugin.register_transformer
def _11(fmt: PairedEndFastqManifestPhred64) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    warnings.warn(_phred64_warning)
    return _fastq_manifest_helper_partial(fmt, _write_phred64_to_phred33,
                                          single_end=False)


@plugin.register_transformer
def _12(dirfmt: SingleLanePerSampleSingleEndFastqDirFmt) \
        -> QIIME1DemuxDirFmt:
    with dirfmt.manifest.view(FastqManifestFormat).open() as fh:
        input_manifest = _parse_and_validate_manifest_partial(
            fh, single_end=True, absolute=False)

    result = QIIME1DemuxDirFmt()
    fp = str(result.path / 'seqs.fna')
    with open(fp, 'w') as fh:
        i = 0
        for r in input_manifest.iterrows():
            sample_id = r[1]['sample-id']
            filename = r[1]['filename']
            if re.search(r"\s", sample_id) is not None:
                raise ValueError(
                    "Whitespace was found in the ID for sample %s. Sample "
                    "IDs with whitespace are incompatible with FASTA."
                    % sample_id)
            fq_reader = skbio.io.read('%s/%s' % (str(dirfmt), filename),
                                      format='fastq', constructor=skbio.DNA,
                                      phred_offset=33, verify=False)
            for seq in fq_reader:
                seq.metadata['id'] = '%s_%d' % (sample_id, i)
                seq.write(fh)
                i += 1

    return result


@plugin.register_transformer
def _13(ff: FastqManifestFormat) -> pd.DataFrame:
    return _manifest_to_df(ff, ff.path.parent)


@plugin.register_transformer
def _14(fmt: SingleEndFastqManifestPhred33V2) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    old_fmt = _manifest_v2_to_v1(fmt, FastqManifestFormat)
    return _fastq_manifest_helper_partial(old_fmt, _copy_with_compression,
                                          single_end=True)


@plugin.register_transformer
def _15(fmt: SingleEndFastqManifestPhred64V2) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    warnings.warn(_phred64_warning)
    old_fmt = _manifest_v2_to_v1(fmt, FastqManifestFormat)
    return _fastq_manifest_helper_partial(old_fmt, _write_phred64_to_phred33,
                                          single_end=True)


@plugin.register_transformer
def _16(fmt: PairedEndFastqManifestPhred33V2) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    old_fmt = _manifest_v2_to_v1(fmt, FastqManifestFormat)
    return _fastq_manifest_helper_partial(old_fmt, _copy_with_compression,
                                          single_end=False)


@plugin.register_transformer
def _17(fmt: PairedEndFastqManifestPhred64V2) \
        -> SingleLanePerSamplePairedEndFastqDirFmt:
    warnings.warn(_phred64_warning)
    old_fmt = _manifest_v2_to_v1(fmt, FastqManifestFormat)
    return _fastq_manifest_helper_partial(old_fmt, _write_phred64_to_phred33,
                                          single_end=False)


@plugin.register_transformer
def _18(dirfmt: SampleIdIndexedSingleEndPerSampleDirFmt) \
        -> SingleLanePerSampleSingleEndFastqDirFmt:
    return _single_lane_per_sample_fastq_helper_partial(
        dirfmt, SingleLanePerSampleSingleEndFastqDirFmt,
        parse_sample_id_only=True)


@plugin.register_transformer
def _19(dirfmt: MultiFASTADirectoryFormat) \
        -> MultiMAGSequencesDirFmt:
    return _mag_manifest_helper(
        dirfmt, MultiMAGSequencesDirFmt,
        MultiMAGManifestFormat, DNAFASTAFormat)


@plugin.register_transformer
def _20(ff: MultiMAGManifestFormat) -> pd.DataFrame:
    df = pd.read_csv(str(ff), header=0, comment='#')
    df.filename = df.filename.apply(
        lambda f: os.path.join(ff.path.parent, f))
    df.set_index(['sample-id', 'mag-id'], inplace=True)
    return df


@plugin.register_transformer
def _21(dirfmt: MultiMAGSequencesDirFmt) \
        -> MultiFASTADirectoryFormat:
    result = MultiFASTADirectoryFormat()
    for sample_id, mag in dirfmt.sample_dict().items():
        os.makedirs(os.path.join(result.path, sample_id))
        for mag_id, mag_fp in mag.items():
            shutil.copy(
                mag_fp, os.path.join(result.path, sample_id, f"{mag_id}.fa")
            )
    return result
