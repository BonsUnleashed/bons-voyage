"""Minimal NBT writer/reader (stdlib only) for Minecraft structure templates.

Value model used by the writer:
  int        -> TAG_Int
  str        -> TAG_String
  dict       -> TAG_Compound
  list       -> TAG_List (element type inferred from first element; empty -> TAG_End list)
Wrapper classes below force other tag types when needed.
"""
import gzip
import struct
import io

TAG_END, TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG = 0, 1, 2, 3, 4
TAG_FLOAT, TAG_DOUBLE, TAG_BYTE_ARRAY, TAG_STRING = 5, 6, 7, 8
TAG_LIST, TAG_COMPOUND, TAG_INT_ARRAY, TAG_LONG_ARRAY = 9, 10, 11, 12


class Byte(int):
    pass


class IntArray(list):
    pass


def _tag_type(v):
    if isinstance(v, Byte):
        return TAG_BYTE
    if isinstance(v, bool):
        return TAG_BYTE
    if isinstance(v, int):
        return TAG_INT
    if isinstance(v, str):
        return TAG_STRING
    if isinstance(v, dict):
        return TAG_COMPOUND
    if isinstance(v, IntArray):
        return TAG_INT_ARRAY
    if isinstance(v, list):
        return TAG_LIST
    raise TypeError(f"unsupported NBT value: {v!r}")


def _write_payload(out, v, ttype):
    if ttype == TAG_BYTE:
        out.write(struct.pack(">b", int(v)))
    elif ttype == TAG_INT:
        out.write(struct.pack(">i", v))
    elif ttype == TAG_STRING:
        raw = v.encode("utf-8")
        out.write(struct.pack(">H", len(raw)))
        out.write(raw)
    elif ttype == TAG_COMPOUND:
        for name, val in v.items():
            vt = _tag_type(val)
            out.write(struct.pack(">b", vt))
            raw = name.encode("utf-8")
            out.write(struct.pack(">H", len(raw)))
            out.write(raw)
            _write_payload(out, val, vt)
        out.write(b"\x00")
    elif ttype == TAG_LIST:
        et = _tag_type(v[0]) if v else TAG_END
        out.write(struct.pack(">bi", et, len(v)))
        for item in v:
            _write_payload(out, item, et)
    elif ttype == TAG_INT_ARRAY:
        out.write(struct.pack(">i", len(v)))
        for item in v:
            out.write(struct.pack(">i", item))
    else:
        raise TypeError(f"unsupported tag type {ttype}")


def write_nbt(path, root: dict):
    buf = io.BytesIO()
    buf.write(struct.pack(">bH", TAG_COMPOUND, 0))  # root: unnamed compound
    _write_payload(buf, root, TAG_COMPOUND)
    with open(path, "wb") as f:
        f.write(gzip.compress(buf.getvalue(), mtime=0))


# ---- reader (for validation) ----

def _read_payload(f, ttype):
    if ttype == TAG_BYTE:
        return struct.unpack(">b", f.read(1))[0]
    if ttype == TAG_SHORT:
        return struct.unpack(">h", f.read(2))[0]
    if ttype == TAG_INT:
        return struct.unpack(">i", f.read(4))[0]
    if ttype == TAG_LONG:
        return struct.unpack(">q", f.read(8))[0]
    if ttype == TAG_FLOAT:
        return struct.unpack(">f", f.read(4))[0]
    if ttype == TAG_DOUBLE:
        return struct.unpack(">d", f.read(8))[0]
    if ttype == TAG_BYTE_ARRAY:
        n = struct.unpack(">i", f.read(4))[0]
        return list(f.read(n))
    if ttype == TAG_STRING:
        n = struct.unpack(">H", f.read(2))[0]
        return f.read(n).decode("utf-8")
    if ttype == TAG_LIST:
        et, n = struct.unpack(">bi", f.read(5))
        return [_read_payload(f, et) for _ in range(n)]
    if ttype == TAG_COMPOUND:
        d = {}
        while True:
            t = struct.unpack(">b", f.read(1))[0]
            if t == TAG_END:
                return d
            n = struct.unpack(">H", f.read(2))[0]
            name = f.read(n).decode("utf-8")
            d[name] = _read_payload(f, t)
    if ttype in (TAG_INT_ARRAY, TAG_LONG_ARRAY):
        n = struct.unpack(">i", f.read(4))[0]
        sz, fmt = (4, ">i") if ttype == TAG_INT_ARRAY else (8, ">q")
        return [struct.unpack(fmt, f.read(sz))[0] for _ in range(n)]
    raise ValueError(f"bad tag type {ttype}")


def read_nbt(path):
    with gzip.open(path, "rb") as f:
        t = struct.unpack(">b", f.read(1))[0]
        assert t == TAG_COMPOUND, "root must be compound"
        n = struct.unpack(">H", f.read(2))[0]
        f.read(n)
        return _read_payload(f, TAG_COMPOUND)
