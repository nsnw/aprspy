import pytest

from aprspy import APRS
from aprspy.packets.message import MessagePacket
from aprspy.exceptions import ParseError, GenerateError

RAW = r'XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9  :This is a test message{001'


@pytest.fixture
def packet():
    return APRS.parse_packet(RAW)


def test_empty():
    assert repr(MessagePacket()) == "<MessagePacket>"


def test_repr_with_source_only():
    m = MessagePacket()
    m.source = "YY1YY"
    assert repr(m) == "<MessagePacket: YY1YY>"


def test_type(packet):
    assert type(packet) == MessagePacket


def test_repr(packet):
    assert repr(packet) == f"<MessagePacket: {packet.source} -> {packet.addressee}>"


def test_data_type_id(packet):
    assert packet.data_type_id == ":"


def test_source(packet):
    assert str(packet.source) == "XX1XX-1"


def test_destination(packet):
    assert str(packet.destination) == "APRS"


def test_path(packet):
    assert str(packet.path) == "TCPIP*,qAC,TEST"


def test_addressee(packet):
    assert packet.addressee == "YY9YY-9"


def test_message(packet):
    assert packet.message == "This is a test message"


def test_message_id(packet):
    assert packet.message_id == "001"


def test_addressee_none(packet):
    packet.addressee = None
    assert packet.addressee is None


def test_message_none(packet):
    packet.message = None
    assert packet.message is None


def test_message_id_none(packet):
    packet.message_id = None
    assert packet.message_id is None


def test_invalid_message_id():
    with pytest.raises(ParseError):
        APRS.parse_packet('XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9  :This is a test message{000001')


def test_invalid_message_addressee_type():
    m = MessagePacket()
    with pytest.raises(TypeError):
        m.addressee = 123


def test_invalid_message_addressee_value():
    m = MessagePacket()
    with pytest.raises(ValueError):
        m.addressee = "XXX1XXX-11"


def test_invalid_message_type():
    m = MessagePacket()
    with pytest.raises(TypeError):
        m.message = 123


def test_invalid_message_id_type():
    m = MessagePacket()
    with pytest.raises(TypeError):
        m.message_id = 123


def test_invalid_message_id_value():
    m = MessagePacket()
    with pytest.raises(ValueError):
        m.message_id = "123456"


def test_invalid_bulletin_id_type():
    m = MessagePacket()
    with pytest.raises(TypeError):
        m.bulletin_id = "1"


def test_invalid_bulletin_id_value():
    m = MessagePacket()
    with pytest.raises(ValueError):
        m.bulletin_id = 10


def test_invalid_announcement_id_type():
    m = MessagePacket()
    with pytest.raises(TypeError):
        m.announcement_id = 1


def test_invalid_announcement_id_value():
    m = MessagePacket()
    with pytest.raises(ValueError):
        m.announcement_id = "AA"


def test_invalid_group_bulletin_name_type():
    m = MessagePacket()
    with pytest.raises(TypeError):
        m.group_bulletin_name = 123


def test_invalid_group_bulletin_name_value():
    m = MessagePacket()
    with pytest.raises(ValueError):
        m.group_bulletin_name = "ABCDEF"


# --- Bulletin ---

def test_bulletin_packet():
    p = APRS.parse_packet(r'XX1XX-1>APRS,TCPIP*,qAC,TEST::BLN3     :Snow expected in Tampa RSN')
    assert type(p) == MessagePacket
    assert repr(p) == f"<MessagePacket: {p.source} -> Bulletin #{p.bulletin_id}>"
    assert str(p.source) == "XX1XX-1"
    assert p.addressee == "BLN3"
    assert p.bulletin_id == 3
    assert p.message == "Snow expected in Tampa RSN"
    p.bulletin_id = None
    assert p.bulletin_id is None


# --- Announcement ---

def test_announcement_packet():
    p = APRS.parse_packet(r'XX1XX-1>APRS,TCPIP*,qAC,TEST::BLNQ     :Mt St Helen digi will be QRT this weekend')
    assert type(p) == MessagePacket
    assert repr(p) == f"<MessagePacket: {p.source} -> Announcement {p.announcement_id}>"
    assert p.addressee == "BLNQ"
    assert p.bulletin_id is None
    assert p.announcement_id == "Q"
    assert p.message == "Mt St Helen digi will be QRT this weekend"
    p.announcement_id = None
    assert p.announcement_id is None


# --- Group bulletin ---

def test_group_bulletin_packet():
    p = APRS.parse_packet(r'XX1XX-1>APRS,TCPIP*,qAC,TEST::BLN4WX   :Stand by your snowplows')
    assert type(p) == MessagePacket
    assert repr(p) == f"<MessagePacket: {p.source} -> Group Bulletin {p.group_bulletin_name} #{p.bulletin_id}>"
    assert p.addressee == "BLN4WX"
    assert p.bulletin_id == 4
    assert p.group_bulletin_name == "WX"
    assert p.message == "Stand by your snowplows"
    p.bulletin_id = None
    assert p.bulletin_id is None
    p.group_bulletin_name = None
    assert p.group_bulletin_name is None


# --- Error cases ---

def test_invalid_addressee_field_size():
    # Under-padded addressee (8 chars instead of 9) is now accepted leniently
    p = APRS.parse_packet(r'XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9 :This is a test message{001')
    assert p.addressee == 'YY9YY-9'
    assert p.message == 'This is a test message'


def test_message_invalid_message_id():
    with pytest.raises(ParseError):
        APRS.parse_packet(r'XX1XX-1>APRS,TCPIP*,qAC,TEST::YY9YY-9  :This is a test message{123456')


def test_invalid_announcement_id():
    # Non-standard announcement IDs (e.g. BLNALUX used by some regional nets) are now accepted
    p = APRS.parse_packet(r'XX1XX-1>APRS,TCPIP*,qAC,TEST::BLNAA    :This is a test bulletin')
    assert p.announcement_id == 'A'


def test_invalid_bulletin():
    with pytest.raises(ParseError):
        APRS.parse_packet(r'XX1XX-1>APRS,TCPIP*,qAC,TEST::BLN      :This is a test bulletin')


# --- Generation ---

def test_generate_message():
    m = MessagePacket()
    m.addressee = "YY1YY-12"
    m.message = "This is a test message"
    assert m.info == "YY1YY-12 :This is a test message"


def test_generate_message_with_message_id():
    m = MessagePacket()
    m.addressee = "YY1YY-12"
    m.message = "This is a test message"
    m.message_id = "001"
    assert m.info == "YY1YY-12 :This is a test message{001"


def test_generate_bulletin():
    m = MessagePacket()
    m.bulletin_id = 1
    m.message = "This is a test bulletin"
    assert m.info == "BLN1     :This is a test bulletin"


def test_generate_group_bulletin():
    m = MessagePacket()
    m.bulletin_id = 1
    m.group_bulletin_name = "TEST"
    m.message = "This is a test group bulletin"
    assert m.info == "BLN1TEST :This is a test group bulletin"


def test_generate_announcement():
    m = MessagePacket()
    m.announcement_id = "A"
    m.message = "This is a test announcement"
    assert m.info == "BLNA     :This is a test announcement"


def test_generate_invalid_no_addressee():
    m = MessagePacket()
    with pytest.raises(GenerateError):
        m.info


def test_generate_missing_message():
    m = MessagePacket()
    m.addressee = "YY1YY-12"
    with pytest.raises(GenerateError):
        m.info
