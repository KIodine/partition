import struct

from collections import namedtuple as _nt
from dataclasses import dataclass
from io import IOBase

from .const import (
    LBA_SIZE,
    MBR_CODE_MAX,
    MBR_NPART,
    MBR_PART_LEN,
    MBR_MARK_LEN,
    MBR_MARK_STR,
    MBR_PART_INACT,
    MBR_PART_ACTIV,
    MBR_FSMARK_PROTECTIVE,
)


__all__ = [
    "MBRPartitionHeader",
    "MBR",
]


mbr_header_struct = struct.Struct("<446s64s2s")
mbr_part_header_struct = struct.Struct("<B3sB3sII") # Must be size of 16.
assert mbr_part_header_struct.size == MBR_PART_LEN


@dataclass
class MBRPartitionHeader():
    # ---
    status: int
    chs_addr_first: bytes
    partition_type: int
    chs_addr_last: bytes
    lba_start: int
    lba_count: int
    # ---
    @property
    def is_gpt_protected(self) -> bool:
        return self.partition_type == MBR_FSMARK_PROTECTIVE
    pass


class MBR():
    """Parse MBR from bytes."""
    def __init__(self, b: bytes):
        # LBA might not be 512, but MBR is fixed-sized so this should
        # be fine. Just make sure there's enough stuff to parse.
        assert len(b) >= LBA_SIZE
        # > Use `struct`?
        tmp_struct = mbr_header_struct.unpack(
            b[:mbr_header_struct.size]
        )
        self._code = tmp_struct[0]
        self._headers_raw = tmp_struct[1]
        self._mark = tmp_struct[2]
        self.headers = tuple(
            MBRPartitionHeader(*mbr_part_header_struct.unpack(part_b))
            for part_b in struct.unpack("<16s16s16s16s", self._headers_raw)
        )
        assert self.mark == MBR_MARK_STR
        
        return
    
    def __str__(self) -> str:
        return "<MasterBootRecord code={}[{}] headers={} mark={}>".format(
            type(self._code), len(self._code), self.headers, self._mark
        )
    
    @property
    def code(self) -> bytes:
        return self._code
    
    @property
    def mark(self) -> bytes:
        return self._mark
    pass
