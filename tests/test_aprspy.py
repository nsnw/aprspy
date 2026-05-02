import pytest

from aprspy import APRS, GenericPacket, BEACON_ADDRESSES
from aprspy.utils import APRSUtils
from aprspy.exceptions import ParseError
from aprspy.components import Station, Path
from aprspy.packets.position import PositionPacket
from .data import (
    VALID_SOURCES,
    INVALID_SOURCES,
    VALID_DESTINATIONS,
    INVALID_DESTINATIONS,
    VALID_POSITION_PACKETS,
    TEST_PACKET,
    TEST_SOURCE,
    TEST_DESTINATION,
    TEST_PATH,
    TEST_DATA_TYPE_ID,
    TEST_INFO
)


# Test valid source callsigns.
@pytest.mark.parametrize("source", VALID_SOURCES)
def test_validate_source_with_valid_sources(source):
    assert APRS.validate_source(source)


# Test invalid source callsigns.
@pytest.mark.parametrize("source", INVALID_SOURCES)
def test_validate_source_with_invalid_sources(source):
    with pytest.raises(ParseError):
        APRS.validate_source(source)


# Test valid destination callsigns or data.
@pytest.mark.parametrize("destination", VALID_DESTINATIONS)
def test_validate_destination_with_valid_destinations(destination):
    assert APRS.validate_destination(destination)


# Test invalid destination callsigns or data.
@pytest.mark.parametrize("destination", INVALID_SOURCES)
def test_validate_destination_with_invalid_destinations(destination):
    with pytest.raises(ParseError):
        APRS.validate_destination(destination)


# Test parsing the basic details of a packet.
def test_parse_basic_data():
    (source, destination, path, data_type_id, info) = APRS.parse_basic_data(TEST_PACKET)

    assert source == TEST_SOURCE
    assert destination == TEST_DESTINATION
    assert path == TEST_PATH
    assert data_type_id == TEST_DATA_TYPE_ID
    assert info == TEST_INFO


# Test that common beacon destinations are identified as such.
@pytest.mark.parametrize("destination", BEACON_ADDRESSES)
def test_is_beacon_destination_with_common_beacon_destination(destination):
    assert APRS.is_beacon_destination(destination)


# Test that other destinations are not identified as beacons.
def test_is_beacon_destination_with_non_beacon_destination():
    assert not APRS.is_beacon_destination("FAKE")


# Test that position packet data type IDs are correctly identified.
@pytest.mark.parametrize("data_type_id", ["!", "/", "=", "@"])
def test_is_position_data_type_id(data_type_id):
    assert APRS.is_position_data_type_id(data_type_id)


# Test that other data type IDs are not identified as position packets.
def test_is_position_data_type_id_with_non_position_data_type_id():
    assert not APRS.is_position_data_type_id(">")


# Test identifying position packets (of all kinds).
@pytest.mark.parametrize("packet", VALID_POSITION_PACKETS)
def test_is_position_packet_with_valid_position_packet(packet):
    (source, destination, path, data_type_id, info) = APRS.parse_basic_data(packet)

    assert APRS.get_packet_type(
        packet=packet,
        source=source,
        destination=destination,
        path=path,
        data_type_id=data_type_id,
        info=info
    ) is PositionPacket

#
#
# def test_parse():
#     packet = APRS.parse(TEST_PACKET)

