import json
import pytest

from aprspy import APRS
from aprspy.packets.generic import GenericPacket
from .data import TEST_PACKET, TEST_SOURCE, TEST_DESTINATION, TEST_PATH, TEST_INFO


@pytest.fixture
def packet():
    return APRS.parse_packet(TEST_PACKET)


def test_to_dict_returns_dict(packet):
    result = packet.to_dict()
    assert isinstance(result, dict)


def test_to_dict_source(packet):
    result = packet.to_dict()
    assert result["source"] == TEST_SOURCE


def test_to_dict_destination(packet):
    result = packet.to_dict()
    assert result["destination"] == TEST_DESTINATION


def test_to_dict_path(packet):
    result = packet.to_dict()
    assert result["path"] == TEST_PATH


def test_to_dict_info(packet):
    result = packet.to_dict()
    assert result["info"] == TEST_INFO


def test_to_json_returns_string(packet):
    result = packet.to_json()
    assert isinstance(result, str)


def test_to_json_is_valid_json(packet):
    result = packet.to_json()
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_to_json_source(packet):
    result = json.loads(packet.to_json())
    assert result["source"] == TEST_SOURCE


def test_to_json_destination(packet):
    result = json.loads(packet.to_json())
    assert result["destination"] == TEST_DESTINATION
