# Conditions de Coupe Calculator

Application de calcul automatique des conditions de coupe pour l'usinage.

## Structure du Projet

```
projet_resi/
├── src/
│   ├── calculations/
│   │   └── cutting_calculations.py  # Fonctions de calcul
│   ├── data/
│   │   └── data_loader.py          # Gestion des données
│   ├── ui/
│   │   └── components.py           # Composants d'interface
│   └── app.py                      # Application principale
├── conditions_coupe_sandvik.json   # Données de coupe
├── machine_capacities.json         # Capacités machine
├── launcher.py                     # Script de lancement
├── requirements.txt                # Dépendances
└── README.md                       # Documentation
```

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/roslane07/conditions-coupe-app.git
cd projet_resi
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

1. Lancez l'application avec le script de lancement :
```bash
python launcher.py
```

2. L'application s'ouvrira dans votre navigateur par défaut.

## Fonctionnalités

- Calcul automatique des conditions de coupe
- Visualisation des courbes de capacité machine
- Validation des paramètres de coupe
- Interface utilisateur intuitive
- Gestion des erreurs et des avertissements

## Fichiers de Configuration

- `conditions_coupe_sandvik.json` : Paramètres de coupe pour différents outils
- `machine_capacities.json` : Capacités de la machine (puissance et couple)

## Développement

### Structure du Code

- `src/calculations/cutting_calculations.py` : Contient toutes les formules de calcul
- `src/data/data_loader.py` : Gère le chargement et la validation des données
- `src/ui/components.py` : Composants d'interface utilisateur réutilisables
- `src/app.py` : Application principale

### Ajout de Nouveaux Outils

Pour ajouter un nouvel outil, modifiez le fichier `conditions_coupe_sandvik.json` en ajoutant une nouvelle entrée avec les paramètres suivants :
```json
{
    "nom_de_l_outil": {
        "Vc": 100,    // Vitesse de coupe (m/min)
        "fn": 0.1,    // Avance par dent (mm)
        "ap": 2,      // Profondeur de passe (mm)
        "ae": 20,     // Largeur de coupe (mm)
        "kc1": 2000,  // Force spécifique (N/mm²)
        "m0": 0.2,    // Coefficient matériau
        "Y0": 0.3,    // Limite élastique (MPa)
        "kr": 90,     // Angle de coupe (°)
        "D": 10       // Diamètre outil (mm)
    }
}
```



