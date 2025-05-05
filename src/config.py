"""
Configuration file for the cutting conditions calculator.
Contains constants, settings, and default values.
"""

# File paths
CONDITIONS_FILE = "conditions_coupe_sandvik.json"
MACHINE_CAPACITIES_FILE = "machine_capacities.json"

# Default values
DEFAULT_MAX_POWER = 14.9  # kW
DEFAULT_MAX_TORQUE = 95.0  # Nm

# UI settings
PAGE_CONFIG = {
    "page_title": "Conditions de coupe",
    "page_icon": "🔧",
    "layout": "wide"
}

# Plot settings
PLOT_CONFIG = {
    "power_color": "blue",
    "torque_color": "red",
    "power_title": "Puissance (kW)",
    "torque_title": "Couple (Nm)",
    "rotation_title": "Vitesse de rotation (tr/min)"
}

# Validation settings
VALIDATION_THRESHOLDS = {
    "power_warning": 0.8,  # 80% of max power
    "torque_warning": 0.8,  # 80% of max torque
    "engagement_warning": 0.7  # 70% of tool diameter
}

# Error messages
ERROR_MESSAGES = {
    "file_not_found": "Fichier introuvable : {path}",
    "invalid_json": "JSON invalide dans le fichier {path} : {error}",
    "invalid_data": "Structure de données invalide : {error}",
    "calculation_error": "Erreur lors du calcul : {error}",
    "launch_error": "Erreur lors du lancement : {error}"
}

# Success messages
SUCCESS_MESSAGES = {
    "calculation_complete": "Calcul terminé avec succès",
    "data_loaded": "Données chargées avec succès",
    "parameters_valid": "Paramètres valides"
}

# Warning messages
WARNING_MESSAGES = {
    "power_exceeded": "La puissance de coupe ({value:.2f} kW) dépasse la capacité machine ({max:.2f} kW)",
    "torque_exceeded": "Le couple de coupe ({value:.2f} Nm) dépasse la capacité machine ({max:.2f} Nm)",
    "engagement_exceeded": "La longueur d'engagement ({value:.2f} mm) dépasse 70% du diamètre ({diameter:.2f} mm)"
} 