#
#
# def test_init_packet():
#     packet = GenericPacket()
#     assert repr(packet) == "<GenericPacket>"
#
#     packet = GenericPacket(source="XX1XX", destination="APRS", path="TCPIP*,qAR,T2TEST",
#                         data_type_id=">", info="This is a test status message")
#
#     assert repr(packet) == "<GenericPacket: XX1XX>"
#     assert packet.source == "XX1XX"
#     assert packet.destination == "APRS"
#     assert packet.data_type_id == ">"
#     assert packet.info == "This is a test status message"
#
#
# def test_packet_properties():
#     packet = GenericPacket()
#     station = Station(callsign="XX1XX-11")
#     dest = Station(callsign="APRS")
#     path = Path(path="TCPIP*,qAR,T2TEST")
#
#     packet.source = station
#     assert packet.source == station
#
#     packet.destination = dest
#     assert packet.destination == dest
#
#     packet.path = path
#     assert packet.path == path
#
#
# def test_invalid_packet_properties():
#     packet = GenericPacket()
#
#     # Source is too long
#     try:
#         packet.source = "XXX1XXX-11"
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
#
#     # Source type is invalid
#     try:
#         packet.source = 11
#         assert False
#     except TypeError:
#         assert True
#     except Exception:
#         assert False
#
#     # Destination is too long
#     try:
#         packet.destination = "XXX1XXX-11"
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
#
#     # Destination type is invalid
#     try:
#         packet.destination = 11
#         assert False
#     except TypeError:
#         assert True
#     except Exception:
#         assert False
#
#     # Path type is invalid
#     try:
#         packet.path = False
#         assert False
#     except TypeError:
#         assert True
#     except Exception:
#         assert False
#
#
# def test_timestamp():
#     timestamp = APRSUtils.decode_timestamp("091234z")
#
#
# #def test_packet():
# #    raw = 'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005Test packet'
# #
# #    packet = APRS.parse(raw)
# #
# #    assert packet.raw == raw
#
#
# def test_invalid_packet():
#     # Missing > after source
#     try:
#         APRS.parse('XX1XXAPRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet')
#         assert False
#     except ParseError:
#         assert True
#     except Exception:
#         assert False
#
#     # Source is too long
#     try:
#         APRS.parse('XXX1XXX-11>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet')
#         assert False
#     except ParseError:
#         assert True
#     except Exception:
#         assert False
#
#     # Destination is too long
#     try:
#         APRS.parse('XX1XX>APRSAPRSAPRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet')
#         assert False
#     except ParseError:
#         assert True
#     except Exception:
#         assert False
#
#     # Destination is invalid
#     try:
#         APRS.parse('XX1XX>aprs,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet')
#         assert False
#     except ParseError:
#         assert True
#     except Exception:
#         assert False
#
#     # Destination is invalid
#     try:
#         APRS.parse('XX1XX>APRS-XX,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005000Test packet')
#         assert False
#     except ParseError:
#         assert True
#     except Exception:
#         assert False
#
#     # Packet is too short
#     try:
#         APRS.parse('XX1XX>APRS,TCPIP*,qAC,FOURTH:=')
#         assert False
#     except ParseError:
#         assert True
#     except Exception:
#         assert False
#
#
# def test_decode_phg():
#     (power, height, gain, directivity) = APRSUtils.decode_phg("5132")
#
#     assert power == 25
#     assert height == 20
#     assert gain == 3
#     assert directivity == 90
#
#     (power, height, gain, directivity) = APRSUtils.decode_phg("5130")
#
#     assert power == 25
#     assert height == 20
#     assert gain == 3
#     assert directivity is None
#
#
# def test_decode_invalid_phg():
#     # PHG values must be numerical
#     try:
#         APRSUtils.decode_phg("PHG513T")
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
#
#
# def test_encode_phg():
#     phg = APRSUtils.encode_phg(power=25, height=20, gain=3, directivity=90)
#     assert phg == "5132"
#
#     phg = APRSUtils.encode_phg(power=25, height=20, gain=3, directivity=None)
#     assert phg == "5130"
#
#
# def test_decode_dfs():
#     (strength, height, gain, directivity) = APRSUtils.decode_dfs("2360")
#
#     assert strength == 2
#     assert height == 80
#     assert gain == 6
#     assert directivity == None
#
#     (strength, height, gain, directivity) = APRSUtils.decode_dfs("2361")
#
#     assert strength == 2
#     assert height == 80
#     assert gain == 6
#     assert directivity == 45
#
#
# def test_decode_invalid_dfs():
#     # DFS values must be numerical
#     try:
#         APRSUtils.decode_dfs("DFS236Z")
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
#
#
# def test_encode_invalid_phg():
#     # Invalid power
#     try:
#         phg = APRSUtils.encode_phg(power=10, height=80, gain=6, directivity=None)
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
#
#     try:
#         phg = APRSUtils.encode_phg(power="10", height=80, gain=6, directivity=None)
#         assert False
#     except TypeError:
#         assert True
#     except Exception:
#         assert False
#
#     # Invalid height
#     try:
#         phg = APRSUtils.encode_phg(power=25, height=90, gain=6, directivity=None)
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
#
#     try:
#         phg = APRSUtils.encode_phg(power=25, height="90", gain=6, directivity=None)
#         assert False
#     except TypeError:
#         assert True
#     except Exception:
#         assert False
#
#     # Invalid gain
#     try:
#         phg = APRSUtils.encode_phg(power=25, height=80, gain=10, directivity=None)
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
#
#     try:
#         phg = APRSUtils.encode_phg(power=25, height=80, gain="10", directivity=None)
#         assert False
#     except TypeError:
#         assert True
#     except Exception:
#         assert False
#
#     # Invalid directivity
#     try:
#         phg = APRSUtils.encode_phg(power=25, height=80, gain=6, directivity=47)
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
#
#     try:
#         phg = APRSUtils.encode_phg(power=25, height=80, gain=6, directivity="None")
#         assert False
#     except TypeError:
#         assert True
#     except Exception:
#         assert False
#
#
# def test_encode_dfs():
#     dfs = APRSUtils.encode_dfs(strength=2, height=80, gain=6, directivity=None)
#     assert dfs == "2360"
#
#     dfs = APRSUtils.encode_dfs(strength=2, height=80, gain=6, directivity=45)
#     assert dfs == "2361"
#
# def test_encode_invalid_dfs():
#     # Invalid strength
#     try:
#         dfs = APRSUtils.encode_dfs(strength=10, height=80, gain=6, directivity=None)
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
#
#     try:
#         dfs = APRSUtils.encode_dfs(strength="2", height=80, gain=6, directivity=None)
#         assert False
#     except TypeError:
#         assert True
#     except Exception:
#         assert False
#
#     # Invalid height
#     try:
#         dfs = APRSUtils.encode_dfs(strength=2, height=90, gain=6, directivity=None)
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
#
#     try:
#         dfs = APRSUtils.encode_dfs(strength=2, height="80", gain=6, directivity=None)
#         assert False
#     except TypeError:
#         assert True
#     except Exception:
#         assert False
#
#     # Invalid gain
#     try:
#         dfs = APRSUtils.encode_dfs(strength=2, height=80, gain=10, directivity=None)
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
#
#     try:
#         dfs = APRSUtils.encode_dfs(strength=2, height=80, gain="6", directivity=None)
#         assert False
#     except TypeError:
#         assert True
#     except Exception:
#         assert False
#
#     # Invalid directivity
#     try:
#         dfs = APRSUtils.encode_dfs(strength=2, height=80, gain=6, directivity=47)
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
#
#     try:
#         dfs = APRSUtils.encode_dfs(strength=2, height=80, gain=6, directivity="None")
#         assert False
#     except TypeError:
#         assert True
#     except Exception:
#         assert False
#
#
# def test_decode_nrq():
#     # Test with example from APRS 1.01
#     n, r, q = APRSUtils.decode_nrq("729")
#
#     assert n == 87.5
#     assert r == 4
#     assert q == 1
#
#     # Test with 0
#     n, r, q = APRSUtils.decode_nrq("029")
#
#     assert n == None
#     assert r == None
#     assert q == None
#
#     # Test with manual
#     n, r, q = APRSUtils.decode_nrq("929")
#
#     assert n == "manual"
#
#     # Test different qualities
#     # These don't fit neatly into 2 ** x
#     n, r, q = APRSUtils.decode_nrq("722")
#
#     assert q == 120
#
#     n, r, q = APRSUtils.decode_nrq("721")
#
#     assert q == 240
#
#     n, r, q = APRSUtils.decode_nrq("720")
#
#     assert q == None
#
#
# def test_decode_invalid_nrq():
#     try:
#         APRSUtils.decode_nrq("S29")
#         assert False
#     except ValueError:
#         assert True
#     except Exception:
#         assert False
