# 🚀 Quick Start - CV Matching System

## Installation Rapide en 3 Étapes

### Étape 1: Créer la Table en Base de Données

Connectez-vous à PostgreSQL et exécutez:

```bash
psql -U postgres -d hr_analytics -f backend/sql/create_job_offers.sql
```

Ou copiez-collez le contenu du fichier `backend/sql/create_job_offers.sql` dans pgAdmin.

---

### Étape 2: Démarrer le Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Vérifiez que l'API fonctionne: http://localhost:8000/docs

---

### Étape 3: Démarrer le Frontend

```bash
cd frontend
npm run dev
```

Accédez à: http://localhost:3000/job-offers

---

## ✅ Vérification Rapide

### Test Backend

1. Aller sur http://localhost:8000/docs
2. Essayer l'endpoint `GET /api/v1/cv-matching/jobs`
3. Vous devriez voir 5 offres d'exemple
4. Essayer `GET /api/v1/cv-matching/categories`
5. Vous devriez voir 43 catégories professionnelles

### Test Frontend

1. Aller sur http://localhost:3000/job-offers
2. Vous devriez voir les 5 offres d'exemple
3. Cliquer sur "Matcher un CV" sur une offre
4. Uploader un CV (PDF ou DOCX)
5. Voir les résultats de matching

---

## 🎯 Fonctionnalités Principales

### Gestion des Offres
- ✅ Créer une offre d'emploi
- ✅ Lister toutes les offres
- ✅ Filtrer par catégorie
- ✅ Rechercher par mot-clé
- ✅ Désactiver une offre

### Matching CV
- ✅ Upload CV (PDF/DOCX)
- ✅ Parsing automatique du CV
- ✅ Prédiction de la catégorie professionnelle (43 classes)
- ✅ Scoring détaillé:
  - Compétences (35%)
  - Expérience (25%)
  - Catégorie (25%)
  - Éducation (15%)
- ✅ Recommandations personnalisées

---

## 📝 Example d'Utilisation

### 1. Créer une Nouvelle Offre

Sur `/job-offers`, cliquer **"Nouvelle Offre"**:

```
Titre: Data Engineer
Description: Concevoir et maintenir des pipelines de données...
Catégorie: Data Science
Compétences requises: Python, SQL, Spark, Airflow
Compétences préférées: Kafka, AWS, Docker
Éducation: Master, Ingénieur
Expérience: 3 ans
Localisation: Paris
Salaire: 45000-65000 EUR
Contrat: CDI
Département: Data
```

### 2. Matcher un CV

1. Cliquer **"Matcher un CV"** sur l'offre
2. Uploader un fichier CV
3. Cliquer **"Analyser le CV"**
4. Voir les résultats:
   - Score global: 78.5%
   - Compétences: 85%
   - Expérience: 70%
   - Catégorie: 90% (Data Science)
   - Éducation: 80%

### 3. Interpréter les Résultats

**Score > 75%** 🟢  
→ Excellent match! Le candidat correspond très bien au poste

**Score 50-75%** 🟡  
→ Bon match avec quelques lacunes à combler

**Score 25-50%** 🟠  
→ Match partiel, formation recommandée

**Score < 25%** 🔴  
→ Profil inadapté pour ce poste

---

## 🔧 Troubleshooting

### La table n'existe pas
```
relation "job_offers" does not exist
```
➜ Exécutez le script SQL `create_job_offers.sql`

### Modèle ML introuvable
```
RuntimeError: Impossible de charger les modèles
```
➜ Vérifiez que les fichiers .pkl existent dans `backend/ml/models/`:
- cv_matching_model.pkl
- cv_tfidf.pkl
- cv_label_encoder.pkl

### Import cv_parser échoue
```
ModuleNotFoundError: No module named 'cv_parser'
```
➜ Vérifiez que le service `cv_parser.py` existe dans `backend/app/services/`

---

## 📚 Documentation Complète

Voir [CV_MATCHING_README.md](CV_MATCHING_README.md) pour:
- Architecture détaillée
- Endpoints API complets
- Configuration ML
- Exemples de requêtes

---

## 🎉 C'est Tout!

Votre système de CV Matching est prêt. Profitez-en! 🚀

---

**Questions?** Consultez la documentation ou les logs du backend.
