import pytest

from aprspy import APRS
from aprspy.packets.mice import MICEPacket
from aprspy.exceptions import ParseError


RAW = r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW)


def test_empty():
    assert repr(MICEPacket()) == "<MICEPacket>"


def test_type(packet):
    assert type(packet) == MICEPacket


def test_repr(packet):
    assert repr(packet) == f"<MICEPacket: {packet.source}>"


def test_data_type_id(packet):
    assert packet.data_type_id == "`"


def test_source(packet):
    assert str(packet.source) == "XX1XX-1"


def test_destination(packet):
    assert str(packet.destination) == "U1PRSS"


def test_path(packet):
    assert str(packet.path) == "WIDE1-1,WIDE2-2,qAR,CALGRY"


def test_latitude(packet):
    assert packet.latitude == 51.038833


def test_longitude(packet):
    assert packet.longitude == -114.073667


def test_course(packet):
    assert packet.course == 238


def test_speed(packet):
    assert packet.speed == 0


def test_altitude(packet):
    assert packet.altitude == 1086


def test_symbol_table(packet):
    assert packet.symbol_table == "/"


def test_symbol_id(packet):
    assert packet.symbol_id == "k"


def test_comment(packet):
    assert packet.comment == "Test Mic-E packet"


def test_message_bits(packet):
    assert packet.message_bits is not None
    assert "a" in packet.message_bits
    assert "b" in packet.message_bits
    assert "c" in packet.message_bits
    assert "custom" in packet.message_bits


def test_missing_symbol_table():
    with pytest.raises(ParseError):
        APRS.parse_packet(r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk')


def test_missing_symbol_id():
    with pytest.raises(ParseError):
        APRS.parse_packet(r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"B')


def test_packets_first_destination_bit():
    for raw in [
        r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>F1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>51PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
    ]:
        p = APRS.parse_packet(raw)
        assert p.latitude == 51.038833


def test_packets_second_destination_bit():
    for raw in [
        r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>UBPRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>UQPRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
    ]:
        p = APRS.parse_packet(raw)
        assert p.latitude == 51.038833


def test_packets_third_destination_bit():
    for raw in [
        r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>U1ARSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>U10RSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
    ]:
        p = APRS.parse_packet(raw)
        assert p.latitude == 51.038833


def test_packets_fourth_destination_bit():
    raw = r'XX1XX-1>U1P2SS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    p = APRS.parse_packet(raw)
    assert p.latitude == -51.038833


def test_packets_fifth_destination_bit():
    raw = r'XX1XX-1>U1PR3S,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    p = APRS.parse_packet(raw)
    assert p.longitude == -14.073667


def test_packets_sixth_destination_bit():
    raw = r'XX1XX-1>U1PRS3,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    p = APRS.parse_packet(raw)
    assert p.longitude == 114.073667


def test_packets_klz_destination_bit():
    for raw in [
        r'XX1XX-1>U1PRKK,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>U1PRLL,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>U1PRZZ,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
    ]:
        p = APRS.parse_packet(raw)
        assert p.latitude == 51.033333


def test_packet_with_invalid_destination_bit():
    with pytest.raises(ParseError):
        APRS.parse_packet(r'XX1XX-1>M1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet')


def test_packets_with_80_subtracted_from_longitude():
    p = APRS.parse_packet(
        r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`l\Fl"Bk/]"?l}Test Mic-E packet'
    )
    assert p.longitude == -100.073667


def test_packets_with_190_subtracted_from_longitude():
    p = APRS.parse_packet(
        r'XX1XX-1>U1PRSS,WIDE1-1,WIDE2-2,qAR,CALGRY:`x\Fl"Bk/]"?l}Test Mic-E packet'
    )
    assert p.longitude == -2.073667
