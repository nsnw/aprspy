import json
import pytest

from aprspy import APRS
from aprspy.packets.generic import GenericPacket
from aprspy.packets.position import PositionPacket
from aprspy.exceptions import GenerateError

RAW_POSITION = 'XX1XX>APRS,TCPIP*,qAC,TEST:!4903.50N/07201.75W-Test'


@pytest.fixture
def position():
    return APRS.parse_packet(RAW_POSITION)


# --- to_dict ---

def test_to_dict_returns_dict(position):
    assert isinstance(position.to_dict(), dict)


def test_to_dict_has_latitude(position):
    d = position.to_dict()
    assert 'latitude' in d
    assert d['latitude'] == 49.058333


def test_to_dict_has_longitude(position):
    d = position.to_dict()
    assert 'longitude' in d
    assert d['longitude'] == -72.029167


def test_to_dict_strips_underscore_prefix(position):
    d = position.to_dict()
    assert 'latitude' in d
    assert '_latitude' not in d


# --- to_json ---

def test_to_json_returns_string(position):
    assert isinstance(position.to_json(), str)


def test_to_json_is_valid_json(position):
    j = position.to_json()
    parsed = json.loads(j)
    assert isinstance(parsed, dict)


def test_to_json_has_latitude(position):
    parsed = json.loads(position.to_json())
    assert parsed['latitude'] == 49.058333


# --- generate ---

def test_generate():
    p = GenericPacket()
    p.source = "XX1XX"
    p.destination = "APRS"
    p.path = "TCPIP*,qAC,TEST"
    p.data_type_id = ">"
    p.info = "Test status"
    result = p.generate()
    assert result == "XX1XX>APRS,TCPIP*,qAC,TEST:>Test status"


def test_generate_missing_source():
    p = GenericPacket()
    p.destination = "APRS"
    p.path = "TCPIP*,qAC,TEST"
    p.data_type_id = "!"
    with pytest.raises(GenerateError):
        p.generate()


def test_generate_missing_destination():
    p = GenericPacket()
    p.source = "XX1XX"
    p.path = "TCPIP*,qAC,TEST"
    p.data_type_id = "!"
    with pytest.raises(GenerateError):
        p.generate()


def test_generate_missing_path():
    p = GenericPacket()
    p.source = "XX1XX"
    p.destination = "APRS"
    p.data_type_id = "!"
    with pytest.raises(GenerateError):
        p.generate()
