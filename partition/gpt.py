import struct

from collections import namedtuple as _nt
from io import (
    IOBase,
)
from typing import (
    List,
)

from . import mbr
from .util import (
    iter_chunk
)
from .const import (
    LBA_SIZE,
    GPT_HEADER_SIZE,
    GPT_ENTRY_SIZE,
)

__all__ = [
    "GPT",
    "GPTHeader",
    "GPTEntry",
    "GPTPartEntry",
    "parse_entries",
]


gpt_struct = struct.Struct("<8s4sII4sQQQQ16sQIII420s")
assert gpt_struct.size == LBA_SIZE
entry_struct = struct.Struct("<16s16sQQQ72s")

GPTHeader = _nt(
    "GPTHeader",
    (
        "signature",
        "revision",
        "header_size",
        "header_crc32",
        "reserved_0",
        "current_lba",
        "backup_lba",
        "first_lba",
        "last_lba",             # inclusive.
        "disk_guid",
        "part_start_lba",
        "part_entries",
        "part_entry_size",      # Canonnically 128.
        "part_entries_crc32",
        "reserved_1"
    )
)

GPTPartEntry = _nt(
    "GPTPartitionEntry",
    (
        "type_guid",
        "unique_guid",
        "first_lba",
        "last_lba",
        "attr_flags",
        "name", # UTF-16
    )
)


def GPT(b: bytes) -> GPTHeader:
    assert len(b) == LBA_SIZE
    return GPTHeader(
        *gpt_struct.unpack(b)
    )

def GPTEntry(b: bytes) -> GPTPartEntry:
    # Hard-coded size, are there different size exists?
    assert len(b) == GPT_ENTRY_SIZE
    return GPTPartEntry(
        *entry_struct.unpack(b)
    )


# or from file?
def parse_entries(f: IOBase, n: int, size: int) -> List[GPTPartEntry]:
    chunk_reader = iter_chunk(f, size)
    return [
        GPTEntry(next(chunk_reader)) for _ in range(n)
    ]