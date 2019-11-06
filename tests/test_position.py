import pytest

from geopy import Point
from datetime import datetime

from aprspy import APRS
from aprspy.packets.position import PositionPacket, CompressionFix, CompressionSource, \
    CompressionOrigin
from aprspy.exceptions import ParseError


def test_empty():
    packet = PositionPacket()

    assert str(packet) == "<PositionPacket>"


def test_init():
    packet = PositionPacket()
    point = Point(51, -114, 1000)

    packet.point = point
    packet.power = 50
    packet.height = 50
    packet.gain = 3
    packet.directivity = 90
    packet.radio_range = 10
    packet.strength = 9
    packet.bearing = 180
    packet.number = 12.5
    packet.df_range = 20
    packet.quality = 1

    assert packet.point == point
    assert packet.power == 50
    assert packet.height == 50
    assert packet.gain == 3
    assert packet.directivity == 90
    assert packet.radio_range == 10
    assert packet.strength == 9
    assert packet.bearing == 180
    assert packet.number == 12.5
    assert packet.df_range == 20
    assert packet.quality == 1


def test_parse_uncompressed_position():
    lat, lng, amb, st, sid = PositionPacket._parse_uncompressed_position("5100.00N/11400.00Wk")

    assert lat == 51
    assert lng == -114
    assert amb == 0
    assert st == "/"
    assert sid == "k"


def test_parse_invalid_uncompressed_position():
    with pytest.raises(ParseError):
        # Missing symbol ID
        PositionPacket._parse_uncompressed_position("5100.00N/11400.00W")


def test_parse_compressed_position_with_altitude():
    (lat, lng, alt, course, speed, radio_range, fix, source,
     origin) = PositionPacket._parse_compressed_position(
        "/5L!!<*e7OS]S"
    )

    assert lat == 49.5
    assert lng == -72.750004
    assert alt == 10004.52

    assert fix == CompressionFix.OLD
    assert source == CompressionSource.OTHER
    assert origin == CompressionOrigin.COMPRESSED


def test_parse_compressed_position_with_radio_range():

    (lat, lng, alt, course, speed, radio_range, fix, source,
     origin) = PositionPacket._parse_compressed_position(
        "/5L!!<*e7>{?!"
    )

    assert lat == 49.5
    assert lng == -72.750004
    assert radio_range == 20.13

    assert fix == CompressionFix.CURRENT
    assert source == CompressionSource.GLL
    assert origin == CompressionOrigin.TNC_BTEXT


def test_parse_compressed_position_without_altitude():

    (lat, lng, alt, course, speed, radio_range, fix, source,
     origin) = PositionPacket._parse_compressed_position(
        "/5L!!<*e7> sT"
    )

    assert lat == 49.5
    assert lng == -72.750004
    assert alt is None

    assert fix is None
    assert source is None
    assert origin is None


@pytest.mark.parametrize(
    "input_raw, latitude, longitude, data_type_id, timestamp", [
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet',
         50.508333, -100.338333, "=", None),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30E$221/000/A=005000Test packet',
         50.508333, 100.338333, "=", None),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50S/10020.30W$221/000/A=005000Test packet',
         -50.508333, -100.338333, "=", None),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50S/10020.30E$221/000/A=005000Test packet',
         -50.508333, 100.338333, "=", None),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:!5030.50N/10020.30W$221/000/A=005000Test packet',
         50.508333, -100.338333, "!", None),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:!5030.50N/10020.30E$221/000/A=005000Test packet',
         50.508333, 100.338333, "!", None),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:!5030.50S/10020.30W$221/000/A=005000Test packet',
         -50.508333, -100.338333, "!", None),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:!5030.50S/10020.30E$221/000/A=005000Test packet',
         -50.508333, 100.338333, "!", None),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:/092345z5030.50N/10020.30W$221/000/A=005000Test packet',
         50.508333, -100.338333, "/", "092345z"),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:/092345z5030.50N/10020.30E$221/000/A=005000Test packet',
         50.508333, 100.338333, "/", "092345z"),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:/092345z5030.50S/10020.30W$221/000/A=005000Test packet',
         -50.508333, -100.338333, "/", "092345z"),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:/092345z5030.50S/10020.30E$221/000/A=005000Test packet',
         -50.508333, 100.338333, "/", "092345z"),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:@092345/5030.50N/10020.30W$221/000/A=005000Test packet',
         50.508333, -100.338333, "@", "092345/"),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:@092345/5030.50N/10020.30E$221/000/A=005000Test packet',
         50.508333, 100.338333, "@", "092345/"),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:@092345/5030.50S/10020.30W$221/000/A=005000Test packet',
         -50.508333, -100.338333, "@", "092345/"),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:@092345/5030.50S/10020.30E$221/000/A=005000Test packet',
         -50.508333, 100.338333, "@", "092345/"),
    ]
)
def test_parse_uncompressed_positions(input_raw, latitude, longitude, data_type_id, timestamp):
    packet = APRS.parse(input_raw)

    assert type(packet) == PositionPacket
    assert repr(packet) == f"<PositionPacket: {packet.source}>"
    assert packet.data_type_id == data_type_id

    assert packet.source == "XX1XX"
    assert packet.destination == "APRS"
    assert str(packet.path) == "TCPIP*,qAC,FOURTH"

    assert type(packet.point) == Point
    assert packet.latitude == latitude
    assert packet.longitude == longitude
    assert packet.ambiguity == 0
    assert packet.altitude == 5000

    assert packet.course == 221
    assert packet.speed == 0

    assert packet.symbol_table == "/"
    assert packet.symbol_id == "$"

    assert packet.compressed is False

    if timestamp:
        assert packet.timestamp.day == 9
        assert packet.timestamp.hour == 23
        assert packet.timestamp.minute == 45

    assert packet.comment == "Test packet"


