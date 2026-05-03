import pytest

from aprspy import APRS
from aprspy.packets.query import QueryPacket
from aprspy.exceptions import ParseError


RAW_APRS = 'XX1XX>APRS,TCPIP*,qAC,TEST:?APRS?'
RAW_WX = 'XX1XX>APRS,TCPIP*,qAC,TEST:?WX?'
RAW_IGATE = 'XX1XX>APRS,TCPIP*,qAC,TEST:?IGATE?'
RAW_SERVERS = 'XX1XX>APRS,TCPIP*,qAC,TEST:?SERVERS?'
RAW_TARGETED = 'XX1XX>APRS,TCPIP*,qAC,TEST:?APRS?YY2YY-9'
RAW_LOWERCASE = 'XX1XX>APRS,TCPIP*,qAC,TEST:?aprs?'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW_APRS)


@pytest.fixture
def targeted():
    return APRS.parse_packet(RAW_TARGETED)


def test_empty():
    assert repr(QueryPacket()) == "<QueryPacket>"


def test_type(packet):
    assert type(packet) == QueryPacket


def test_repr(packet):
    assert repr(packet) == "<QueryPacket: APRS>"


def test_data_type_id(packet):
    assert packet.data_type_id == "?"


def test_query_type_aprs(packet):
    assert packet.query_type == "APRS"


def test_query_type_wx():
    p = APRS.parse_packet(RAW_WX)
    assert p.query_type == "WX"


def test_query_type_igate():
    p = APRS.parse_packet(RAW_IGATE)
    assert p.query_type == "IGATE"


def test_query_type_servers():
    p = APRS.parse_packet(RAW_SERVERS)
    assert p.query_type == "SERVERS"


def test_query_type_normalised_to_uppercase():
    p = APRS.parse_packet(RAW_LOWERCASE)
    assert p.query_type == "APRS"


def test_no_target(packet):
    assert packet.target is None


def test_targeted_type(targeted):
    assert type(targeted) == QueryPacket


def test_targeted_query_type(targeted):
    assert targeted.query_type == "APRS"


def test_targeted_target(targeted):
    assert targeted.target == "YY2YY-9"
