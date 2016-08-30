# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os
import types
from itertools import zip_longest

import skbio
import skbio.io
import pandas as pd

import qiime
from qiime.plugin import SemanticType, TextFileFormat
import qiime.plugin.resource as resource

from .plugin_setup import plugin


FeatureData = SemanticType('FeatureData', field_names='type')

Taxonomy = SemanticType('Taxonomy', variant_of=FeatureData.field['type'])

Sequence = SemanticType('Sequence', variant_of=FeatureData.field['type'])

PairedEndSequence = SemanticType('PairedEndSequence',
                                 variant_of=FeatureData.field['type'])

AlignedSequence = SemanticType('AlignedSequence',
                               variant_of=FeatureData.field['type'])


# Formats
class TaxonomyFormat(TextFileFormat):
    # TODO: revisit sniffer/validation
    pass


class DNAFASTAFormat(TextFileFormat):
    # TODO: revisit sniffer/validation
    pass


class AlignedDNAFASTAFormat(TextFileFormat):
    # TODO: revisit sniffer/validation
    pass


class TaxonomyDirectoryFormat(resource.DirectoryFormat):
    taxonomy = resource.File('taxonomy.tsv', format=TaxonomyFormat)


class DNASequencesDirectoryFormat(resource.DirectoryFormat):
    dna_sequences = resource.File('dna-sequences.fasta', format=DNAFASTAFormat)


class PairedDNASequencesDirectoryFormat(resource.DirectoryFormat):
    left_dna_sequences = resource.File('left-dna-sequences.fasta',
                                       format=DNAFASTAFormat)
    right_dna_sequences = resource.File('right-dna-sequences.fasta',
                                        format=DNAFASTAFormat)


class AlignedDNASequencesDirectoryFormat(resource.DirectoryFormat):
    aligned_dna_sequences = resource.File('aligned-dna-sequences.fasta',
                                          format=AlignedDNAFASTAFormat)


# Transformers
@plugin.register_transformer
def _1(data: pd.DataFrame) -> TaxonomyDirectoryFormat:
    df = TaxonomyDirectoryFormat()
    df.taxonomy.set(data, pd.DataFrame)
    return df


@plugin.register_transformer
def _2(data: pd.DataFrame) -> TaxonomyFormat:
    ff = TaxonomyFormat()
    with ff.open() as fh:
        data.to_csv(fh, sep='\t', header=True, index=True)
    return ff


def _read_taxonomy(fh):
    # Using read_csv for access to comment parameter, and set index_col,
    # header, and parse_dates to Series.from_csv default settings for
    # better handling of round-trips.
    #
    # Using `dtype=object` and `set_index` to avoid type casting/inference of
    # any columns or the index.
    df = pd.read_csv(fh, sep='\t', comment='#', header=0,
                     parse_dates=True, skip_blank_lines=True, dtype=object)
    df.set_index(df.columns[0], drop=True, append=False, inplace=True)
    return df


@plugin.register_transformer
def _3(df: TaxonomyDirectoryFormat) -> pd.DataFrame:
    return df.taxonomy.view(pd.DataFrame)


@plugin.register_transformer
def _4(ff: TaxonomyFormat) -> pd.DataFrame:
    with ff.open() as fh:
        return _read_taxonomy(fh)


@plugin.register_transformer
def _5(df: TaxonomyDirectoryFormat) -> pd.Series:
    return df.taxonomy.view(pd.Series)


@plugin.register_transformer
def _6(ff: TaxonomyFormat) -> pd.Series:
    with ff.open() as fh:
        data = _read_taxonomy(fh)
        return data.iloc[:, 0]


@plugin.register_transformer
def _7(df: TaxonomyDirectoryFormat) -> qiime.Metadata:
    return df.taxonomy.view(qiime.Metadata)


@plugin.register_transformer
def _8(ff: TaxonomyFormat) -> qiime.Metadata:
    with ff.open() as fh:
        data = _read_taxonomy(fh)
        return qiime.Metadata(data)


# LEFT OFF HERE:
######################################################################
# TODO can this be generalized to any iterable type? See:
#     https://github.com/biocore/scikit-bio/issues/1031#issuecomment-225252290
def dna_sequences_to_generator(data_dir):
    return skbio.io.read(os.path.join(data_dir, 'dna-sequences.fasta'),
                         format='fasta', constructor=skbio.DNA)


