from . import (
    gpt, mbr
)

from io import IOBase
from functools import partial

from .const import (
    LBA_SIZE,
)


__all__ = [
    "PartitionTable"
]


class PartitionTable():
    """Partition tables from a disk."""
    pass

