import pytest

from aprspy import APRS
from aprspy.packets.beacon import BeaconPacket

RAW = 'XX1XX>BEACON,TCPIP*,qAC,TEST:This is a beacon'

@pytest.fixture
def packet():
    return APRS.parse_packet(RAW)


def test_empty():
    assert repr(BeaconPacket()) == "<BeaconPacket>"


def test_type(packet):
    assert type(packet) == BeaconPacket


def test_repr(packet):
    assert repr(packet) == f"<BeaconPacket: {packet.source}>"


def test_data_type_id(packet):
    assert packet.data_type_id is None


def test_comment(packet):
    assert packet.comment == "This is a beacon"


def test_comment_setter():
    p = BeaconPacket()
    p.comment = "hello"
    assert p.comment == "hello"


def test_source(packet):
    assert str(packet.source) == "XX1XX"
