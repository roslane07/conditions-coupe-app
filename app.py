# -- coding: utf-8 --
import streamlit as st
import json, os, sys, math
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from streamlit.runtime.scriptrunner import get_script_run_ctx

# =============================================================================
# 1) Configuration générale
# =============================================================================
st.set_page_config(page_title="Conditions de coupe", page_icon="🔧", layout="wide")
st.title("Calcul automatique des conditions de coupe")
st.markdown("""
<style>
  html, body, [class*="css"] { font-family: 'Roboto', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

if get_script_run_ctx() is None:
    st.error("⚠ Lancez l'app avec streamlit run app.py")
    sys.exit(1)

# =============================================================================
# 2) Chargement des données
# =============================================================================
@st.cache_data
def load_conditions(path="conditions_coupe_sandvik.json"):
    if not os.path.exists(path):
        st.error(f"Fichier introuvable : {path}")
        st.stop()
    return json.load(open(path, encoding="utf-8"))

@st.cache_data
def load_machine_caps(path="machine_capacities.json"):
    if not os.path.exists(path):
        st.error(f"Fichier introuvable : {path}")
        st.stop()
    return json.load(open(path, encoding="utf-8"))

def get_local_capacity(n, caps, max_power, max_torque):
    """
    Retourne (power, torque) pour un régime n donné par interpolation
    linéaire entre les deux points machine_caps encadrant n.
    """
    ns = [rec["n"] for rec in caps]
    # fallback global
    if n <= ns[0] or n >= ns[-1]:
        return max_power, max_torque
    for i in range(len(ns)-1):
        n1, n2 = ns[i], ns[i+1]
        if n1 <= n <= n2:
            p1, p2 = caps[i]["power"], caps[i+1]["power"]
            t1, t2 = caps[i]["torque"], caps[i+1]["torque"]
            α = (n - n1) / (n2 - n1)
            power = p1 + α * (p2 - p1)
            torque= t1 + α * (t2 - t1)
            return power, torque
    return max_power, max_torque

conds        = load_conditions()
machine_caps = load_machine_caps()

if "history" not in st.session_state:
    st.session_state.history = []

# Variables d'état pour gérer le calcul et l'enregistrement
if "calculation_done" not in st.session_state:
    st.session_state.calculation_done = False
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# =============================================================================
# 3) Fonctions de calcul
# =============================================================================
def rotation_speed(Vc, D): 
    return (1000 * Vc) / (math.pi * D)

def hex_co(fn, kr): 
    return fn * math.sin(math.radians(kr))

def length_la(ap, kr):
    return ap / math.sin(math.radians(kr)) if kr and kr != 0 else float("inf")

def coefficient_kc(kc1, fn, kr, m0, Y0):
    hex = hex_co(fn, kr)
    if hex == 0:
        raise ValueError("Invalid input parameters: hex coordinate cannot be zero")
    return kc1 * (1/hex**m0) * (1 - Y0/100)

def power_pc(F, Vc): 
    return F * Vc / 60000

def torque_mc(Pc, n): 
    return (30000 * Pc) / (n * math.pi)

def effort_axial_percage(kc1, fn, D): 
    return kc1 * fn * D

# =============================================================================
# 4) Barre latérale
# =============================================================================
st.sidebar.header("⚙ Paramètres machine global")
max_power  = st.sidebar.number_input("Puissance max (kW)", value=10.5, step=0.1)
max_torque = st.sidebar.number_input("Couple max (Nm)" , value=95.0, step=1.0)

plaquette_key = st.sidebar.selectbox("Choisir une plaquette", list(conds.keys()))

img_name = plaquette_key.replace(" ", "_") + ".png"
img_path = os.path.join("images", img_name)
if os.path.exists(img_path):
    st.sidebar.image(img_path, caption=plaquette_key, use_container_width=True)

p = conds[plaquette_key]

# =============================================================================
# 5) Affichage des recommandations
# =============================================================================
def color_span(txt, col):
    return f"<span style='color:{col}; font-weight:bold'>{txt}</span>"

st.subheader(f"Recommandations — {plaquette_key}")
md = [
    f"- *Opération* : {p['operation']}",
    f"- *Matériau*  : {p['material']}",
    "- *Avance fn* : "
      f"{color_span(str(p['avance_f_mmtr']), '#4CAF50')} "
      f"(recommandé : {color_span(p['avance_f_rec'], '#2196F3')})",
    "- *Vc* : "
      f"{color_span(str(p['vitesse_coupe_Vc_mmin']), '#4CAF50')} "
      f"(recommandé : {color_span(p['vitesse_coupe_rec'], '#2196F3')})"
]
if plaquette_key == "N123G2-0300-0001-CF 1125":
    md.append(
      "- *Largeur plaquette* : "
      f"{color_span(f"{p['insert_length_mm']} mm", '#FF9800')} "
      f"(utilisée comme ap pour les calculs)"
    )
elif "profondeur_passe_ap_mm" in p:
    md.append(
      "- *ap* : "
      f"{color_span(str(p['profondeur_passe_ap_mm']), '#4CAF50')} "
      f"(recommandé : {color_span(p['profondeur_passe_rec'], '#2196F3')})"
    )
if "hex_mm" in p:
    md.append(
      "- *hex* : "
      f"{color_span(str(p['hex_mm']), '#4CAF50')} "
      f"(recommandé : {color_span(p['hex_rec'], '#2196F3')})"
    )
md.append(
    "- *Y₀* : "
    f"{color_span(str(p['Y0'])+' %', '#9E9E9E')}"
)
st.markdown("\n".join(md), unsafe_allow_html=True)

# =============================================================================
# 6) Saisie des entrées utilisateur
# =============================================================================
col1, col2, col3 = st.columns(3)
with col1:
    D  = st.number_input("Diamètre D (mm)", min_value=0.1, value=50.0, step=0.1)
    fn = st.number_input("Avance fn (mm/tr)",
                         min_value=p['avance_f_mmtr'][0],
                         max_value=p['avance_f_mmtr'][1],
                         value=p['avance_f_rec'])
    operation = p['operation'].lower()

with col2:
    Vc = st.number_input("Vc (m/min)",
                         min_value=p['vitesse_coupe_Vc_mmin'][0],
                         max_value=p['vitesse_coupe_Vc_mmin'][1],
                         value=p['vitesse_coupe_rec'])
    if plaquette_key == "N123G2-0300-0001-CF 1125":
        st.info("ℹ Pour cette plaquette de gorge, la largeur de la plaquette (3.0 mm) est utilisée comme ap pour les calculs.")
        ap = p.get('insert_length_mm', 0.0)
    elif "profondeur_passe_ap_mm" in p:
        ap = st.number_input("ap (mm)",
                             min_value=p['profondeur_passe_ap_mm'][0],
                             max_value=p['profondeur_passe_ap_mm'][1],
                             value=p['profondeur_passe_rec'])
    else:
        ap = 0.0

with col3:
    if "hex_mm" in p:
        hexv = st.number_input("hex (mm)",
                               min_value=p['hex_mm'][0],
                               max_value=p['hex_mm'][1],
                               value=p['hex_rec'])
    else:
        hexv = 0.0
    kr = st.number_input("Angle KAPR (°)", min_value=0.0, max_value=180.0, value=95.0)
    m0 = st.number_input("m₀ (épaisseur copeau)", value=0.25, disabled=True)
    Y0 = p['Y0']

# =============================================================================
# 7) Calculs
# =============================================================================
n = rotation_speed(Vc, D)
local_max_power, local_max_torque = get_local_capacity(n, machine_caps, max_power, max_torque)

if "perçage" in operation:
    kc1 = 400
    Y0 = 20
    m0 = 0.25  # Peut être rendu paramétrable si besoin
    kr = 90    # Peut être rendu paramétrable si besoin
    hexv = fn * math.sin(math.radians(kr))
    kc = kc1 * ((2 / hexv)**m0) * (1 - Y0/100)
    Fa = kc * fn * D
    Pc = (Fa * Vc) / 240000  # Spécifique au perçage
    Mc = torque_mc(Pc, n)
    hexv_chart = hexv
    La = None
elif "alésage" in operation:
    kc1 = 400
    Y0 = p.get('Y0', 6)
    m0 = 0.25  # Peut être rendu paramétrable si besoin
    # Utiliser les variables déjà saisies dans la section 6
    kc = kc1 * (1 / hexv**m0) * (1 - Y0/100)
    Fc = kc * ap * fn
    n = rotation_speed(Vc, D)
    Pc = power_pc(Fc, Vc)
    Mc = torque_mc(Pc, n)
    La = length_la(ap, 90)  # kr=90° par défaut pour l'alésage
    Fa = None
else:
    hexv = hex_co(fn, kr)
    if plaquette_key == "N123G2-0300-0001-CF 1125":
        ap = p.get('insert_length_mm', 0.0)
        st.info("ℹ Pour cette plaquette de gorge, la largeur de la plaquette (3.0 mm) est utilisée comme ap pour les calculs.")
        Y0 = 20
    La   = length_la(ap, kr) if ap>0 else 0.0
    kc   = coefficient_kc(400, fn, kr, m0, Y0)
    Fc   = kc * ap * fn
    Pc   = power_pc(Fc, Vc)
    Mc   = torque_mc(Pc, n)


# =============================================================================
# 8) Calculs (bouton "Calculer")
# =============================================================================
if st.sidebar.button("Calculer"):
    # 1) Calculs de base
    n = rotation_speed(Vc, D)
    local_max_power, local_max_torque = get_local_capacity(n, machine_caps, max_power, max_torque)
    is_perc = "perçage" in operation

    if is_perc:
        kc1 = 400
        Y0 = 20
        m0 = 0.25
        kr = 90
        hexv_chart = fn * math.sin(math.radians(kr))
        kc = kc1 * ((2 / hexv_chart)**m0) * (1 - Y0/100)
        Fa = kc * fn * D
        Pc = (Fa * Vc) / 240000  # Spécifique au perçage
        Mc = torque_mc(Pc, n)
        La = None
    elif "alésage" in operation:
        kc1 = 400
        Y0 = p.get('Y0', 6)
        m0 = 0.25
        if 'hex_mm' in p:
            hexv_chart = st.session_state.get('hexv', p['hex_rec'])
        else:
            hexv_chart = p.get('hex_rec', 0.25)
        kc = kc1 * (1 / hexv_chart**m0) * (1 - Y0/100)
        ap = st.session_state.get('ap', p['profondeur_passe_rec'])
        fn = st.session_state.get('fn', p['avance_f_rec'])
        Fc = kc * ap * fn
        Vc = st.session_state.get('Vc', p['vitesse_coupe_rec'])
        D = st.session_state.get('D', 50.0)
        n = rotation_speed(Vc, D)
        Pc = power_pc(Fc, Vc)
        Mc = torque_mc(Pc, n)
        La = length_la(ap, 90)
        Fa = None
    else:
        if plaquette_key == "N123G2-0300-0001-CF 1125":
            Y0 = 20
        kc = coefficient_kc(400, fn, kr, m0, Y0)
        hexv_chart = hex_co(fn, kr)
        if plaquette_key == "N123G2-0300-0001-CF 1125":
            ap = p.get('insert_length_mm', 0.0)
        La = length_la(ap, kr) if ap>0 else None
        Fc = kc * ap * fn
        Pc = power_pc(Fc, Vc); Mc = torque_mc(Pc, n)
        Fa = None

    # 2) Préparer la liste des métriques à afficher
    metrics = [
        ("n (tr/min)", f"{n:.1f}"),
        ("Kc (N/mm²)" , f"{kc:.1f}")
    ]
    if is_perc:
        metrics.append(("Fa (N)", f"{Fa:.1f}"))
    else:
        metrics.append(("hex (mm)", f"{hexv_chart:.3f}"))
        metrics.append(("La (mm)", f"{La:.2f}" if La is not None else "—", f"{0.7*D:.2f}"))

    metrics.append(("Pc (kW)", f"{Pc:.2f}", f"{local_max_power:.2f}", "inverse"))
    metrics.append(("Mc (Nm)", f"{Mc:.2f}", f"{local_max_torque:.2f}", "inverse"))

    # 3) Afficher dynamiquement
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        if len(m) == 2:
            label, value = m
            col.metric(label, value)
        elif len(m) == 3:
            label, val, ref = m
            col.metric(label, val, delta=ref)
        elif len(m) == 4:
            label, val, ref, delta_color = m
            col.metric(label, val, delta=ref, delta_color=delta_color)

    # 4) Diagnostic résumé
    errs = []
    if Pc > local_max_power:    errs.append(f"⚠ Pc={Pc:.2f} kW > {local_max_power:.2f} kW (interpolée)")
    if Mc > local_max_torque:   errs.append(f"⚠ Mc={Mc:.2f} Nm > {local_max_torque:.2f} Nm (interpolé)")
    if La is not None and La > 0.7*D:
        errs.append(f"⚠ La={La:.2f} mm > 0.7·D={0.7*D:.2f} mm")

    if not errs:
        st.success("✅ Tous les paramètres sont dans les limites locales.")
    else:
        for e in errs:
            st.error(e)

    # 5) Diagnostic détaillé pédagogique
    with st.expander("Voir le diagnostic détaillé"):
        st.markdown("### Interpolation des capacités machine")
        st.markdown(f"- Vitesse de rotation demandée : *n = {n:.1f} tr/min*")
        # Trouver les deux points d'interpolation
        caps = sorted(machine_caps, key=lambda rec: rec["n"])
        ns = [rec["n"] for rec in caps]
        idx = None
        for i in range(len(ns)-1):
            if ns[i] <= n <= ns[i+1]:
                idx = i
                break
        if idx is not None:
            n1, n2 = ns[idx], ns[idx+1]
            p1, p2 = caps[idx]["power"], caps[idx+1]["power"]
            t1, t2 = caps[idx]["torque"], caps[idx+1]["torque"]
            alpha = (n - n1) / (n2 - n1)
            st.markdown(f"- Points utilisés : n₁ = {n1}, n₂ = {n2}")
            st.markdown(f"- Puissance : P₁ = {p1:.2f} kW, P₂ = {p2:.2f} kW")
            st.markdown(f"- Couple : T₁ = {t1:.2f} Nm, T₂ = {t2:.2f} Nm")
            st.markdown(f"- α = (n - n₁) / (n₂ - n₁) = ({n:.1f} - {n1}) / ({n2} - {n1}) = {alpha:.3f}")
            st.markdown(f"- Puissance interpolée = P₁ + α·(P₂-P₁) = {p1:.2f} + {alpha:.3f}·({p2:.2f}-{p1:.2f}) = *{local_max_power:.2f} kW*")
            st.markdown(f"- Couple interpolé = T₁ + α·(T₂-T₁) = {t1:.2f} + {alpha:.3f}·({t2:.2f}-{t1:.2f}) = *{local_max_torque:.2f} Nm*")
        else:
            st.markdown("- n hors plage, valeurs max utilisées.")

        st.markdown("---")
        st.markdown("### Formules et calculs")
        st.markdown(f"- *Vitesse de rotation* : n = (1000 × Vc) / (π × D) = (1000 × {Vc}) / (π × {D}) = *{n:.1f} tr/min*")
        if not is_perc:
            if plaquette_key == "N123G2-0300-0001-CF 1125":
                st.markdown(f"- *Kc* = kc1 × (1/hex)^m0 × (1-Y0/100) = 400 × (1/{hexv_chart:.3f})^{m0} × (1-20/100) = *{kc:.1f} N/mm²*")
                st.markdown(f"- *hex* = fn × sin(kr) = {fn} × sin({kr}) = *{hexv_chart:.3f} mm*")
                st.markdown(f"- *La* = insert_length_mm / sin(kr) = {p.get('insert_length_mm', 0.0)} / sin({kr}) = *{La:.2f} mm*")
                st.markdown(f"- *Fc* = Kc × insert_length_mm × fn = {kc:.1f} × {p.get('insert_length_mm', 0.0)} × {fn} = *{kc*p.get('insert_length_mm', 0.0)*fn:.1f} N*")
            else:
                st.markdown(f"- *Kc* = kc1 × (1/hex)^m0 × (1-Y0/100) = 400 × (1/{hexv_chart:.3f})^{m0} × (1-{Y0}/100) = *{kc:.1f} N/mm²*")
                st.markdown(f"- *hex* = fn × sin(kr) = {fn} × sin({kr}) = *{hexv_chart:.3f} mm*")
                if La is not None:
                    st.markdown(f"- *La* = ap / sin(kr) = {ap} / sin({kr}) = *{La:.2f} mm*")
                    st.markdown(f"- *Fc* = Kc × ap × fn = {kc:.1f} × {ap} × {fn} = *{kc*ap*fn:.1f} N*")
            st.markdown(f"- *Pc* = Fc × Vc / 60000 = {kc*ap*fn:.1f} × {Vc} / 60000 = *{Pc:.2f} kW*")
            st.markdown(f"- *Mc* = (30000 × Pc) / (n × π) = (30000 × {Pc:.2f}) / ({n:.1f} × π) = *{Mc:.2f} kN.m*")
        else:
            st.markdown(f"- *Y₀* = 20 (fixé pour le perçage)")
            st.markdown(f"- *kc* = 400 × ((2/hex)^0.25) × (1-20/100) = 400 × ((2/{hexv_chart:.3f})^0.25) × 0.8 = *{kc:.1f} N/mm²*")
            st.markdown(f"- *hex* = fn × sin(kr) = {fn} × sin({kr}) = *{hexv_chart:.3f} mm*")
            st.markdown(f"- *Fa* = kc × fn × D = {kc:.1f} × {fn} × {D} = *{Fa:.1f} N*")
            st.markdown(f"- *Pc* = Fa × Vc / 240000 = {Fa:.1f} × {Vc} / 240000 = *{Pc:.2f} kW*")
            st.markdown(f"- *Mc* = (30000 × Pc) / (n × π) = (30000 × {Pc:.2f}) / ({n:.1f} × π) = *{Mc:.2f} kN.m*")
        st.markdown("---")
        st.markdown("### Comparaisons et contrôles")
        st.markdown(f"- *Puissance de coupe* : {Pc:.2f} kW {'<=' if Pc<=local_max_power else '>'} {local_max_power:.2f} kW (interpolée)")
        st.markdown(f"- *Couple de coupe* : {Mc:.2f} Nm {'<=' if Mc<=local_max_torque else '>'} {local_max_torque:.2f} Nm (interpolé)")
        if La is not None:
            st.markdown(f"- *Longueur d'engagement* : {La:.2f} mm {'<=' if La<=0.7*D else '>'} {0.7*D:.2f} mm (0.7×D)")

    # 6) Activer l'enregistrement
    st.session_state.calculation_done = True
    st.session_state.last_result = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Plaquette": plaquette_key,
        "Op": p["operation"],
        "Vc": round(Vc, 1),
        "fn": round(fn, 3),
        "D": round(D, 1),
        **({"ap": round(ap, 2), "hex": round(hexv, 3), "La": round(La, 2)} if La is not None else {}),
        "Pc": round(Pc, 2) if Pc is not None else None,
        "Mc": round(Mc, 2) if Mc is not None else None,
        **({"Fa": round(Fa, 2)} if is_perc else {})
    }

# Bouton Enregistrer (activé seulement après calcul)
if st.session_state.calculation_done and st.sidebar.button("Enregistrer"):
    st.session_state.history.append(st.session_state.last_result)
    st.success("✅ Calcul enregistré dans l'historique.")
    st.session_state.calculation_done = False
    st.session_state.last_result = None


# =============================================================================
# 10) Jauges graphiques
# =============================================================================
g1, g2 = st.columns(2)
with g1:
    fig1 = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=Pc, delta={'reference':local_max_power},
        title={'text':"Puissance (kW)"},
        gauge={
            'axis':{'range':[0,local_max_power]},
            'steps':[
                {'range':[0,0.8*local_max_power],'color':'lightgreen'},
                {'range':[0.8*local_max_power,local_max_power],'color':'yellow'}
            ],
            'threshold':{'value':local_max_power,'line':{'color':'red','width':4}}
        }
    ))
    st.plotly_chart(fig1, use_container_width=True)

with g2:
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=Mc, delta={'reference':local_max_torque},
        title={'text':"Couple (Nm)"},
        gauge={
            'axis':{'range':[0,local_max_torque]},
            'steps':[
                {'range':[0,0.8*local_max_torque],'color':'lightblue'},
                {'range':[0.8*local_max_torque,local_max_torque],'color':'orange'}
            ],
            'threshold':{'value':local_max_torque,'line':{'color':'red','width':4}}
        }
    ))
    st.plotly_chart(fig2, use_container_width=True)

# =============================================================================
# 11) Historique & onglets
# =============================================================================
res = {
    "Date":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "Plaquette":plaquette_key,
    "Op": p['operation'],
    "Vc": round(Vc,1), "fn": round(fn,3), "D": round(D,1),
    **({"ap":round(ap,2), "hex":round(hexv,3), "La":round(La,2)} if ap>0 else {}),
    "Pc":round(Pc,2), "Mc":round(Mc,2),
    **({"Fa":round(Fa,2)} if "perçage" in operation else {})
}
if not st.session_state.history or st.session_state.history[-1]!=res:
    st.session_state.history.append(res)

tabs = st.tabs(["Calcul","Historique"])
with tabs[1]:
    df = pd.DataFrame(st.session_state.history)
    if df.empty:
        st.info("Aucun calcul enregistré.")
    else:
        st.dataframe(df, use_container_width=True)
        st.download_button("Exporter CSV", df.to_csv(index=False).encode(), "history.csv")

# =============================================================================
# Footer
# =============================================================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color: grey;'>"
    "Usiné par <b>La 36-154, La 128 et La 132</b> – Arts et Métiers Rabat – Projet RESI 2025"
    "</div>",
    unsafe_allow_html=True
)