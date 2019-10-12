import pytest

from geopy import Point
from aprspy import APRS, APRSPacket, PositionPacket, MICEPacket, StatusPacket, MessagePacket,\
    ParseError
from aprspy.components import Station, Path, PathHop


def test_init_packet():
    packet = APRSPacket()
    assert repr(packet) == "<APRSPacket>"

    packet = APRSPacket(source="XX1XX", destination="APRS", path="TCPIP*,qAR,T2TEST",
                        info=">This is a test status message")

    assert repr(packet) == "<APRSPacket: XX1XX>"
    assert packet.source == "XX1XX"
    assert packet.destination == "APRS"
    assert packet.info == ">This is a test status message"


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


def test_packet_properties():
    packet = APRSPacket()
    station = Station(callsign="XX1XX-11")
    dest = Station(callsign="APRS")
    path = Path(path="TCPIP*,qAR,T2TEST")

    packet.source = station
    assert packet.source == station

    packet.destination = dest
    assert packet.destination == dest

    packet.path = path
    assert packet.path == path


def test_invalid_packet_properties():
    packet = APRSPacket()

    # Source is too long
    try:
        packet.source = "XXX1XXX-11"
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    # Source type is invalid
    try:
        packet.source = 11
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Destination is too long
    try:
        packet.destination = "XXX1XXX-11"
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    # Destination type is invalid
    try:
        packet.destination = 11
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Path type is invalid
    try:
        packet.path = False
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False


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
    assert alt == None



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
    lat, ambiguity = APRS.decode_uncompressed_latitude("4903.55N")

    assert lat == 49.059167
    assert ambiguity == 0

    # Test uncompressed latitude with 1 level of ambiguity
    lat, ambiguity = APRS.decode_uncompressed_latitude("4903.5 N")

    assert lat == 49.058333
    assert ambiguity == 1

    # Test uncompressed latitude with 2 levels of ambiguity
    lat, ambiguity = APRS.decode_uncompressed_latitude("4903.  N")

    assert lat == 49.05
    assert ambiguity == 2

    # Test uncompressed latitude with 3 levels of ambiguity
    lat, ambiguity = APRS.decode_uncompressed_latitude("490 .  N")

    assert lat == 49
    assert ambiguity == 3

    # Test uncompressed latitude with 4 levels of ambiguity
    lat, ambiguity = APRS.decode_uncompressed_latitude("49  .  N")

    assert lat == 49
    assert ambiguity == 4


def test_decode_invalid_uncompressed_latitude():
    # Test invalid latitudes
    try:
        # 91 degrees north is not a valid latitude
        APRS.decode_uncompressed_latitude("9100.00N")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # West is not a valid latitude direction
        APRS.decode_uncompressed_latitude("4903.50W")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # Period is in the wrong position
        APRS.decode_uncompressed_latitude("49035.0N")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # >4 units of ambiguity is invalid for latitude
        APRS.decode_uncompressed_latitude("5   . N")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # Random garbage
        APRS.decode_uncompressed_latitude("GARBAGE")
        assert False
    except ValueError:
        assert True
    except:
        assert False


def test_encode_uncompressed_latitude():
    # Test latitude
    latitude = APRS.encode_uncompressed_latitude(51.473821)
    assert latitude == "5128.43N"

    # Test latitude with differing levels of ambiguity
    latitude = APRS.encode_uncompressed_latitude(51.473821, 1)
    assert latitude == "5128.4 N"

    latitude = APRS.encode_uncompressed_latitude(51.473821, 2)
    assert latitude == "5128.  N"

    latitude = APRS.encode_uncompressed_latitude(51.473821, 3)
    assert latitude == "512 .  N"

    latitude = APRS.encode_uncompressed_latitude(51.473821, 4)
    assert latitude == "51  .  N"

    # ints are allowed too
    latitude = APRS.encode_uncompressed_latitude(51)
    assert latitude == "5100.00N"

    # Ensure that southern latitudes work
    latitude = APRS.encode_uncompressed_latitude(-51)
    assert latitude == "5100.00S"


