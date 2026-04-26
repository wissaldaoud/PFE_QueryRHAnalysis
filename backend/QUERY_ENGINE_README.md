# 🤖 Moteur de Requêtes RH Intelligent

## 📋 Vue d'ensemble

Ce moteur de requêtes permet aux utilisateurs de poser des questions en **français naturel** sur leurs données RH et d'obtenir des réponses structurées avec visualisations suggérées.

### Architecture à 2 bases de données

```
┌─────────────────────────────────────────────────────────┐
│                   UTILISATEUR RH                        │
│         "Combien d'employés actifs?"                    │
└────────────────────┬────────────────────────────────────┘
                     │
      ┌──────────────▼──────────────┐
      │   FastAPI Backend           │
      │   POST /api/query/execute   │
      └──────────────┬──────────────┘
                     │
      ┌──────────────▼──────────────────┐
      │  QueryEngineService             │
      │  1. Auth via APP_DB (users)     │
      │  2. Question → Claude API       │
      │  3. SQL → DWH_DB execution      │
      │  4. Response formatting         │
      └──────────────┬──────────────────┘
                     │
       ┌─────────────┴─────────────┐
       │                           │
┌──────▼────────┐         ┌────────▼────────┐
│   APP_DB      │         │    DWH_DB       │
│ hr_analytics  │         │ hr_datawarehouse│
│               │         │                 │
│ • users       │         │ • fact_employes │
│ • auth        │         │ • dim_depts     │
│ • sessions    │         │ • fact_conges   │
└───────────────┘         │ • fact_perfs    │
                          └─────────────────┘
                          ↑
                    ┌─────┴──────┐
                    │ Qlik Sense │
                    └────────────┘
```

## 🔑 Principes clés

1. **Séparation stricte** : Le moteur interroge **uniquement DWH_DB**, jamais APP_DB
2. **NLP avec Claude** : Questions FR → SQL PostgreSQL via API Anthropic
3. **Sécurité** : Seules les requêtes SELECT autorisées, validation user
4. **Cohérence** : Qlik Sense et moteur de requêtes utilisent la même base DWH

## 🚀 Installation & Configuration

### 1. Variables d'environnement

Ajoutez ces variables dans `.env` :

```bash
# DWH Database (Qlik datawarehouse)
DWH_HOST=localhost
DWH_PORT=5432
DWH_DB=hr_datawarehouse
DWH_USER=hr_user
DWH_PASSWORD=hr_password123

# Claude API
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

### 2. Dépendances Python

Installez les dépendances requises :

```bash
cd backend
env/Scripts/activate  # Windows
pip install anthropic psycopg2-binary
```

### 3. Remplacer les anciens fichiers

```powershell
# Backup anciens fichiers
Move-Item app\services\query_engine_service.py app\services\query_engine_service_old.py
Move-Item app\api\v1\endpoints\query_engine.py app\api\v1\endpoints\query_engine_old.py

# Activer nouveaux fichiers
Move-Item app\services\query_engine_service_new.py app\services\query_engine_service.py
Move-Item app\api\v1\endpoints\query_engine_new.py app\api\v1\endpoints\query_engine.py
```

### 4. Démarrer le backend

```powershell
cd backend
$env:PYTHONPATH = "C:\Users\wdaoud\Desktop\test\backend"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 📡 API Endpoints

### POST `/api/v1/query/execute`

Exécuter une requête en langage naturel.

**Request:**
```json
{
  "question": "Combien d'employés actifs?"
}
```

**Response:**
```json
{
  "success": true,
  "answer": "Il y a **235 employés actifs** dans l'entreprise.",
  "query_type": "query_success",
  "sql_query": "SELECT COUNT(*) FROM fact_employes WHERE statut = 'actif'",
  "data": {
    "rows": [{"count": 235}],
    "columns": ["count"],
    "count": 1
  },
  "visualization": {
    "type": "metric",
    "value": 235,
    "label": "count"
  }
}
```

### GET `/api/v1/query/history?limit=20`

Récupérer l'historique des requêtes de l'utilisateur.

### GET `/api/v1/query/health`

Vérifier la santé du service (APP_DB, DWH_DB, Claude API).

## 🎯 Exemples de questions

### Questions simples
- "Combien d'employés actifs?"
- "Combien de départements?"
- "Nombre de congés en attente"

### Listes et filtres
- "Liste des employés du département IT"
- "Top 10 des salaires les plus élevés"
- "Employés embauchés en 2024"

