# Prédiction de Turnover RH - Guide Complet

## 📋 Vue d'ensemble

Système de prédiction de turnover utilisant XGBoost, MLflow et FastAPI pour identifier les employés à risque de départ.

## 🏗️ Architecture

```
backend/
├── ml/
│   ├── train_turnover.py      # Script d'entraînement
│   ├── mapper.py               # Mapping DWH → IBM HR
│   ├── data/                   # Dataset IBM HR Analytics
│   │   └── WA_Fn-UseC_-HR-Employee-Attrition.csv
│   └── models/                 # Modèles entraînés
│       └── turnover_model.pkl
├── app/
│   ├── services/
│   │   └── ml_service.py       # Service de prédiction
│   └── routes/
│       └── prediction.py       # API endpoints
```

## 🚀 Installation

### 1. Installer les dépendances ML

```bash
cd backend
pip install xgboost mlflow scikit-learn pandas numpy
```

### 2. Télécharger le dataset IBM HR Analytics

Télécharger depuis Kaggle:
https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset

Placer le fichier dans: `backend/ml/data/WA_Fn-UseC_-HR-Employee-Attrition.csv`

### 3. Entraîner le modèle

```bash
cd backend
python ml/train_turnover.py
```

Résultat attendu:
- Modèle sauvegardé: `ml/models/turnover_model.pkl`
- Métriques loggées dans MLflow
- Accuracy, F1-Score, AUC-ROC affichés

### 4. Démarrer MLflow (optionnel)

```bash
mlflow ui --port 5000
```

Interface: http://localhost:5000

## 📊 Utilisation du Mapper

### Test du mapper

```bash
cd backend
python ml/mapper.py
```

### Mapping automatique

Le mapper transforme les données DWH PostgreSQL en features IBM HR:

| DWH PostgreSQL | IBM HR Feature | Transformation |
|----------------|----------------|----------------|
| `age` | `Age` | Direct |
| `anciennete_annees` | `YearsAtCompany` | Direct |
| `nb_absences` | `WorkLifeBalance` | 0→4, 1-3→3, 4-8→2, 9+→1 |
| `total_jours_absence` | `OverTime` | >15→0, ≤15→1 |
| `sexe_encoded` | `Gender` | Direct |

## 🔌 API Endpoints

### 1. Prédiction individuelle

```bash
GET /api/predict/turnover/12345
```

**Réponse:**
```json
{
  "success": true,
  "employe_id": 12345,
  "score": 67.8,
  "niveau": "Élevé",
  "recommandation": "Risque critique! Intervention immédiate recommandée",
  "details": {
    "age": 35,
    "anciennete": 5,
    "absences": 8,
    "department": "Sales"
  }
}
```

### 2. Analyse globale

```bash
GET /api/predict/all?limit=50
```

Retourne les 50 employés les plus à risque, triés par score décroissant.

### 3. Simulation What-If

```bash
POST /api/predict/simulate
Content-Type: application/json

{
  "employe_id": 12345,
  "modifications": {
    "nb_absences": 2,
    "salaire_mensuel": 7000,
    "anciennete_annees": 6
  }
}
```

**Réponse:**
```json
{
  "success": true,
  "employe_id": 12345,
  "avant": {
    "score": 67.8,
    "niveau": "Élevé"
  },
  "apres": {
    "score": 45.2,
    "niveau": "Moyen"
  },
  "delta": 22.6,
  "impact": "Réduction du risque de 22.60%",
  "recommandation": "Modifications bénéfiques"
}
```

### 4. Health Check

```bash
GET /api/predict/health
```

Vérifie que le modèle est chargé et opérationnel.

## 🧠 Modèle XGBoost

### Paramètres

- `n_estimators`: 200
- `max_depth`: 6
- `learning_rate`: 0.1
- `objective`: binary:logistic

### Features utilisées

Le modèle utilise les features du dataset IBM HR Analytics:
- Age
- YearsAtCompany
- WorkLifeBalance
- OverTime
- Gender
- MaritalStatus
- Department
- JobRole
- MonthlyIncome
- DistanceFromHome
- JobSatisfaction
- Et autres...

### Métriques de performance

Après entraînement, vous devriez voir:
- **Accuracy**: ~85-90%
- **F1-Score**: ~0.60-0.70
- **AUC-ROC**: ~0.80-0.85

## 🗄️ Requêtes DWH

Le service ML interroge automatiquement:

```sql
SELECT 
    e.nudoss,
    e.age,
    e.sexe_encoded,
    c.anciennete_annees,
    c.type_contrat,
    c.department,
    a.nb_absences,
    a.total_jours_absence,
    af.poste as job_role
FROM dim.dim_employe e
LEFT JOIN fait.fait_contrat c ON e.nudoss = c.nudoss
LEFT JOIN fait.fait_absence a ON e.nudoss = a.nudoss
LEFT JOIN fait.fait_affectation af ON e.nudoss = af.nudoss
WHERE e.nudoss = :employe_id
  AND e.actif = true
```

## 📈 Dashboard FastAPI

Accéder à la documentation interactive:

```
http://localhost:8000/docs
```

Section: **Prédictions ML 🤖**

## 🔧 Configuration

### Variables d'environnement DWH

```bash
export DWH_HOST=localhost
export DWH_PORT=5432
export DWH_DATABASE=qlik_hr_dwh
export DWH_USER=hranalytics
export DWH_PASSWORD=hranalytics2026
```

### MLflow Tracking URI

Dans `backend/app/core/config.py`:

```python
MLFLOW_TRACKING_URI = "http://localhost:5000"
```

## 🧪 Tests

### Test complet du pipeline

```bash
# 1. Test du mapper
python ml/mapper.py

# 2. Entraînement
python ml/train_turnover.py

# 3. Test API (serveur doit être démarré)
curl http://localhost:8000/api/predict/health
```

## 📝 Niveaux de risque

| Score | Niveau | Action recommandée |
|-------|--------|--------------------|
| 0-30% | Faible | Employé stable. Maintenir conditions actuelles |
| 30-60% | Moyen | Surveiller satisfaction. Envisager entretien individuel |
| 60-100% | Élevé | Intervention urgente: entretien RH, plan de rétention |

## 🎯 Cas d'usage

### 1. Identification proactive

Détecter les employés à risque avant qu'ils ne démissionnent.

### 2. Analyse d'impact

Simuler l'effet d'une augmentation de salaire ou d'un changement de poste.

### 3. Reporting RH

Générer des rapports mensuels sur les risques de turnover par département.

### 4. Dashboard temps réel

Intégrer les scores dans un dashboard de suivi RH.

## ⚠️ Limitations

- Le modèle est entraîné sur des données IBM (USA)
- Nécessite adaptation des thresholds selon votre contexte
- Les données DWH doivent être à jour
- Performances dépendent de la qualité des données

## 🔄 Mise à jour du modèle

Re-entraîner périodiquement avec des données fraîches:

```bash
# Télécharger nouvelles données
# Remplacer le CSV dans ml/data/

# Re-entraîner
python ml/train_turnover.py

# Le modèle sera automatiquement rechargé au prochain appel API
```

## 📞 Support

En cas de problème:
1. Vérifier les logs: logs backend
2. Tester `/api/predict/health`
3. Vérifier connexion DWH
4. Confirmer que le modèle existe: `ml/models/turnover_model.pkl`

## 🎓 Références

- **XGBoost**: https://xgboost.readthedocs.io/
- **MLflow**: https://mlflow.org/
- **IBM HR Analytics Dataset**: https://www.kaggle.com/pavansubhasht/ibm-hr-analytics-attrition-dataset
