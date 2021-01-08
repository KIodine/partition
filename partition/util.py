from io import IOBase

from .const import (
    LBA_SIZE,
)


# Move this function to `utils.py`?
def iter_chunk(f: IOBase, chunk_sz: int):
    #assert f.tell() == 0
    while True:
        buf = f.read(chunk_sz)
        if len(buf) == 0:
            break
        if len(buf) < chunk_sz:
            raise Exception(
                f"Misaligned chunk size, size={len(buf)}, ftell={f.tell()}."
            )
        yield buf
    return

def iter_lba(f: IOBase):
    return iter_chunk(f, LBA_SIZE)
