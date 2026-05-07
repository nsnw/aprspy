import pytest

from aprspy import APRS
from aprspy.packets.ultimeter import UltimeterPacket
from aprspy.exceptions import ParseError

# Direction 0xC0 = 192 -> 192 * 360/256 = 270.0 degrees (West)
# Speed 0x14 = 20 MPH
# Temp 0x55 = 85 °F
# Rain total 0x0064 = 100
# Rain today 0x001E = 30
# Info field = C0 14 55 0064 001E = 14 hex chars
RAW = 'XX1XX>APRS,TCPIP*,qAC,TEST:*C014550064001E'

# Hash variant (KPH): same data, different DTI
RAW_KPH = 'XX1XX>APRS,TCPIP*,qAC,TEST:#C014550064001E'

# Negative temperature: 0xF6 = 246 unsigned -> 246-256 = -10 °F
RAW_NEG_TEMP = 'XX1XX>APRS,TCPIP*,qAC,TEST:*C014F60064001E'

# North wind: 0x00 = 0 degrees
RAW_NORTH = 'XX1XX>APRS,TCPIP*,qAC,TEST:*0014550064001E'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW)


@pytest.fixture
def kph_packet():
    return APRS.parse_packet(RAW_KPH)


def test_empty():
    assert repr(UltimeterPacket()) == "<UltimeterPacket>"


def test_type(packet):
    assert type(packet) == UltimeterPacket


def test_repr(packet):
    assert repr(packet) == f"<UltimeterPacket: {packet.source}>"


def test_data_type_id_mph(packet):
    assert packet.data_type_id == '*'


def test_data_type_id_kph(kph_packet):
    assert kph_packet.data_type_id == '#'


def test_wind_unit_mph(packet):
    assert packet.wind_unit == 'mph'


def test_wind_unit_kph(kph_packet):
    assert kph_packet.wind_unit == 'kph'


def test_wind_direction(packet):
    # 0xC0 = 192; 192 * 360/256 = 270.0
    assert packet.wind_direction == 270.0


def test_wind_direction_north():
    p = APRS.parse_packet(RAW_NORTH)
    assert p.wind_direction == 0.0


def test_wind_speed(packet):
    # 0x14 = 20
    assert packet.wind_speed == 20


def test_temperature(packet):
    # 0x55 = 85
    assert packet.temperature == 85


def test_temperature_negative():
    p = APRS.parse_packet(RAW_NEG_TEMP)
    # 0xF6 = 246 unsigned -> -10 signed
    assert p.temperature == -10


def test_rain_total(packet):
    # 0x0064 = 100
    assert packet.rain_total == 100


def test_rain_today(packet):
    # 0x001E = 30
    assert packet.rain_today == 30


def test_too_short():
    with pytest.raises(ParseError):
        APRS.parse_packet('XX1XX>APRS,TCPIP*,qAC,TEST:*C014550064', strict=True)
