# aprspy - An APRS packet parser for Python

[![version](https://img.shields.io/pypi/v/aprspy.svg)](https://pypi.python.org/pypi/aprspy)
[![license](https://img.shields.io/pypi/l/aprspy.svg)](https://github.com/nsnw/aprspy/blob/master/COPYING)
[![build](https://travis-ci.org/nsnw/aprspy.svg?branch=master)](https://travis-ci.org/nsnw/aprspy)
[![docs](https://readthedocs.org/projects/aprspy/badge/?version=latest)](https://aprspy.readthedocs.io/en/latest/?badge=latest)
[![issues](https://img.shields.io/github/issues/nsnw/aprspy.svg)](https://github.com/nsnw/aprspy/issues)
[![coverage-status](https://coveralls.io/repos/github/nsnw/aprspy/badge.svg?branch=master)](https://coveralls.io/github/nsnw/aprspy?branch=master)

## Introduction

**aprspy** is an APRS packet parser and generator for Python.

Currently supports:-

### Decoding
 * Standard compressed/uncompressed location packets
 * Mic-E location packets
 * Message packets (including bulletins and announcements)
 * Status report packets

### Encoding
 * Uncompressed location packets
 * Message packets

## Usage

Brief usage explanation:

```
    >>> from aprspy import APRS
    >>> packet = APRS.parse('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005Test packet')
    >>> packet
    <PositionPacket: XX1XX>
    >>> packet.latitude
    50.508333
    >>> packet.longitude
    -100.338333
    >>> packet.course
    221
```

## Documentation

Documentation can be found at
<https://aprspy.readthedocs.io/en/latest/>.

## Development

Dependencies are now managed with `poetry`, and dependencies needed for development can be installed with
`poetry install --with=dev`.

The documentation can be built locally by running `make` in the `docs/`
folder.

## Copyright

This module is released under the MIT License, and is copyright 2019-2025
Andy Smith.
