import pytest

from aprspy import APRS
from aprspy.packets.telemetry_definition import (
    TelemetryParameterNamePacket,
    TelemetryUnitLabelPacket,
    TelemetryEquationCoefficientsPacket,
    TelemetryBitSenseProjectNamePacket,
)

RAW_PARM = 'XX1XX>APRS,TCPIP*,qAC,TEST::XX1XX    :PARM.Bat,Temp,Pres,Hum,Lux,D1,D2,D3,D4,D5,D6,D7,D8'
RAW_UNIT = 'XX1XX>APRS,TCPIP*,qAC,TEST::XX1XX    :UNIT.V,C,hPa,pct,lux,on,on,on,on,on,on,on,on'
RAW_EQNS = 'XX1XX>APRS,TCPIP*,qAC,TEST::XX1XX    :EQNS.0,1,0,0,1,0,0,1,0,0,1,0,0,1,0'
RAW_BITS = 'XX1XX>APRS,TCPIP*,qAC,TEST::XX1XX    :BITS.11111111,My Project'
RAW_BITS_NO_TITLE = 'XX1XX>APRS,TCPIP*,qAC,TEST::XX1XX    :BITS.10110101'


@pytest.fixture
def parm():
    return APRS.parse_packet(RAW_PARM)


@pytest.fixture
def unit():
    return APRS.parse_packet(RAW_UNIT)


@pytest.fixture
def eqns():
    return APRS.parse_packet(RAW_EQNS)


@pytest.fixture
def bits():
    return APRS.parse_packet(RAW_BITS)


# --- PARM ---

def test_parm_type(parm):
    assert type(parm) == TelemetryParameterNamePacket


def test_parm_repr(parm):
    assert repr(parm) == f"<TelemetryParameterNamePacket: {parm.source}>"


def test_parm_data_type_id(parm):
    assert parm.data_type_id == ":"


def test_parm_analog_names(parm):
    assert parm.a1 == 'Bat'
    assert parm.a2 == 'Temp'
    assert parm.a3 == 'Pres'
    assert parm.a4 == 'Hum'
    assert parm.a5 == 'Lux'


def test_parm_digital_names(parm):
    assert parm.b1 == 'D1'
    assert parm.b8 == 'D8'


# --- UNIT ---

def test_unit_type(unit):
    assert type(unit) == TelemetryUnitLabelPacket


def test_unit_repr(unit):
    assert repr(unit) == f"<TelemetryUnitLabelPacket: {unit.source}>"


def test_unit_analog_units(unit):
    assert unit.a1 == 'V'
    assert unit.a2 == 'C'
    assert unit.a3 == 'hPa'
    assert unit.a4 == 'pct'
    assert unit.a5 == 'lux'


def test_unit_digital_labels(unit):
    assert unit.b1 == 'on'
    assert unit.b8 == 'on'


# --- EQNS ---

def test_eqns_type(eqns):
    assert type(eqns) == TelemetryEquationCoefficientsPacket


def test_eqns_repr(eqns):
    assert repr(eqns) == f"<TelemetryEquationCoefficientsPacket: {eqns.source}>"


def test_eqns_channel1(eqns):
    assert eqns.a1_1 == '0'
    assert eqns.a1_2 == '1'
    assert eqns.a1_3 == '0'


def test_eqns_channel2(eqns):
    assert eqns.a2_1 == '0'
    assert eqns.a2_2 == '1'
    assert eqns.a2_3 == '0'


def test_eqns_channel5(eqns):
    assert eqns.a5_1 == '0'
    assert eqns.a5_2 == '1'
    assert eqns.a5_3 == '0'


# --- BITS ---

def test_bits_type(bits):
    assert type(bits) == TelemetryBitSenseProjectNamePacket


def test_bits_repr(bits):
    assert repr(bits) == f"<TelemetryBitSenseProjectNamePacket: {bits.source}>"


def test_bits_values(bits):
    assert bits.b1 == '1'
    assert bits.b2 == '1'
    assert bits.b8 == '1'


def test_bits_project_title(bits):
    assert bits.project_title == 'My Project'


def test_bits_no_project_title():
    p = APRS.parse_packet(RAW_BITS_NO_TITLE)
    assert p.b1 == '1'
    assert p.b3 == '1'
    assert p.project_title is None
