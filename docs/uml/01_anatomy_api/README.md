# Anatomy API

## Purpose
Defines the structural vocabulary for brain regions, areas, nuclei, cortical layers, and coordinates.

## Contract
- `BrainRegion`: hierarchical anatomical container.
- `BrainArea`: functional/anatomical subdivision.
- `Nucleus`: subcortical anatomical unit.
- `CorticalLayer`: layer metadata and local population membership.
- `AnatomicalCoordinate`: coordinate/provenance representation.

## Invariants
Regions have stable IDs; parent/child relationships form a directed hierarchy; anatomical labels are metadata, not claims of one-to-one functional equivalence.

## Tests
Validate construction, parent/child relationships, serialization, and unknown-region handling.

## UML
See `../01_anatomy_api.puml`.
