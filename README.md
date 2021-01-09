# partition
`partition` library provides several facilities for parsing MBR/GPT to
structured objects.

## Description

## Limitation
Must run python > 3.7 for module `dataclasses`.

## Feature
`partition` currently supports MBR and GPT parsing, may add writing some day.

## Installation
TODO

## Usage
```python
byte_file = ... # some way for providing file-like object
table = partition.PartitionTable(byte_file)
table.isGPT # property indicating is GPT partition table exists.
```

## License
`partition` is distributed under MIT license.

## References
- [UEFI spec v2.8](https://uefi.org/sites/default/files/resources/UEFI_Spec_2_8_final.pdf)
