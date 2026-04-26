# 🚀 Guide d'utilisation du Notebook d'amélioration

## 📋 Vue d'ensemble

Ce Jupyter Notebook améliore le modèle de prédiction de turnover RH en passant d'un **F1-Score de 37.5%** à plus de **60%** grâce à:
- Équilibrage SMOTE
- Optimisation GridSearchCV
- Comparaison de 3 modèles (XGBoost, Random Forest, LightGBM)
- Threshold optimization
- Explainability SHAP

## 🛠️ Installation

### 1. Installer les dépendances

```powershell
cd backend
.\env\Scripts\Activate.ps1
pip install -r requirements-ml.txt
```

Cela installera:
- XGBoost, Random Forest, LightGBM
- MLflow pour tracking
- SMOTE (imbalanced-learn)
- SHAP pour explainability
- Jupyter pour exécuter le notebook

### 2. Vérifier l'installation

```powershell
jupyter --version
python -c "import xgboost, lightgbm, shap, imblearn; print('✅ Toutes les dépendances installées')"
```

## 📂 Prérequis

Le dataset IBM HR Analytics doit être présent:
```
backend/ml/data/WA_Fn-UseC_-HR-Employee-Attrition.csv
```

Si absent, télécharger depuis:
https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset

## 🚀 Utilisation

### Méthode 1: VS Code (recommandé)

