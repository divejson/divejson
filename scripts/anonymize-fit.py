#!/usr/bin/env python3
"""Remove identifying FIT metadata while preserving native dive readings byte for byte.

Requires fitdecode, installed with divejson. Run with an input export and an output path.
Only allowlisted native fields survive. Timestamps receive one fixed shift; all other
retained field payloads are copied from the export without numeric re-encoding.
"""
from __future__ import annotations

import argparse
import io
import struct
from datetime import datetime, timezone
from pathlib import Path

import fitdecode

EPOCH = datetime(1989, 12, 31, tzinfo=timezone.utc)
ANONYMOUS_START = datetime(2000, 1, 1, tzinfo=timezone.utc)
FIELDS = {
    "file_id": {0, 1, 2},  # type, manufacturer, product
    "session": {2, 5, 7, 8, 140, 141, 143, 144, 155, 253},
    "dive_summary": {0, 1, 2, 3, 5, 6, 9, 11, 253},
    "dive_gas": {0, 1, 2, 254},
    "record": {13, 92, 93, 95, 96, 97, 129, 253},
}
TIMESTAMPS = {("session", 2), ("session", 253), ("dive_summary", 253), ("record", 253)}


def crc16(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xA001 if crc & 1 else 0)
    return crc


def anonymize(data: bytes) -> bytes:
    with fitdecode.FitReader(io.BytesIO(data), keep_raw_chunks=True) as reader:
        frames = list(reader)
    header = next(frame for frame in frames if isinstance(frame, fitdecode.FitHeader))
    messages = [frame for frame in frames if isinstance(frame, fitdecode.FitDataMessage)]
    session = next(frame for frame in messages if frame.name == "session")
    shift = int((ANONYMOUS_START - session.get_value("start_time")).total_seconds())
    body = bytearray()
    definitions: dict[bytes, int] = {}
    for frame in messages:
        allowed = FIELDS.get(frame.name)
        if allowed is None:
            continue
        fields = []
        payload = bytearray()
        offset = 1
        for field in frame.def_mesg.field_defs:
            # A compressed header omits timestamp bytes; materialise that timestamp below.
            compressed = frame.time_offset is not None and field.def_num == 253
            raw = frame.chunk.bytes[offset:offset + field.size] if not compressed else b""
            if not compressed:
                offset += field.size
            if field.def_num not in allowed:
                continue
            if (frame.name, field.def_num) in TIMESTAMPS:
                value = frame.get_value(field.def_num)
                if value is None:
                    continue
                raw = struct.pack(frame.def_mesg.endian + "I", int((value - EPOCH).total_seconds()) + shift)
            fields.append((field.def_num, field.size, field.base_type.identifier))
            payload += raw
        assert fields
        architecture = 0 if frame.def_mesg.endian == "<" else 1
        definition = bytes([0, architecture]) + struct.pack(frame.def_mesg.endian + "H", frame.global_mesg_num)
        definition += bytes([len(fields)]) + b"".join(bytes(field) for field in fields)
        if definition not in definitions:
            if len(definitions) >= 16:
                raise ValueError("the reduced export needs more than 16 native message definitions")
            local = len(definitions)
            definitions[definition] = local
            body += bytes([0x40 | local]) + definition
        body += bytes([definitions[definition]]) + payload
    encoded_header = bytes([12, header.proto_ver[0] << 4 | header.proto_ver[1]])
    encoded_header += struct.pack("<HI", header.profile_ver[0] * 100 + header.profile_ver[1], len(body)) + b".FIT"
    result = encoded_header + body
    result += struct.pack("<H", crc16(result))
    with fitdecode.FitReader(io.BytesIO(result), check_crc=fitdecode.CrcCheck.RAISE) as reader:
        for frame in reader:
            if isinstance(frame, fitdecode.FitDataMessage):
                assert all(field.def_num in FIELDS[frame.name] for field in frame.def_mesg.field_defs)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_bytes(anonymize(args.input.read_bytes()))


if __name__ == "__main__":
    main()
