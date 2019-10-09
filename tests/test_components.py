import pytest # noqa

from aprspy.components import Station, Path, PathHop


def test_station():
    s = Station(callsign="XX1XX", ssid="11")

    assert s.callsign == "XX1XX"
    assert s.ssid == "11"
    assert str(s) == "XX1XX-11"
    assert repr(s) == "<Station: XX1XX-11>"

    s.ssid = None

    assert s.callsign == "XX1XX"
    assert s.ssid is None
    assert str(s) == "XX1XX"
    assert repr(s) == "<Station: XX1XX>"

    s.ssid = 12

    assert s.callsign == "XX1XX"
    assert s.ssid == "12"
    assert str(s) == "XX1XX-12"
    assert repr(s) == "<Station: XX1XX-12>"

    s = Station(callsign="XX1XX-10")

    assert s.callsign == "XX1XX"
    assert s.ssid == "10"
    assert str(s) == "XX1XX-10"
    assert repr(s) == "<Station: XX1XX-10>"


def test_invalid_station_callsign():
    try:
        Station(callsign=1)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    try:
        Station(callsign="XX1XXXX")
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False


def test_invalid_station_ssid():
    try:
        Station(callsign="XX1XX", ssid=False)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    try:
        Station(callsign="XX1XX", ssid="WTF")
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False

    try:
        Station(callsign="XX1XX", ssid=16)
        assert False
    except ValueError:
        assert True
    except Exception:
        assert False


def test_path_hop():
    ph = PathHop(station="XX1XX-1", used=False)

    assert str(ph.station) == "XX1XX-1"
    assert ph.used is False
    assert str(ph) == "XX1XX-1"
    assert repr(ph) == "<PathHop: XX1XX-1>"

    ph.used = True

    assert str(ph.station) == "XX1XX-1"
    assert ph.used is True
    assert str(ph) == "XX1XX-1*"
    assert repr(ph) == "<PathHop: XX1XX-1*>"


def test_path_hop_with_station():
    s = Station(callsign="XX1XX", ssid=15)
    ph = PathHop(station=s)

    assert ph.station == s
    assert str(ph.station) == "XX1XX-15"
    assert ph.station.callsign == "XX1XX"
    assert ph.station.ssid == "15"


def test_invalid_path_hop():
    # Test invalid input for the station
    try:
        PathHop(station=1)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Test invalid input for the used flag
    try:
        PathHop(station="XX1XX-1", used=1)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False


def test_path():
    p = Path(path="TCPIP*,qAR,T2TEST")

    assert p.hops[0].station.callsign == "TCPIP"
    assert p.hops[0].used is True

    assert p.hops[1].station.callsign == "qAR"
    assert p.hops[1].used is False

    assert p.hops[2].station.callsign == "T2TEST"
    assert p.hops[2].used is False

    assert str(p) == "TCPIP*,qAR,T2TEST"
    assert repr(p) == "<Path: TCPIP*,qAR,T2TEST>"


def test_invalid_path():
    # Test invalid input for the path
    try:
        Path(path=1)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False
