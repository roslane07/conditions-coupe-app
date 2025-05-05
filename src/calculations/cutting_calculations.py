"""
Module for cutting condition calculations.
Contains all mathematical formulas and calculations related to cutting operations.
"""

import math
from typing import Tuple, Optional
import streamlit as st
from calculations.cutting_calculations import rotation_speed, coefficient_kc, power_pc, torque_mc, length_la

def rotation_speed(Vc: float, D: float) -> float:
    """
    Calculate rotation speed (n) in RPM from cutting speed (Vc) and diameter (D).
    
    Args:
        Vc (float): Cutting speed in m/min
        D (float): Tool diameter in mm
        
    Returns:
        float: Rotation speed in RPM
    """
    if D <= 0:
        raise ValueError("Tool diameter must be positive")
    return (1000 * Vc) / (math.pi * D)

def hex_co(fn: float, kr: float) -> float:
    """
    Calculate hex coordinate from feed per tooth and cutting edge angle.
    
    Args:
        fn (float): Feed per tooth in mm
        kr (float): Cutting edge angle in degrees
        
    Returns:
        float: Hex coordinate
    """
    return fn * math.sin(math.radians(kr))

def length_la(ap: float, kr: float) -> float:
    """
    Calculate length of engagement from depth of cut and cutting edge angle.
    
    Args:
        ap (float): Depth of cut in mm
        kr (float): Cutting edge angle in degrees
        
    Returns:
        float: Length of engagement in mm
    """
    if kr == 0:
        return float("inf")
    return ap / math.sin(math.radians(kr))

def coefficient_kc(kc1: float, hexv: float, m0: float, Y0: float) -> float:
    """
    Calculate specific cutting force coefficient.
    
    Args:
        kc1 (float): Specific cutting force for 1mm² chip area
        hexv (float): Chip thickness (user-provided or calculated)
        m0 (float): Material constant
        Y0 (float): Yield strength in MPa
        
    Returns:
        float: Specific cutting force coefficient
    """
    if hexv == 0:
        raise ValueError("Invalid input parameters: hex coordinate cannot be zero")
    return kc1 * (1/hexv**m0) * (1 - Y0/100)

def power_pc(F: float, Vc: float) -> float:
    """
    Calculate cutting power from cutting force and cutting speed.
    
    Args:
        F (float): Cutting force in N
        Vc (float): Cutting speed in m/min
        
    Returns:
        float: Cutting power in kW
    """
    return F * Vc / 60000

def torque_mc(Pc: float, n: float) -> float:
    """
    Calculate cutting torque from power and rotation speed.
    
    Args:
        Pc (float): Cutting power in kW
        n (float): Rotation speed in RPM
        
    Returns:
        float: Cutting torque in Nm
    """
    if n == 0:
        raise ValueError("Rotation speed cannot be zero")
    return (300000 * Pc )/ (n*3.14)

def effort_axial_percage(kc1: float, fn: float, D: float) -> float:
    """
    Calculate axial force for drilling.
    
    Args:
        kc1 (float): Specific cutting force for 1mm² chip area
        fn (float): Feed per tooth in mm
        D (float): Tool diameter in mm
        
    Returns:
        float: Axial force in N
    """
    return kc1 * fn * D

def get_local_capacity(n: float, machine_caps: list, max_power: float, max_torque: float) -> Tuple[float, float]:
    """
    Get machine capacity (power and torque) for a given rotation speed.
    
    Args:
        n (float): Rotation speed in RPM
        machine_caps (list): List of machine capacity records
        max_power (float): Maximum power in kW
        max_torque (float): Maximum torque in Nm
        
    Returns:
        Tuple[float, float]: (power, torque) for the given rotation speed
    """
    if not machine_caps:
        return max_power, max_torque
        
    caps = sorted(machine_caps, key=lambda rec: rec["n"])
    ns = [rec["n"] for rec in caps]
    
    # Return max values if n is outside the range
    if n <= ns[0] or n >= ns[-1]:
        return max_power, max_torque
        
    # Find the interval and interpolate
    for i in range(len(ns)-1):
        n1, n2 = ns[i], ns[i+1]
        if n1 <= n <= n2:
            p1, p2 = caps[i]["power"], caps[i+1]["power"]
            t1, t2 = caps[i]["torque"], caps[i+1]["torque"]
            α = (n - n1) / (n2 - n1)
            power = p1 + α * (p2 - p1)
            torque = t1 + α * (t2 - t1)
            return power, torque
            
    return max_power, max_torque 

