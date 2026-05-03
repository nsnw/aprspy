import pytest

from aprspy import APRS
from aprspy.packets.third_party import ThirdPartyPacket
from aprspy.packets.position import PositionPacket
from aprspy.packets.weather import WeatherPacket
from aprspy.exceptions import ParseError


# Outer packet wrapping an inner position packet
INNER_POSITION = 'XX1XX>APRS,TCPIP*,qAC,TEST:!4903.50N/07201.75W-Test comment'
RAW = f'YY2YY>APRS,TCPIP*,qAC,TEST:}}{INNER_POSITION}'

# Outer packet wrapping an inner weather packet
INNER_WEATHER = 'XX1XX>APRS,TCPIP*,qAC,TEST:_10090556c220s004g005t077r000p001P002h50b09900wRSS'
RAW_WEATHER = f'YY2YY>APRS,TCPIP*,qAC,TEST:}}{INNER_WEATHER}'

# Outer packet wrapping a malformed inner packet
RAW_BAD_INNER = 'YY2YY>APRS,TCPIP*,qAC,TEST:}notapacket'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW)


@pytest.fixture
def weather_packet():
    return APRS.parse_packet(RAW_WEATHER)


def test_empty():
    assert repr(ThirdPartyPacket()) == "<ThirdPartyPacket>"


def test_type(packet):
    assert type(packet) == ThirdPartyPacket


def test_repr_with_inner(packet):
    assert repr(packet) == f"<ThirdPartyPacket: {packet.inner_packet!r}>"


def test_repr_no_inner():
    p = ThirdPartyPacket()
    p._source = 'YY2YY'
    assert repr(p) == "<ThirdPartyPacket: YY2YY>"


def test_data_type_id(packet):
    assert packet.data_type_id == "}"


def test_source(packet):
    assert str(packet.source) == 'YY2YY'


def test_inner_raw(packet):
    assert packet.inner_raw == INNER_POSITION


def test_inner_packet_type(packet):
    assert type(packet.inner_packet) == PositionPacket


def test_inner_source(packet):
    assert str(packet.inner_packet.source) == 'XX1XX'


def test_inner_position(packet):
    assert packet.inner_packet.latitude == 49.058333
    assert packet.inner_packet.longitude == -72.029167


def test_inner_comment(packet):
    assert packet.inner_packet.comment == 'Test comment'


def test_inner_weather_type(weather_packet):
    assert type(weather_packet.inner_packet) == WeatherPacket


def test_inner_weather_fields(weather_packet):
    assert weather_packet.inner_packet.wind_direction == 220
    assert weather_packet.inner_packet.temperature == 77
    assert weather_packet.inner_packet.humidity == 50
    assert weather_packet.inner_packet.pressure == 990.0


def test_bad_inner_raises():
    with pytest.raises(ParseError):
        APRS.parse_packet(RAW_BAD_INNER)
