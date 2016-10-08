# Version 0.0.5 (2016-10-08)

* MAINT: removes generic citation/support info in favor of default (#70)

* MAINT: update artifacts to new format (#69)

* TST: Add format, transformer, and type tests to FeatureData (#60)

* TST: Add format, transformer, and type tests to FeatureTable (#64)

* ENH: adds transformers (#68)

* ENH: Pluralize registrations

* FIX/REF: Remove dupe BIOM registration, register formats

* ENH: adds transformer supporting biom 1.0.0 import (#66)

* ENH: biom.Table -> pd.DataFrame transformer (#65)

* TST: Update import location of TestPluginBase (#63)

* BUG: ignore axis metadata for BIOM v1 and v2 readers/writers (#61)

* BUG: fixes broken transformer (#59)

* ENH: makes iterators importable (#58)

* BUG: bootstrap matplotib config (#57)

* BIOM v2.1.0 support (#53)

* MAINT: update .qza files to archive version 0.3.0 (#55)

* BUG: add package data to setup.py (#54)

* BUG: DNAIterator -> DNAFASTAFormat now uses gener. (#51)

* BUG: PairedDNAIt->PairedDNASeqDirFmt write_data (#52)

* TST: distance matrix subpackage (#40)

* REF/ENH: organized imports into subpackages (#38)

* ENH: adds demux types and transformers (#36)

* ENH/REF: Use new view-types/transformers (#34)

* ENH: add compatible/small rooted/unrooted phylogeny .qza files (#33)

* BUG: remove incompatible/large phylogeny .qza files (#32)

* ENH: adds Rooted and Unrooted subtypes to Phylogeny

# Version 0.0.2-dev

## Other changes
* Added ``BIOMV210Format``

# Version 0.0.2 (2016-08-08)

## Backward incompatible changes
* ``Phylogeny`` now defines subtypes ``Rooted`` and ``Unrooted``.
* The ``AlphaDiversity`` type was removed in favor of ``SampleData[AlphaDiversity]``.

## Other changes
* Several new types were added:
  * ``FeatureData[Taxonomy]``
  * ``FeatureData[Sequence]``
  * ``FeatureData[AlignedSequence]``
  * ``ReferenceFeatures[SSU]``
  * ``SampleData[AlphaDiversity]``

# Version 0.0.1 (2016-07-14)

Initial alpha release. At this stage, major backwards-incompatible API changes are expected to happen.
