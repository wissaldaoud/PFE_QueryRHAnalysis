# 🚀 Module HR Analytics Avancé

Module Python complet pour une plateforme RH Analytics avec Machine Learning et NLP.

## 📋 Vue d'ensemble

Ce module offre **3 fonctionnalités principales** pour la gestion des ressources humaines :

### 1. 🎯 CV Matching avec NLP
Compare automatiquement un CV avec une offre d'emploi en utilisant des embeddings sémantiques avancés (Sentence Transformers).

**Fonctionnalités :**
- Score de correspondance global (0-1)
- Scores détaillés : compétences, expérience, intitulé, éducation
- Identification des compétences manquantes
- Recommandations personnalisées
- Support multilingue (français, anglais, etc.)

### 2. 📚 Recommandation de Formation
Recommande les meilleures formations pour un employé en fonction de son profil et de ses objectifs de carrière.

**Fonctionnalités :**
- Analyse du skill gap (compétences manquantes)
- Matching sémantique avec le catalogue de formations
- Score de pertinence par formation
- Priorisation (haute/moyenne/basse)
- Explications détaillées des recommandations

### 3. 🔮 Scoring RH Prédictif
Calcule des scores prédictifs pour anticiper le churn, évaluer la performance et mesurer l'engagement.

**Fonctionnalités :**
- **Score de churn** : probabilité de départ (0-1)
- **Score de performance** : performance prédictive (0-1)
- **Score d'engagement** : niveau d'engagement (0-1)
- Identification des facteurs clés
- Recommandations RH actionnables
- Analytics globales workforce

---

## 🏗️ Architecture

```
backend/
├── app/
│   ├── services/
│   │   ├── cv_matching.py              # Module CV Matching
│   │   ├── training_recommendation.py  # Module Recommandation
│   │   ├── predictive_scoring.py       # Module Scoring Prédictif
│   │   └── hr_analytics.py             # Service principal (orchestrateur)
│   └── api/
│       └── v1/
│           └── endpoints/
│               └── hr_analytics.py      # Routes API FastAPI
├── test_hr_analytics_full.py           # Tests avec données fictives
└── requirements-hr-analytics.txt       # Dépendances
```

---

## 🔧 Installation

### 1. Cloner et installer les dépendances

```bash
cd backend
pip install -r requirements-hr-analytics.txt
```

### 2. Téléchargement automatique du modèle

Au premier lancement, le modèle Sentence Transformer sera téléchargé automatiquement (~500 MB).

```python
from app.services.hr_analytics import HRAnalyticsService

# Initialisation (télécharge le modèle si nécessaire)
service = HRAnalyticsService()
```

---

## 🚀 Utilisation

### 1️⃣ CV Matching

```python
from app.services.hr_analytics import HRAnalyticsService
from app.services.cv_matching import CVData, JobOffer

# Initialiser le service
service = HRAnalyticsService()

# Données du CV
cv = CVData(
    skills=["Python", "FastAPI", "Machine Learning", "SQL", "Docker"],
    experiences=[
        "Développeur Backend avec 3 ans d'expérience",
        "Création d'APIs RESTful et microservices"
    ],
    job_titles=["Développeur Backend", "Data Scientist Junior"],
    education=["Master en Informatique"],
    years_of_experience=3.5
)

# Offre d'emploi
job = JobOffer(
    required_skills=["Python", "FastAPI", "PostgreSQL", "Docker"],
    preferred_skills=["Kubernetes", "MLflow"],
    job_title="Senior Backend Developer",
    description="Développement d'une plateforme ML avec Python et FastAPI",
    required_experience_years=3.0
)

# Matching
result = service.match_cv_to_job(cv, job)

print(f"Score global: {result.overall_score:.1%}")
print(f"Compétences manquantes: {result.missing_required_skills}")
print(f"Recommandations: {result.recommendations}")
```

### 2️⃣ Recommandation de Formation

