import pytest

from aprspy import APRS, StatusPacket
from aprspy.exceptions import ParseError

# Input packets
raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>211248zPHG71801/Test status'
raw_with_timestamp = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>091234zTest status with a timestamp'
raw_without_timestamp = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>Test status without a timestamp'
raw_with_mh6 = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21XA/- Test status with 6 digit Maidenhead locator'
raw_with_mh6_without_status = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21XA/-'
raw_with_mh4 = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21/- Test status with 4 digit Maidenhead locator'
raw_with_mh4_without_status = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21/-'
raw_with_hdg_and_pwr = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>Test status with heading and power^B7'


@pytest.fixture
def packet():
    packet = APRS.parse(raw)
    return packet


@pytest.fixture
def packet_with_timestamp():
    packet = APRS.parse(raw_with_timestamp)
    return packet


@pytest.fixture
def packet_without_timestamp():
    packet = APRS.parse(raw_without_timestamp)
    return packet


@pytest.fixture
def packet_with_mh6():
    packet = APRS.parse(raw_with_mh6)
    return packet


@pytest.fixture
def packet_with_mh6_without_status():
    packet = APRS.parse(raw_with_mh6_without_status)
    return packet


@pytest.fixture
def packet_with_mh4():
    packet = APRS.parse(raw_with_mh4)
    return packet


@pytest.fixture
def packet_with_mh4_without_status():
    packet = APRS.parse(raw_with_mh4_without_status)
    return packet


@pytest.fixture
def packet_with_hdg_and_pwr():
    packet = APRS.parse(raw_with_hdg_and_pwr)
    return packet


def test_empty_packet():
    packet = StatusPacket()

    assert repr(packet) == "<StatusPacket>"


def test_type(packet):
    assert type(packet) == StatusPacket


def test_repr(packet):
    assert repr(packet) == f"<StatusPacket: {packet.source}>"


def test_data_type_id(packet):
    assert packet.data_type_id == ">"


def test_status_message(packet):
    assert packet.status_message == "PHG71801/Test status"


def test_with_mh6_maidenhead_locator(packet_with_mh6):
    assert packet_with_mh6.maidenhead_locator == "DO21XA"


def test_with_mh6_symbol_table(packet_with_mh6):
    assert packet_with_mh6.symbol_table == "/"


def test_with_mh6_symbol_id(packet_with_mh6):
    assert packet_with_mh6.symbol_id == "-"


def test_with_mh6_status_message(packet_with_mh6):
    assert packet_with_mh6.status_message == "Test status with 6 digit Maidenhead locator"


def test_with_mh6_without_status_status_message(packet_with_mh6_without_status):
    assert packet_with_mh6_without_status.status_message is None


def test_with_mh4_symbol_table(packet_with_mh4):
    assert packet_with_mh4.symbol_table == "/"


def test_with_mh4_symbol_id(packet_with_mh4):
    assert packet_with_mh4.symbol_id == "-"


def test_with_mh4_maidenhead_locator(packet_with_mh4):
    assert packet_with_mh4.maidenhead_locator == "DO21"


def test_with_mh4_status_message(packet_with_mh4):
    assert packet_with_mh4.status_message == "Test status with 4 digit Maidenhead locator"


def test_with_mh4_without_status_status_message(packet_with_mh4_without_status):
    assert packet_with_mh4_without_status.status_message is None


def test_with_hdg_and_pwr_status_message(packet_with_hdg_and_pwr):
    assert packet_with_hdg_and_pwr.status_message == "Test status with heading and power^B7"


def test_invalid_mh6_status_message_missing_initial_space():
    with pytest.raises(ParseError):
        # Invalid status message - missing initial space
        raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21XA/-Test status with 6 digit Maidenhead locator'
        APRS.parse(raw)


def test_invalid_mh4_status_message_missing_initial_space():

    with pytest.raises(ParseError):
        # Invalid status message - missing initial space
        raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21/-Test status with 4 digit Maidenhead locator'
        APRS.parse(raw)
