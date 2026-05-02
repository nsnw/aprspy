import pytest
from datetime import timezone

from aprspy import APRS
from aprspy.packets.nmea import NMEAPacket
from aprspy.exceptions import ParseError


RAW_GPRMC = 'XX1XX>APRS,TCPIP*,qAC,TEST:$GPRMC,092345,A,4903.55,N,07201.75,W,36.0,88.0,090409,,,A*62'
RAW_GPGGA = 'XX1XX>APRS,TCPIP*,qAC,TEST:$GPGGA,092345.00,4903.55,N,07201.75,W,1,08,1.0,100.0,M,0.0,M,,*47'
RAW_GPGLL = 'XX1XX>APRS,TCPIP*,qAC,TEST:$GPGLL,4903.55,N,07201.75,W,092345,A*39'
RAW_BAD_CHECKSUM = 'XX1XX>APRS,TCPIP*,qAC,TEST:$GPRMC,092345,A,4903.55,N,07201.75,W,36.0,88.0,090409,,,A*FF'
RAW_UNKNOWN_TYPE = 'XX1XX>APRS,TCPIP*,qAC,TEST:$GPZDA,092345.00,09,04,2009,,*69'


@pytest.fixture
def gprmc():
    return APRS.parse_packet(RAW_GPRMC)


@pytest.fixture
def gpgga():
    return APRS.parse_packet(RAW_GPGGA)


@pytest.fixture
def gpgll():
    return APRS.parse_packet(RAW_GPGLL)


def test_empty():
    assert repr(NMEAPacket()) == "<NMEAPacket>"


def test_type(gprmc):
    assert type(gprmc) == NMEAPacket


def test_repr_with_sentence_type(gprmc):
    assert repr(gprmc) == "<NMEAPacket: RMC>"


def test_data_type_id(gprmc):
    assert gprmc.data_type_id == "$"


# --- GPRMC ---

def test_gprmc_sentence_type(gprmc):
    assert gprmc.sentence_type == "RMC"


def test_gprmc_checksum_valid(gprmc):
    assert gprmc.checksum_valid is True


def test_gprmc_latitude(gprmc):
    assert round(gprmc.latitude, 4) == 49.0592


def test_gprmc_longitude(gprmc):
    assert round(gprmc.longitude, 4) == -72.0292


def test_gprmc_speed(gprmc):
    assert gprmc.speed == 36.0


def test_gprmc_course(gprmc):
    assert gprmc.course == 88


def test_gprmc_timestamp(gprmc):
    assert gprmc.timestamp.year == 2009
    assert gprmc.timestamp.month == 4
    assert gprmc.timestamp.day == 9
    assert gprmc.timestamp.hour == 9
    assert gprmc.timestamp.minute == 23
    assert gprmc.timestamp.second == 45
    assert gprmc.timestamp.tzinfo == timezone.utc


def test_gprmc_nmea_sentence(gprmc):
    assert gprmc.nmea_sentence == '$GPRMC,092345,A,4903.55,N,07201.75,W,36.0,88.0,090409,,,A*62'


# --- GPGGA ---

def test_gpgga_sentence_type(gpgga):
    assert gpgga.sentence_type == "GGA"


def test_gpgga_checksum_valid(gpgga):
    assert gpgga.checksum_valid is True


def test_gpgga_latitude(gpgga):
    assert round(gpgga.latitude, 4) == 49.0592


def test_gpgga_longitude(gpgga):
    assert round(gpgga.longitude, 4) == -72.0292


def test_gpgga_altitude(gpgga):
    # 100.0m converted to feet = 328
    assert gpgga.altitude == 328


def test_gpgga_no_speed(gpgga):
    assert gpgga.speed is None


def test_gpgga_no_course(gpgga):
    assert gpgga.course is None


# --- GPGLL ---

def test_gpgll_sentence_type(gpgll):
    assert gpgll.sentence_type == "GLL"


def test_gpgll_checksum_valid(gpgll):
    assert gpgll.checksum_valid is True


def test_gpgll_latitude(gpgll):
    assert round(gpgll.latitude, 4) == 49.0592


def test_gpgll_longitude(gpgll):
    assert round(gpgll.longitude, 4) == -72.0292


def test_gpgll_no_speed(gpgll):
    assert gpgll.speed is None


# --- Bad checksum ---

def test_bad_checksum_flag():
    p = APRS.parse_packet(RAW_BAD_CHECKSUM)
    assert p.checksum_valid is False


def test_bad_checksum_still_parses():
    p = APRS.parse_packet(RAW_BAD_CHECKSUM)
    assert round(p.latitude, 4) == 49.0592
    assert round(p.longitude, 4) == -72.0292
    assert p.speed == 36.0


# --- Unknown sentence type ---

def test_unknown_sentence_type():
    p = APRS.parse_packet(RAW_UNKNOWN_TYPE)
    assert type(p) == NMEAPacket
    assert p.sentence_type == "ZDA"
    assert p.latitude is None
    assert p.longitude is None
