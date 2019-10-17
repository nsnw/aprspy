import pytest

from geopy import Point
from aprspy import APRS
from aprspy.packets.position import PositionPacket
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
    lat, lng, alt, course, speed, radio_range = PositionPacket._parse_compressed_position(
        "/5L!!<*e7OS]S"
    )

    assert lat == 49.5
    assert lng == -72.750004
    assert alt == 10004.52


def test_parse_compressed_position_with_radio_range():

    lat, lng, alt, course, speed, radio_range = PositionPacket._parse_compressed_position(
        "/5L!!<*e7>{?!"
    )

    assert lat == 49.5
    assert lng == -72.750004
    assert radio_range == 20.13


def test_parse_compressed_position_without_altitude():

    lat, lng, alt, course, speed, radio_range = PositionPacket._parse_compressed_position(
        "/5L!!<*e7> sT"
    )

    assert lat == 49.5
    assert lng == -72.750004
    assert alt is None


def test_parse_positions():
    raw_packets = [
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet',
         50.508333, -100.338333, "="),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30E$221/000/A=005000Test packet',
         50.508333, 100.338333, "="),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50S/10020.30W$221/000/A=005000Test packet',
         -50.508333, -100.338333, "="),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50S/10020.30E$221/000/A=005000Test packet',
         -50.508333, 100.338333, "="),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:!5030.50N/10020.30W$221/000/A=005000Test packet',
         50.508333, -100.338333, "!", ),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:!5030.50N/10020.30E$221/000/A=005000Test packet',
         50.508333, 100.338333, "!"),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:!5030.50S/10020.30W$221/000/A=005000Test packet',
         -50.508333, -100.338333, "!"),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:!5030.50S/10020.30E$221/000/A=005000Test packet',
         -50.508333, 100.338333, "!"),
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

    for raw in raw_packets:
        packet = APRS.parse(raw[0])

        assert type(packet) == PositionPacket
        assert repr(packet) == f"<PositionPacket: {packet.source}>"
        assert packet.data_type_id == raw[3]

        assert packet.source == "XX1XX"
        assert packet.destination == "APRS"
        assert str(packet.path) == "TCPIP*,qAC,FOURTH"

        assert type(packet.point) == Point
        assert packet.latitude == raw[1]
        assert packet.longitude == raw[2]
        assert packet.ambiguity == 0

        assert packet.course == 221
        assert packet.speed == 0

        assert packet.symbol_table == "/"
        assert packet.symbol_id == "$"

        if len(raw) == 5:
            # TODO - Fix timestamps
            # assert packet.timestamp == raw[4]
            assert packet.timestamp is not None

        assert packet.comment == "/A=005000Test packet"

    # TODO - fix longitude and speed
    raw_packets = [
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=/5L!!<*e7>7P[Test packet', 49.5, -72.750004),
    ]

    for raw in raw_packets:
        packet = APRS.parse(raw[0])

        assert type(packet) == PositionPacket
        assert repr(packet) == f"<PositionPacket: {packet.source}>"
        assert packet.data_type_id == "="

        assert packet.source == "XX1XX"
        assert packet.destination == "APRS"
        assert str(packet.path) == "TCPIP*,qAC,FOURTH"

        assert packet.latitude == raw[1]
        assert packet.longitude == raw[2]
        assert packet.ambiguity is None

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
