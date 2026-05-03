import pytest

from aprspy import APRS
from aprspy.packets.user_defined import UserDefinedPacket

# DTI '{', then user_id='A', packet_type='B', data='SOMEDATA'
RAW = 'XX1XX>APRS,TCPIP*,qAC,TEST:{ABSOMEDATA'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW)


def test_type(packet):
    assert type(packet) == UserDefinedPacket


def test_repr(packet):
    assert repr(packet) == f"<UserDefinedPacket: {packet.source}>"


def test_data_type_id(packet):
    assert packet.data_type_id == "{"
