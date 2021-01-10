from . import (
    gpt, mbr
)

from copy import deepcopy
from dataclasses import astuple
from functools import partial
from io import IOBase, SEEK_SET, FileIO
from zlib import crc32

from .const import (
    LBA_SIZE,
    MBR_FSMARK_PROTECTIVE,
    GPT_COMMON_HEADER_SZ
)
from .gpt import (
    gpt_header_sz,
    gpt_struct,
)


# NOTE: The UEFI reference does not mention which CRC32 it is using,
#   but the one in `zlib` produces desired results, so I assume that's
#   the case.

# PROPOSAL:
#   - Add `write_table` method, convert object back to bytes.


__all__ = [
    "PartitionTable"
]


class PartitionTable():
    """Partition tables from a disk."""
    # infos: MBR, GPT, size of partitions.
    def __init__(
            self, f: FileIO, lba_size: int=LBA_SIZE,
        ):
        self.MBR = None
        self.GPT = None
        self.gpt_partitions = None
        # ---
        # > Keep raw buffers?
        mbr_b = f.read(lba_size)
        # Avoid incomplete buffer.
        assert len(mbr_b) == lba_size
        self.MBR = mbr.MBR(mbr_b)
        if self.MBR.headers[0].partition_type != MBR_FSMARK_PROTECTIVE:
            return
        
        gpt_b = f.read(lba_size)
        assert len(gpt_b) == lba_size
        
        gpt_hdr_sz = gpt_header_sz.unpack(gpt_b[:gpt_header_sz.size])
        assert len(gpt_hdr_sz) == 1
        if gpt_hdr_sz[0] != GPT_COMMON_HEADER_SZ:
            raise Warning(
                "The header you're reading might have different structure "+
                "that this implementation cannot parse properly!"
            )

        self.GPT = gpt.GPT(gpt_b)
        self.gpt_partitions = gpt.parse_entries(
            f, self.GPT.part_entries, self.GPT.part_entry_size
        )

        if self.isGPT is False:
            return

        # Verify checksum.

        f.seek(lba_size*self.GPT.part_start_lba, SEEK_SET)
        tmp_crc32 = crc32(
            f.read(self.GPT.part_entries*self.GPT.part_entry_size)
        )
        assert self.GPT.part_entries_crc32 == tmp_crc32

        tmp_gpt = deepcopy(self.GPT)
        tmp_gpt.header_crc32 = 0
        # NOTE: We assume dataclasses retains the order which fields are
        #   declared, otherwise we are going to hardcode the fields.
        tmp_gpt_b = gpt_struct.pack(*astuple(tmp_gpt))
        tmp_crc32 = crc32(tmp_gpt_b[0:self.GPT.header_size])
        assert self.GPT.header_crc32 == tmp_crc32

        del tmp_gpt, tmp_gpt_b, tmp_crc32

        return
    
    @property
    def isMBR(self):
        return self.GPT is None

    @property
    def isGPT(self):
        return not self.GPT is None

    # def write_table(self) -> bytes:

    pass

