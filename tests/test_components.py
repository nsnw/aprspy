import pytest # noqa

from aprspy.components import Station, Path, PathHop


def test_station_with_ssid():
    s = Station(callsign="XX1XX", ssid=11)

    assert s.callsign == "XX1XX"
    assert s.ssid == 11
    assert str(s) == "XX1XX-11"
    assert repr(s) == "<Station: XX1XX-11>"

    # Test AX.25 validity
    assert s.is_valid_ax25 is True


def test_station_without_ssid():
    s = Station(callsign="XX1XX")

    assert s.callsign == "XX1XX"
    assert s.ssid is None
    assert str(s) == "XX1XX"
    assert repr(s) == "<Station: XX1XX>"

    # Test AX.25 validity
    assert s.is_valid_ax25 is True


def test_station_with_alpha_ssid():
    s = Station(callsign="XX1XX", ssid="ZZ")

    assert s.callsign == "XX1XX"
    assert s.ssid == "ZZ"
    assert str(s) == "XX1XX-ZZ"
    assert repr(s) == "<Station: XX1XX-ZZ>"

    # Test AX.25 validity
    assert s.is_valid_ax25 is False


def test_station_with_numeric_ssid_15():
    s = Station(callsign="XX1XX", ssid="15")

    assert s.callsign == "XX1XX"
    assert s.ssid == 15
    assert str(s) == "XX1XX-15"
    assert repr(s) == "<Station: XX1XX-15>"

    # Test AX.25 validity
    assert s.is_valid_ax25 is True


def test_station_with_numeric_sid_over_15():
    s = Station(callsign="XX1XX", ssid="16")

    assert s.callsign == "XX1XX"
    assert s.ssid == "16"
    assert str(s) == "XX1XX-16"
    assert repr(s) == "<Station: XX1XX-16>"

    # Test AX.25 validity
    assert s.is_valid_ax25 is False


def test_station_with_alpha_sid_zero():
    s = Station(callsign="XX1XX", ssid="0")

    assert s.callsign == "XX1XX"
    assert s.ssid == None
    assert str(s) == "XX1XX"
    assert repr(s) == "<Station: XX1XX>"

    # Test AX.25 validity
    assert s.is_valid_ax25 is True


def test_station_with_numeric_sid_zero():
    s = Station(callsign="XX1XX", ssid=0)

    assert s.callsign == "XX1XX"
    assert s.ssid == None
    assert str(s) == "XX1XX"
    assert repr(s) == "<Station: XX1XX>"

    # Test AX.25 validity
    assert s.is_valid_ax25 is True


def test_station_with_combined_callsign_and_ssid():
    s = Station(callsign="XX1XX-10")

    assert s.callsign == "XX1XX"
    assert s.ssid == 10
    assert str(s) == "XX1XX-10"
    assert repr(s) == "<Station: XX1XX-10>"


def test_station_with_oversize_callsign():
    s = Station(callsign="XX1XXXX")

    assert s.is_valid_ax25 is False


def test_invalid_station_callsign_type():
    with pytest.raises(TypeError):
        Station(callsign=1)


def test_invalid_station_callsign_value():
    with pytest.raises(ValueError):
        Station(callsign="XX1_X")


def test_invalid_station_ssid_type():
    with pytest.raises(TypeError):
        Station(callsign="XX1XX", ssid=False)


def test_invalid_station_ssid_value():
    with pytest.raises(ValueError):
        Station(callsign="XX1XX", ssid="WTF")


def test_invalid_station_ssid_int_value():
    with pytest.raises(ValueError):
        Station(callsign="XX1XX", ssid=16)


def test_path_hop():
    ph = PathHop(hop="XX1XX-1", used=False)

    assert str(ph.hop) == "XX1XX-1"
    assert ph.used is False
    assert str(ph) == "XX1XX-1"
    assert repr(ph) == "<PathHop: XX1XX-1>"

    ph.used = True

    assert str(ph.hop) == "XX1XX-1"
    assert ph.used is True
    assert str(ph) == "XX1XX-1*"
    assert repr(ph) == "<PathHop: XX1XX-1*>"


def test_invalid_path_hop():
    # Test invalid input for the station
    try:
        PathHop(h=1)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False

    # Test invalid input for the used flag
    try:
        PathHop(h="XX1XX-1", used=1)
        assert False
    except TypeError:
        assert True
    except Exception:
        assert False


def test_path():
    p = Path(path="TCPIP*,qAR,T2TEST")

    assert p.hops[0].hop.callsign == "TCPIP"
    assert p.hops[0].used is True

    #assert p.hops[1].hop.callsign == "qAR"
    #assert p.hops[1].used is False

    assert p.hops[2].hop.callsign == "T2TEST"
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