def test_encode_invalid_uncompressed_latitude():
    # Must be a float or int
    try:
        latitude = APRS.encode_uncompressed_latitude("51")
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Must be be between -90 and 90
    try:
        latitude = APRS.encode_uncompressed_latitude(91)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    # Ambiguity must be an int
    try:
        latitude = APRS.encode_uncompressed_latitude(51, "1")
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # ...and it must be be between 0 and 4
    try:
        latitude = APRS.encode_uncompressed_latitude(51, 5)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False


def test_decode_uncompressed_longitude():
    # Test uncompressed longitude without ambiguity
    lng = APRS.decode_uncompressed_longitude("07211.75W")

    assert lng == -72.195833

    # Test uncompressed longitude with 1 level of ambiguity
    lng = APRS.decode_uncompressed_longitude("07211.75W", 1)

    assert lng == -72.195

    # Test uncompressed longitude with 2 levels of ambiguity
    lng = APRS.decode_uncompressed_longitude("07211.75W", 2)

    assert lng == -72.183333

    # Test uncompressed longitude with 3 levels of ambiguity
    lng = APRS.decode_uncompressed_longitude("07211.75W", 3)

    assert lng == -72.166667

    # Test uncompressed longitude with 4 levels of ambiguity
    lng = APRS.decode_uncompressed_longitude("07211.75W", 4)

    assert lng == -72.0


def test_decode_invalid_uncompressed_longitude():
    # Test invalid latitudes
    try:
        # 181 degrees west is not a valid longitude
        APRS.decode_uncompressed_longitude("18100.00W")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # North is not a valid longitude direction
        APRS.decode_uncompressed_longitude("07201.75N")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # Period is in the wrong position
        APRS.decode_uncompressed_longitude("072017.5N")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # Ambiguity must be 1-4
        APRS.decode_uncompressed_longitude("07201.75W", 5)
        assert False
    except ValueError:
        assert True
    except:
        assert False

    try:
        # Random garbage
        APRS.decode_uncompressed_longitude("GARBAGE")
        assert False
    except ValueError:
        assert True
    except:
        assert False


def test_encode_uncompressed_longitude():
    # Test longitude
    longitude = APRS.encode_uncompressed_longitude(-114.434325)
    assert longitude == "11426.06W"

    # Test longitude with differing levels of ambiguity
    longitude = APRS.encode_uncompressed_longitude(-114.434325, 1)
    assert longitude == "11426.0 W"

    longitude = APRS.encode_uncompressed_longitude(-114.434325, 2)
    assert longitude == "11426.  W"

    longitude = APRS.encode_uncompressed_longitude(-114.434325, 3)
    assert longitude == "1142 .  W"

    longitude = APRS.encode_uncompressed_longitude(-114.434325, 4)
    assert longitude == "114  .  W"

    # Test eastern latitudes too
    longitude = APRS.encode_uncompressed_longitude(114.434325, 4)
    assert longitude == "114  .  E"


def test_encode_invalid_uncompressed_longitude():
    # Must be a float or int
    try:
        longitude = APRS.encode_uncompressed_longitude("114")
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Must be be between -180 and 180
    try:
        longitude = APRS.encode_uncompressed_longitude(181)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    # Ambiguity must be an int
    try:
        longitude = APRS.encode_uncompressed_longitude(114, "1")
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # ...and it must be be between 0 and 4
    try:
        longitude = APRS.encode_uncompressed_longitude(114, 5)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False


def test_compressed_latitude():
    # Test compressed latitude
    lat = APRS.decode_compressed_latitude("5L!!")

    assert lat == 49.5

    # Test invalid input
    try:
        # Length must be 4
        APRS.decode_compressed_latitude("5L!!!")
        assert False
    except ValueError:
        assert True
    except:
        assert False


def test_compressed_longitude():
    # Test compressed longitude
    lng = APRS.decode_compressed_longitude("<*e7")

    assert lng == -72.750004

    # Test invalid input
    try:
        # Length must be 4
        APRS.decode_compressed_latitude("<*e77")
        assert False
    except ValueError:
        assert True
    except:
        assert False


def test_timestamp():
    timestamp = APRS.decode_timestamp("091234z")


#def test_packet():
#    raw = 'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005Test packet'
#
#    packet = APRS.parse(raw)
#
#    assert packet.raw == raw


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