def generator_to_dna_sequences(view, data_dir):
    file = os.path.join(data_dir, 'dna-sequences.fasta')

    skbio.io.write(view, format='fasta', into=file)


def paired_dna_sequences_to_generator(data_dir):
    left = skbio.io.read(os.path.join(data_dir, 'left-dna-sequences.fasta'),
                         format='fasta', constructor=skbio.DNA)
    right = skbio.io.read(os.path.join(data_dir, 'right-dna-sequences.fasta'),
                          format='fasta', constructor=skbio.DNA)
    for lseq, rseq in zip_longest(left, right):
        if rseq is None:
            raise ValueError('more left sequences than right sequences')
        if lseq is None:
            raise ValueError('more right sequences than left sequences')
        if rseq.metadata['id'] != lseq.metadata['id']:
            raise ValueError(lseq.metadata['id'] + ' and ' +
                             rseq.metadata['id'] + ' differ')
        yield lseq, rseq


def generator_to_paired_dna_sequences(view, data_dir):
    lfilepath = os.path.join(data_dir, 'left-dna-sequences.fasta')
    rfilepath = os.path.join(data_dir, 'right-dna-sequences.fasta')

    with open(lfilepath, 'w') as lfile, open(rfilepath, 'w') as rfile:
        for lseq, rseq in view:
            if rseq.metadata['id'] != lseq.metadata['id']:
                raise ValueError(lseq.metadata['id'] + ' and ' +
                                 rseq.metadata['id'] + ' differ')
            skbio.io.write(lseq, format='fasta', into=lfile)
            skbio.io.write(rseq, format='fasta', into=rfile)


def aligned_dna_sequences_to_tabular_msa(data_dir):
    return skbio.TabularMSA.read(
        os.path.join(data_dir, 'aligned-dna-sequences.fasta'),
        constructor=skbio.DNA, format='fasta')


def tabular_msa_to_aligned_dna_sequences(view, data_dir):
    return view.write(os.path.join(data_dir, 'aligned-dna-sequences.fasta'),
                      format='fasta')


plugin.register_data_layout(taxonomy_data_layout)
plugin.register_data_layout_reader('taxonomy', 1, pd.Series,
                                   taxonomy_to_pandas_series)
plugin.register_data_layout_reader('taxonomy', 1, pd.DataFrame,
                                   taxonomy_to_pandas_dataframe)
plugin.register_data_layout_reader('taxonomy', 1, qiime.Metadata,
                                   taxonomy_to_qiime_metadata)
plugin.register_data_layout_writer('taxonomy', 1, pd.Series,
                                   pandas_to_taxonomy)
plugin.register_data_layout_writer('taxonomy', 1, pd.DataFrame,
                                   pandas_to_taxonomy)

plugin.register_data_layout(dna_sequences_data_layout)
plugin.register_data_layout_reader('dna-sequences', 1, types.GeneratorType,
                                   dna_sequences_to_generator)
plugin.register_data_layout_writer('dna-sequences', 1, types.GeneratorType,
                                   generator_to_dna_sequences)

plugin.register_data_layout(paired_dna_sequences_data_layout)
plugin.register_data_layout_reader('paired-dna-sequences', 1,
                                   types.GeneratorType,
                                   paired_dna_sequences_to_generator)
plugin.register_data_layout_writer('paired-dna-sequences', 1,
                                   types.GeneratorType,
                                   generator_to_paired_dna_sequences)

plugin.register_data_layout(aligned_dna_sequences_data_layout)
plugin.register_data_layout_reader('aligned-dna-sequences', 1,
                                   skbio.TabularMSA,
                                   aligned_dna_sequences_to_tabular_msa)
plugin.register_data_layout_writer('aligned-dna-sequences', 1,
                                   skbio.TabularMSA,
                                   tabular_msa_to_aligned_dna_sequences)

plugin.register_semantic_type(FeatureData)
plugin.register_semantic_type(Taxonomy)
plugin.register_semantic_type(Sequence)
plugin.register_semantic_type(PairedEndSequence)
plugin.register_semantic_type(AlignedSequence)

plugin.register_type_to_data_layout(FeatureData[Taxonomy], 'taxonomy', 1)
plugin.register_type_to_data_layout(FeatureData[Sequence], 'dna-sequences', 1)
plugin.register_type_to_data_layout(FeatureData[PairedEndSequence],
                                    'paired-dna-sequences', 1)
plugin.register_type_to_data_layout(FeatureData[AlignedSequence],
                                    'aligned-dna-sequences', 1)
