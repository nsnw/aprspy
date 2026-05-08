import pytest

from aprspy import APRS
from aprspy.packets.ultimeter import UltimeterPacket, Ultimeter2000Packet
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


# Ultimeter 2000 ($ULTW) tests
# VE3KSR-13 sample: $ULTW017600D501E8023427D0FFFC95AF000102B1007B006E000000E5
ULTW_RAW = 'VE3KSR-13>APRS,TCPIP*,qAC,T2CSNOW:$ULTW017600D501E8023427D0FFFC95AF000102B1007B006E000000E5'

# ERINB sample with missing humidity (----)
ULTW_MISSING = 'ERINB>APRS,qAR,N7MPS:$ULTW00000000029300002779FFF48FF10001----007A051400000000'


@pytest.fixture
def ultw_packet():
    return APRS.parse_packet(ULTW_RAW)


def test_ultw_type(ultw_packet):
    assert type(ultw_packet) == Ultimeter2000Packet


def test_ultw_repr(ultw_packet):
    assert repr(ultw_packet) == f"<Ultimeter2000Packet: {ultw_packet.source}>"


def test_ultw_empty():
    assert repr(Ultimeter2000Packet()) == "<Ultimeter2000Packet>"


def test_ultw_wind_speed_peak(ultw_packet):
    # 0x0176 = 374 -> 37.4 mph
    assert ultw_packet.wind_speed_peak == 37.4


def test_ultw_wind_direction(ultw_packet):
    # 0x00D5 = 213 degrees
    assert ultw_packet.wind_direction == 213


def test_ultw_outdoor_temp(ultw_packet):
    # 0x01E8 = 488 -> 48.8 °F
    assert ultw_packet.outdoor_temp == 48.8


def test_ultw_rain_total(ultw_packet):
    # 0x2342 = 9026, but field is 0x2342? Let me recalculate from the payload.
    # Payload fields: 0176 00D5 01E8 0234 27D0 FFFC 95AF 0001 02B1 007B 006E 0000 00E5
    # F3 = 0234 = 564 -> 5.64 in
    assert ultw_packet.rain_total == pytest.approx(5.64)


def test_ultw_barometric_pressure(ultw_packet):
    # F4 = 27D0 = 10192 -> 1019.2 mbar
    assert ultw_packet.barometric_pressure == pytest.approx(1019.2)


def test_ultw_outdoor_humidity(ultw_packet):
    # F8 = 02B1 = 689 -> 68.9 %
    assert ultw_packet.outdoor_humidity == pytest.approx(68.9)


def test_ultw_wind_speed_avg(ultw_packet):
    # F10 = 006E = 110 -> 11.0 mph
    assert ultw_packet.wind_speed_avg == pytest.approx(11.0)


def test_ultw_rain_today(ultw_packet):
    # F11 = 0000 = 0 -> 0.00 in
    assert ultw_packet.rain_today == pytest.approx(0.0)


def test_ultw_missing_humidity():
    p = APRS.parse_packet(ULTW_MISSING)
    assert type(p) == Ultimeter2000Packet
    assert p.outdoor_humidity is None


def test_ultw_no_parse_warnings(ultw_packet):
    assert ultw_packet.parse_warnings == []


def test_ultw_too_short():
    with pytest.raises(ParseError):
        APRS.parse_packet('XX1XX>APRS,TCPIP*,qAC,TEST:$ULTW0176', strict=True)


# !! raw format tests
# K4CCC-9 sample: !!000000C20205010F27C002C3--------007B001900000000
ULTW_RAW_FORMAT = 'K4CCC-9>APRS,WIDE2-2,qAR,W4DEX:!!000000C20205010F27C002C3--------007B001900000000'

# Station with missing barometer and humidity
ULTW_RAW_MISSING = 'ELPASO>APN382,CABALL*,WIDE3-2,qAO,N7SGT-10:!!0000008002140000----------------0009004A00000000'


@pytest.fixture
def raw_format_packet():
    return APRS.parse_packet(ULTW_RAW_FORMAT)


def test_raw_format_type(raw_format_packet):
    assert type(raw_format_packet) == Ultimeter2000Packet


def test_raw_format_wind_speed_peak(raw_format_packet):
    # F0 = 0000 = 0 → 0.0 mph
    assert raw_format_packet.wind_speed_peak == 0.0


def test_raw_format_wind_direction(raw_format_packet):
    # F1 = 00C2 = 194 degrees
    assert raw_format_packet.wind_direction == 194


def test_raw_format_outdoor_temp(raw_format_packet):
    # F2 = 0205 = 517 → 51.7 °F
    assert raw_format_packet.outdoor_temp == pytest.approx(51.7)


def test_raw_format_barometric_pressure(raw_format_packet):
    # F4 = 27C0 = 10176 → 1017.6 mbar
    assert raw_format_packet.barometric_pressure == pytest.approx(1017.6)


def test_raw_format_outdoor_humidity(raw_format_packet):
    # F5 = 02C3 = 707 → 70.7 %
    assert raw_format_packet.outdoor_humidity == pytest.approx(70.7)


def test_raw_format_missing_fields():
    p = APRS.parse_packet(ULTW_RAW_MISSING)
    assert type(p) == Ultimeter2000Packet
    assert p.barometric_pressure is None
    assert p.outdoor_humidity is None


def test_raw_format_no_parse_warnings(raw_format_packet):
    assert raw_format_packet.parse_warnings == []


def test_raw_format_too_short():
    with pytest.raises(ParseError):
        APRS.parse_packet('XX1XX>APRS,TCPIP*,qAC,TEST:!!0000', strict=True)
