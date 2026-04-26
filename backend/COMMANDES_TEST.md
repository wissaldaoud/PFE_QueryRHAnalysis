# 🚀 COMMANDES POUR TESTER L'INTÉGRATION HR ANALYTICS ML

## ⚡ Démarrage rapide (5 minutes)

### Étape 1 : Installer les dépendances ML

```powershell
# Dans le dossier backend
cd backend

# Activer l'environnement virtuel
.venv\Scripts\Activate.ps1

# Installer les dépendances ML (torch, transformers, sentence-transformers)
pip install torch>=2.0.0 transformers>=4.30.0 sentence-transformers>=2.2.2

# OU réinstaller toutes les dépendances
pip install -r requirements.txt
```

⏱️ **Temps estimé :** 2-3 minutes

---

### Étape 2 : Démarrer le serveur

```powershell
# Dans le dossier backend/backend
cd backend

# Démarrer le serveur FastAPI
python -m uvicorn app.main:app --reload --port 8000
```

**Au premier démarrage :**
- Le modèle Sentence Transformer (~500 MB) sera téléchargé automatiquement
- Cherchez dans les logs : "✅ Service HR Analytics initialisé avec succès"
- Si erreur : Le service continuera de fonctionner sans HR Analytics ML

⏱️ **Premier démarrage :** 3-5 minutes (téléchargement du modèle)  
⏱️ **Démarrages suivants :** 10-20 secondes

---

### Étape 3 : Tester l'intégration

#### Option A : Test automatique (recommandé)

```powershell
# Dans un nouveau terminal, depuis backend/backend
python test_integration.py
```

Ce script teste automatiquement :
- ✅ Health check du service
- ✅ CV Matching avec données fictives
- ✅ Scoring prédictif avec données fictives

#### Option B : Documentation interactive Swagger

1. Ouvrir dans le navigateur : **http://localhost:8000/docs**
2. Chercher la section **HR Analytics Advanced 🎯**
3. Tester les endpoints interactivement

#### Option C : Test manuel avec cURL

```powershell
# Health check
curl http://localhost:8000/api/v1/hr-analytics/health

# CV Matching
curl -X POST http://localhost:8000/api/v1/hr-analytics/cv-matching `
  -H "Content-Type: application/json" `
  -d '{\"cv\": {\"skills\": [\"Python\", \"FastAPI\"], \"experiences\": [\"3 ans Backend\"], \"job_titles\": [\"Developer\"], \"education\": [\"Master\"], \"years_of_experience\": 3.0}, \"job_offer\": {\"required_skills\": [\"Python\", \"FastAPI\"], \"preferred_skills\": [], \"job_title\": \"Backend Developer\", \"description\": \"API development\", \"required_experience_years\": 2.0}}'
```

---

### Étape 4 : Tests approfondis (optionnel)

```powershell
# Test complet avec 4 scénarios détaillés
python test_hr_analytics_full.py
```