```python
from app.services.training_recommendation import EmployeeProfile, TrainingCourse

# Profil employé
employee = EmployeeProfile(
    employee_id="EMP001",
    current_skills=["Python", "SQL", "Excel"],
    training_history=["Introduction à Python"],
    current_position="Analyste RH Junior",
    target_position="Data Analyst RH"
)

# Catalogue de formations
courses = [
    TrainingCourse(
        course_id="FORM001",
        title="Python Avancé pour Data Science",
        description="Formation avancée en Python avec Pandas et NumPy",
        skills_taught=["Pandas", "NumPy", "Data Analysis"],
        level="intermédiaire",
        duration_hours=40,
        category="Data Science"
    ),
    # ... autres formations
]

# Mapping compétences requises par poste
skills_map = {
    "Data Analyst RH": ["Python", "Pandas", "SQL", "Power BI"]
}

# Recommandations
recs = service.recommend_trainings(
    employee=employee,
    available_courses=courses,
    required_skills_map=skills_map,
    top_n=5
)

for rec in recs:
    print(f"{rec.course.title}: {rec.relevance_score:.1%} ({rec.priority})")
    print(f"  Compétences comblées: {rec.skill_gap_addressed}")
```

### 3️⃣ Scoring Prédictif

```python
from app.services.predictive_scoring import EmployeeHistory

# Historique RH
history = EmployeeHistory(
    employee_id="EMP101",
    tenure_months=18,
    absences_last_year=12,
    average_performance_score=3.2,
    promotion_count=0,
    training_hours_last_year=5,
    salary_percentile=25,
    department="IT",
    manager_changes_count=3,
    overtime_hours_monthly=35,
    team_size=8,
    remote_work_percentage=20
)

# Calcul des scores
score = service.calculate_predictive_scores(history)

print(f"Risque de churn: {score.churn_risk_score:.1%} [{score.risk_level}]")
print(f"Performance: {score.performance_score:.1%}")
print(f"Engagement: {score.engagement_score:.1%}")
print(f"Recommandations: {score.recommendations}")
```

---

## 🌐 API REST avec FastAPI

### Démarrage du serveur

```bash
cd backend
uvicorn app.main:app --reload
```

### Endpoints disponibles

#### 1. Health Check
```bash
GET /api/v1/hr-analytics/health
```

#### 2. CV Matching
```bash
POST /api/v1/hr-analytics/cv-matching
Content-Type: application/json

{
  "cv": {
    "skills": ["Python", "FastAPI", "ML"],
    "experiences": ["3 ans Backend Development"],
    "job_titles": ["Backend Developer"],
    "education": ["Master Informatique"],
    "years_of_experience": 3.5
  },
  "job_offer": {
    "required_skills": ["Python", "FastAPI"],
    "preferred_skills": ["Docker"],
    "job_title": "Senior Backend Dev",
    "description": "Développement plateforme ML",
    "required_experience_years": 3.0
  }
}
```

#### 3. Recommandation de Formation
```bash
POST /api/v1/hr-analytics/training-recommendation

{
  "employee": {
    "employee_id": "EMP001",
    "current_skills": ["Python", "SQL"],
    "current_position": "Analyste RH",
    "target_position": "Data Analyst RH"
  },
  "available_courses": [...],
  "top_n": 5
}
```

#### 4. Scoring Prédictif
```bash
POST /api/v1/hr-analytics/predictive-scoring

{
  "employee_id": "EMP101",
  "tenure_months": 18,
  "absences_last_year": 12,
  "average_performance_score": 3.2,
  ...
}
```

#### 5. Analytics Workforce
```bash
POST /api/v1/hr-analytics/analytics/workforce

{
  "histories": [...]  # Liste d'historiques employés
}
```

---

## 🧪 Tests

### Exécuter les tests avec données fictives

```bash
cd backend
python test_hr_analytics_full.py
```

Le script de test inclut :
- ✅ Test CV Matching avec CV et offre fictifs
- ✅ Test Recommandation avec catalogue de formations
- ✅ Test Scoring Prédictif avec 3 profils d'employés
- ✅ Test Analytics Workforce avec équipe de 8 personnes

