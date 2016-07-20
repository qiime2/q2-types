# ----------------------------------------------------------------------------
# Copyright (c) 2016--, QIIME development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os

import skbio
import skbio.io
import pandas as pd

import qiime
from qiime.plugin import SemanticType, DataLayout, FileFormat
from .plugin_setup import plugin


FeatureData = SemanticType('FeatureData', field_names='type')

Taxonomy = SemanticType('Taxonomy', variant_of=FeatureData.field['type'])

Sequence = SemanticType('Sequence', variant_of=FeatureData.field['type'])

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


class FASTAFormat(FileFormat):
    name = 'fasta'

    @classmethod
    def sniff(cls, filepath):
        sniffer = skbio.io.io_registry.get_sniffer('fasta')
        return sniffer(filepath)[0]


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

sequences_data_layout = DataLayout('sequences', 1)
sequences_data_layout.register_file('sequences.fasta', FASTAFormat)

aligned_dna_sequences_data_layout = DataLayout('aligned-dna-sequences', 1)
aligned_dna_sequences_data_layout.register_file('aligned-dna-sequences.fasta',
                                                AlignedDNAFASTAFormat)


def _read_taxonomy(data_dir):
    filepath = os.path.join(data_dir, 'taxonomy.tsv')
    # Using read_csv for access to comment parameter, and set index_col,
    # header, and parse_dates to Series.from_csv default settings for
    # better handling of round-trips
    return pd.read_csv(filepath, sep='\t', comment='#', index_col=0, header=0,
                       parse_dates=True, skip_blank_lines=True, dtype=object)


def _write_taxonomy(view, data_dir):
    filepath = os.path.join(data_dir, 'taxonomy.tsv')
    view.to_csv(filepath, sep='\t', header=True, index=True)


def taxonomy_to_pandas_series(data_dir):
    df = _read_taxonomy(data_dir)
    return df.iloc[:, 0]


def taxonomy_to_qiime_metadata(data_dir):
    df = _read_taxonomy(data_dir)
    return qiime.Metadata(df)


def pandas_to_taxonomy(view, data_dir):
    _write_taxonomy(view, data_dir)


def sequences_to_pandas_series(data_dir):
    index = []
    seqs = []
    for seq in skbio.io.read(os.path.join(data_dir, 'sequences.fasta'),
                             format='fasta'):
        index.append(seq.metadata['id'])
        seqs.append(seq)
    return pd.Series(data=seqs, index=index)


def pandas_series_to_sequences(view, data_dir):
    file = os.path.join(data_dir, 'sequences.fasta')

    # https://github.com/biocore/scikit-bio/issues/1031#issuecomment-225252290
    def generator():
        yield from view

    skbio.io.write(generator(), format='fasta', into=file)


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
plugin.register_data_layout_reader('taxonomy', 1, qiime.Metadata,
                                   taxonomy_to_qiime_metadata)
plugin.register_data_layout_writer('taxonomy', 1, pd.Series,
                                   pandas_to_taxonomy)
plugin.register_data_layout_writer('taxonomy', 1, pd.DataFrame,
                                   pandas_to_taxonomy)

plugin.register_data_layout(sequences_data_layout)
plugin.register_data_layout_reader('sequences', 1, pd.Series,
                                   sequences_to_pandas_series)
plugin.register_data_layout_writer('sequences', 1, pd.Series,
                                   pandas_series_to_sequences)

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
plugin.register_semantic_type(AlignedSequence)

plugin.register_type_to_data_layout(FeatureData[Taxonomy], 'taxonomy', 1)
plugin.register_type_to_data_layout(FeatureData[Sequence], 'sequences', 1)
plugin.register_type_to_data_layout(FeatureData[AlignedSequence],
                                    'aligned-dna-sequences', 1)
