import pytest

from aprspy import APRS
from aprspy.packets.item_report import ItemReportPacket
from aprspy.exceptions import ParseError


RAW_LIVE = 'XX1XX>APRS,TCPIP*,qAC,TEST:)ITEM!4903.50N/07201.75W>Test item'
RAW_KILLED = 'XX1XX>APRS,TCPIP*,qAC,TEST:)ITEM_4903.50N/07201.75W>'
RAW_COMPRESSED = 'XX1XX>APRS,TCPIP*,qAC,TEST:)COMPITEM!/5L!!<*e7>7P[Test compressed item'
RAW_SHORT_NAME = 'XX1XX>APRS,TCPIP*,qAC,TEST:)ABC!4903.50N/07201.75W>Short name'
RAW_LONG_NAME = 'XX1XX>APRS,TCPIP*,qAC,TEST:)LONGNAME1!4903.50N/07201.75W>Long name'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW_LIVE)


@pytest.fixture
def killed():
    return APRS.parse_packet(RAW_KILLED)


@pytest.fixture
def compressed():
    return APRS.parse_packet(RAW_COMPRESSED)


def test_empty():
    assert repr(ItemReportPacket()) == "<ItemReportPacket>"


def test_type(packet):
    assert type(packet) == ItemReportPacket


def test_repr(packet):
    assert repr(packet) == "<ItemReportPacket: ITEM>"


def test_data_type_id(packet):
    assert packet.data_type_id == ")"


def test_item_name(packet):
    assert packet.item_name == "ITEM"


def test_item_name_short():
    p = APRS.parse_packet(RAW_SHORT_NAME)
    assert p.item_name == "ABC"


def test_item_name_long():
    p = APRS.parse_packet(RAW_LONG_NAME)
    assert p.item_name == "LONGNAME1"


def test_alive_live(packet):
    assert packet.alive is True


def test_alive_killed(killed):
    assert killed.alive is False


def test_latitude(packet):
    assert packet.latitude == 49.058333


def test_longitude(packet):
    assert packet.longitude == -72.029167


def test_symbol_table(packet):
    assert packet.symbol_table == "/"


def test_symbol_id(packet):
    assert packet.symbol_id == ">"


def test_comment(packet):
    assert packet.comment == "Test item"


def test_no_comment(killed):
    assert killed.comment is None


def test_compressed_latitude(compressed):
    assert compressed.latitude == 49.5


def test_compressed_longitude(compressed):
    assert compressed.longitude == -72.750004


def test_compressed_comment(compressed):
    assert compressed.comment == "Test compressed item"


def test_invalid_packet():
    with pytest.raises((ParseError, AttributeError)):
        APRS.parse_packet('XX1XX>APRS,TCPIP*,qAC,TEST:)AB!4903.50N/07201.75W>')
