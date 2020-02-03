import pytest

from aprspy import APRS, MessagePacket
from aprspy.exceptions import ParseError, GenerateError

# Input packet
raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9  :This is a test message{001'


@pytest.fixture
def packet():
    packet = APRS.parse(raw)
    return packet


def test_empty():
    packet = MessagePacket()

    assert repr(packet) == "<MessagePacket>"


def test_repr_with_source_only():
    packet = MessagePacket()
    packet.source = "YY1YY-12"

    assert repr(packet) == "<MessagePacket: YY1YY-12>"


def test_message_packet():
    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9  :This is a test message{001'
    APRS.parse(raw)


def test_type(packet):
    assert type(packet) == MessagePacket


def test_repr(packet):
    assert repr(packet) == f"<MessagePacket: {packet.source} -> {packet.addressee}>"


def test_data_type_id(packet):
    assert packet.data_type_id == ":"


def test_source(packet):
    assert packet.source == "XX1XX-1"


def test_destination(packet):
    assert packet.destination == "APRS"


def test_path(packet):
    assert str(packet.path) == "TCPIP*,qAC,TEST"


def test_addressee(packet):
    assert packet.addressee == "YY9YY-9"


def test_message(packet):
    assert packet.message == "This is a test message"


def test_message_id(packet):
    assert packet.message_id == "001"


def test_addressee_none(packet):
    # Test resetting attributes to None
    packet.addressee = None
    assert packet.addressee is None


def test_message_none(packet):
    packet.message = None
    assert packet.message is None


def test_message_id_none(packet):
    packet.message_id = None
    assert packet.message_id is None


def test_invalid_message_id():
    # Message IDs have a maximum length of 5
    try:
        APRS.parse('XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9  :This is a test message{000001')
        assert False
    except ParseError:
        assert True
    except Exception:
        assert False


def test_invalid_message_addressee_type():
    m = MessagePacket()

    # Addressee must be a str
    with pytest.raises(TypeError):
        m.addressee = 123


def test_invalid_message_addressee_value():
    m = MessagePacket()

    # Addressee must be 9 characters or less
    with pytest.raises(ValueError):
        m.addressee = "XXX1XXX-11"


def test_invalid_message_type():
    m = MessagePacket()

    # Message must be a str
    with pytest.raises(TypeError):
        m.message = 123


# TODO
# Disable this for now, because it's routinely violated
# def test_invalid_message_value():
#    m = MessagePacket()
#
#    # Message must be 67 characters or less
#    with pytest.raises(ValueError):
#        m.message = "This message is 68 characters long, which is a little bit too long.."


def test_invalid_message_id_type():
    m = MessagePacket()

    # Message ID must be a str and 5 characters or less
    with pytest.raises(TypeError):
        m.message_id = 123


def test_invalid_message_id_value():
    m = MessagePacket()

    # Message ID must be 5 characters or less
    with pytest.raises(ValueError):
        m.message_id = "123456"


def test_invalid_bulletin_id_type():
    m = MessagePacket()

    # Bulletin ID must be an int
    with pytest.raises(TypeError):
        m.bulletin_id = "1"


def test_invalid_bulletin_id_value():
    m = MessagePacket()

    # Bulletin ID must be between 0 and 9 inclusive
    with pytest.raises(ValueError):
        m.bulletin_id = 10


def test_invalid_announcement_id_type():
    m = MessagePacket()

    # Announcement ID must be a str
    with pytest.raises(TypeError):
        m.announcement_id = 1


def test_invalid_accouncement_id_value():
    m = MessagePacket()

    # Announcement ID must be a single character
    with pytest.raises(ValueError):
        m.announcement_id = "AA"


def test_invalid_group_bulletin_name_type():
    m = MessagePacket()

    # Group bulletin name must be a str with a maximum length of 5 characters
    with pytest.raises(TypeError):
        m.group_bulletin_name = 123


def test_invalid_group_bulletin_name_value():
    m = MessagePacket()

    # Group bulletin name must be a str with a maximum length of 5 characters
    with pytest.raises(ValueError):
        m.group_bulletin_name = "ABCDEF"


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
    assert repr(packet) == \
        f"<MessagePacket: {packet.source} -> Announcement {packet.announcement_id}>"
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
    assert repr(packet) == \
        f"<MessagePacket: {packet.source} -> Group Bulletin " \
        f"{packet.group_bulletin_name} #{packet.bulletin_id}>"
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


def test_invalid_addressee_field_size():
    raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9 :This is a test message{001'

    # This message does not have the correct size for the addressee field, so the 2nd ':' is in the
    # wrong position
    with pytest.raises(ParseError):
        APRS.parse(raw)


def test_message_invalid_message_id():
    with pytest.raises(ParseError):
        # This message has a message ID that is too long (> 5 characters long)
        raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9  :This is a test message{123456'
        APRS.parse(raw)


def test_invalid_announcement_id():
    with pytest.raises(ParseError):
        # This message has an invalid announcement ID (> 1 character long)
        raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::BLNAA    :This is a test bulletin'
        APRS.parse(raw)


def test_invalid_bulletin():
    with pytest.raises(ParseError):
        # This message does not have a bulletin or announcement ID
        raw = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::BLN      :This is a test bulletin'
        APRS.parse(raw)


def test_generate_message():
    m = MessagePacket()
    m.source = "XX1XX-11"
    m.destination = "APRS"
    m.path = "TCPIP*,qAR,T2TEST"
    m.addressee = "YY1YY-12"
    m.message = "This is a test message"

    assert m.info == "YY1YY-12 :This is a test message"


def test_generate_message_with_message_id():
    m = MessagePacket()
    m.source = "XX1XX-11"
    m.destination = "APRS"
    m.path = "TCPIP*,qAR,T2TEST"
    m.addressee = "YY1YY-12"
    m.message = "This is a test message"
    m.message_id = "001"

    assert m.info == "YY1YY-12 :This is a test message{001"


def test_generate_bulletin():
    m = MessagePacket()
    m.source = "XX1XX-11"
    m.destination = "APRS"
    m.path = "TCPIP*,qAR,T2TEST"
    m.bulletin_id = 1
    m.message = "This is a test bulletin"

    assert m.info == "BLN1     :This is a test bulletin"


def test_generate_group_bulletin():
    m = MessagePacket()
    m.source = "XX1XX-11"
    m.destination = "APRS"
    m.path = "TCPIP*,qAR,T2TEST"
    m.bulletin_id = 1
    m.group_bulletin_name = "TEST"
    m.message = "This is a test group bulletin"

    assert m.info == "BLN1TEST :This is a test group bulletin"


def test_generate_announcement():
    m = MessagePacket()
    m.source = "XX1XX-11"
    m.destination = "APRS"
    m.path = "TCPIP*,qAR,T2TEST"
    m.announcement_id = "A"
    m.message = "This is a test announcement"

    assert m.info == "BLNA     :This is a test announcement"


def test_generate_invalid_message():
    m = MessagePacket()
    m.source = "XX1XX-11"
    m.destination = "APRS"
    m.path = "TCPIP*,qAR,T2TEST"

    with pytest.raises(GenerateError):
        m.info


def test_generate_missing_message():
    m = MessagePacket()
    m.source = "XX1XX-11"
    m.destination = "APRS"
    m.path = "TCPIP*,qAR,T2TEST"
    m.addressee = "YY1YY-12"

    with pytest.raises(GenerateError):
        m.info