### Tests unitaires avec pytest

```bash
pytest test_hr_analytics_full.py -v
```

---

## 📊 Modèle ML Utilisé

**Sentence Transformer : `paraphrase-multilingual-MiniLM-L12-v2`**

- ✅ Multilingue (50+ langues, dont français et anglais)
- ✅ Léger (~420 MB)
- ✅ Performant pour le matching sémantique
- ✅ Production-ready

**Pourquoi ce modèle ?**
- Embeddings de haute qualité pour comparer textes
- Support du français (essentiel pour CVs et formations en FR)
- Rapide en inférence
- Pré-entraîné sur des tâches de paraphrase (parfait pour le matching)

---

## 🔐 Bonnes Pratiques & Sécurité

### ✅ Validation des données
- Tous les inputs sont validés avec Pydantic
- Gestion d'exceptions complète
- Logging détaillé pour le debugging

### ✅ Performance
- Embeddings mis en cache si possible
- Batch processing disponible
- Optimisé pour production

### ✅ Scalabilité
- Service stateless (peut être répliqué)
- Séparation des modules (microservices-ready)
- Compatible avec Docker/Kubernetes

---

## 🚀 Intégration CI/CD & MLflow

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements-hr-analytics.txt .
RUN pip install --no-cache-dir -r requirements-hr-analytics.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### MLflow pour suivi des modèles

```python
import mlflow

# Initialiser MLflow
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("hr_analytics")

# Logger les métriques
with mlflow.start_run():
    mlflow.log_param("model_name", "paraphrase-multilingual-MiniLM-L12-v2")
    mlflow.log_metric("avg_matching_score", 0.78)
    mlflow.log_artifact("model_config.json")
```

---

## 📈 Métriques & Monitoring

Le module expose des métriques pour monitoring :
- Temps de réponse par endpoint
- Nombre de CVs matchés
- Distribution des scores de churn
- Nombre de recommandations générées

---

## 🤝 Contribution

### Structure du code
- **Docstrings** : Toutes les fonctions sont documentées
- **Type hints** : Types annotés partout
- **Exceptions** : Gestion robuste des erreurs
- **Tests** : Coverage des fonctionnalités principales

### Ajouter une nouvelle fonctionnalité
1. Créer un nouveau module dans `app/services/`
2. Ajouter les routes API dans `app/api/v1/endpoints/`
3. Écrire les tests dans `test_*.py`
4. Mettre à jour ce README

---

## 📝 Roadmap

### Version 1.0 (Actuelle) ✅
- [x] CV Matching avec Sentence Transformers
- [x] Recommandation de formation
- [x] Scoring prédictif (churn, performance, engagement)
- [x] API REST FastAPI
- [x] Tests avec données fictives

### Version 1.1 (Prochaine)
- [ ] Extraction automatique de CV depuis PDF/DOCX
- [ ] Fine-tuning du modèle sur données RH
- [ ] Dashboard de visualisation avec Plotly
- [ ] Intégration avec base de données RH
- [ ] Export des rapports en PDF

### Version 2.0 (Future)
- [ ] Modèle de churn avec ML supervisé (Random Forest)
- [ ] Recommandations de carrière (parcours professionnel)
- [ ] Analyse de sentiment sur feedbacks employés
- [ ] Prédiction de turnover par département

---

## 📞 Support

Pour des questions ou des problèmes :
- 📧 Email : support@hranalytics.com
- 📝 Issues : GitHub Issues
- 📚 Documentation : Ce README

---

## 📜 Licence

MIT License - Libre d'utilisation pour projets commerciaux et open-source.

---

## 🙏 Remerciements

- **Sentence Transformers** : Pour les embeddings sémantiques
- **FastAPI** : Pour le framework API
- **Scikit-learn** : Pour les outils ML
- **PyTorch** : Pour le backend ML

---

**Développé avec ❤️ pour révolutionner les RH avec le Machine Learning**
