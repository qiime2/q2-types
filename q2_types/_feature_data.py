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
from qiime.plugin import SemanticType, DataLayout, FileFormat
from .plugin_setup import plugin


FeatureData = SemanticType('FeatureData', field_names='type')

Taxonomy = SemanticType('Taxonomy', variant_of=FeatureData.field['type'])

Sequence = SemanticType('Sequence', variant_of=FeatureData.field['type'])

PairedEndSequence = SemanticType('PairedEndSequence',
                                 variant_of=FeatureData.field['type'])

AlignedSequence = SemanticType('AlignedSequence',
                               variant_of=FeatureData.field['type'])


class TaxonomyFormat(FileFormat):
    name = 'taxonomy'

    @classmethod
    def sniff(cls, filepath):
        with open(filepath, 'r') as fh:
            # validate up to 10 data lines (i.e. non-comment lines)
            # recreate behavior of zip(fh, range(10)) accounting for comments
            count = 0
            while count < 10:
                line = fh.readline()
                if line == '':
                    break
                elif line.startswith('#'):
                    continue
                else:
                    cells = line.split('\t')
                    if len(cells) < 2:
                        return False
                    count += 1
            return False if count == 0 else True


class DNAFASTAFormat(FileFormat):
    name = 'dna-fasta'

    @classmethod
    def sniff(cls, filepath):
        sniffer = skbio.io.io_registry.get_sniffer('fasta')
        if sniffer(filepath)[0]:
            generator = skbio.io.read(filepath, constructor=skbio.DNA,
                                      format='fasta')
            try:
                for seq, _ in zip(generator, range(5)):
                    pass
                return True
            # ValueError raised by skbio if there are invalid DNA chars.
            except ValueError:
                pass
        return False


class AlignedDNAFASTAFormat(FileFormat):
    name = 'aligned-dna-fasta'

    @classmethod
    def sniff(cls, filepath):
        sniffer = skbio.io.io_registry.get_sniffer('fasta')
        if sniffer(filepath)[0]:
            generator = skbio.io.read(filepath, constructor=skbio.DNA,
                                      format='fasta')
            try:
                initial_length = len(next(generator))
                for seq, _ in zip(generator, range(4)):
                    if len(seq) != initial_length:
                        return False
                return True
            # ValueError raised by skbio if there are invalid DNA chars.
            except (StopIteration, ValueError):
                pass
        return False


taxonomy_data_layout = DataLayout('taxonomy', 1)
taxonomy_data_layout.register_file('taxonomy.tsv', TaxonomyFormat)

dna_sequences_data_layout = DataLayout('dna-sequences', 1)
dna_sequences_data_layout.register_file('dna-sequences.fasta', DNAFASTAFormat)

paired_dna_sequences_data_layout = DataLayout('paired-dna-sequences', 1)
paired_dna_sequences_data_layout.register_file('left-dna-sequences.fasta',
                                               DNAFASTAFormat)
paired_dna_sequences_data_layout.register_file('right-dna-sequences.fasta',
                                               DNAFASTAFormat)

aligned_dna_sequences_data_layout = DataLayout('aligned-dna-sequences', 1)
aligned_dna_sequences_data_layout.register_file('aligned-dna-sequences.fasta',
                                                AlignedDNAFASTAFormat)


def _read_taxonomy(data_dir):
    filepath = os.path.join(data_dir, 'taxonomy.tsv')
    # Using read_csv for access to comment parameter, and set index_col,
    # header, and parse_dates to Series.from_csv default settings for
    # better handling of round-trips.
    #
    # Using `dtype=object` and `set_index` to avoid type casting/inference of
    # any columns or the index.
    df = pd.read_csv(filepath, sep='\t', comment='#', header=0,
                     parse_dates=True, skip_blank_lines=True, dtype=object)
    df.set_index(df.columns[0], drop=True, append=False, inplace=True)
    return df


def _write_taxonomy(view, data_dir):
    filepath = os.path.join(data_dir, 'taxonomy.tsv')
    view.to_csv(filepath, sep='\t', header=True, index=True)


def taxonomy_to_pandas_series(data_dir):
    df = _read_taxonomy(data_dir)
    return df.iloc[:, 0]


def taxonomy_to_pandas_dataframe(data_dir):
    df = _read_taxonomy(data_dir)
    return df


def taxonomy_to_qiime_metadata(data_dir):
    df = _read_taxonomy(data_dir)
    return qiime.Metadata(df)


def pandas_to_taxonomy(view, data_dir):
    _write_taxonomy(view, data_dir)


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
