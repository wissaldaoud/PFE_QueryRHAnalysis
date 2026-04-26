"""Script simple pour enrichir le dataset automatiquement"""

from ml.enrich_dataset import DatasetEnricher

print("Démarrage de l'enrichissement...")

# Créer l'enrichisseur
enricher = DatasetEnricher()

# Charger les données
enricher.load_data()

# Générer 2 variations par ligne (3x plus de données)
enricher.generate_synthetic_variations(n_variations=2)

# Remplacer l'original avec backup
enricher.replace_original(backup=True)

print("\n✅ ENRICHISSEMENT TERMINÉ!")
print("Le dataset contient maintenant 3x plus de données.")
