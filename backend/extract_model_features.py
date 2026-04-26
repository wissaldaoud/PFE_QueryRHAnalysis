"""
Script pour extraire les features du modèle Gradient Boosting
"""
import joblib
import os

model_path = r"C:\Users\wdaoud\Documents\Models\gradient_boosting_turnover.pkl"

print(f"📂 Chargement du modèle: {model_path}")
print()

try:
    model = joblib.load(model_path)
    
    print(f"✅ Modèle chargé: {type(model).__name__}")
    print(f"✅ Nombre de features attendues: {model.n_features_in_}")
    print()
    
    # Essayer de récupérer les noms des features si disponibles
    if hasattr(model, 'feature_names_in_'):
        print("📋 Noms des features:")
        for i, feature in enumerate(model.feature_names_in_, 1):
            print(f"  {i:2d}. {feature}")
        
        # Sauvegarder les features
        features_path = r"C:\Users\wdaoud\Documents\Models\turnover_features.pkl"
        joblib.dump(list(model.feature_names_in_), features_path)
        print()
        print(f"💾 Features sauvegardées dans: {features_path}")
    else:
        print("⚠️ Le modèle n'a pas de noms de features enregistrés")
        print()
        print("Je dois créer les features manuellement.")
        print("Voici les features que le modèle attend (38 colonnes):")
        print()
        print("Veuillez me fournir la liste des features utilisées lors de l'entraînement")
        print("ou le fichier CSV d'entraînement pour que je puisse les extraire.")

except Exception as e:
    print(f"❌ Erreur: {e}")
