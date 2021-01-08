import struct

from collections import namedtuple as _nt
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


mbr_header_struct = struct.Struct("<B3sB3sII") # Must be size of 16.
assert mbr_header_struct.size == MBR_PART_LEN

MBRPartHeader = _nt(
    "MBRPartitionHeader",
    (
        "status",
        "chs_addr_first",
        "partition_type",
        "chs_addr_last",
        "lba_start",
        "lba_count"
    )
)


class MBR():
    """Parse MBR from bytes."""
    def __init__(self, b: bytes):
        assert len(b) == LBA_SIZE
        self._code = b[0:MBR_CODE_MAX]
        self._headers_raw = b[
            MBR_CODE_MAX: MBR_CODE_MAX+MBR_PART_LEN*MBR_NPART
        ]
        self._mark = b[MBR_CODE_MAX+MBR_PART_LEN*MBR_NPART:]
        self.headers = tuple(
            MBRPartHeader(*mbr_header_struct.unpack(part_b))
            for part_b in (
                self._headers_raw[i*MBR_PART_LEN:i*MBR_PART_LEN+MBR_PART_LEN]
                for i in range(MBR_NPART)
            )
        )
        return
    
    def __str__(self) -> str:
        return "<code={}[{}] headers={} mark={}>".format(
            type(self._code), len(self._code), self.headers, self._mark
        )
    
    @property
    def code(self) -> bytes:
        return self._code
    
    @property
    def mark(self) -> bytes:
        return self.mark
    pass
