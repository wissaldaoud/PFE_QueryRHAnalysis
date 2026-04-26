"""
Entraînement XGBoost OPTIMISÉ - Turnover Qlik
Version soutenance (corrigée + équilibrée)
"""

import pandas as pd
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from xgboost import XGBClassifier

print("="*80)
print("🚀 TRAINING OPTIMISÉ TURNOVER")
print("="*80)

# 1. LOAD DATA
df = pd.read_csv("data/employes_qlik_historique.csv")

print(f"✅ {len(df)} employés")
print(f"📊 Turnover : {df['est_parti'].mean()*100:.1f}%")

# 2. FEATURE ENGINEERING (🔥 IMPORTANT)

df['is_cdi'] = df['type_contrat'].str.upper().str.contains('CDI').astype(int)

df['taux_absenteisme'] = df['nb_absences'] / (df['anciennete_annees']*12).clip(lower=1)

# 🔥 nouvelles features
df['is_junior'] = (df['anciennete_annees'] < 2).astype(int)
df['is_senior'] = (df['anciennete_annees'] > 10).astype(int)
df['absences_high'] = (df['nb_absences'] > 8).astype(int)

features = [
    'age', 'anciennete_annees', 'sexe_code', 'is_cdi',
    'nb_absences', 'total_jours_absence', 'taux_absenteisme',
    'is_junior', 'is_senior', 'absences_high'
]

X = df[features].fillna(0)
y = df['est_parti']

# 3. SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 🔥 gestion déséquilibre
scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()
print(f"⚖️ scale_pos_weight = {scale_pos_weight:.2f}")

# 4. MODEL (🔥 amélioré)
model = XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    scale_pos_weight=scale_pos_weight,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    eval_metric='logloss'
)

print("\n🚀 Training...")
model.fit(X_train, y_train)

# 5. EVALUATION
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print("\n📊 RESULTATS :")
print(f"ROC AUC : {roc_auc_score(y_test, y_proba):.3f}")
print(classification_report(y_test, y_pred, zero_division=0))

# 🔥 check recall (important soutenance)
recall_parti = classification_report(y_test, y_pred, output_dict=True)['1']['recall']
print(f"\n🎯 Recall (détection des départs) : {recall_parti:.2f}")

# 6. SAVE MODEL (🔥 FIX COMPATIBLE AVEC TON SERVICE)

bundle = {
    "model": model,
    "feature_names": features,
    "model_version": "XGBoost_Qlik_v2",
    "threshold": 0.25   # 🔥 ajusté
}

Path("app/ml/models").mkdir(parents=True, exist_ok=True)

model_path = Path("app/ml/models/turnover_model_real.pkl")
joblib.dump(bundle, model_path)

print(f"\n💾 Modèle sauvegardé : {model_path}")
print("\n🎉 MODEL OPTIMISÉ PRÊT !")