@pytest.mark.parametrize(
    "input_raw, latitude, longitude", [
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=/5L!!<*e7>7P[Test packet', 49.5, -72.750004),
    ]
)
def test_parse_compressed_positions(input_raw, latitude, longitude):
    packet = APRS.parse(input_raw)

    assert type(packet) == PositionPacket
    assert repr(packet) == f"<PositionPacket: {packet.source}>"
    assert packet.data_type_id == "="

    assert packet.source == "XX1XX"
    assert packet.destination == "APRS"
    assert str(packet.path) == "TCPIP*,qAC,FOURTH"

    assert packet.latitude == latitude
    assert packet.longitude == longitude
    assert packet.ambiguity == 0

    assert packet.course == 88
    assert packet.speed == 36.2

    assert packet.symbol_table == "/"
    assert packet.symbol_id == ">"

    assert packet.comment == "Test packet"


def test_position_with_df():

    packet = APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W\088/036/270/729')

    assert packet.course == 88
    assert packet.speed == 36
    assert packet.bearing == 270
    assert packet.number == 87.5
    assert packet.df_range == 4
    assert packet.quality == 1


def test_position_with_df_missing_df_values():
    with pytest.raises(ParseError):
        # Missing DF values
        APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W\\')


def test_position_with_df_invalid_df_format():
    with pytest.raises(ParseError):
        # Invalid DF format
        APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W\088036270729')


def test_position_with_phg():

    packet = APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$PHG5132')

    assert packet.power == 25
    assert packet.height == 20
    assert packet.gain == 3
    assert packet.directivity == 90


def test_position_with_rng():

    packet = APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$RNG0050')

    assert packet.radio_range == 50


def test_position_with_dfs():

    packet = APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$DFS2360')

    assert packet.strength == 2
    assert packet.height == 80
    assert packet.gain == 6
    assert packet.directivity is None


def test_position_with_weather():
    # TODO - Weather is not yet implemented
    packet = APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W_TEST')


def test_position_with_invalid_data_type_id():
    with pytest.raises(ParseError):
        # This is a contrived example
        packet = APRS.parse(
            'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet'
        )
        packet.data_type_id = "X"
        packet._parse()


def test_position_with_missing_timestamp():
    with pytest.raises(ParseError):
        # This packet should have a timestamp
        APRS.parse('XX1XX>APRS,TCPIP*,qAC,FOURTH:@5030.50S/10020.30E$221/000/A=005000Test packet')


def test_parse_data_with_phg():
    phg, rng, dfs, course, speed, altitude, comment = PositionPacket._parse_data(
        "PHG5132"
    )

    assert phg == "5132"


def test_parse_data_with_rng():
    phg, rng, dfs, course, speed, altitude, comment = PositionPacket._parse_data(
        "RNG0050"
    )

    assert rng == "0050"


def test_parse_data_with_dfs():
    phg, rng, dfs, course, speed, altitude, comment = PositionPacket._parse_data(
        "DFS2360"
    )

    assert dfs == "2360"


def test_parse_data_with_altitude():
    phg, rng, dfs, course, speed, altitude, comment = PositionPacket._parse_data(
        "/A=002000Test status"
    )

    assert altitude == 2000


def test_invalid_messaging_type():
    p = PositionPacket()

    with pytest.raises(TypeError):
        p.messaging = None


def test_invalid_compressed_type():
    p = PositionPacket()

    with pytest.raises(TypeError):
        p.compressed = None


@pytest.mark.parametrize(
    "latitude, longitude, timestamp, timestamp_type, messaging, expected_output", [
        (
            51.5, -100, None, None, False,
            "XX1XX>APRS,TCPIP:!5130.00N/10000.00Wk"
        ),
        (
            51.5, 100, None, None, False,
            "XX1XX>APRS,TCPIP:!5130.00N/10000.00Ek"
        ),
        (
            -51.5, -100, None, None, False,
            "XX1XX>APRS,TCPIP:!5130.00S/10000.00Wk"
        ),
        (
            51.5, -100, None, None, True,
            "XX1XX>APRS,TCPIP:=5130.00N/10000.00Wk"
        ),
        (
            51.5, -100, datetime(2019, 10, 26, 10, 00, 30), "zulu", False,
            "XX1XX>APRS,TCPIP:/261000z5130.00N/10000.00Wk"
        ),
        (
            51.5, -100, datetime(2019, 10, 26, 10, 00, 30), "hms", False,
            "XX1XX>APRS,TCPIP:/100030h5130.00N/10000.00Wk"
        ),
        (
            51.5, -100, datetime(2019, 10, 26, 10, 00, 30), "local", False,
            "XX1XX>APRS,TCPIP:/261000/5130.00N/10000.00Wk"
        ),
    ]
)
def test_generate(latitude, longitude, timestamp, timestamp_type, messaging, expected_output):
    p = PositionPacket()

    p.source = "XX1XX"
    p.destination = "APRS"
    p.path = "TCPIP"

    p.symbol_table = "/"
    p.symbol_id = "k"

    p.latitude = latitude
    p.longitude = longitude

    p.timestamp = timestamp
    p.timestamp_type = timestamp_type

    p.messaging = messaging

    output = p.generate()

    assert output == expected_output


@pytest.mark.parametrize(
    "latitude, longitude, timestamp, timestamp_type, messaging, expected_output", [
        (
            49.5, -72.75, None, None, False,
            "XX1XX>APRS,TCPIP:!/5L!!<*e7k sTTest comment"
        ),
        (
            49.5, 72.75, None, None, False,
            "XX1XX>APRS,TCPIP:!/5L!!`q7ek sTTest comment"
        ),
        (
            -49.5, -72.75, None, None, False,
            "XX1XX>APRS,TCPIP:!/gP!!<*e7k sTTest comment"
        ),
        (
            49.5, -72.75, None, None, True,
            "XX1XX>APRS,TCPIP:=/5L!!<*e7k sTTest comment"
        ),
        (
            49.5, -72.75, datetime(2019, 10, 26, 10, 00, 30), "zulu", False,
            "XX1XX>APRS,TCPIP:/261000z/5L!!<*e7k sTTest comment"
        ),
        (
            49.5, -72.75, datetime(2019, 10, 26, 10, 00, 30), "hms", False,
            "XX1XX>APRS,TCPIP:/100030h/5L!!<*e7k sTTest comment"
        ),
        (
            49.5, -72.75, datetime(2019, 10, 26, 10, 00, 30), "local", False,
            "XX1XX>APRS,TCPIP:/261000//5L!!<*e7k sTTest comment"
        ),
        (
            49.5, -72.75, datetime(2019, 10, 26, 10, 00, 30), "zulu", True,
            "XX1XX>APRS,TCPIP:@261000z/5L!!<*e7k sTTest comment"
        ),
        (
            49.5, -72.75, datetime(2019, 10, 26, 10, 00, 30), "hms", True,
            "XX1XX>APRS,TCPIP:@100030h/5L!!<*e7k sTTest comment"
        ),
        (
            49.5, -72.75, datetime(2019, 10, 26, 10, 00, 30), "local", True,
            "XX1XX>APRS,TCPIP:@261000//5L!!<*e7k sTTest comment"
        ),
    ]
)
def test_generate_compressed(latitude, longitude, timestamp, timestamp_type, messaging,
                             expected_output):
    p = PositionPacket()

    p.source = "XX1XX"
    p.destination = "APRS"
    p.path = "TCPIP"

    p.symbol_table = "/"
    p.symbol_id = "k"

    p.latitude = latitude
    p.longitude = longitude

    p.timestamp = timestamp
    p.timestamp_type = timestamp_type

    p.messaging = messaging
    p.comment = "Test comment"
    p.compressed = True

    output = p.generate()

    assert output == expected_output


@pytest.fixture
def generated_packet() -> PositionPacket:
    p = PositionPacket()

    p.source = "XX1XX"
    p.destination = "APRS"
    p.path = "TCPIP"

    p.symbol_table = "/"
    p.symbol_id = "k"

    p.latitude = 51.5
    p.longitude = -100

    p.comment = "Test comment"

    return p


def test_generate_with_phg(generated_packet):
    generated_packet.power = 25
    generated_packet.height = 20
    generated_packet.gain = 3
    generated_packet.directivity = 90

    output = generated_packet.generate()

    assert output == "XX1XX>APRS,TCPIP:!5130.00N/10000.00WkPHG5132Test comment"


def test_generate_with_dfs(generated_packet):
    generated_packet.strength = 2
    generated_packet.height = 20
    generated_packet.gain = 3
    generated_packet.directivity = 90

    output = generated_packet.generate()

    assert output == "XX1XX>APRS,TCPIP:!5130.00N/10000.00WkDFS2132Test comment"


def test_generate_with_course_and_speed(generated_packet):
    generated_packet.course = 80
    generated_packet.speed = 50

    output = generated_packet.generate()

    assert output == "XX1XX>APRS,TCPIP:!5130.00N/10000.00Wk080/050Test comment"


def test_generate_with_radio_range(generated_packet):
    generated_packet.radio_range = 50

    output = generated_packet.generate()

    assert output == "XX1XX>APRS,TCPIP:!5130.00N/10000.00WkRNG0050Test comment"
