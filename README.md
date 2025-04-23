# 💡 Conditions de Coupe – Application Streamlit

Cette application permet de **calculer automatiquement les conditions de coupe** (vitesse, couple, puissance, etc.) à partir de plaquettes SANDVIK et des données saisies par l’utilisateur. Elle a été développée dans le cadre du projet RESI à l'École Arts et Métiers – Campus de Rabat.

---

## 🧮 Fonctionnalités

- Sélection de plaquettes issues du catalogue Sandvik
- Calcul dynamique des paramètres :
  - Vitesse de rotation (`n`)
  - Épaisseur de copeau (`hex`)
  - Longueur d’arête engagée (`La`)
  - Puissance (`Pc`)
  - Couple (`Mc`)
- Visualisation via jauges interactives avec Plotly
- Historique des calculs avec export Excel
- Export individuel ou complet des résultats
- Interface fluide via Streamlit

---

## 🛠️ Technologies utilisées

- [Python 3.10+](https://www.python.org)
- [Streamlit](https://streamlit.io)
- [Plotly](https://plotly.com/python/)
- Pandas

---

## 🚀 Lancement local

```bash
git clone https://github.com/<roslane07>/conditions-coupe-app.git
cd conditions-coupe-app
pip install -r requirements.txt
streamlit run app.py
