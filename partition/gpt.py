import struct

from collections import namedtuple as _nt
from dataclasses import dataclass
from io import (
    FileIO,
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
    GPT_TYPE_NONE,
)


# TODO: (Done)Modify program, no hardcoded LBA size.
#   In that case, how to adapt struct format to variable LBA size?
#   Just don't count reserved bytes?


__all__ = [
    "GPT",
    "GPTHeader",
    "GPTEntry",
    "GPTPartitionEntry",
    "parse_entries",
]

gpt_header_sz = struct.Struct("<12xI") # read header size only.
gpt_struct = struct.Struct("<8s4sII4sQQQQ16sQIII") #420s")
#assert gpt_struct.size == LBA_SIZE
entry_struct = struct.Struct("<16s16sQQQ72s")


@dataclass
class GPTHeader():
    # ---
    signature: bytes
    revision: bytes
    header_size: int
    header_crc32: int
    reserved_0: bytes
    current_lba: int
    backup_lba: int
    first_lba: int
    last_lba: int
    disk_guid: bytes
    part_start_lba: int
    part_entries: int
    part_entry_size: int        # usually 128.
    part_entries_crc32: int
    #reserved_1: bytes
    # ---
    @property
    def disk_size(self):
        return (self.backup_lba + 1)*LBA_SIZE
    pass

@dataclass
class GPTPartitionEntry():
    # ---
    type_guid: bytes
    unique_guid: bytes
    first_lba: int
    last_lba: int
    attr_flags: int
    name: bytes
    # ---
    @property
    def partition_size(self):
        return (self.last_lba-self.first_lba+1)*LBA_SIZE
    
    @property
    def is_valid_partition(self):
        return (self.type_guid != GPT_TYPE_NONE)
    pass


def GPT(b: bytes) -> GPTHeader:
    assert len(b) >= LBA_SIZE
    return GPTHeader(
        *gpt_struct.unpack(b[:gpt_struct.size])
    )

def GPTEntry(b: bytes) -> GPTPartitionEntry:
    # Hard-coded size, are there different size exists?
    assert len(b) == GPT_ENTRY_SIZE
    return GPTPartitionEntry(
        *entry_struct.unpack(b)
    )


# or from file?
def parse_entries(f: FileIO, n: int, size: int) -> List[GPTPartitionEntry]:
    chunk_reader = iter_chunk(f, size)
    entry_list = list()
    entry = None
    for _ in range(n):
        try:
            entry = GPTEntry(next(chunk_reader))
        except StopIteration:
            raise Exception(f"Insufficient file size: {f.tell()}")
        entry_list.append(entry)
    return entry_list

