import pytest

from aprspy import APRS, MessagePacket
from aprspy.exceptions import ParseError


def test_empty_message_packet():
    packet = MessagePacket()

    assert repr(packet) == "<MessagePacket>"


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

    # Test resetting attributes to None
    packet.addressee = None
    assert packet.addressee is None

    packet.message = None
    assert packet.message is None

    packet.message_id = None
    assert packet.message_id is None


def test_invalid_message_packet():
    # Message IDs have a maximum length of 5
    try:
        APRS.parse('XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9  :This is a test message{000001')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False


def test_invalid_message_packet_properties():
    m = MessagePacket()

    # Addressee must be a str and 5 characters or less
    try:
        m.addressee = 123
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    try:
        m.addressee = "XXX1XXX-11"
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    # Message must be a str and 67 characters or less
    try:
        m.message = 123
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    try:
        m.message = "This message is 68 characters long, which is a little bit too long.."
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    # Message ID must be a str and 5 characters or less
    try:
        m.message_id = 123
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    try:
        m.message_id = "123456"
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    # Bulletin ID must be an int between 0 and 9 inclusive
    try:
        m.bulletin_id = "1"
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    try:
        m.bulletin_id = 10
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    # Announcement ID must be a single character
    try:
        m.announcement_id = 1
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    try:
        m.announcement_id = "AA"
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    # Group bulletin name must be a str with a maximum length of 5 characters
    try:
        m.group_bulletin_name = 123
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    try:
        m.group_bulletin_name = "ABCDEF"
        assert False
    except ValueError:
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
    assert packet.bulletin_id == 3
    assert packet.message == "Snow expected in Tampa RSN"

    # Test resetting attributes to None
    packet.bulletin_id = None
    assert packet.bulletin_id is None


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
    assert packet.bulletin_id is None
    assert packet.announcement_id == "Q"
    assert packet.message == "Mt St Helen digi will be QRT this weekend"

    # Test resetting attributes to None
    packet.announcement_id = None
    assert packet.announcement_id is None


def test_group_bulletin_packet():
    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::BLN4WX   :Stand by your snowplows'

    packet = APRS.parse(raw)

    assert type(packet) == MessagePacket
    assert repr(packet) == f"<MessagePacket: {packet.source} -> Group Bulletin {packet.group_bulletin_name} #{packet.bulletin_id}>"
    assert packet.data_type_id == ":"

    assert packet.source == "XX1XX-1"
    assert packet.destination == "APRS"
    assert str(packet.path) == "TCPIP*,qAC,TEST"

    assert packet.addressee == "BLN4WX"
    assert packet.bulletin_id == 4
    assert packet.group_bulletin_name == "WX"
    assert packet.message == "Stand by your snowplows"

    # Test resetting attributes to None
    packet.bulletin_id = None
    assert packet.bulletin_id is None

    packet.group_bulletin_name = None
    assert packet.group_bulletin_name is None


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


def test_invalid_message_id():
    with pytest.raises(ParseError):
        # This message has a message ID that is too long (> 5 characters long)
        raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9  :This is a test message{123456'
        APRS.parse(raw)
