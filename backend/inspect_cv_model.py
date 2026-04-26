"""Script pour inspecter le modèle CV matching"""
import pickle
import joblib
import pathlib

# Charger le modèle
model_path = pathlib.Path("ml/models/cv_matching_model.pkl")
print(f"Chargement de {model_path}...")

# Essayer avec joblib d'abord
try:
    model = joblib.load(model_path)
    print("Chargé avec joblib")
except Exception as e:
    print(f"Erreur joblib: {e}")
    # Essayer avec pickle
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print("Chargé avec pickle")

print(f"\nType du modèle: {type(model)}")
print(f"Classe: {model.__class__.__name__ if hasattr(model, '__class__') else 'N/A'}")

# Si c'est un dictionnaire
if isinstance(model, dict):
    print(f"\nClés du modèle: {list(model.keys())}")
    for key, value in model.items():
        print(f"  {key}: {type(value).__name__}")
        
# Si c'est un modèle sklearn
elif hasattr(model, 'predict'):
    print(f"\nMéthodes: {[m for m in dir(model) if not m.startswith('_')]}")
    if hasattr(model, 'feature_names_in_'):
        print(f"Features: {model.feature_names_in_}")

# Charger les autres fichiers
print("\n" + "="*50)
print("Autres fichiers du modèle:")
print("="*50)

# TF-IDF
tfidf_path = pathlib.Path("ml/models/cv_tfidf.pkl")
if tfidf_path.exists():
    try:
        tfidf = joblib.load(tfidf_path)
        print(f"\nTF-IDF: {type(tfidf).__name__}")
        if hasattr(tfidf, 'get_feature_names_out'):
            features = tfidf.get_feature_names_out()
            print(f"  Vocabulaire size: {len(features)}")
            print(f"  Exemples de features: {features[:10].tolist()}")
    except Exception as e:
        print(f"\nErreur TF-IDF: {e}")

# Label encoder
encoder_path = pathlib.Path("ml/models/cv_label_encoder.pkl")
if encoder_path.exists():
    try:
        encoder = joblib.load(encoder_path)
        print(f"\nLabel Encoder: {type(encoder).__name__}")
        if hasattr(encoder, 'classes_'):
            print(f"  Classes: {encoder.classes_}")
    except Exception as e:
        print(f"\nErreur encodeur: {e}")

# Dataset
dataset_path = pathlib.Path("ml/models/cv_dataset.pkl")
if dataset_path.exists():
    try:
        dataset = joblib.load(dataset_path)
        print(f"\nDataset: {type(dataset)}")
        if isinstance(dataset, dict):
            print(f"  Clés: {list(dataset.keys())}")
            for key in list(dataset.keys())[:3]:
                print(f"    {key}: {type(dataset[key])}")
    except Exception as e:
        print(f"\nErreur dataset: {e}")
