import pytest

from aprspy import APRS
from aprspy.packets.weather import WeatherPacket
from aprspy.packets.position import PositionPacket
from aprspy.exceptions import ParseError


RAW = 'XX1XX>APRS,TCPIP*,qAC,TEST:_10090556c220s004g005t077r000p001P002h50b09900wRSS'
RAW_NEG_TEMP = 'XX1XX>APRS,TCPIP*,qAC,TEST:_10090556c220s004g005t-07r000p000P000h50b09900wRSS'
RAW_HUMIDITY_100 = 'XX1XX>APRS,TCPIP*,qAC,TEST:_10090556c220s004g005t077r000p000P000h00b09900wRSS'
RAW_UNKNOWN_FIELDS = 'XX1XX>APRS,TCPIP*,qAC,TEST:_10090556c...s...g...t077r...p...P...h..b.....wRSS'
RAW_POSITION_BASED = 'XX1XX>APRS,TCPIP*,qAC,TEST:@092345z4903.50N/07201.75W_220/004g005t077r000p001P002h50b09900'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW)


@pytest.fixture
def position_based():
    return APRS.parse_packet(RAW_POSITION_BASED)


def test_empty():
    assert repr(WeatherPacket()) == "<WeatherPacket>"


def test_type(packet):
    assert type(packet) == WeatherPacket


def test_repr(packet):
    assert repr(packet) == f"<WeatherPacket: {packet.source}>"


def test_data_type_id(packet):
    assert packet.data_type_id == "_"


# --- Timestamp ---

def test_timestamp_month(packet):
    assert packet.timestamp.month == 10


def test_timestamp_day(packet):
    assert packet.timestamp.day == 9


def test_timestamp_hour(packet):
    assert packet.timestamp.hour == 5


def test_timestamp_minute(packet):
    assert packet.timestamp.minute == 56


# --- Weather fields ---

def test_wind_direction(packet):
    assert packet.wind_direction == 220


def test_wind_speed(packet):
    assert packet.wind_speed == 4


def test_wind_gust(packet):
    assert packet.wind_gust == 5


def test_temperature(packet):
    assert packet.temperature == 77


def test_temperature_negative():
    p = APRS.parse_packet(RAW_NEG_TEMP)
    assert p.temperature == -7


def test_rain_1h(packet):
    assert packet.rain_1h == 0.0


def test_rain_24h(packet):
    assert packet.rain_24h == 0.01


def test_rain_since_midnight(packet):
    assert packet.rain_since_midnight == 0.02


def test_humidity(packet):
    assert packet.humidity == 50


def test_humidity_100():
    p = APRS.parse_packet(RAW_HUMIDITY_100)
    assert p.humidity == 100


def test_pressure(packet):
    assert packet.pressure == 990.0


def test_weather_software(packet):
    assert packet.weather_software == "RSS"


# --- Unknown/missing fields ---

def test_unknown_fields():
    p = APRS.parse_packet(RAW_UNKNOWN_FIELDS)
    assert p.wind_direction is None
    assert p.wind_speed is None
    assert p.wind_gust is None
    assert p.humidity is None
    assert p.pressure is None
    assert p.rain_1h is None
    assert p.temperature == 77


# --- Position-based weather ---

def test_position_based_type(position_based):
    assert type(position_based) == PositionPacket


def test_position_based_has_position(position_based):
    assert position_based.latitude == 49.058333
    assert position_based.longitude == -72.029167


def test_position_based_wind_from_course_speed(position_based):
    # For position-based weather, wind dir/speed come from course/speed data extension
    assert position_based.course == 220
    assert position_based.speed == 4


def test_position_based_weather_fields(position_based):
    assert position_based.wind_gust == 5
    assert position_based.temperature == 77
    assert position_based.humidity == 50
    assert position_based.pressure == 990.0
    assert position_based.rain_24h == 0.01


# --- Error cases ---

def test_too_short():
    with pytest.raises(ParseError):
        APRS.parse_packet('XX1XX>APRS,TCPIP*,qAC,TEST:_1009', strict=True)


def test_ddmmhhmm_fallback():
    # SP9SVH-2 firmware emits DDMMHHMM instead of MMDDHHMM. Month 16 is
    # invalid; the swap to day=16/month=05 is plausible and should produce
    # a LENIENT TIMESTAMP_FIELD_ORDER_SWAPPED warning.
    from aprspy.warnings import ParseWarningCode
    raw = 'SP9SVH-2>APRX29,WIDE1-1,QA6L9,qAR,SQ9LDR-2:_16050154c226s000g000t050r000p013P003h097b10014'
    p = APRS.parse_packet(raw)
    assert type(p) == WeatherPacket
    assert p.timestamp.month == 5
    assert p.timestamp.day == 16
    assert p.timestamp.hour == 1
    assert p.timestamp.minute == 54
    assert p.temperature == 50
    assert p.pressure == 1001.4
    assert any(w.code == ParseWarningCode.TIMESTAMP_FIELD_ORDER_SWAPPED for w in p.parse_warnings)
