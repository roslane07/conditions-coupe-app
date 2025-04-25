<<<<<<< HEAD
import streamlit as st 
import json
import math
import os
import sys
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit.runtime.scriptrunner import get_script_run_ctx
import plotly.express as px
import re

if get_script_run_ctx() is None:
    print("Erreur : utilisez 'python -m streamlit run app.py'")
    sys.exit(1)

@st.cache_data
def load_conditions(path='conditions_coupe_sandvik.json'):
    if not os.path.exists(path):
        st.error(f"Fichier introuvable : {path}")
        st.stop()
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def rotation_speed(Vc, D): return (1000 * Vc) / (math.pi * D)
def hex_co(fn, kr): return fn * math.sin(math.radians(kr))
def length_la(ap, kr): return ap / math.sin(math.radians(kr)) if kr else float('inf')
def coefficient_kc(kc1, fn, kr, m, Y0):
    s = math.sin(math.radians(kr))
    return kc1 * (1 / (fn * s)**m) * (1 - Y0/100)
def power_pc(Fc, Vc): return Fc * Vc / 60000
def torque_mc(Pc, n): return 9.55 * Pc / n
def effort_axial_percage(kc, fn, D): return kc * fn * D
def colored(label, value, unit, warn=False):
    color = "red" if warn else "green"
    return f"<div style='color:{color}; font-weight:bold'>{label} : {value:.2f} {unit}</div>"

st.set_page_config(page_title="Conditions de coupe", layout="wide")
st.title(" Calcul automatique des conditions de coupe")

tabs = st.tabs([" Calcul", " Historique"])
conditions = load_conditions()
if "history" not in st.session_state:
    st.session_state.history = []