Ce script teste :
- ✅ CV Matching avec analyse détaillée
- ✅ Recommandation de formation (5 formations)
- ✅ Scoring prédictif (3 profils d'employés)
- ✅ Analytics workforce (8 employés)

⏱️ **Temps d'exécution :** 1-2 minutes

---

## 📊 Endpoints disponibles

Une fois le serveur démarré, ces endpoints sont disponibles :

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/v1/hr-analytics/health` | GET | Health check du service |
| `/api/v1/hr-analytics/cv-matching` | POST | Comparer CV et offre d'emploi |
| `/api/v1/hr-analytics/cv-matching/batch` | POST | Comparer plusieurs CVs |
| `/api/v1/hr-analytics/training-recommendation` | POST | Recommander des formations |
| `/api/v1/hr-analytics/predictive-scoring` | POST | Calculer scores prédictifs |
| `/api/v1/hr-analytics/predictive-scoring/batch` | POST | Batch scoring multiple employés |
| `/api/v1/hr-analytics/predictive-scoring/high-risk` | POST | Identifier employés à risque |
| `/api/v1/hr-analytics/analytics/workforce` | POST | Analytics globales workforce |

---

## 🔍 Vérification de l'intégration

### Checklist

- [ ] **Serveur démarre sans erreur**
  ```powershell
  python -m uvicorn app.main:app --reload
  ```
  
- [ ] **Message de succès dans les logs**
  ```
  ✅ Service HR Analytics initialisé avec succès
  ```

- [ ] **Health check répond**
  ```powershell
  curl http://localhost:8000/api/v1/hr-analytics/health
  ```
  Réponse attendue :
  ```json
  {
    "cv_matching": true,
    "training_recommendation": true,
    "predictive_scoring": true,
    "service_status": "healthy"
  }
  ```

- [ ] **Documentation Swagger accessible**
  - Ouvrir : http://localhost:8000/docs
  - Section "HR Analytics Advanced 🎯" visible

- [ ] **Tests automatiques passent**
  ```powershell
  python test_integration.py
  ```
  Résultat attendu : `3/3 tests réussis (100%)`

---

## 🐛 Dépannage

### Problème : "HR Analytics service not initialized"

**Cause :** Les dépendances ML ne sont pas installées

**Solution :**
```powershell
pip install torch>=2.0.0 transformers>=4.30.0 sentence-transformers>=2.2.2
```

---

### Problème : "Out of Memory" au démarrage

**Cause :** Le modèle utilise trop de RAM (besoin de ~2 GB)

**Solution 1 :** Fermer d'autres applications

**Solution 2 :** Utiliser un modèle plus léger
```python
# Modifier dans hr_analytics.py
service = HRAnalyticsService(model_name="paraphrase-MiniLM-L6-v2")
```

---

### Problème : Téléchargement du modèle très lent

**Cause :** Connexion internet lente

**Solution :** Télécharger manuellement
```powershell
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"
```

---

### Problème : "ModuleNotFoundError: No module named 'torch'"

**Cause :** PyTorch n'est pas installé

**Solution :**
```powershell
# Windows
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# OU version CPU uniquement
pip install torch
```

---

## 📚 Documentation complète

- **Guide d'intégration** : [INTEGRATION_HR_ANALYTICS.md](INTEGRATION_HR_ANALYTICS.md)
- **Documentation technique** : [HR_ANALYTICS_README.md](HR_ANALYTICS_README.md)
- **Exemples API** : [hr_analytics_api_examples.json](hr_analytics_api_examples.json)
- **Quick Start** : [quick_start_hr_analytics.py](quick_start_hr_analytics.py)

---

## 🎯 Utilisation en production

### Connexion à la base de données RH

```python
# Exemple : Récupérer les employés depuis votre BDD
from app.db.session import get_db
from app.models.employee import Employee

employees = db.query(Employee).all()

# Convertir en EmployeeHistory pour le scoring
histories = [
    EmployeeHistory(
        employee_id=emp.id,
        tenure_months=(datetime.now() - emp.hire_date).days / 30,
        absences_last_year=emp.absences,
        average_performance_score=emp.performance_score,
        # ... autres champs
    )
    for emp in employees
]

# Calculer les scores
scores = service.batch_calculate_scores(histories)
```

### Scheduler pour analyses régulières

```python
# Exemple avec APScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=1)  # Tous les jours à 1h
async def daily_churn_analysis():
    """Analyse quotidienne du risque de churn"""
    high_risk = service.identify_high_risk_employees(all_histories)
    # Envoyer alertes RH si nécessaire
    await send_hr_alerts(high_risk)

scheduler.start()
```

---

## 🚀 Prochaines étapes

1. ✅ **Tester tous les endpoints** dans Swagger UI
2. ✅ **Intégrer avec votre BDD RH** pour données réelles
3. ✅ **Créer des dashboards** de visualisation (Power BI, Tableau)
4. ✅ **Automatiser les analyses** avec des schedulers
5. ✅ **Monitorer avec MLflow** pour tracking des modèles
6. ✅ **Déployer en production** avec Docker

---

**Module développé avec ❤️ par un expert ML**
