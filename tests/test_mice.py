import pytest

from aprspy import APRS, MICEPacket
from aprspy.exceptions import ParseError

# Input packet
raw = r'XX1XX-1>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}Test Mic-E packet'


@pytest.fixture
def packet():
    packet = APRS.parse(raw)
    return packet


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
