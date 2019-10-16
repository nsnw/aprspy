import pytest

from geopy import Point
from aprspy import APRS
from aprspy.utils import APRSUtils
from aprspy.packets.position import PositionPacket
from aprspy.exceptions import ParseError


def test_empty_packet():
    packet = PositionPacket()

    assert str(packet) == "<PositionPacket>"


def test_init_position_packet():
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
    # Missing symbol ID
    try:
        PositionPacket._parse_uncompressed_position("5100.00N/11400.00W")
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False


def test_parse_compressed_position():
    lat, lng, alt, course, speed, radio_range = PositionPacket._parse_compressed_position(
        "/5L!!<*e7OS]S"
    )

    assert lat == 49.5
    assert lng == -72.750004
    assert alt == 10004.52

    lat, lng, alt, course, speed, radio_range = PositionPacket._parse_compressed_position(
        "/5L!!<*e7>{?!"
    )

    assert lat == 49.5
    assert lng == -72.750004
    assert radio_range == 20.13

    lat, lng, alt, course, speed, radio_range = PositionPacket._parse_compressed_position(
        "/5L!!<*e7> sT"
    )

    assert lat == 49.5
    assert lng == -72.750004
    assert alt is None


def test_parse_invalid_compressed_position():
    # Missing symbol ID
    try:
        PositionPacket._parse_compressed_position("/5L!!<*e7> s")
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    # Missing
    try:
        PositionPacket._parse_compressed_position("/5L!!<*e7>}AA")
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False


def test_decode_uncompressed_latitude():
    # Test uncompressed latitude without ambiguity
    lat, ambiguity = APRSUtils.decode_uncompressed_latitude("4903.55N")

    assert lat == 49.059167
    assert ambiguity == 0

    # Test uncompressed latitude with 1 level of ambiguity
    lat, ambiguity = APRSUtils.decode_uncompressed_latitude("4903.5 N")

    assert lat == 49.058333
    assert ambiguity == 1

    # Test uncompressed latitude with 2 levels of ambiguity
    lat, ambiguity = APRSUtils.decode_uncompressed_latitude("4903.  N")

    assert lat == 49.05
    assert ambiguity == 2

    # Test uncompressed latitude with 3 levels of ambiguity
    lat, ambiguity = APRSUtils.decode_uncompressed_latitude("490 .  N")

    assert lat == 49
    assert ambiguity == 3

    # Test uncompressed latitude with 4 levels of ambiguity
    lat, ambiguity = APRSUtils.decode_uncompressed_latitude("49  .  N")

    assert lat == 49
    assert ambiguity == 4


def test_decode_invalid_uncompressed_latitude():
    # Test invalid latitudes
    try:
        # 91 degrees north is not a valid latitude
        APRSUtils.decode_uncompressed_latitude("9100.00N")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # West is not a valid latitude direction
        APRSUtils.decode_uncompressed_latitude("4903.50W")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # Period is in the wrong position
        APRSUtils.decode_uncompressed_latitude("49035.0N")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # >4 units of ambiguity is invalid for latitude
        APRSUtils.decode_uncompressed_latitude("5   . N")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # Random garbage
        APRSUtils.decode_uncompressed_latitude("GARBAGE")
        assert False
    except ValueError:
        assert True
    except:
        assert False


def test_encode_uncompressed_latitude():
    # Test latitude
    latitude = APRSUtils.encode_uncompressed_latitude(51.473821)
    assert latitude == "5128.43N"

    # Test latitude with differing levels of ambiguity
    latitude = APRSUtils.encode_uncompressed_latitude(51.473821, 1)
    assert latitude == "5128.4 N"

    latitude = APRSUtils.encode_uncompressed_latitude(51.473821, 2)
    assert latitude == "5128.  N"

    latitude = APRSUtils.encode_uncompressed_latitude(51.473821, 3)
    assert latitude == "512 .  N"

    latitude = APRSUtils.encode_uncompressed_latitude(51.473821, 4)
    assert latitude == "51  .  N"

    # ints are allowed too
    latitude = APRSUtils.encode_uncompressed_latitude(51)
    assert latitude == "5100.00N"

    # Ensure that southern latitudes work
    latitude = APRSUtils.encode_uncompressed_latitude(-51)
    assert latitude == "5100.00S"


def test_encode_invalid_uncompressed_latitude():
    # Must be a float or int
    try:
        latitude = APRSUtils.encode_uncompressed_latitude("51")
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Must be be between -90 and 90
    try:
        latitude = APRSUtils.encode_uncompressed_latitude(91)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    # Ambiguity must be an int
    try:
        latitude = APRSUtils.encode_uncompressed_latitude(51, "1")
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # ...and it must be be between 0 and 4
    try:
        latitude = APRSUtils.encode_uncompressed_latitude(51, 5)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False


def test_decode_uncompressed_longitude():
    # Test uncompressed longitude without ambiguity
    lng = APRSUtils.decode_uncompressed_longitude("07211.75W")

    assert lng == -72.195833

    # Test uncompressed longitude with 1 level of ambiguity
    lng = APRSUtils.decode_uncompressed_longitude("07211.75W", 1)

    assert lng == -72.195

    # Test uncompressed longitude with 2 levels of ambiguity
    lng = APRSUtils.decode_uncompressed_longitude("07211.75W", 2)

    assert lng == -72.183333

    # Test uncompressed longitude with 3 levels of ambiguity
    lng = APRSUtils.decode_uncompressed_longitude("07211.75W", 3)

    assert lng == -72.166667

    # Test uncompressed longitude with 4 levels of ambiguity
    lng = APRSUtils.decode_uncompressed_longitude("07211.75W", 4)

    assert lng == -72.0