st.set_page_config(page_title="Calcul conditions de coupe - Alésage", layout="wide")
st.title("Calcul automatique des conditions de coupe — Alésage")

# Paramètres recommandés (à charger depuis le JSON si besoin)
hex_min, hex_max, hex_rec = 0.12, 0.4, 0.25
ap_min, ap_max, ap_rec = 0.5, 4.0, 1.25
fn_min, fn_max, fn_rec = 0.12, 0.4, 0.25
vc_min, vc_max, vc_rec = 55, 560, 445
d_default = 50.0
kr = 95.0
kc1 = 400
m0 = 0.25
Y0 = 6

# Bloc unique de saisie
col1, col2, col3 = st.columns(3)
with col1:
    D = st.number_input("Diamètre D (mm)", min_value=0.1, value=d_default, step=0.1, key="d_alesage")
    fn = st.number_input("Avance fn (mm/tr)", min_value=fn_min, max_value=fn_max, value=fn_rec, key="fn_alesage")
with col2:
    Vc = st.number_input("Vc (m/min)", min_value=vc_min, max_value=vc_max, value=vc_rec, key="vc_alesage")
    ap = st.number_input("ap (mm)", min_value=ap_min, max_value=ap_max, value=ap_rec, key="ap_alesage")
with col3:
    hexv = st.number_input("hex (mm)", min_value=hex_min, max_value=hex_max, value=hex_rec, key="hex_alesage")
    st.number_input("Angle KAPR (°)", min_value=0.0, max_value=180.0, value=kr, key="kr_alesage", disabled=True)
    st.number_input("m₀ (épaisseur copeau)", value=m0, key="m0_alesage", disabled=True)
    st.number_input("Y₀ (%)", value=Y0, key="y0_alesage", disabled=True)

if st.button("Calculer"):
    n = rotation_speed(Vc, D)
    kc = coefficient_kc(kc1, hexv, m0, Y0)
    Fc = kc * ap * fn
    Pc = power_pc(Fc, Vc)
    Mc = torque_mc(Pc, n)
    La = length_la(ap, kr)

    # Affichage des résultats
    st.subheader("Résultats")
    st.metric("n (tr/min)", f"{n:.1f}")
    st.metric("Kc (N/mm²)", f"{kc:.1f}")
    st.metric("Fc (N)", f"{Fc:.1f}")
    st.metric("Pc (kW)", f"{Pc:.2f}")
    st.metric("Mc (Nm)", f"{Mc:.2f}")
    st.metric("La (mm)", f"{La:.2f}")

    # Diagnostic détaillé
    with st.expander("Voir le diagnostic détaillé"):
        st.write(f"hex = {hexv:.3f} mm (saisi)")
        st.write(f"kc = {kc1} × (1/{hexv:.3f}^{m0}) × (1-{Y0}/100) = {kc:.1f} N/mm²")
        st.write(f"Fc = kc × ap × fn = {kc:.1f} × {ap} × {fn} = {Fc:.1f} N")
        st.write(f"Pc = Fc × Vc / 60000 = {Fc:.1f} × {Vc} / 60000 = {Pc:.2f} kW")
        st.write(f"Mc = (30000 × Pc) / (n × π) = (30000 × {Pc:.2f}) / ({n:.1f} × π) = {Mc:.2f} Nm")
        st.write(f"La = ap / sin(kr) = {ap} / sin({kr}) = {La:.2f} mm") 