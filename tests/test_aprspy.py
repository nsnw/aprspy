import pytest

from aprspy import APRS, GenericPacket
from aprspy.utils import APRSUtils
from aprspy.exceptions import ParseError
from aprspy.components import Station, Path


def test_init_packet():
    packet = GenericPacket()
    assert repr(packet) == "<GenericPacket>"

    packet = GenericPacket(source="XX1XX", destination="APRS", path="TCPIP*,qAR,T2TEST",
                        data_type_id=">", info="This is a test status message")

    assert repr(packet) == "<GenericPacket: XX1XX>"
    assert packet.source == "XX1XX"
    assert packet.destination == "APRS"
    assert packet.data_type_id == ">"
    assert packet.info == "This is a test status message"


def test_packet_properties():
    packet = GenericPacket()
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
    packet = GenericPacket()

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


def test_timestamp():
    timestamp = APRSUtils.decode_timestamp("091234z")


#def test_packet():
#    raw = 'XX1XX>APRS,TCPIP*,qAC,FOURTH:=5030.50N/10020.30W$221/000/A=005Test packet'
#
#    packet = APRS.parse(raw)
#
#    assert packet.raw == raw


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


def test_decode_phg():
    (power, height, gain, directivity) = APRSUtils.decode_phg("5132")

    assert power == 25
    assert height == 20
    assert gain == 3
    assert directivity == 90

    (power, height, gain, directivity) = APRSUtils.decode_phg("5130")

    assert power == 25
    assert height == 20
    assert gain == 3
    assert directivity is None


def test_decode_invalid_phg():
    # PHG values must be numerical
    try:
        APRSUtils.decode_phg("PHG513T")
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False


def test_encode_phg():
    phg = APRSUtils.encode_phg(power=25, height=20, gain=3, directivity=90)
    assert phg == "5132"

    phg = APRSUtils.encode_phg(power=25, height=20, gain=3, directivity=None)
    assert phg == "5130"


def test_decode_dfs():
    (strength, height, gain, directivity) = APRSUtils.decode_dfs("2360")

    assert strength == 2
    assert height == 80
    assert gain == 6
    assert directivity == None

    (strength, height, gain, directivity) = APRSUtils.decode_dfs("2361")

    assert strength == 2
    assert height == 80
    assert gain == 6
    assert directivity == 45


def test_decode_invalid_dfs():
    # DFS values must be numerical
    try:
        APRSUtils.decode_dfs("DFS236Z")
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False


def test_encode_invalid_phg():
    # Invalid power
    try:
        phg = APRSUtils.encode_phg(power=10, height=80, gain=6, directivity=None)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        phg = APRSUtils.encode_phg(power="10", height=80, gain=6, directivity=None)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Invalid height
    try:
        phg = APRSUtils.encode_phg(power=25, height=90, gain=6, directivity=None)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        phg = APRSUtils.encode_phg(power=25, height="90", gain=6, directivity=None)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Invalid gain
    try:
        phg = APRSUtils.encode_phg(power=25, height=80, gain=10, directivity=None)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        phg = APRSUtils.encode_phg(power=25, height=80, gain="10", directivity=None)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Invalid directivity
    try:
        phg = APRSUtils.encode_phg(power=25, height=80, gain=6, directivity=47)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        phg = APRSUtils.encode_phg(power=25, height=80, gain=6, directivity="None")
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False


def test_encode_dfs():
    dfs = APRSUtils.encode_dfs(strength=2, height=80, gain=6, directivity=None)
    assert dfs == "2360"

    dfs = APRSUtils.encode_dfs(strength=2, height=80, gain=6, directivity=45)
    assert dfs == "2361"

def test_encode_invalid_dfs():
    # Invalid strength
    try:
        dfs = APRSUtils.encode_dfs(strength=10, height=80, gain=6, directivity=None)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        dfs = APRSUtils.encode_dfs(strength="2", height=80, gain=6, directivity=None)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Invalid height
    try:
        dfs = APRSUtils.encode_dfs(strength=2, height=90, gain=6, directivity=None)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        dfs = APRSUtils.encode_dfs(strength=2, height="80", gain=6, directivity=None)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Invalid gain
    try:
        dfs = APRSUtils.encode_dfs(strength=2, height=80, gain=10, directivity=None)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        dfs = APRSUtils.encode_dfs(strength=2, height=80, gain="6", directivity=None)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Invalid directivity
    try:
        dfs = APRSUtils.encode_dfs(strength=2, height=80, gain=6, directivity=47)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        dfs = APRSUtils.encode_dfs(strength=2, height=80, gain=6, directivity="None")
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False


def test_decode_nrq():
    # Test with example from APRS 1.01
    n, r, q = APRSUtils.decode_nrq("729")

    assert n == 87.5
    assert r == 4
    assert q == 1

    # Test with 0
    n, r, q = APRSUtils.decode_nrq("029")

    assert n == None
    assert r == None
    assert q == None

    # Test with manual
    n, r, q = APRSUtils.decode_nrq("929")

    assert n == "manual"

    # Test different qualities
    # These don't fit neatly into 2 ** x
    n, r, q = APRSUtils.decode_nrq("722")

    assert q == 120

    n, r, q = APRSUtils.decode_nrq("721")

    assert q == 240

    n, r, q = APRSUtils.decode_nrq("720")

    assert q == None


def test_decode_invalid_nrq():
    try:
        APRSUtils.decode_nrq("S29")
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False
