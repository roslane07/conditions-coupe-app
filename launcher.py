<<<<<<< HEAD
import subprocess
import os
import sys
import importlib.util
from datetime import datetime

def log(msg):
    try:
        with open("log_lancement.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception as e:
        pass  # Ne pas bloquer le programme à cause du log

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "ignore").decode())  # Supprime les emojis non supportés

# ========== En-tête ==========
safe_print("============================================")
safe_print("   LANCEUR AUTOMATIQUE - CONDITIONS DE COUPE")
safe_print("============================================\n")

# ========== Aller dans le dossier du projet ==========
project_path = os.path.join(os.path.expanduser("~"), "Downloads", "projet_resi")
if not os.path.exists(os.path.join(project_path, "app.py")):
    safe_print(" Fichier app.py introuvable dans :")
    safe_print("   " + project_path)
    log("app.py introuvable")
    sys.exit(1)

os.chdir(project_path)

# ========== Vérifier si streamlit est installé ==========
def is_installed(pkg):
    return importlib.util.find_spec(pkg) is not None

if not is_installed("streamlit"):
    safe_print(" Le module 'streamlit' n'est pas installé.")
    safe_print(" Installez-le avec : pip install streamlit --user")
    log("streamlit non installé")
    sys.exit(1)

# ========== Lancer Streamlit ==========
try:
    safe_print(" Lancement de l'application...")
    log("Lancement de l'application Streamlit")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
except Exception as e:
    safe_print(" Erreur lors du lancement :")
    safe_print(str(e))
    log("Erreur lors du lancement : " + str(e))
=======
import subprocess
import os
import sys
import importlib.util
from datetime import datetime

def log(msg):
    try:
        with open("log_lancement.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception as e:
        pass  # Ne pas bloquer le programme à cause du log

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "ignore").decode())  # Supprime les emojis non supportés

# ========== En-tête ==========
safe_print("============================================")
safe_print("   LANCEUR AUTOMATIQUE - CONDITIONS DE COUPE")
safe_print("============================================\n")

# ========== Aller dans le dossier du projet ==========
project_path = os.path.join(os.path.expanduser("~"), "Downloads", "projet_resi")
if not os.path.exists(os.path.join(project_path, "app.py")):
    safe_print(" Fichier app.py introuvable dans :")
    safe_print("   " + project_path)
    log("app.py introuvable")
    sys.exit(1)

os.chdir(project_path)

# ========== Vérifier si streamlit est installé ==========
def is_installed(pkg):
    return importlib.util.find_spec(pkg) is not None

if not is_installed("streamlit"):
    safe_print(" Le module 'streamlit' n'est pas installé.")
    safe_print(" Installez-le avec : pip install streamlit --user")
    log("streamlit non installé")
    sys.exit(1)

# ========== Lancer Streamlit ==========
try:
    safe_print(" Lancement de l'application...")
    log("Lancement de l'application Streamlit")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
except Exception as e:
    safe_print(" Erreur lors du lancement :")
    safe_print(str(e))
    log("Erreur lors du lancement : " + str(e))
>>>>>>> 681319ec4cbccdcfb39712e58a283910aa0ec27e
