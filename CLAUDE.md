# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (includes dev tools)
poetry install --with=dev

# Run tests
make test
# or directly
pytest

# Run a single test file
pytest tests/test_position.py -v

# Run a single test by name
pytest tests/test_position.py::TestPositionPacket::test_parse -v

# Build documentation
make doc

# Build distribution
make dist
```

## Architecture

**aprspy** is a Python library for parsing and generating APRS (Automatic Packet Reporting System) packets used in amateur radio.

### Entry point

`APRS` class in `aprspy/__init__.py` is the sole public API. All methods are classmethods — users never instantiate it. `APRS.parse_packet(raw_str)` is the main parsing entry point; it returns a typed `Packet` subclass.

### Packet hierarchy

`packets/base.py` defines the `Packet` base class. Each subclass in `aprspy/packets/` handles a distinct APRS data type, identified by `data_type_id` (a single character at the start of the info field):

| Class | `data_type_id` | Notes |
|---|---|---|
| `PositionPacket` | `! / = @` | Largest/most complex; handles compressed and uncompressed position |
| `MICEPacket` | `` ` ' `` | Mic-E encoded position |
| `MessagePacket` | `:` | Also parent of telemetry definition packets |
| `ObjectPacket` | `;` | |
| `ItemReportPacket` | `)` | |
| `StatusPacket` | `>` | |
| `TelemetryPacket` | `T` | |
| `BeaconPacket` | destination in `BEACON_ADDRESSES` | |
| `GenericPacket` | fallback | |

Telemetry sub-types (`TelemetryParameterNamePacket`, `TelemetryUnitLabelPacket`, etc.) are message packets with structured info fields matching patterns like `::[call]:PARM.`.

### Key supporting modules

- `components.py` — `Station` (callsign + SSID) and `Path` (routing path with `QConstruct` enum)
- `utils.py` — Protocol-level parsing helpers (coordinate decoding, compression, base-91 encoding, etc.)
- `exceptions.py` — `ParseError`, `GenerateError`, `UnsupportedError`, `InvalidSourceException`, `InvalidDestinationException` (all extend `APRSException`)

### Test data

`tests/data.py` contains shared raw packet strings and expected parsed values used across test files.

## Wiki

Project documentation lives on the wiki at https://wiki.nsnw.ca/

| Page | Content |
|---|---|
| [NSNW:aprspy](https://wiki.nsnw.ca/wiki/NSNW:aprspy) | Architecture, packet hierarchy, key files, API overview |
| [NSNW:aprspy/Log](https://wiki.nsnw.ca/wiki/NSNW:aprspy/Log) | Dated development history and non-obvious notes |
| [NSNW:aprspy/Todo](https://wiki.nsnw.ca/wiki/NSNW:aprspy/Todo) | Bugs, improvements, and ideas |
| [APRS](https://wiki.nsnw.ca/wiki/APRS) | APRS protocol hub (14 sub-pages covering spec details) |

When doing significant work on this project, add a dated entry to `NSNW:aprspy/Log` and update `NSNW:aprspy/Todo` accordingly.

### Adding a new packet type

1. Create `aprspy/packets/<name>.py` with a class extending `Packet`
2. Implement the `parse()` classmethod (calls `super().parse()` first for base fields)
3. Register the type in `APRS.get_packet_type()` in `aprspy/__init__.py`
4. Add tests in `tests/test_<name>.py`
