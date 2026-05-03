import pytest

from aprspy import APRS
from aprspy.packets.station_capability import StationCapabilityPacket

RAW = 'XX1XX>APRS,TCPIP*,qAC,TEST:<IGATE,MSG_CNT=3,LOC_CNT=1'
RAW_NO_VALUES = 'XX1XX>APRS,TCPIP*,qAC,TEST:<IGATE,RELAY'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW)


def test_empty():
    assert repr(StationCapabilityPacket()) == "<StationCapabilityPacket>"


def test_type(packet):
    assert type(packet) == StationCapabilityPacket


def test_repr(packet):
    assert repr(packet) == f"<StationCapabilityPacket: {packet.source}>"


def test_data_type_id(packet):
    assert packet.data_type_id == "<"


def test_capabilities_count(packet):
    assert len(packet.capabilities) == 3


def test_capability_token_only(packet):
    assert packet.capabilities[0] == ('IGATE',)


def test_capability_with_value(packet):
    assert packet.capabilities[1] == ('MSG_CNT', '3')
    assert packet.capabilities[2] == ('LOC_CNT', '1')


def test_capabilities_token_only():
    p = APRS.parse_packet(RAW_NO_VALUES)
    assert ('IGATE',) in p.capabilities
    assert ('RELAY',) in p.capabilities