def test_mice_packet():
    raw = r'VE6LY-9>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}146.850MHz Andy S andy@nsnw.ca='

    packet = APRS.parse(raw)

    assert type(packet) == MICEPacket
    assert repr(packet) == f"<MICEPacket: {packet.source}>"
    assert packet.data_type_id == "`"

    assert packet.source == "VE6LY-9"
    assert packet.destination == "U1PRSS-1"
    assert str(packet.path) == "WIDE1-1,WIDE2-2,qAR,CALGRY"

    assert packet.latitude == 51.038833
    assert packet.longitude == -114.073667

    assert packet.course == 238
    assert packet.speed == 0
    assert packet.altitude == 1086

    assert packet.symbol_table == "/"
    assert packet.symbol_id == "k"

    assert packet.comment == "146.850MHz Andy S andy@nsnw.ca="


def test_invalid_mice_packet():
    # Missing symbol table
    try:
        APRS.parse(r'VE6LY-9>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False

    # Missing symbol ID
    try:
        APRS.parse(r'VE6LY-9>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"B')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False



def test_status_packet():
    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>211248zPHG71801/Test status'

    packet = APRS.parse(raw)

    assert type(packet) == StatusPacket
    assert repr(packet) == f"<StatusPacket: {packet.source}>"
    assert packet.data_type_id == ">"

    assert packet.status_message == "PHG71801/Test status"

    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>091234zTest status with a timestamp'

    packet = APRS.parse(raw)

    assert type(packet) == StatusPacket
    assert repr(packet) == f"<StatusPacket: {packet.source}>"
    assert packet.data_type_id == ">"

    assert packet.status_message == "Test status with a timestamp"

    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>Test status without a timestamp'

    packet = APRS.parse(raw)

    assert type(packet) == StatusPacket
    assert repr(packet) == f"<StatusPacket: {packet.source}>"
    assert packet.data_type_id == ">"

    assert packet.status_message == "Test status without a timestamp"

    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21XA/- Test status with 6 digit Maidenhead locator'

    packet = APRS.parse(raw)

    assert type(packet) == StatusPacket
    assert repr(packet) == f"<StatusPacket: {packet.source}>"
    assert packet.data_type_id == ">"

    assert packet.maidenhead_locator == "DO21XA"
    assert packet.symbol_table == "/"
    assert packet.symbol_id == "-"
    assert packet.status_message == "Test status with 6 digit Maidenhead locator"

    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21XA/-'

    packet = APRS.parse(raw)

    assert type(packet) == StatusPacket
    assert repr(packet) == f"<StatusPacket: {packet.source}>"
    assert packet.data_type_id == ">"

    assert packet.maidenhead_locator == "DO21XA"
    assert packet.symbol_table == "/"
    assert packet.symbol_id == "-"
    assert packet.status_message == None

    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21/- Test status with 4 digit Maidenhead locator'

    packet = APRS.parse(raw)

    assert type(packet) == StatusPacket
    assert repr(packet) == f"<StatusPacket: {packet.source}>"
    assert packet.data_type_id == ">"

    assert packet.maidenhead_locator == "DO21"
    assert packet.symbol_table == "/"
    assert packet.symbol_id == "-"
    assert packet.status_message == "Test status with 4 digit Maidenhead locator"

    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21/-'

    packet = APRS.parse(raw)

    assert type(packet) == StatusPacket
    assert repr(packet) == f"<StatusPacket: {packet.source}>"
    assert packet.data_type_id == ">"

    assert packet.maidenhead_locator == "DO21"
    assert packet.symbol_table == "/"
    assert packet.symbol_id == "-"
    assert packet.status_message == None

    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21/- Test status with heading and power^B7'

    packet = APRS.parse(raw)

    assert type(packet) == StatusPacket
    assert repr(packet) == f"<StatusPacket: {packet.source}>"
    assert packet.data_type_id == ">"

    assert packet.maidenhead_locator == "DO21"
    assert packet.symbol_table == "/"
    assert packet.symbol_id == "-"
    assert packet.status_message == "Test status with heading and power^B7"



def test_invalid_status_packet():
    # Invalid status messages
    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21XA/-Test status with 6 digit Maidenhead locator'

    try:
        packet = APRS.parse(raw)
        assert False
    except ParseError:
        assert True
    except:
        assert False

    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST:>DO21/-Test status with 4 digit Maidenhead locator'

    try:
        packet = APRS.parse(raw)
        assert False
    except ParseError:
        assert True
    except:
        assert False


def test_message_packet():
    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9  :This is a test message{001'

    packet = APRS.parse(raw)

    assert type(packet) == MessagePacket
    assert repr(packet) == f"<MessagePacket: {packet.source} -> {packet.addressee}>"
    assert packet.data_type_id == ":"

    assert packet.source == "XX1XX-1"
    assert packet.destination == "APRS"
    assert str(packet.path) == "TCPIP*,qAC,TEST"

    assert packet.addressee == "YY9YY-9"
    assert packet.message == "This is a test message"
    assert packet.message_id == "001"


def test_invalid_message_packet():
    # Message IDs have a maximum length of 5
    try:
        APRS.parse('XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9  :This is a test message{000001')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False


def test_bulletin_packet():
    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::BLN3     :Snow expected in Tampa RSN'

    packet = APRS.parse(raw)

    assert type(packet) == MessagePacket
    assert repr(packet) == f"<MessagePacket: {packet.source} -> Bulletin #{packet.bulletin_id}>"
    assert packet.data_type_id == ":"

    assert packet.source == "XX1XX-1"
    assert packet.destination == "APRS"
    assert str(packet.path) == "TCPIP*,qAC,TEST"

    assert packet.addressee == "BLN3"
    assert packet.bulletin is True
    assert packet.bulletin_id == 3
    assert packet.message == "Snow expected in Tampa RSN"


def test_announcement_packet():
    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::BLNQ     :Mt St Helen digi will be QRT this weekend'

    packet = APRS.parse(raw)

    assert type(packet) == MessagePacket
    assert repr(packet) == f"<MessagePacket: {packet.source} -> Announcement {packet.announcement_id}>"
    assert packet.data_type_id == ":"

    assert packet.source == "XX1XX-1"
    assert packet.destination == "APRS"
    assert str(packet.path) == "TCPIP*,qAC,TEST"

    assert packet.addressee == "BLNQ"
    assert packet.bulletin is True
    assert packet.bulletin_id == None
    assert packet.message == "Mt St Helen digi will be QRT this weekend"


def test_group_bulletin_packet():
    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::BLN4WX   :Stand by your snowplows'

    packet = APRS.parse(raw)

    assert type(packet) == MessagePacket
    assert repr(packet) == f"<MessagePacket: {packet.source} -> Group Bulletin {packet.group_bulletin} #{packet.bulletin_id}>"
    assert packet.data_type_id == ":"

    assert packet.source == "XX1XX-1"
    assert packet.destination == "APRS"
    assert str(packet.path) == "TCPIP*,qAC,TEST"

    assert packet.addressee == "BLN4WX"
    assert packet.bulletin is True
    assert packet.bulletin_id == 4
    assert packet.group_bulletin == "WX"
    assert packet.message == "Stand by your snowplows"


def test_invalid_uncompressed_longitude():
    # North is invalid for longitude
    try:
        APRS.decode_uncompressed_longitude("10020.30N")
        assert False
    except ValueError:
        assert True
    except:
        assert False

    # >180 is invalid for longitude
    try:
        APRS.decode_uncompressed_longitude("18120.30W")
        assert False
    except ValueError:
        assert True
    except:
        assert False


def test_invalid_packet():
    # Missing > after source
    try:
        APRS.parse('XX1XXAPRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False

    # Source is too long
    try:
        APRS.parse('XXX1XXX-11>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False

    # Destination is too long
    try:
        APRS.parse('XX1XX>APRSAPRSAPRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False

    # Destination is invalid
    try:
        APRS.parse('XX1XX>aprs,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False

    # Destination is invalid
    try:
        APRS.parse('XX1XX>APRS-XX,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False

    # Packet is too short
    try:
        APRS.parse('XX1XX>APRS,TCPIP*,qAC,FOURTH:=')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False


def test_invalid_message_packet():
    # This message does not have the correct size for the addressee field, so the 2nd ':' is in the
    # wrong position
    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9 :This is a test message{001'

    try:
        packet = APRS.parse(raw)
        assert False
    except ParseError:
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


def test_decode_phg():
    (power, height, gain, directivity) = APRS.decode_phg("5132")

    assert power == 25
    assert height == 20
    assert gain == 3
    assert directivity == 90

    (power, height, gain, directivity) = APRS.decode_phg("5130")

    assert power == 25
    assert height == 20
    assert gain == 3
    assert directivity is None


def test_decode_invalid_phg():
    # PHG values must be numerical
    try:
        APRS.decode_phg("PHG513T")
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False


def test_encode_phg():
    phg = APRS.encode_phg(power=25, height=20, gain=3, directivity=90)
    assert phg == "5132"

    phg = APRS.encode_phg(power=25, height=20, gain=3, directivity=None)
    assert phg == "5130"


def test_decode_dfs():
    (strength, height, gain, directivity) = APRS.decode_dfs("2360")

    assert strength == 2
    assert height == 80
    assert gain == 6
    assert directivity == None

    (strength, height, gain, directivity) = APRS.decode_dfs("2361")

    assert strength == 2
    assert height == 80
    assert gain == 6
    assert directivity == 45


def test_decode_invalid_dfs():
    # DFS values must be numerical
    try:
        APRS.decode_dfs("DFS236Z")
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False


def test_encode_invalid_phg():
    # Invalid power
    try:
        phg = APRS.encode_phg(power=10, height=80, gain=6, directivity=None)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        phg = APRS.encode_phg(power="10", height=80, gain=6, directivity=None)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Invalid height
    try:
        phg = APRS.encode_phg(power=25, height=90, gain=6, directivity=None)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        phg = APRS.encode_phg(power=25, height="90", gain=6, directivity=None)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Invalid gain
    try:
        phg = APRS.encode_phg(power=25, height=80, gain=10, directivity=None)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        phg = APRS.encode_phg(power=25, height=80, gain="10", directivity=None)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Invalid directivity
    try:
        phg = APRS.encode_phg(power=25, height=80, gain=6, directivity=47)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        phg = APRS.encode_phg(power=25, height=80, gain=6, directivity="None")
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False


def test_encode_dfs():
    dfs = APRS.encode_dfs(strength=2, height=80, gain=6, directivity=None)
    assert dfs == "2360"

    dfs = APRS.encode_dfs(strength=2, height=80, gain=6, directivity=45)
    assert dfs == "2361"

def test_encode_invalid_dfs():
    # Invalid strength
    try:
        dfs = APRS.encode_dfs(strength=10, height=80, gain=6, directivity=None)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        dfs = APRS.encode_dfs(strength="2", height=80, gain=6, directivity=None)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Invalid height
    try:
        dfs = APRS.encode_dfs(strength=2, height=90, gain=6, directivity=None)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        dfs = APRS.encode_dfs(strength=2, height="80", gain=6, directivity=None)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Invalid gain
    try:
        dfs = APRS.encode_dfs(strength=2, height=80, gain=10, directivity=None)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        dfs = APRS.encode_dfs(strength=2, height=80, gain="6", directivity=None)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Invalid directivity
    try:
        dfs = APRS.encode_dfs(strength=2, height=80, gain=6, directivity=47)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        dfs = APRS.encode_dfs(strength=2, height=80, gain=6, directivity="None")
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False


def test_decode_nrq():
    # Test with example from APRS 1.01
    n, r, q = APRS.decode_nrq("729")

    assert n == 87.5
    assert r == 4
    assert q == 1

    # Test with 0
    n, r, q = APRS.decode_nrq("029")

    assert n == None
    assert r == None
    assert q == None

    # Test with manual
    n, r, q = APRS.decode_nrq("929")

    assert n == "manual"

    # Test different qualities
    # These don't fit neatly into 2 ** x
    n, r, q = APRS.decode_nrq("722")

    assert q == 120

    n, r, q = APRS.decode_nrq("721")

    assert q == 240

    n, r, q = APRS.decode_nrq("720")

    assert q == None


def test_decode_invalid_nrq():
    try:
        APRS.decode_nrq("S29")
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False
