import pytest

from aprspy import APRS
from aprspy.packets.telemetry import TelemetryPacket
from aprspy.exceptions import ParseError

RAW = 'XX1XX>APRS,TCPIP*,qAC,TEST:T#005,100,200,050,075,025,10110101'
RAW_MIC = 'XX1XX>APRS,TCPIP*,qAC,TEST:T#MIC,100,200,050,075,025,10110101'
RAW_NO_DIGITAL = 'XX1XX>APRS,TCPIP*,qAC,TEST:T#005,100,200,050,075,025,'
RAW_WITH_COMMENT = 'XX1XX>APRS,TCPIP*,qAC,TEST:T#005,100,200,050,075,025,10110101 Test comment'
RAW_FLOAT = 'XX1XX>APRS,TCPIP*,qAC,TEST:T#005,3.14,200,050,075,025,10110101'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW)


def test_empty():
    assert repr(TelemetryPacket()) == "<TelemetryPacket>"


def test_type(packet):
    assert type(packet) == TelemetryPacket


def test_repr(packet):
    assert repr(packet) == f"<TelemetryPacket: {packet.source}>"


def test_data_type_id(packet):
    assert packet.data_type_id == "T"


def test_sequence_number(packet):
    assert packet.sequence_number == '005'


def test_sequence_number_mic():
    p = APRS.parse_packet(RAW_MIC)
    assert p.sequence_number == 'MIC'


def test_av1(packet):
    assert str(packet.av1) == '100'


def test_av2(packet):
    assert str(packet.av2) == '200'


def test_av3(packet):
    assert str(packet.av3) == '50'


def test_av4(packet):
    assert str(packet.av4) == '75'


def test_av5(packet):
    assert str(packet.av5) == '25'


def test_av_float():
    p = APRS.parse_packet(RAW_FLOAT)
    assert p.av1.value == 3.14


def test_dv(packet):
    assert str(packet.dv) == '10110101'


def test_no_digital_value():
    p = APRS.parse_packet(RAW_NO_DIGITAL)
    assert p.dv is None


def test_comment_with_space():
    p = APRS.parse_packet(RAW_WITH_COMMENT)
    assert p.comment == 'Test comment'
