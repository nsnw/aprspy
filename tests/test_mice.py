import pytest

from aprspy import APRS, MICEPacket
from aprspy.exceptions import ParseError

# Input packet
raw = r'XX1XX-1>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'


@pytest.fixture
def packet():
    packet = APRS.parse(raw)
    return packet


def test_empty(packet):
    packet = MICEPacket()

    assert repr(packet) == "<MICEPacket>"


def test_type(packet):
    assert type(packet) == MICEPacket


def test_repr(packet):
    assert repr(packet) == f"<MICEPacket: {packet.source}>"


def test_data_type_id(packet):
    assert packet.data_type_id == "`"


def test_source(packet):
    assert packet.source == "XX1XX-1"


def test_destination(packet):
    assert packet.destination == "U1PRSS-1"


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


def test_missing_symbol_table():
    # Missing symbol table
    with pytest.raises(ParseError):
        APRS.parse(r'XX1XX-1>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk')


def test_missing_symbol_id():
    # Missing symbol ID
    with pytest.raises(ParseError):
        APRS.parse(r'XX1XX-1>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"B')


def test_packets_first_destination_bit():
    # All these are the same latitude, but with different first bits
    raw = [
        r'XX1XX-1>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>F1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>51PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    ]

    for r in raw:
        p = APRS.parse(r)

        assert p.latitude == 51.038833


def test_packets_second_destination_bit():
    # All these are the same latitude, but with different second bits
    raw = [
        r'XX1XX-1>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>UBPRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>UQPRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    ]

    for r in raw:
        p = APRS.parse(r)

        assert p.latitude == 51.038833


def test_packets_third_destination_bit():
    # All these are the same latitude, but with different third bits
    raw = [
        r'XX1XX-1>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>U1ARSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>U10RSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    ]

    for r in raw:
        p = APRS.parse(r)

        assert p.latitude == 51.038833


def test_packets_fourth_destination_bit():
    # The fourth bit can be used to flip the latitude
    raw = r'XX1XX-1>U1P2SS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    p = APRS.parse(raw)

    assert p.latitude == -51.038833


def test_packets_fifth_destination_bit():
    # The fifth bit can be used to add an offset to the longitude
    raw = r'XX1XX-1>U1PR3S-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    p = APRS.parse(raw)

    assert p.longitude == -14.073667


def test_packets_sixth_destination_bit():
    # The sixth bit can be used to flip the longitude
    raw = r'XX1XX-1>U1PRS3-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    p = APRS.parse(raw)

    assert p.longitude == 114.073667


def test_packets_klz_destination_bit():
    # KLZ can be used to denote a space
    raw = [
        r'XX1XX-1>U1PRKK-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>U1PRLL-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet',
        r'XX1XX-1>U1PRZZ-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'
    ]

    for r in raw:
        p = APRS.parse(r)

        assert p.latitude == 51.033333


def test_packet_with_invalid_destination_bit():
    with pytest.raises(ParseError):
        APRS.parse(r'XX1XX-1>M1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet')


def test_packet_with_missing_speed_and_course():
    with pytest.raises(ParseError):
        APRS.parse(r'XX1XX-1>M1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet')


def test_packets_with_80_subtracted_from_longitude():
    p = APRS.parse(
        r'XX1XX-1>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`l\Fl"Bk/]"?l}Test Mic-E packet'
    )

    assert p.longitude == -100.073667


def test_packets_with_190_subtracted_from_longitude():
    p = APRS.parse(
        r'XX1XX-1>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`x\Fl"Bk/]"?l}Test Mic-E packet'
    )

    assert p.longitude == -2.073667
