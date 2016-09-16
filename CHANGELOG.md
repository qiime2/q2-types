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
