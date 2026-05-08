import pytest
from aprspy import APRS
from aprspy.packets.position import PositionPacket, CompressionFix, CompressionSource, \
    CompressionOrigin
from aprspy.exceptions import ParseError
from .data import (
    POSITION_TIMESTAMP_MESSAGING_DATA_TYPE_IDS,
    VALID_POSITION_WITH_X1J_HEADER_PACKETS
)


@pytest.mark.parametrize(
    "with_timestamp,messaging_capable,data_type_id",
    POSITION_TIMESTAMP_MESSAGING_DATA_TYPE_IDS
)
def test_set_data_type_id(
        with_timestamp, messaging_capable, data_type_id
):
    packet = PositionPacket()

    packet.set_data_type_id(
        with_timestamp=with_timestamp,
        messaging_capable=messaging_capable
    )

    assert packet.data_type_id == data_type_id


@pytest.mark.parametrize(
    "data_type_id,result", [
        ("@", True),    # With timestamp, messaging capable
        ("/", True),    # With timestamp, not messaging capable
        ("=", False),   # Without timestamp, messaging capable
        ("!", False),   # Without timestamp, not messaging capable
    ]
)
def test_with_timestamp(
        data_type_id, result
):
    packet = PositionPacket()
    packet.data_type_id = data_type_id

    assert packet.with_timestamp == result


@pytest.mark.parametrize(
    "with_timestamp,messaging_capable,data_type_id",
    POSITION_TIMESTAMP_MESSAGING_DATA_TYPE_IDS
)
def test_with_timestamp_setter(
        with_timestamp, messaging_capable, data_type_id
):
    packet = PositionPacket()

    packet.with_timestamp = with_timestamp
    assert packet.with_timestamp is with_timestamp


@pytest.mark.parametrize(
    "with_timestamp,messaging_capable,data_type_id",
    POSITION_TIMESTAMP_MESSAGING_DATA_TYPE_IDS
)
def test_messaging_capable_setter(
        with_timestamp, messaging_capable, data_type_id
):
    packet = PositionPacket()

    packet.messaging_capable = messaging_capable
    assert packet.messaging_capable is messaging_capable


@pytest.mark.parametrize(
    "raw,result", [
        (packet, True) for packet in VALID_POSITION_WITH_X1J_HEADER_PACKETS
    ]
)
def test_offset(raw, result):
    packet = APRS.parse_packet(packet=raw)

    assert packet.offset is not None
    assert packet.with_timestamp is False
    assert packet.messaging_capable is False


def test_parse_uncompressed_position():
    lat, lng, amb, st, sid = PositionPacket._parse_uncompressed_position("5100.00N/11400.00Wk")

    assert lat == 51
    assert lng == -114
    assert amb == 0
    assert st == "/"
    assert sid == "k"


def test_parse_invalid_uncompressed_position():
    # Missing symbol code is now accepted leniently (symbol_id = None)
    lat, lng, amb, st, sid = PositionPacket._parse_uncompressed_position("5100.00N/11400.00W")
    assert lat == 51
    assert lng == -114
    assert sid is None


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
    packet = APRS.parse_packet(input_raw)

    assert type(packet) == PositionPacket
    assert repr(packet) == f"<PositionPacket: {packet.source}>"
    assert packet.data_type_id == data_type_id

    assert str(packet.source) == "XX1XX"
    assert str(packet.destination) == "APRS"
    assert str(packet.path) == "TCPIP*,qAC,FOURTH"

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
    packet = APRS.parse_packet(input_raw)

    assert type(packet) == PositionPacket
    assert repr(packet) == f"<PositionPacket: {packet.source}>"
    assert packet.data_type_id == "="

    assert str(packet.source) == "XX1XX"
    assert str(packet.destination) == "APRS"
    assert str(packet.path) == "TCPIP*,qAC,FOURTH"

    assert packet.latitude == latitude
    assert packet.longitude == longitude
    assert packet.ambiguity == 0

    assert packet.course == 88
    assert packet.speed == 36.2

    assert packet.symbol_table == "/"
    assert packet.symbol_id == ">"

    assert packet.comment == "Test packet"


def test_position_with_phg():
    packet = APRS.parse_packet(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$PHG5132')

    assert packet.power == 25
    assert packet.height == 20
    assert packet.gain == 3
    assert packet.directivity == 90


def test_position_with_rng():
    packet = APRS.parse_packet(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$RNG0050')

    assert packet.radio_range == 50


def test_position_with_dfs():
    packet = APRS.parse_packet(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$DFS2360')

    assert packet.strength == 2
    assert packet.height == 80
    assert packet.gain == 6
    assert packet.directivity is None


def test_position_with_missing_timestamp():
    p = APRS.parse_packet('XX1XX>APRS,TCPIP*,qAC,FOURTH:@5030.50S/10020.30E$221/000/A=005000Test packet')
    assert p.timestamp is None
    assert p.latitude is not None


def test_parse_data_with_phg():
    phg, rng, dfs, course, speed, altitude, comment = PositionPacket._parse_data("PHG5132")

    assert phg == "5132"


def test_parse_data_with_rng():
    phg, rng, dfs, course, speed, altitude, comment = PositionPacket._parse_data("RNG0050")

    assert rng == "0050"


def test_parse_data_with_dfs():
    phg, rng, dfs, course, speed, altitude, comment = PositionPacket._parse_data("DFS2360")

    assert dfs == "2360"


def test_parse_data_with_altitude():
    phg, rng, dfs, course, speed, altitude, comment = PositionPacket._parse_data(
        "/A=002000Test status"
    )

    assert altitude == 2000


def test_position_ambiguity():
    packet = APRS.parse_packet('XX1XX>APRS,TCPIP*,qAC,FOURTH:!49  .  N/072  .  W-')

    assert packet.ambiguity == 4
    assert packet.latitude == 49.0
    assert packet.longitude == -72.0


def test_compressed_lowercase_overlay():
    from aprspy.warnings import ParseWarningCode
    # DigiPi sends lowercase overlay chars (e.g. 'b') in compressed position
    p = APRS.parse_packet(
        'KK4DLV-2>APDW18,KV3B-1,WIDE1*,qAO,N4CJR-1:!b:eXQ:sml#  ! KK4DLV WIDE1 DigiPi'
    )
    assert type(p) == PositionPacket
    assert p.symbol_table == 'b'
    assert any(w.code == ParseWarningCode.POSITION_LOWERCASE_OVERLAY for w in p.parse_warnings)
