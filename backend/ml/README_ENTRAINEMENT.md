# 🎯 ENTRAÎNEMENT MODÈLE TURNOVER SUR DONNÉES QLIK RÉELLES

## 📋 Vue d'ensemble

Ce guide explique comment entraîner le modèle de prédiction de turnover sur **vos vraies données** issues du DWH PostgreSQL (chargé depuis Oracle via Qlik).

---

## 🚀 PROCESSUS COMPLET (3 étapes)

### **Étape 1 : Extraire les données depuis PostgreSQL**

```bash
cd backend
python scripts/extract_qlik_data.py
```

**Ce script :**
- ✅ Se connecte à PostgreSQL (DWH Qlik)
- ✅ Extrait les employés avec leurs données RH (âge, ancienneté, absences...)
- ✅ Calcule la target `est_parti` (0 ou 1)
- ✅ Sauvegarde dans `ml/data/employes_qlik_historique.csv`

**Résultat attendu :**
```
✅ 1234 employés extraits
   - Partis (1)  : 247
   - Actifs (0)  : 987
   - Taux turnover : 20.0%

💾 Données sauvegardées : backend\ml\data\employes_qlik_historique.csv
```

---

### **Étape 2 : Entraîner le modèle**

```bash
python ml/scripts/train_turnover_real.py
```

**Ce script :**
- ✅ Charge les données extraites
- ✅ Feature engineering (sexe_code, is_cdi, taux_absenteisme...)
- ✅ Split train/test (80/20)
- ✅ Entraîne XGBoost avec scale_pos_weight
- ✅ Évalue (accuracy, ROC AUC, cross-validation)
- ✅ Sauvegarde dans `ml/models/turnover_model_real.pkl`

**Résultat attendu :**
```
🎉 ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS

📊 Métriques du modèle :
   - Accuracy Test  : 82.5%
   - ROC AUC        : 78.3%
   - Features       : 7
   - Échantillons   : 1234 (987 train / 247 test)

✅ Modèle sauvegardé : backend\ml\models\turnover_model_real.pkl
```

---

### **Étape 3 : Tester le modèle**

```bash
python test_turnover_real.py
```

**Ce script :**
- ✅ Charge le modèle entraîné
- ✅ Teste 4 profils types (risque élevé, faible, débutant, senior)
- ✅ Affiche les prédictions + SHAP + recommandations

**Résultat attendu :**
```
🧪 TEST 1/4 : Profil à RISQUE ÉLEVÉ

📊 RÉSULTATS :
   - Risque de départ    : 68.5%
   - Niveau de risque    : ÉLEVÉ
   - Priorité d'action   : CRITIQUE
   - Confiance           : 82%

🔍 Top 5 facteurs SHAP :
   1. 🔴 Ancienneté (années)           :  0.1523  (↑ augmente le risque)
   2. 🔴 Contrat CDI                   : -0.0892  (↓ diminue le risque)
   3. 🔴 Nombre d'absences             :  0.0654  (↑ augmente le risque)
   ...

✅ Le modèle est opérationnel !
```

---

## 📊 FEATURES UTILISÉES

Le modèle utilise **7 features** issues de vos données Qlik :

| Feature | Source | Description |
|---------|--------|-------------|
| `age` | DIM_Employe.age | Âge de l'employé |
| `anciennete_annees` | FAIT_Contrat.duree_contrat_jours / 365 | Ancienneté en années |
| `sexe_code` | DIM_Employe.code_sexe | M=1, F=0 |
| `is_cdi` | FAIT_Contrat.categorie_contrat | CDI=1, autres=0 |
| `nb_absences` | FAIT_Absence (agrégé) | Nombre d'absences 12 derniers mois |
| `total_jours_absence` | FAIT_Absence (agrégé) | Total jours d'absence |
| `taux_absenteisme` | Calculé | nb_absences / (anciennete * 12) |

---

## ⚠️ PROBLÈMES FRÉQUENTS

### **1. Aucun départ détecté (`est_parti` = 0 partout)**

**Cause :** La colonne `flag_employe_actif` contient que des 1.

