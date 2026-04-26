import joblib

# Charger le label encoder
le = joblib.load(r'C:\Users\wdaoud\Desktop\test\backend\ml\models\cv_label_encoder.pkl')

print('📋 CATÉGORIES DU MODÈLE CV MATCHING:')
print('='*60)

cats = list(le.classes_)
for i, cat in enumerate(cats, 1):
    print(f'{i:2d}. {cat}')

print(f'\n✅ Nombre total de catégories: {len(le.classes_)}')
print(f'\n🔍 "Food" présent? {"OUI" if "Food" in le.classes_ else "NON"}')
