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


@pytest.mark.parametrize("raw,expected_info", [
    ('N0HI-7>ID,KB9KC,qAR,VE3QBZ-7:N0HI-7 LinBPQ Switch on Raspberry Pi4', 'N0HI-7 LinBPQ Switch on Raspberry Pi4'),
    ('DISABL>ID,qAR,N6PAZ-10:Network Node', 'Network Node'),
    ('K8QIK-13>ID,qAR,KB8UVN-7:Network node (STSSW1)', 'Network node (STSSW1)'),
    ('KB8UVN-7>ID,qAR,K8GPS-10:Network node (JTSW1)', 'Network node (JTSW1)'),
    ('WL7CLI>ID,qAR,K0IRO-10:NONE, WL7CLI digipeater, NONE gateway', 'NONE, WL7CLI digipeater, NONE gateway'),
])
def test_id_destination_info_preserved(raw, expected_info):
    # ID-destination frames carry freeform text; the leading char must not be
    # consumed as a data_type_id.
    p = APRS.parse_packet(raw)
    assert type(p) == BeaconPacket
    assert p.data_type_id is None
    assert p.info == expected_info