with tabs[0]:
    st.sidebar.header(" Paramètres machine")
    max_power = st.sidebar.number_input(" Puissance max (kW)", value=10.5)
    max_torque = st.sidebar.number_input(" Couple max (Nm)", value=95.0)

    # Sélection de la plaquette
    plaquette_key = st.sidebar.selectbox(" Choisir une plaquette", list(conditions.keys()))

    # Affichage de l'image correspondant à la plaquette sélectionnée
    import re
    image_file = re.sub(r'[^a-zA-Z0-9_-]', '_', plaquette_key) + ".png"
    image_path = os.path.join("images", image_file)

    if os.path.exists(image_path):
        st.sidebar.image(image_path, caption=f"Plaquette : {plaquette_key}", use_container_width=True)

    else:
        st.sidebar.info(" Aucune image disponible pour cette plaquette.")


    p = conditions[plaquette_key]

    st.subheader(f" Recommandations — {plaquette_key}")
    st.markdown(f"- **Opération** : `{p['operation']}`\n- **Matériau** : `{p['material']}`\n- **Avance fn** : `{p['avance_f_mmtr']}`\n- **Vc** : `{p['vitesse_coupe_Vc_mmin']}`\n- **ap** : `{p['profondeur_passe_ap_mm']}`")

    col1, col2, col3 = st.columns(3)
    with col1:
        D = st.number_input("Diamètre D (mm)", value=50.0, min_value=0.1)
        fn = st.number_input("Avance fn (mm/tr)", value=sum(p['avance_f_mmtr'])/2)
        operation = p['operation'].lower()
    with col2:
        Vc = st.number_input("Vitesse de coupe Vc (m/min)", value=sum(p['vitesse_coupe_Vc_mmin'])/2)
        ap = st.number_input("Profondeur de passe ap (mm)", value=p['profondeur_passe_ap_mm'][0] if isinstance(p['profondeur_passe_ap_mm'][0], (int, float)) else 1.0)
        kc1 = st.number_input("kc spécifique (N/mm²)", value=1000.0)
    with col3:
        kr = st.number_input("Angle KAPR (°)", value=95.0)
        m = st.number_input("m (épaisseur copeau)", value=0.25)
        Y0 = st.number_input("Y0 (%)", value=0.0)

    n = rotation_speed(Vc, D)
    if operation == "perçage":
        Fa = effort_axial_percage(kc1, fn, D)
        Pc = power_pc(Fa, Vc) if Vc > 0 else 0
        Mc = torque_mc(Pc, n) if n > 0 else 0
    else:
        hex_ = hex_co(fn, kr)
        La = length_la(ap, kr)
        kc = coefficient_kc(kc1, fn, kr, m, Y0)
        Fc = kc * ap * fn
        Pc = power_pc(Fc, Vc)
        Mc = torque_mc(Pc, n)

    st.subheader(" Résultats")
    if operation == "perçage":
        st.markdown(colored("n", n, "tr/min"), unsafe_allow_html=True)
        st.markdown(colored("Fₐ (Effort axial)", Fa, "N"), unsafe_allow_html=True)
        st.markdown(colored("Pₐ (Puissance)", Pc, "kW", Pc > max_power), unsafe_allow_html=True)
        st.markdown(colored("Mₐ (Couple)", Mc, "Nm", Mc > max_torque), unsafe_allow_html=True)
    else:
        st.markdown(colored("n", n, "tr/min"), unsafe_allow_html=True)
        st.markdown(colored("hex", hex_, "mm"), unsafe_allow_html=True)
        st.markdown(colored("La", La, "mm"), unsafe_allow_html=True)
        st.markdown(colored("Pc", Pc, "kW", Pc > max_power), unsafe_allow_html=True)
        st.markdown(colored("Mc", Mc, "Nm", Mc > max_torque), unsafe_allow_html=True)

    warnings = []
    if operation == "perçage":
        if Pc > max_power:
            warnings.append("⚠️ Puissance absorbée trop élevée. Diminuez `Vc` ou `fn`.")
        if Mc > max_torque:
            warnings.append("⚠️ Couple trop élevé. Diminuez `D`, `Vc`, ou `fn`.")
    else:
        if La > 0.7 * D:
            warnings.append("⚠️ La longueur d’arête La dépasse la limite recommandée. Réduisez `ap`.")
        if Pc > max_power:
            warnings.append("⚠️ Puissance absorbée trop élevée. Diminuez `Vc`, `fn`, ou `ap`.")
        if Mc > max_torque:
            warnings.append("⚠️ Couple trop élevé. Diminuez `Vc`, `fn`, ou `ap`.")

    st.subheader(" Diagnostic de validation des entrées")
    if warnings:
        for msg in warnings:
            st.error(msg)
    else:
        st.success("✅ Tous les paramètres sont dans les limites recommandées. Aucun dépassement détecté.")

    colG1, colG2 = st.columns(2)
    with colG1:
        fig_pc = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=Pc,
            delta={'reference': max_power, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            title={'text': "Puissance absorbée (kW)"},
            gauge={
                'axis': {'range': [0, max_power]},
                'bar': {'color': 'orange'},
                'steps': [
                    {'range': [0, max_power * 0.8], 'color': 'lightgreen'},
                    {'range': [max_power * 0.8, max_power], 'color': 'yellow'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': max_power}
            }
        ))
        st.plotly_chart(fig_pc, use_container_width=True)

    with colG2:
        fig_mc = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=Mc,
            delta={'reference': max_torque, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            title={'text': "Couple de coupe (Nm)"},
            gauge={
                'axis': {'range': [0, max_torque]},
                'bar': {'color': 'blue'},
                'steps': [
                    {'range': [0, max_torque * 0.8], 'color': 'lightblue'},
                    {'range': [max_torque * 0.8, max_torque], 'color': 'orange'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': max_torque}
            }
        ))
        st.plotly_chart(fig_mc, use_container_width=True)

    result = {
        "Date": str(datetime.now()),
        "Plaquette": plaquette_key,
        "Operation": p['operation'],
        "Vc (m/min)": Vc,
        "fn (mm/tr)": fn,
        "ap (mm)": ap,
        "D (mm)": D,
        "n (tr/min)": round(n, 2),
        "Pc (kW)": round(Pc, 2),
        "Mc (Nm)": round(Mc, 2)
    }
    if operation == "perçage":
        result["Fa (N)"] = round(Fa, 2)
    else:
        result["hex (mm)"] = round(hex_, 3)
        result["La (mm)"] = round(La, 2)

    if len(st.session_state.history) == 0 or result != st.session_state.history[-1]:
        st.session_state.history.append(result)

    st.download_button(
        "📥 Exporter ce calcul (Excel)",
        pd.DataFrame([result]).to_csv(index=False).encode(),
        file_name="calcul_actuel.csv"
    )

with tabs[1]:
    st.subheader(" Historique des calculs")
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        st.dataframe(df_hist, use_container_width=True)

        operations = df_hist['Operation'].unique().tolist()
        selected_ops = st.multiselect("Filtrer par type d'opération", operations, default=operations)
        df_filtered = df_hist[df_hist['Operation'].isin(selected_ops)]

        df_filtered['Date_f'] = pd.to_datetime(df_filtered['Date']).dt.strftime("%Y-%m-%d %H:%M:%S")

        st.subheader(" Évolution de la puissance et du couple")
        if "Pc (kW)" in df_filtered.columns and "Mc (Nm)" in df_filtered.columns:
            fig_p = px.bar(
                df_filtered,
                x="Date_f",
                y="Pc (kW)",
                title="Évolution de la Puissance (kW)",
                labels={"Pc (kW)": "Puissance (kW)", "Date_f": "Date"},
                animation_frame="Date_f",
                range_y=[0, df_filtered["Pc (kW)"].max() * 1.1]
            )
            st.plotly_chart(fig_p, use_container_width=True)

            fig_m = px.bar(
                df_filtered,
                x="Date_f",
                y="Mc (Nm)",
                title="Évolution du Couple (Nm)",
                labels={"Mc (Nm)": "Couple (Nm)", "Date_f": "Date"},
                animation_frame="Date_f",
                range_y=[0, df_filtered["Mc (Nm)"].max() * 1.1]
            )
            st.plotly_chart(fig_m, use_container_width=True)
        else:
            st.warning("Certaines colonnes nécessaires pour les graphiques ne sont pas présentes.")

        selected_index = st.selectbox(
            "Choisir un calcul à exporter individuellement",
            options=range(len(df_hist)),
            format_func=lambda i: f"{df_hist.iloc[i]['Date']} – {df_hist.iloc[i]['Plaquette']}"
        )
        selected_calc = df_hist.iloc[[selected_index]]

        st.download_button("📤 Exporter ce calcul spécifique", selected_calc.to_csv(index=False).encode(), file_name="calcul_selectionne.csv")
        st.download_button("📦 Exporter tout l'historique", df_hist.to_csv(index=False).encode(), file_name="historique_complet.csv")
    else:
        st.info("Aucun calcul encore enregistré.")



# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color: grey;'>"
    "Usiné par <b>La 36-154, La 128 et La 132, </b> – Arts et Métiers Rabat – Projet RESI 2025"
    "</div>",
    unsafe_allow_html=True
)
=======
import streamlit as st 
import json
import math
import os
import sys
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit.runtime.scriptrunner import get_script_run_ctx
import plotly.express as px
import re

if get_script_run_ctx() is None:
    print("Erreur : utilisez 'python -m streamlit run app.py'")
    sys.exit(1)

@st.cache_data
def load_conditions(path='conditions_coupe_sandvik.json'):
    if not os.path.exists(path):
        st.error(f"Fichier introuvable : {path}")
        st.stop()
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def rotation_speed(Vc, D): return (1000 * Vc) / (math.pi * D)
def hex_co(fn, kr): return fn * math.sin(math.radians(kr))
def length_la(ap, kr): return ap / math.sin(math.radians(kr)) if kr else float('inf')
def coefficient_kc(kc1, fn, kr, m, Y0):
    s = math.sin(math.radians(kr))
    return kc1 * (1 / (fn * s)**m) * (1 - Y0/100)
def power_pc(Fc, Vc): return Fc * Vc / 60000
def torque_mc(Pc, n): return 9.55 * Pc / n
def effort_axial_percage(kc, fn, D): return kc * fn * D
def colored(label, value, unit, warn=False):
    color = "red" if warn else "green"
    return f"<div style='color:{color}; font-weight:bold'>{label} : {value:.2f} {unit}</div>"

st.set_page_config(page_title="Conditions de coupe", layout="wide")
st.title(" Calcul automatique des conditions de coupe")

tabs = st.tabs([" Calcul", " Historique"])
conditions = load_conditions()
if "history" not in st.session_state:
    st.session_state.history = []

with tabs[0]:
    st.sidebar.header(" Paramètres machine")
    max_power = st.sidebar.number_input(" Puissance max (kW)", value=10.5)
    max_torque = st.sidebar.number_input(" Couple max (Nm)", value=95.0)

    # Sélection de la plaquette
    plaquette_key = st.sidebar.selectbox(" Choisir une plaquette", list(conditions.keys()))

    # Affichage de l'image correspondant à la plaquette sélectionnée
    import re
    image_file = re.sub(r'[^a-zA-Z0-9_-]', '_', plaquette_key) + ".png"
    image_path = os.path.join("images", image_file)

    if os.path.exists(image_path):
        st.sidebar.image(image_path, caption=f"Plaquette : {plaquette_key}", use_container_width=True)

    else:
        st.sidebar.info(" Aucune image disponible pour cette plaquette.")


    p = conditions[plaquette_key]

    st.subheader(f" Recommandations — {plaquette_key}")
    st.markdown(f"- **Opération** : `{p['operation']}`\n- **Matériau** : `{p['material']}`\n- **Avance fn** : `{p['avance_f_mmtr']}`\n- **Vc** : `{p['vitesse_coupe_Vc_mmin']}`\n- **ap** : `{p['profondeur_passe_ap_mm']}`")

    col1, col2, col3 = st.columns(3)
    with col1:
        D = st.number_input("Diamètre D (mm)", value=50.0, min_value=0.1)
        fn = st.number_input("Avance fn (mm/tr)", value=sum(p['avance_f_mmtr'])/2)
        operation = p['operation'].lower()
    with col2:
        Vc = st.number_input("Vitesse de coupe Vc (m/min)", value=sum(p['vitesse_coupe_Vc_mmin'])/2)
        ap = st.number_input("Profondeur de passe ap (mm)", value=p['profondeur_passe_ap_mm'][0] if isinstance(p['profondeur_passe_ap_mm'][0], (int, float)) else 1.0)
        kc1 = st.number_input("kc spécifique (N/mm²)", value=1000.0)
    with col3:
        kr = st.number_input("Angle KAPR (°)", value=95.0)
        m = st.number_input("m (épaisseur copeau)", value=0.25)
        Y0 = st.number_input("Y0 (%)", value=0.0)

    n = rotation_speed(Vc, D)
    if operation == "perçage":
        Fa = effort_axial_percage(kc1, fn, D)
        Pc = power_pc(Fa, Vc) if Vc > 0 else 0
        Mc = torque_mc(Pc, n) if n > 0 else 0
    else:
        hex_ = hex_co(fn, kr)
        La = length_la(ap, kr)
        kc = coefficient_kc(kc1, fn, kr, m, Y0)
        Fc = kc * ap * fn
        Pc = power_pc(Fc, Vc)
        Mc = torque_mc(Pc, n)

    st.subheader(" Résultats")
    if operation == "perçage":
        st.markdown(colored("n", n, "tr/min"), unsafe_allow_html=True)
        st.markdown(colored("Fₐ (Effort axial)", Fa, "N"), unsafe_allow_html=True)
        st.markdown(colored("Pₐ (Puissance)", Pc, "kW", Pc > max_power), unsafe_allow_html=True)
        st.markdown(colored("Mₐ (Couple)", Mc, "Nm", Mc > max_torque), unsafe_allow_html=True)
    else:
        st.markdown(colored("n", n, "tr/min"), unsafe_allow_html=True)
        st.markdown(colored("hex", hex_, "mm"), unsafe_allow_html=True)
        st.markdown(colored("La", La, "mm"), unsafe_allow_html=True)
        st.markdown(colored("Pc", Pc, "kW", Pc > max_power), unsafe_allow_html=True)
        st.markdown(colored("Mc", Mc, "Nm", Mc > max_torque), unsafe_allow_html=True)

    warnings = []
    if operation == "perçage":
        if Pc > max_power:
            warnings.append("⚠️ Puissance absorbée trop élevée. Diminuez `Vc` ou `fn`.")
        if Mc > max_torque:
            warnings.append("⚠️ Couple trop élevé. Diminuez `D`, `Vc`, ou `fn`.")
    else:
        if La > 0.7 * D:
            warnings.append("⚠️ La longueur d’arête La dépasse la limite recommandée. Réduisez `ap`.")
        if Pc > max_power:
            warnings.append("⚠️ Puissance absorbée trop élevée. Diminuez `Vc`, `fn`, ou `ap`.")
        if Mc > max_torque:
            warnings.append("⚠️ Couple trop élevé. Diminuez `Vc`, `fn`, ou `ap`.")

    st.subheader(" Diagnostic de validation des entrées")
    if warnings:
        for msg in warnings:
            st.error(msg)
    else:
        st.success("✅ Tous les paramètres sont dans les limites recommandées. Aucun dépassement détecté.")

    colG1, colG2 = st.columns(2)
    with colG1:
        fig_pc = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=Pc,
            delta={'reference': max_power, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            title={'text': "Puissance absorbée (kW)"},
            gauge={
                'axis': {'range': [0, max_power]},
                'bar': {'color': 'orange'},
                'steps': [
                    {'range': [0, max_power * 0.8], 'color': 'lightgreen'},
                    {'range': [max_power * 0.8, max_power], 'color': 'yellow'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': max_power}
            }
        ))
        st.plotly_chart(fig_pc, use_container_width=True)

    with colG2:
        fig_mc = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=Mc,
            delta={'reference': max_torque, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
            title={'text': "Couple de coupe (Nm)"},
            gauge={
                'axis': {'range': [0, max_torque]},
                'bar': {'color': 'blue'},
                'steps': [
                    {'range': [0, max_torque * 0.8], 'color': 'lightblue'},
                    {'range': [max_torque * 0.8, max_torque], 'color': 'orange'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': max_torque}
            }
        ))
        st.plotly_chart(fig_mc, use_container_width=True)

    result = {
        "Date": str(datetime.now()),
        "Plaquette": plaquette_key,
        "Operation": p['operation'],
        "Vc (m/min)": Vc,
        "fn (mm/tr)": fn,
        "ap (mm)": ap,
        "D (mm)": D,
        "n (tr/min)": round(n, 2),
        "Pc (kW)": round(Pc, 2),
        "Mc (Nm)": round(Mc, 2)
    }
    if operation == "perçage":
        result["Fa (N)"] = round(Fa, 2)
    else:
        result["hex (mm)"] = round(hex_, 3)
        result["La (mm)"] = round(La, 2)

    if len(st.session_state.history) == 0 or result != st.session_state.history[-1]:
        st.session_state.history.append(result)

    st.download_button(
        "📥 Exporter ce calcul (Excel)",
        pd.DataFrame([result]).to_csv(index=False).encode(),
        file_name="calcul_actuel.csv"
    )

with tabs[1]:
    st.subheader(" Historique des calculs")
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        st.dataframe(df_hist, use_container_width=True)

        operations = df_hist['Operation'].unique().tolist()
        selected_ops = st.multiselect("Filtrer par type d'opération", operations, default=operations)
        df_filtered = df_hist[df_hist['Operation'].isin(selected_ops)]

        df_filtered['Date_f'] = pd.to_datetime(df_filtered['Date']).dt.strftime("%Y-%m-%d %H:%M:%S")

        st.subheader(" Évolution de la puissance et du couple")
        if "Pc (kW)" in df_filtered.columns and "Mc (Nm)" in df_filtered.columns:
            fig_p = px.bar(
                df_filtered,
                x="Date_f",
                y="Pc (kW)",
                title="Évolution de la Puissance (kW)",
                labels={"Pc (kW)": "Puissance (kW)", "Date_f": "Date"},
                animation_frame="Date_f",
                range_y=[0, df_filtered["Pc (kW)"].max() * 1.1]
            )
            st.plotly_chart(fig_p, use_container_width=True)

            fig_m = px.bar(
                df_filtered,
                x="Date_f",
                y="Mc (Nm)",
                title="Évolution du Couple (Nm)",
                labels={"Mc (Nm)": "Couple (Nm)", "Date_f": "Date"},
                animation_frame="Date_f",
                range_y=[0, df_filtered["Mc (Nm)"].max() * 1.1]
            )
            st.plotly_chart(fig_m, use_container_width=True)
        else:
            st.warning("Certaines colonnes nécessaires pour les graphiques ne sont pas présentes.")

        selected_index = st.selectbox(
            "Choisir un calcul à exporter individuellement",
            options=range(len(df_hist)),
            format_func=lambda i: f"{df_hist.iloc[i]['Date']} – {df_hist.iloc[i]['Plaquette']}"
        )
        selected_calc = df_hist.iloc[[selected_index]]

        st.download_button("📤 Exporter ce calcul spécifique", selected_calc.to_csv(index=False).encode(), file_name="calcul_selectionne.csv")
        st.download_button("📦 Exporter tout l'historique", df_hist.to_csv(index=False).encode(), file_name="historique_complet.csv")
    else:
        st.info("Aucun calcul encore enregistré.")



# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color: grey;'>"
    "Usiné par <b>La 36-154, La 128 et La 132, </b> – Arts et Métiers Rabat – Projet RESI 2025"
    "</div>",
    unsafe_allow_html=True
)
>>>>>>> 681319ec4cbccdcfb39712e58a283910aa0ec27e