### Statistiques
- "Salaire moyen par département"
- "Taux de turnover par département"
- "Répartition des congés par type"

### Analyses complexes
- "Quels départements ont le budget le plus élevé?"
- "Performance moyenne par département"
- "Employés avec note de performance supérieure à 4"

## 🔒 Sécurité

### Validation SQL
- ✅ Seules les requêtes `SELECT` autorisées
- ❌ Blocage de : INSERT, UPDATE, DELETE, DROP, ALTER, EXEC
- ✅ Utilisation de connexion read-only pour DWH_DB

### Authentification
- ✅ User authentifié requis (JWT token)
- ✅ Validation user_id dans APP_DB
- ✅ Historique séparé par utilisateur

### Credentials
- ✅ Pas d'exposition des credentials DWH dans les responses
- ✅ Variables d'environnement sécurisées
- ✅ API keys Claude chargées depuis .env

## 📊 Schéma DWH

Le moteur connaît ces tables dans `hr_datawarehouse` :

```sql
-- Employés
TABLE fact_employes (
    employe_id, nom, prenom, email,
    departement_id, poste, salaire, statut,
    date_embauche, date_depart
)

-- Départements
TABLE dim_departements (
    departement_id, nom, manager_id, budget
)

-- Congés
TABLE fact_conges (
    conge_id, employe_id, date_debut, date_fin,
    type_conge, statut
)

-- Performances
TABLE fact_performances (
    perf_id, employe_id, annee, note,
    objectifs_atteints
)
```

## 🛠️ Dépannage

### Erreur "Base de données indisponible"
- Vérifiez que PostgreSQL est démarré
- Vérifiez les credentials DWH_* dans .env
- Testez la connexion : `psql -h localhost -U hr_user -d hr_datawarehouse`

### Erreur "ANTHROPIC_API_KEY manquante"
- Obtenez une clé API sur https://console.anthropic.com/
- Ajoutez-la dans .env : `ANTHROPIC_API_KEY=sk-ant-api03-...`

### Erreur "Utilisateur non authentifié"
- Connectez-vous d'abord via `/api/v1/auth/login`
- Incluez le token JWT dans le header `Authorization: Bearer <token>`

## 📈 Visualisations

Le moteur suggère automatiquement le type de visualisation :

| Type | Critères | Exemple |
|------|----------|---------|
| **Metric** | 1 ligne, 1 colonne numérique | Nombre total d'employés |
| **Pie Chart** | 2 colonnes, ≤7 lignes | Répartition par département |
| **Bar Chart** | 2 colonnes, >7 lignes | Salaires par département |
| **Table** | Plusieurs colonnes | Liste détaillée d'employés |

## 🔗 Intégration avec Qlik Sense

Les deux outils partagent la même base `hr_datawarehouse` :

```
Qlik Sense ────────┐
                   ├──→ hr_datawarehouse (source de vérité)
Query Engine ──────┘
```

**Avantages** :
- ✅ Données cohérentes entre dashboards Qlik et requêtes NLP
- ✅ Qlik gère les analyses visuelles complexes
- ✅ Query Engine gère les questions ponctuelles en français
- ✅ Pas de duplication de données

## 📝 Notes pour le PFE

**Justifications techniques** :
1. **Séparation APP_DB / DWH_DB** : Architecture data warehouse classique (OLTP vs OLAP)
2. **Claude API** : État de l'art NLP, meilleur que règles regex
3. **PostgreSQL direct** : Performant, pas de latence ORM pour analytics
4. **Read-only DWH** : Sécurité, pas de modification accidentelle
5. **Visualisation auto** : UX améliorée, pas besoin de choisir manuellement

**Démonstration** :
- Montrez la différence entre question regex (ancien) vs NLP Claude (nouveau)
- Comparez les temps de réponse
- Montrez la cohérence avec Qlik Sense

## 🚀 Prochaines étapes

Pour étendre le moteur :
1. Ajouter plus de tables dans `DWH_SCHEMA`
2. Implémenter export CSV/Excel
3. Ajouter cache Redis pour requêtes fréquentes
4. Implémenter suggestions de questions avec ML
5. Ajouter détection langage (FR/EN)

---

**⚡ Quick Start:**
```bash
# 1. Configure .env avec DWH credentials + ANTHROPIC_API_KEY
# 2. Activate new files
# 3. Start backend: python -m uvicorn app.main:app --reload --port 8000
# 4. Test: POST /api/v1/query/execute {"question": "Combien d'employés?"}
```
