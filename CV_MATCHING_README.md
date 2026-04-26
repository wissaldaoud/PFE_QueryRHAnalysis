# Guide d'Installation - Système de CV Matching avec ML

## 📋 Vue d'Ensemble

Système complet de matching CV avec Machine Learning utilisant:
- **Backend**: FastAPI + RandomForest + TF-IDF
- **Frontend**: Next.js + React + shadcn/ui
- **Base de données**: PostgreSQL

---

## 🚀 Installation

### 1. Créer la table `job_offers`

Connectez-vous à votre base PostgreSQL et exécutez:

```sql
CREATE TABLE IF NOT EXISTS job_offers (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100),
    
    -- Compétences en JSON
    required_skills JSONB DEFAULT '[]'::jsonb,
    preferred_skills JSONB DEFAULT '[]'::jsonb,
    
    -- Éducation 
    required_education JSONB DEFAULT '[]'::jsonb,
    
    -- Expérience
    required_experience_years FLOAT,
    
    -- Informations additionnelles
    location VARCHAR(255),
    salary_range VARCHAR(100),
    contract_type VARCHAR(50),
    department VARCHAR(100),
    
    -- Statut
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Métadonnées
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    created_by INTEGER
);

-- Index pour performances
CREATE INDEX IF NOT EXISTS idx_job_offers_title ON job_offers(title);
CREATE INDEX IF NOT EXISTS idx_job_offers_category ON job_offers(category);
CREATE INDEX IF NOT EXISTS idx_job_offers_is_active ON job_offers(is_active);
```

### 2. Insérer des données d'exemple

```sql
INSERT INTO job_offers (title, description, category, required_skills, preferred_skills, 
    required_education, required_experience_years, location, salary_range, contract_type, department, is_active)
VALUES 
(
    'Data Scientist Senior',
    'Nous recherchons un Data Scientist expérimenté pour rejoindre notre équipe Analytics.',
    'Data Science',
    '["Python", "Machine Learning", "SQL", "Pandas", "Scikit-learn"]'::jsonb,
    '["TensorFlow", "Deep Learning", "MLflow", "Docker"]'::jsonb,
    '["Master en Data Science", "Ingénieur"]'::jsonb,
    5.0,
    'Paris',
    '50000-70000 EUR',
    'CDI',
    'Data & Analytics',
    TRUE
),
(
    'Développeur Python Backend',
    'Développeur Python pour concevoir et maintenir des APIs REST avec FastAPI.',
    'Python Developer',
    '["Python", "FastAPI", "PostgreSQL", "REST API", "Git"]'::jsonb,
    '["Docker", "Kubernetes", "CI/CD", "Redis"]'::jsonb,
    '["Licence Informatique", "Ingénieur"]'::jsonb,
    3.0,
    'Lyon',
    '40000-55000 EUR',
    'CDI',
    'Engineering',
    TRUE
);
```

### 3. Démarrer le Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 4. Démarrer le Frontend

```bash  
cd frontend
npm run dev
```

---

## 📌 Endpoints API

### Gestion des Offres

#### Créer une offre
```http
POST /api/v1/cv-matching/jobs
Content-Type: application/json

{
  "title": "Data Scientist",
  "description": "Description du poste...",
  "category": "Data Science",
  "required_skills": ["Python", "ML", "SQL"],
  "preferred_skills": ["Docker", "AWS"],
  "required_education": ["Master"],
  "required_experience_years": 3,
  "location": "Paris",
  "salary_range": "45000-60000 EUR",
  "contract_type": "CDI",
  "department": "Analytics"
}
```

#### Lister les offres
```http
GET /api/v1/cv-matching/jobs?active_only=true&category=Data%20Science
```

#### Récupérer une offre
```http
GET /api/v1/cv-matching/jobs/{job_id}
```

#### Mettre à jour une offre
```http
PUT /api/v1/cv-matching/jobs/{job_id}
Content-Type: application/json

{
  "is_active": false
}
```

#### Supprimer (désactiver) une offre
```http
DELETE /api/v1/cv-matching/jobs/{job_id}
```

### Matching CV

#### Matcher un CV contre une offre
```http
POST /api/v1/cv-matching/match/{job_id}
Content-Type: application/json

{
  "cv_text": "Texte complet du CV...",
  "skills": ["Python", "SQL", "Machine Learning"],
  "experiences": ["Data Analyst chez XYZ (3 ans)"],
  "job_titles": ["Data Analyst", "Junior Data Scientist"],
  "education": ["Master Data Science"],
  "years_of_experience": 4.5
}
```

