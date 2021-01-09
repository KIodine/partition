from . import (
    gpt, mbr
)

from io import IOBase
from functools import partial

from .const import (
    LBA_SIZE,
    MBR_FSMARK_PROTECTIVE,
)


__all__ = [
    "PartitionTable"
]


class PartitionTable():
    """Partition tables from a disk."""
    # infos: MBR, GPT, size of partitions.
    def __init__(self, f: IOBase):
        self.MBR = None
        self.GPT = None
        self.gpt_partitions = None
        # ---
        mbr_b = f.read(LBA_SIZE)
        assert len(mbr_b) == LBA_SIZE
        self.MBR = mbr.MBR(mbr_b)
        if self.MBR.headers[0].partition_type != MBR_FSMARK_PROTECTIVE:
            return
        
        gpt_b = f.read(LBA_SIZE)
        assert len(gpt_b) == LBA_SIZE
        self.GPT = gpt.GPT(gpt_b)
        self.gpt_partitions = gpt.parse_entries(
            f, self.GPT.part_entries, self.GPT.part_entry_size
        )
        return
    
    @property
    def isMBR(self):
        return self.GPT is None

    @property
    def isGPT(self):
        return not self.GPT is None

    pass

