import pytest

from aprspy import APRS, PositionPacket, MICEPacket, StatusPacket, MessagePacket, ParseError


def test_uncompressed_latitude():
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


def test_uncompressed_longitude():
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
        # Random garbage
        APRS.decode_uncompressed_longitude("GARBAGE")
        assert False
    except ValueError:
        assert True
    except:
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

    assert lng == -72.75000393777269

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


def test_packet():
    raw = 'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005Test packet'

    packet = APRS.parse(raw)

    assert packet.raw == raw


def test_position_packet():
    raw_packets = [
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005Test packet', 50.508333, -100.338333),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30E$221/000/A=005Test packet', 50.508333, 100.338333),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50S/10020.30W$221/000/A=005Test packet', -50.508333, -100.338333),
        ('XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50S/10020.30E$221/000/A=005Test packet', -50.508333, 100.338333),
    ]

    for raw in raw_packets:
        packet = APRS.parse(raw[0])

        assert type(packet) == PositionPacket
        assert repr(packet) == f"<PositionPacket: {packet.source}>"
        assert packet.data_type_id == "="

        assert packet.source == "XX1XX"
        assert packet.destination == "APRS"
        assert packet.path == "TCPIP*,qAC,FOURTH"

        assert packet.latitude == raw[1]
        assert packet.longitude == raw[2]
        assert packet.ambiguity == 0

        assert packet.course == 221
        assert packet.speed == 0

        assert packet.symbol_table == "/"
        assert packet.symbol_id == "$"

        assert packet.comment == "/A=005Test packet"

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
        assert packet.path == "TCPIP*,qAC,FOURTH"

        assert packet.latitude == raw[1]
        assert packet.longitude == raw[2]
        assert packet.ambiguity == None

        assert packet.course == 88
        assert packet.speed == 36.2

        assert packet.symbol_table == "/"
        assert packet.symbol_id == ">"

        assert packet.comment == "Test packet"

def test_mice_packet():
    raw = r'VE6LY-9>U1PRSS-1,WIDE1-1,WIDE2-2,qAR,CALGRY:`*\Fl"Bk/]"?l}146.850MHz Andy S andy@nsnw.ca='

    packet = APRS.parse(raw)

    assert type(packet) == MICEPacket
    assert repr(packet) == f"<MICEPacket: {packet.source}>"
    assert packet.data_type_id == "`"

    assert packet.source == "VE6LY-9"
    assert packet.destination == "U1PRSS-1"
    assert packet.path == "WIDE1-1,WIDE2-2,qAR,CALGRY"

    assert packet.latitude == 51.038833
    assert packet.longitude == -114.073667

    assert packet.course == 238
    assert packet.speed == 0
    assert packet.altitude == 1086

    assert packet.symbol_table == "/"
    assert packet.symbol_id == "k"

    assert packet.comment == "146.850MHz Andy S andy@nsnw.ca="


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
    assert packet.path == "TCPIP*,qAC,TEST"

    assert packet.addressee == "YY9YY-9"
    assert packet.message == "This is a test message"
    assert packet.message_id == "001"


def test_bulletin_packet():
    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::BLN3     :Snow expected in Tampa RSN'

    packet = APRS.parse(raw)

    assert type(packet) == MessagePacket
    assert repr(packet) == f"<MessagePacket: {packet.source} -> Bulletin #{packet.bulletin_id}>"
    assert packet.data_type_id == ":"

    assert packet.source == "XX1XX-1"
    assert packet.destination == "APRS"
    assert packet.path == "TCPIP*,qAC,TEST"

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
    assert packet.path == "TCPIP*,qAC,TEST"

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
    assert packet.path == "TCPIP*,qAC,TEST"

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