1. Ouvrir VS Code
2. Installer l'extension "Jupyter" (ms-toolsai.jupyter)
3. Ouvrir le fichier: `backend/ml/improve_turnover_model.ipynb`
4. Sélectionner le kernel: `backend\env` (l'environnement virtuel)
5. Exécuter toutes les cellules: `Ctrl+Shift+P` → "Run All"

### Méthode 2: Jupyter Lab

```powershell
cd backend/ml
jupyter lab
```

1. Ouvrir `improve_turnover_model.ipynb` dans le navigateur
2. `Kernel` → `Restart & Run All`

### Méthode 3: Jupyter Notebook

```powershell
cd backend/ml
jupyter notebook
```

1. Cliquer sur `improve_turnover_model.ipynb`
2. `Cell` → `Run All`

## 📊 Structure du Notebook

### 17 Cellules organisées:

1. **Titre et objectifs** (Markdown)
2. **Imports** - Toutes les bibliothèques
3. **Chargement dataset** - IBM HR Analytics CSV
4. **Preprocessing** - Encodage, split train/test
5. **Visualisation déséquilibre** - Graphiques avant SMOTE
6. **Application SMOTE** - Équilibrage des classes
7. **XGBoost + GridSearchCV** - Optimisation hyperparamètres
8. **Random Forest** - Entraînement et évaluation
9. **LightGBM** - Entraînement et évaluation
10. **Comparaison 3 modèles** - Tableau et graphiques
11. **Threshold optimization** - Trouver le seuil optimal
12. **Matrice de confusion** - Visualisation des erreurs
13. **Feature importance** - Top 15 features
14. **SHAP explications** - Summary plot + Beeswarm
15. **MLflow tracking** - Logging du meilleur modèle
16. **Sauvegarde modèle** - `turnover_model_v2.pkl`
17. **Résumé V1 vs V2** (Markdown) - Comparaison finale

## ⏱️ Temps d'exécution

- **GridSearchCV (3 modèles)**: ~15-30 minutes selon la machine
- **SHAP calculations**: ~2-5 minutes
- **Total**: 20-35 minutes pour l'exécution complète

💡 **Astuce**: Vous pouvez réduire les grilles de paramètres dans les cellules 7-9 pour accélérer.

## 📈 Résultats attendus

### Métriques V1 (baseline)
```
Accuracy:  86.4%
F1-Score:  37.5% ❌
AUC-ROC:   78.1% ⚠️
Recall:    ~30%  ❌
```

### Métriques V2 (objectifs)
```
F1-Score:  >60% ✅
AUC-ROC:   >85% ✅
Recall:    >60% ✅
```

## 📁 Fichiers générés

Après exécution complète:

```
backend/ml/
├── models/
│   └── turnover_model_v2.pkl    # Meilleur modèle + métadonnées
└── mlruns/                       # Expériences MLflow
    └── turnover_prediction_v2/
```

## 🔍 Visualisations générées

Le notebook produit automatiquement:
- 📊 Graphiques de déséquilibre des classes (avant/après SMOTE)
- 📊 Comparaison des 3 modèles (bar chart)
- 📊 Courbe d'optimisation du seuil
- 🎯 Matrice de confusion
- 📊 Feature importance (top 15)
- 🔍 SHAP summary plot
- 🔍 SHAP beeswarm plot

## 🔄 Intégration du modèle V2

Une fois le notebook exécuté avec succès:

### 1. Copier le modèle V2

```powershell
Copy-Item "backend\ml\models\turnover_model_v2.pkl" "backend\ml\models\turnover_model.pkl" -Force
```

### 2. Mettre à jour ml_service.py

Ouvrir `backend/app/services/ml_service.py` et modifier:

```python
# Charger le package V2 avec seuil optimal
model_data = pickle.load(f)
self.model = model_data['model']
self.optimal_threshold = model_data['optimal_threshold']  # NOUVEAU
self.feature_names = model_data['feature_names']

# Dans predict_turnover(), utiliser le seuil optimal:
proba = self.model.predict_proba(X)[0][1]
prediction = 1 if proba >= self.optimal_threshold else 0  # Au lieu de 0.5
```

### 3. Redémarrer le backend

Le nouveau modèle sera automatiquement chargé.

## 📊 MLflow UI

Pour visualiser les expériences MLflow:

```powershell
cd backend
mlflow ui --port 5000
```

Interface: http://localhost:5000

Vous verrez:
- Toutes les runs de l'expérience `turnover_prediction_v2`
- Comparaison des hyperparamètres
- Métriques (F1, AUC, Recall, etc.)
- Modèles sauvegardés

## 🐛 Troubleshooting

### Erreur: "Dataset not found"

```powershell
# Vérifier le chemin
Test-Path "backend\ml\data\WA_Fn-UseC_-HR-Employee-Attrition.csv"
```

Si `False`, télécharger le dataset depuis Kaggle.

### Erreur: "Module not found"

```powershell
# Réinstaller les dépendances
pip install -r requirements-ml.txt --upgrade
```

### GridSearchCV trop long

Réduire la grille dans les cellules 7-9:

```python
# Grille réduite pour test rapide
param_grid_xgb = {
    'n_estimators': [100, 200],      # Au lieu de [100, 200, 300]
    'max_depth': [4, 6],             # Au lieu de [4, 6, 8]
    'learning_rate': [0.1]           # Au lieu de [0.01, 0.1, 0.2]
}
```

### SHAP trop lent

Réduire la taille de l'échantillon dans la cellule 14:

```python
sample_size = min(50, len(X_test))  # Au lieu de 100
```

## 🎯 Cas d'usage

### Cas 1: Amélioration ponctuelle

Exécuter le notebook une fois pour obtenir un modèle optimisé.

### Cas 2: Re-entraînement périodique

1. Mettre à jour le dataset IBM HR avec de nouvelles données
2. Exécuter le notebook mensuellement
3. Comparer les métriques dans MLflow
4. Déployer si amélioration significative

### Cas 3: Expérimentation

Modifier les hyperparamètres, tester d'autres modèles, essayer différentes techniques de preprocessing.

## 📚 Ressources

- **SMOTE**: https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.SMOTE.html
- **GridSearchCV**: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html
- **SHAP**: https://shap.readthedocs.io/
- **MLflow**: https://mlflow.org/docs/latest/index.html

## 💡 Tips

1. **Exécuter par cellule** pour déboguer en cas d'erreur
2. **Sauvegarder régulièrement** pendant l'exécution
3. **Surveiller la RAM** - GridSearchCV peut être gourmand
4. **Commenter les graphiques** si exécution en mode batch
5. **Versionner vos résultats** avec MLflow

## 🎉 Félicitations!

Une fois toutes les cellules exécutées avec succès, vous aurez:
- ✅ Un modèle optimisé (F1 >60%, AUC >85%)
- ✅ Des explications SHAP pour comprendre le modèle
- ✅ Un threshold optimal pour de meilleures prédictions
- ✅ Un tracking MLflow complet
- ✅ Un modèle prêt pour la production!

---

**Questions?** Consultez le README principal dans `backend/ml/README.md`
