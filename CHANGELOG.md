# Changelog

All notable changes to this project are documented in this file.

## [0.2.0] - 2026-07-22

### Added

- `BaseConstrainedTypedInt`, a real callable branded integer class with
  declarative `gt`, `ge`, `lt`, `le`, and `multiple_of` constraints.
- Constraint configuration and violation exceptions.
- Constraint-aware inheritance, including monotonic range narrowing and least
  common multiple composition for multiple inheritance.
- Strict Pydantic v2 validation, plain integer serialization, and JSON Schema
  generation for constrained integer types.
- Runtime, Pydantic, pickle, public API, and static typing coverage for
  constrained integer classes.
- Canonical guidance for coding agents to use callable constrained classes
  instead of reusable `Annotated` aliases.

### Changed

- Hardened `BaseTypedInt` construction, representation, pickle support, and
  Pydantic serialization against overridden integer conversion hooks.
- Updated the package description and public version for the new constrained
  integer API.

## [0.1.1] - 2026-04-18

### Changed

- Tightened constructor typing and improved documentation and examples.

## [0.1.0] - 2026-03-23

### Added

- Initial `BaseTypedInt` release with strict integer construction, exact runtime
  subtype preservation, pickle support, and optional Pydantic v2 integration.

[0.2.0]: https://github.com/eldenizfamilyanskicode/base-typed-int/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/eldenizfamilyanskicode/base-typed-int/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/eldenizfamilyanskicode/base-typed-int/releases/tag/v0.1.0
