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


@pytest.mark.parametrize("raw,expected_seq,expected_avs", [
    # Truncated: fewer than 5 analog values
    ('SR7SE-1>APLOX1,TCPIP*,qAC,T2POLC:T#418,197', '418', [197, None, None, None, None]),
    ('LA7RR>APRS,TCPIP*,qAS,LD7TG:T#2146,533', '2146', [533, None, None, None, None]),
    ('4O7JAZ>APDW16,TCPIP*,qAC,T2UK:T#502,13.5,23.2', '502', [13.5, 23.2, None, None, None]),
    ('SQ9NFI>APRS,TCPIP*,qAC,T2PRT:T#086,000,106,051,153', '086', [0, 106, 51, 153, None]),
])
def test_truncated_analog_values(raw, expected_seq, expected_avs):
    p = APRS.parse_packet(raw)
    assert p.sequence_number == expected_seq
    assert [p.av1.value, p.av2.value, p.av3.value, p.av4.value, p.av5.value] == expected_avs


def test_sparse_analog_values_with_comment():
    raw = 'KJ4UBX-13>APRS,TCPIP*,qAC,T2UKRAINE:T#055,180,060,012,042,,1111,Solar Power WX Station'
    p = APRS.parse_packet(raw)
    assert p.sequence_number == '055'
    assert [p.av1.value, p.av2.value, p.av3.value, p.av4.value, p.av5.value] == [180, 60, 12, 42, None]
    assert str(p.dv) == '1111'
    assert p.comment == 'Solar Power WX Station'


def test_sparse_analog_values_no_comment():
    raw = 'VA7RCV-15>APZMDM,WIDE1-1,WIDE2-2,qAO,VA7RCV-10:T#795,3.599,21.460,1,99.631,,00000000'
    p = APRS.parse_packet(raw)
    assert p.sequence_number == '795'
    assert [p.av1.value, p.av2.value, p.av3.value, p.av4.value, p.av5.value] == [3.6, 21.46, 1, 99.63, None]
    assert str(p.dv) == '00000000'
