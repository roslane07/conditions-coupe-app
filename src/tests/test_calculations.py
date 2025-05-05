"""
Test module for cutting calculations.
"""

import pytest
from calculations.cutting_calculations import (
    rotation_speed,
    hex_co,
    length_la,
    coefficient_kc,
    power_pc,
    torque_mc,
    effort_axial_percage,
    get_local_capacity
)
import math

def test_rotation_speed():
    """Test rotation speed calculation."""
    # Test normal case
    assert round(rotation_speed(100, 10), 2) == 3183.10
    
    # Test edge case
    with pytest.raises(ValueError):
        rotation_speed(100, 0)

def test_hex_co():
    """Test hex coordinate calculation."""
    assert round(hex_co(0.1, 90), 3) == 0.1
    assert round(hex_co(0.1, 45), 3) == 0.071

def test_length_la():
    """Test length of engagement calculation."""
    assert round(length_la(2, 90), 2) == 2.0
    assert round(length_la(2, 45), 2) == 2.83
    assert length_la(2, 0) == float("inf")

def test_coefficient_kc():
    """Test specific cutting force coefficient calculation."""
    assert round(coefficient_kc(2000, 0.1, 90, 0.2, 0.3), 2) == 1994.0
    
    # Test invalid inputs
    with pytest.raises(ValueError):
        coefficient_kc(2000, 0, 90, 0.2, 0.3)
    with pytest.raises(ValueError):
        coefficient_kc(2000, 0.1, 0, 0.2, 0.3)

def test_power_pc():
    """Test cutting power calculation."""
    assert round(power_pc(1000, 100), 2) == 1.67

def test_torque_mc():
    """Test cutting torque calculation."""
    # Test with Pc = 1 kW and n = 1000 RPM
    expected = (30000 * 1) / (1000 * math.pi)
    assert round(torque_mc(1, 1000), 2) == round(expected, 2)
    
    # Test invalid input
    with pytest.raises(ValueError):
        torque_mc(1, 0)

def test_effort_axial_percage():
    """Test axial force calculation."""
    assert effort_axial_percage(2000, 0.1, 10) == 2000

def test_get_local_capacity():
    """Test machine capacity calculation."""
    machine_caps = [
        {"n": 1000, "power": 5, "torque": 50},
        {"n": 2000, "power": 10, "torque": 100}
    ]
    
    # Test interpolation
    power, torque = get_local_capacity(1500, machine_caps, 10, 100)
    assert round(power, 2) == 7.5
    assert round(torque, 2) == 75.0
    
    # Test below range
    power, torque = get_local_capacity(500, machine_caps, 10, 100)
    assert power == 10
    assert torque == 100
    
    # Test above range
    power, torque = get_local_capacity(3000, machine_caps, 10, 100)
    assert power == 10
    assert torque == 100
    
    # Test empty list
    power, torque = get_local_capacity(1500, [], 10, 100)
    assert power == 10
    assert torque == 100 