**Solutions :**
1. Vérifier la table `dim.dim_employe` :
   ```sql
   SELECT flag_employe_actif, COUNT(*) 
   FROM dim.dim_employe 
   GROUP BY flag_employe_actif;
   ```

2. Si tous à 1, utiliser une autre table (ex: `fait.fait_entree_sortie`) :
   - Modifier `extract_qlik_data.py` ligne 67
   - Remplacer par : `CASE WHEN date_sortie IS NOT NULL THEN 1 ELSE 0 END`

3. **Pour tester uniquement :** le script simule automatiquement 20% de départs

---

### **2. Trop peu de départs (< 50)**

**Impact :** Le modèle sera peu fiable (manque de données positives).

**Solutions :**
- Ajuster le filtre `duree_contrat_jours >= 90` (ligne 91) pour inclure plus d'employés
- Étendre la période d'extraction (inclure des anciens employés)
- Attendre d'avoir plus d'historique (6-12 mois supplémentaires)

---

### **3. Erreur de connexion PostgreSQL**

**Vérifier :**
```bash
# Tester la connexion
python -c "from dwh_connection import get_dwh_engine; print(get_dwh_engine())"
```

**Adapter :** Si erreur, modifier `extract_qlik_data.py` lignes 14-17.

---

## 🔧 CONFIGURATION

### **Adapter la connexion PostgreSQL**

Éditez `backend/dwh_connection.py` ou `extract_qlik_data.py` ligne 16 :

```python
def get_dwh_engine():
    return create_engine(
        'postgresql://USER:PASSWORD@HOST:PORT/DATABASE'
    )
```

---

### **Adapter les features**

Si vous avez d'autres colonnes disponibles (salaire, département, évaluations...), ajoutez-les dans `train_turnover_real.py` :

```python
features_to_use = [
    'age',
    'anciennete_annees',
    'sexe_code',
    'is_cdi',
    'nb_absences',
    'total_jours_absence',
    'taux_absenteisme',
    'salaire_mensuel',        # ← Nouvelle feature
    'nb_promotions',          # ← Nouvelle feature
]
```

---

## 📁 FICHIERS GÉNÉRÉS

```
backend/
├── ml/
│   ├── data/
│   │   └── employes_qlik_historique.csv     ← Données extraites
│   ├── models/
│   │   ├── turnover_model_real.pkl          ← Modèle entraîné ⭐
│   │   ├── turnover_features.pkl            ← Liste des features
│   │   └── training_summary_YYYYMMDD.txt    ← Résumé entraînement
│   └── scripts/
│       └── train_turnover_real.py
├── scripts/
│   └── extract_qlik_data.py
└── test_turnover_real.py
```

---

## ✅ UTILISATION EN PRODUCTION

Le modèle `turnover_model_real.pkl` est **automatiquement chargé** par `predictive_scoring.py` (priorité sur l'ancien modèle IBM).

**Aucune modification de code nécessaire** ! 🎉

Le service charge en priorité :
1. `ml/models/turnover_model_real.pkl` ← **VOTRE MODÈLE**
2. `ml/models/turnover_model.pkl` ← Fallback (IBM)

---

## 🎯 PROCHAINES ÉTAPES

1. **Améliorer la qualité** :
   - Ajouter plus de features (salaire, département, promotions...)
   - Collecter plus d'historique (> 1000 employés avec > 200 départs)

2. **Réentraîner régulièrement** :
   - Tous les 3-6 mois pour capturer les nouvelles tendances
   - Automatiser avec un job schedulé

3. **Monitorer les performances** :
   - Suivre le ROC AUC dans le temps
   - Comparer prédictions vs. départs réels

---

## 📞 AIDE

**Problème ?** Vérifiez :
1. Connection PostgreSQL OK ?
2. Tables `dim.dim_employe`, `fait.fait_contrat`, `fait.fait_absence` existent ?
3. Au moins 100 employés avec `duree_contrat_jours >= 90` ?
4. Au moins 30 départs (`est_parti = 1`) ?

**Logs détaillés :** Chaque script affiche son avancement en temps réel.

---

Créé le 2026-04-05
