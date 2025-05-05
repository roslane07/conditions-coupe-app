"""
Main application file for the cutting conditions calculator.
"""

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
import sys
import os

from ui.components import UIComponents
from data.data_loader import DataLoader
from calculations.cutting_calculations import (
    rotation_speed_alesage,
    coefficient_kc_alesage,
    force_coupe_alesage,
    power_coupe_alesage,
    couple_coupe_alesage,
    longueur_engagement_alesage,
    get_local_capacity
)

def main():
    """Main application function."""
    # Setup page
    UIComponents.setup_page()
    
    # Check if running in Streamlit
    if get_script_run_ctx() is None:
        UIComponents.error_message("Lancez l'app avec `streamlit run app.py`")
        sys.exit(1)
        
    try:
        # Load data
        conditions = DataLoader.load_json("conditions_coupe_sandvik.json")
        machine_caps = DataLoader.load_json("machine_capacities.json")
        
        # Validate data
        DataLoader.validate_cutting_conditions(conditions)
        DataLoader.validate_machine_capacities(machine_caps)
        
        # Get machine parameters
        machine_params = UIComponents.machine_parameters_sidebar()
        
        # Tool selection
        selected_tool = UIComponents.tool_selection(list(conditions.keys()))
        
        # Get cutting conditions for selected tool
        tool_conditions = conditions[selected_tool]
        
        # Bloc unique de saisie pour l'alésage (toujours en dehors du if)
        D = st.number_input("Diamètre D (mm)", min_value=0.1, value=tool_conditions.get('D', 50.0), step=0.1, key="d_alesage")
        fn = st.number_input("Avance fn (mm/tr)", min_value=tool_conditions['avance_f_mmtr'][0], max_value=tool_conditions['avance_f_mmtr'][1], value=tool_conditions['avance_f_rec'], key="fn_alesage")
        Vc = st.number_input("Vc (m/min)", min_value=tool_conditions['vitesse_coupe_Vc_mmin'][0], max_value=tool_conditions['vitesse_coupe_Vc_mmin'][1], value=tool_conditions['vitesse_coupe_rec'], key="vc_alesage")
        ap = st.number_input("ap (mm)", min_value=tool_conditions['profondeur_passe_ap_mm'][0], max_value=tool_conditions['profondeur_passe_ap_mm'][1], value=tool_conditions['profondeur_passe_rec'], key="ap_alesage_unique")
        hexv = st.number_input("hex (mm)", min_value=tool_conditions['hex_mm'][0], max_value=tool_conditions['hex_mm'][1], value=tool_conditions['hex_rec'], key="hex_alesage")
        kr = st.number_input("Angle KAPR (°)", min_value=0.0, max_value=180.0, value=tool_conditions.get('kr', 95.0), key="kr_alesage", disabled=True)
        m0 = st.number_input("m₀ (épaisseur copeau)", value=tool_conditions.get('m0', 0.25), key="m0_alesage", disabled=True)
        Y0 = st.number_input("Y₀ (%)", value=tool_conditions.get('Y0', 6), key="y0_alesage", disabled=True)
        kc1 = tool_conditions.get('kc1', 400)

        # Debug : affiche toutes les valeurs juste avant le calcul
        st.write(f"DEBUG: D={D}, fn={fn}, Vc={Vc}, ap={ap}, hexv={hexv}, kr={kr}, m0={m0}, Y0={Y0}")
        n = rotation_speed_alesage(Vc, D)
        kc = coefficient_kc_alesage(kc1, hexv, m0, Y0)
        Fc = force_coupe_alesage(kc, ap, fn)
        Pc = power_coupe_alesage(Fc, Vc)
        Mc = couple_coupe_alesage(Pc, n)
        La = longueur_engagement_alesage(ap, kr)
        local_power, local_torque = get_local_capacity(
            n,
            machine_caps,
            machine_params["max_power"],
            machine_params["max_torque"]
        )
        st.subheader("Résultats")
        st.metric("n (tr/min)", f"{n:.1f}")
        st.metric("Kc (N/mm²)", f"{kc:.1f}")
        st.metric("Fc (N)", f"{Fc:.1f}")
        st.metric("Pc (kW)", f"{Pc:.2f}")
        st.metric("Mc (Nm)", f"{Mc:.2f}")
        st.metric("La (mm)", f"{La:.2f}")
        st.subheader("Capacités machine")
        st.metric("Puissance disponible (kW)", f"{local_power:.2f}")
        st.metric("Couple disponible (Nm)", f"{local_torque:.2f}")
        if Pc > local_power:
            st.warning(f"La puissance de coupe ({Pc:.2f} kW) dépasse la capacité machine ({local_power:.2f} kW)")
        if Mc > local_torque:
            st.warning(f"Le couple de coupe ({Mc:.2f} Nm) dépasse la capacité machine ({local_torque:.2f} Nm)")
        with st.expander("Voir le diagnostic détaillé"):
            st.write(f"hex = {hexv:.3f} mm (saisi)")
            st.write(f"kc = {kc1} × (1/{hexv:.3f}^{m0}) × (1-{Y0}/100) = {kc:.1f} N/mm²")
            st.write(f"Fc = kc × ap × fn = {kc:.1f} × {ap} × {fn} = {Fc:.1f} N")
            st.write(f"Pc = Fc × Vc / 60000 = {Fc:.1f} × {Vc} / 60000 = {Pc:.2f} kW")
            st.write(f"Mc = (30000 × Pc) / (n × π) = (30000 × {Pc:.2f}) / ({n:.1f} × π) = {Mc:.2f} Nm")
            st.write(f"La = ap / sin(kr) = {ap} / sin({kr}) = {La:.2f} mm")
    except FileNotFoundError as e:
        UIComponents.error_message(str(e))
    except json.JSONDecodeError as e:
        UIComponents.error_message(str(e))
    except ValueError as e:
        UIComponents.error_message(str(e))
    except Exception as e:
        UIComponents.error_message(f"Une erreur inattendue s'est produite: {str(e)}")

if __name__ == "__main__":
    main() 