def test_decode_invalid_uncompressed_longitude():
    # Test invalid latitudes
    try:
        # 181 degrees west is not a valid longitude
        APRSUtils.decode_uncompressed_longitude("18100.00W")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # North is not a valid longitude direction
        APRSUtils.decode_uncompressed_longitude("07201.75N")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # Period is in the wrong position
        APRSUtils.decode_uncompressed_longitude("072017.5N")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # Ambiguity must be 1-4
        APRSUtils.decode_uncompressed_longitude("07201.75W", 5)
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # Random garbage
        APRSUtils.decode_uncompressed_longitude("GARBAGE")
        assert False
    except ValueError:
        assert True
    except:
        assert False


def test_encode_uncompressed_longitude():
    # Test longitude
    longitude = APRSUtils.encode_uncompressed_longitude(-114.434325)
    assert longitude == "11426.06W"

    # Test longitude with differing levels of ambiguity
    longitude = APRSUtils.encode_uncompressed_longitude(-114.434325, 1)
    assert longitude == "11426.0 W"

    longitude = APRSUtils.encode_uncompressed_longitude(-114.434325, 2)
    assert longitude == "11426.  W"

    longitude = APRSUtils.encode_uncompressed_longitude(-114.434325, 3)
    assert longitude == "1142 .  W"

    longitude = APRSUtils.encode_uncompressed_longitude(-114.434325, 4)
    assert longitude == "114  .  W"

    # Test eastern latitudes too
    longitude = APRSUtils.encode_uncompressed_longitude(114.434325, 4)
    assert longitude == "114  .  E"


def test_encode_invalid_uncompressed_longitude():
    # Must be a float or int
    try:
        longitude = APRSUtils.encode_uncompressed_longitude("114")
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Must be be between -180 and 180
    try:
        longitude = APRSUtils.encode_uncompressed_longitude(181)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    # Ambiguity must be an int
    try:
        longitude = APRSUtils.encode_uncompressed_longitude(114, "1")
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # ...and it must be be between 0 and 4
    try:
        longitude = APRSUtils.encode_uncompressed_longitude(114, 5)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False


def test_compressed_latitude():
    # Test compressed latitude
    lat = APRSUtils.decode_compressed_latitude("5L!!")

    assert lat == 49.5

    # Test invalid input
    try:
        # Length must be 4
        APRSUtils.decode_compressed_latitude("5L!!!")
        assert False
    except ValueError:
        assert True
    except:
        assert False


def test_compressed_longitude():
    # Test compressed longitude
    lng = APRSUtils.decode_compressed_longitude("<*e7")

    assert lng == -72.750004

    # Test invalid input
    try:
        # Length must be 4
        APRSUtils.decode_compressed_latitude("<*e77")
        assert False
    except ValueError:
        assert True
    except:
        assert False


def test_position_packet():
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
            #assert packet.timestamp == raw[4]
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
        assert packet.ambiguity == None

        assert packet.course == 88
        assert packet.speed == 36.2

        assert packet.symbol_table == "/"
        assert packet.symbol_id == ">"

        assert packet.comment == "Test packet"


def test_position_packet_with_df():

    packet = APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W\088/036/270/729')

    assert packet.course == 88
    assert packet.speed == 36
    assert packet.bearing == 270
    assert packet.number == 87.5
    assert packet.df_range == 4
    assert packet.quality == 1


def test_invalid_position_packet_with_df():

    # Missing DF values
    try:
        packet = APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W\\')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False

    # Invalid DF format
    try:
        packet = APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W\088036270729')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False


def test_position_packet_with_phg():

    packet = APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$PHG5132')

    assert packet.power == 25
    assert packet.height == 20
    assert packet.gain == 3
    assert packet.directivity == 90


def test_position_packet_with_rng():

    packet = APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$RNG0050')

    assert packet.radio_range == 50


def test_position_packet_with_dfs():

    packet = APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$DFS2360')

    assert packet.strength == 2
    assert packet.height == 80
    assert packet.gain == 6
    assert packet.directivity == None


def test_position_packet_with_weather():
    # TODO - Weather is not yet implemented
    packet = APRS.parse(r'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W_TEST')


def test_invalid_position_packet():
    # Try to parse a non-position packet
    try:
        # This is a contrived example
        packet = APRS.parse(
            'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet'
        )
        packet.data_type_id = "X"
        packet._parse()
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False


def test_invalid_position_packet_with_timestamp():
    # This packet should have a timestamp
    try:
        packet = APRS.parse(
            'XX1XX>APRS,TCPIP*,qAC,FOURTH:@5030.50S/10020.30E$221/000/A=005000Test packet'
        )
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False


def test_invalid_uncompressed_longitude():
    # North is invalid for longitude
    try:
        APRSUtils.decode_uncompressed_longitude("10020.30N")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    # >180 is invalid for longitude
    try:
        APRSUtils.decode_uncompressed_longitude("18120.30W")
        assert False
    except ValueError:
        assert True
    except:
        assert False


def test_parse_data():
    phg, rng, dfs, course, speed, altitude, comment = PositionPacket._parse_data(
        "PHG5132"
    )

    assert phg == "5132"

    phg, rng, dfs, course, speed, altitude, comment = PositionPacket._parse_data(
        "RNG0050"
    )

    assert rng == "0050"

    phg, rng, dfs, course, speed, altitude, comment = PositionPacket._parse_data(
        "DFS2360"
    )

    assert dfs == "2360"

    phg, rng, dfs, course, speed, altitude, comment = PositionPacket._parse_data(
        "/A=002000Test status"
    )

    assert altitude == 2000