**Réponse:**
```json
{
  "success": true,
  "job_offer_id": 1,
  "job_title": "Data Scientist Senior",
  "overall_score": 75.3,
  "skills_score": 80.0,
  "experience_score": 70.5,
  "category_match_score": 85.2,
  "education_score": 90.0,
  "matching_skills": ["Python", "SQL", "Machine Learning"],
  "missing_required_skills": ["Pandas"],
  "missing_preferred_skills": ["Docker", "MLflow"],
  "recommendations": [
    "✅ Excellent profil! Postulez avec confiance",
    "💪 Pour se démarquer: Docker, MLflow"
  ],
  "predicted_category": "Data Science",
  "job_category": "Data Science"
}
```

#### Matcher contre toutes les offres
```http
POST /api/v1/cv-matching/match-all?limit=10
Content-Type: application/json

{
  "cv_text": "...",
  "skills": ["Python", "FastAPI"],
  ...
}
```

#### Upload et matcher un CV (PDF/DOCX)
```http
POST /api/v1/cv-matching/upload-and-match/{job_id}
Content-Type: multipart/form-data

file: [fichier CV]
```

#### Récupérer les catégories disponibles
```http
GET /api/v1/cv-matching/categories
```

**Réponse:**
```json
{
  "success": true,
  "total": 43,
  "categories": [
    "Accountant",
    "Business Analyst",
    "Data Science",
    "DevOps Engineer",
    "Python Developer",
    ...
  ]
}
```

---

## 🖥️ Pages Frontend

### `/job-offers`
- Liste toutes les offres d'emploi
- Créer de nouvelles offres
- Rechercher et filtrer par catégorie
- Accéder au matching pour chaque offre

### `/cv-matching/[id]`
- Upload un CV (PDF/DOCX)
- Voir les résultats de matching détaillés:
  - Score global + breakdown (compétences, expérience, catégorie, éducation)
  - Compétences correspondantes vs manquantes
  - Catégorie professionnelle prédite
  - Recommandations personnalisées

---

## 🎯 Modèle ML

### Architecture
- **Type**: RandomForestClassifier (43 classes)
- **Vectorisation**: TF-IDF (5000 features)
- **Catégories**: 43 professions (Data Science, Python Developer, etc.)

### Fichiers Modèle
```
backend/ml/models/
├── cv_matching_model.pkl      # RandomForest
├── cv_tfidf.pkl                # TF-IDF Vectorizer
├── cv_label_encoder.pkl        # Label Encoder
└── cv_dataset.pkl              # Dataset d'entraînement
```

### Fonctionnement
1. Extraction du texte du CV
2. Vectorisation TF-IDF
3. Prédiction de la catégorie professionnelle
4. Calcul de similarité avec l'offre d'emploi
5. Scoring pondéré:
   - Compétences: 35%
   - Expérience: 25%
   - Catégorie: 25%
   - Éducation: 15%

---

## 🔧 Configuration

### Backend
- Les modèles sont chargés au démarrage via singleton
- Logs détaillés dans le service cv_matching.py

### Frontend
- Composants shadcn/ui pour l'interface
- Upload de fichiers avec parsing automatique
- Visualisation des scores avec Progress bars

---

## 📊 Example de Workflow

1. **Créer une offre**
   - Aller sur `/job-offers`
   - Cliquer "Nouvelle Offre"
   - Remplir les informations
   - Soumettre

2. **Matcher un CV**
   - Cliquer "Matcher un CV" sur une offre
   - Uploader un fichier CV (PDF/DOCX)
   - Analyser
   - Consulter les résultats détaillés

3. **Interpréter les résultats**
   - Score > 75%: Excellent match
   - Score 50-75%: Bon match
   - Score 25-50%: Match partiel
   - Score < 25%: Faible match

---

## 🛠️ Troubleshooting

### Erreur chargement modèle
```
RuntimeError: Impossible de charger les modèles CV matching
```
**Solution:** Vérifiez que les fichiers .pkl existent dans `backend/ml/models/`

### Erreur table non trouvée
```
relation "job_offers" does not exist
```
**Solution:** Exécutez le script SQL de création de table

### Erreur upload CV
```
Erreur traitement CV
```
**Solution:** Vérifiez que le service cv_parser est configuré correctement

---

## 📝 Notes

- Le système utilise le même parseur CV que le reste de l'application
- Les compétences sont matchées avec une similarité TF-IDF (seuil 0.6)
- La catégorie prédite peut différer de la catégorie de l'offre
- Tous les scores sont en pourcentage (0-100)

---

## 🎉 Fonctionnalités

✅ Gestion complète des offres d'emploi  
✅ Upload et parsing CV (PDF/DOCX)  
✅ Matching ML avec RandomForest  
✅ Scoring détaillé multi-critères  
✅ Recommandations personnalisées  
✅ Interface moderne et intuitive  
✅ API REST complète  
✅ 43 catégories professionnelles  

---

**Auteur:** Système HR Analytics  
**Date:** Avril 2026  
**Version:** 1.0
