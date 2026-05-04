import pytest

from aprspy import APRS
from aprspy.packets.status import StatusPacket
from aprspy.exceptions import ParseError


RAW = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>211248zPHG71801/Test status'
RAW_WITH_TIMESTAMP = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>091234zTest status with a timestamp'
RAW_WITHOUT_TIMESTAMP = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>Test status without a timestamp'
RAW_WITH_MH6 = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21XA/- Test status with 6 digit Maidenhead locator'
RAW_WITH_MH6_WITHOUT_STATUS = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21XA/-'
RAW_WITH_MH4 = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21/- Test status with 4 digit Maidenhead locator'
RAW_WITH_MH4_WITHOUT_STATUS = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21/-'
RAW_WITH_HDG_AND_PWR = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>Test status with heading and power^B7'
RAW_EMPTY_INFO = 'XX1XX-1>APRS,TCPIP*,qAC,TEST:>'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW)


@pytest.fixture
def packet_with_timestamp():
    return APRS.parse_packet(RAW_WITH_TIMESTAMP)


@pytest.fixture
def packet_without_timestamp():
    return APRS.parse_packet(RAW_WITHOUT_TIMESTAMP)


@pytest.fixture
def packet_with_mh6():
    return APRS.parse_packet(RAW_WITH_MH6)


@pytest.fixture
def packet_with_mh6_without_status():
    return APRS.parse_packet(RAW_WITH_MH6_WITHOUT_STATUS)


@pytest.fixture
def packet_with_mh4():
    return APRS.parse_packet(RAW_WITH_MH4)


@pytest.fixture
def packet_with_mh4_without_status():
    return APRS.parse_packet(RAW_WITH_MH4_WITHOUT_STATUS)


@pytest.fixture
def packet_with_hdg_and_pwr():
    return APRS.parse_packet(RAW_WITH_HDG_AND_PWR)


def test_empty_packet():
    assert repr(StatusPacket()) == "<StatusPacket>"


def test_type(packet):
    assert type(packet) == StatusPacket


def test_repr(packet):
    assert repr(packet) == f"<StatusPacket: {packet.source}>"


def test_data_type_id(packet):
    assert packet.data_type_id == ">"


def test_status_message(packet):
    assert packet.status_message == "PHG71801/Test status"


def test_with_timestamp(packet_with_timestamp):
    assert packet_with_timestamp.timestamp.day == 9
    assert packet_with_timestamp.timestamp.hour == 12
    assert packet_with_timestamp.timestamp.minute == 34


def test_without_timestamp(packet_without_timestamp):
    assert packet_without_timestamp.timestamp is None
    assert packet_without_timestamp.status_message == "Test status without a timestamp"


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
        APRS.parse_packet(
            r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21XA/-Test status with 6 digit Maidenhead locator'
        )


def test_invalid_mh4_status_message_missing_initial_space():
    # Missing space means it's not a valid Maidenhead status — falls through to plain text
    p = APRS.parse_packet(
        r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21/-Test status with 4 digit Maidenhead locator'
    )
    assert p.maidenhead_locator is None
    assert p.status_message == 'DO21/-Test status with 4 digit Maidenhead locator'


def test_empty_info():
    p = APRS.parse_packet(RAW_EMPTY_INFO)
    assert type(p) == StatusPacket
    assert p.status_message is None
