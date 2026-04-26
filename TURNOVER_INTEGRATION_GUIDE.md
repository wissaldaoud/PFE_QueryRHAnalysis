# Intégration du Modèle de Prédiction de Turnover

## 📋 Vue d'ensemble

Ce guide explique comment intégrer votre modèle Gradient Boosting de prédiction de turnover (`turnover_model.pkl`) dans votre application FastAPI + Next.js.

## 🎯 Ce qui a été créé

### 1. Backend - Service de Prédiction
**Fichier:** `backend/ml/predict_turnover.py`

Classe `TurnoverPredictor` qui:
- ✅ Charge automatiquement `turnover_model.pkl` et `turnover_features.pkl` depuis `C:\Users\wdaoud\Documents\Models\`
- ✅ Calcule automatiquement: `age`, `anciennete_annees`, `duree_presence_jours`
- ✅ Encode `sexe` et `type_contrat` avec one-hot encoding (pd.get_dummies)
- ✅ Respecte l'ordre exact des features: `['age', 'anciennete_annees', 'total_jours_absence', 'nb_absences', 'duree_presence_jours', 'sexe_Féminin', 'sexe_Masculin', 'type_contrat_CDD', 'type_contrat_CDI', 'type_contrat_Inconnu']`
- ✅ Retourne: probabilité, niveau de risque (Faible/Moyen/Élevé), emoji 🟢🟡🔴

### 2. Backend - Endpoint API
**Fichier:** `backend/app/api/v1/endpoints/hr_analytics.py`

**Endpoint:** `POST /api/v1/hr-analytics/predict-turnover`

**Request:**
```json
{
  "date_naissance": "1990-05-15",
  "date_embauche": "2018-03-01",
  "sexe": "Masculin",
  "type_contrat": "CDI",
  "total_jours_absence": 12,
  "nb_absences": 3
}
```

**Response:**
```json
{
  "status": "success",
  "prediction": 0,
  "turnover_probability": 0.2315,
  "turnover_probability_percent": 23.15,
  "risk_level": "Faible",
  "risk_color": "green",
  "risk_emoji": "🟢",
  "features_used": {
    "age": 35,
    "anciennete_annees": 8.1,
    "total_jours_absence": 12,
    "nb_absences": 3,
    "duree_presence_jours": 2961,
    "sexe_Féminin": 0,
    "sexe_Masculin": 1,
    "type_contrat_CDD": 0,
    "type_contrat_CDI": 1,
    "type_contrat_Inconnu": 0
  },
  "model_path": "C:\\Users\\wdaoud\\Documents\\Models\\turnover_model.pkl",
  "computed_at": "2026-04-08T14:23:45.123456"
}
```

### 3. Frontend - Composant React
**Fichier:** `frontend/components/TurnoverPredictor.tsx`

Composant Next.js avec:
- ✅ Champs: Sexe (dropdown), Total jours d'absence, Nombre d'absences
- ✅ Calcul auto de l'âge et ancienneté (affichage)
- ✅ Bouton "Prédire le Turnover"
- ✅ Badge coloré: 🟢 Faible / 🟡 Moyen / 🔴 Élevé
- ✅ Affichage du pourcentage de risque
- ✅ Détails des features utilisées
- ✅ Gestion des erreurs et états de chargement

## 🔧 Installation

### 1. Vérifiez que vos modèles existent

```powershell
# Assurez-vous que ces fichiers existent:
Test-Path "C:\Users\wdaoud\Documents\Models\turnover_model.pkl"
Test-Path "C:\Users\wdaoud\Documents\Models\turnover_features.pkl"  # Optionnel
```

Si `turnover_features.pkl` n'existe pas, les features par défaut seront utilisées.

### 2. Redémarrez le backend

Le backend FastAPI avec uvicorn --reload devrait se recharger automatiquement. Sinon:

```powershell
cd C:\Users\wdaoud\Desktop\test\backend
uvicorn app.main:app --reload
```

### 3. Testez l'endpoint

```powershell
# Test avec PowerShell
$body = @{
    date_naissance = "1990-05-15"
    date_embauche = "2018-03-01"
    sexe = "Masculin"
    type_contrat = "CDI"
    total_jours_absence = 12
    nb_absences = 3
} | ConvertTo-Json

$token = "YOUR_ACCESS_TOKEN"

Invoke-RestMethod -Method POST `
  -Uri "http://127.0.0.1:8000/api/v1/hr-analytics/predict-turnover" `
  -Headers @{ "Authorization" = "Bearer $token"; "Content-Type" = "application/json" } `
  -Body $body
```

## 📦 Intégration dans les pages existantes

### Option 1: Page de détail d'employé

**Fichier:** `frontend/app/employees/[id]/page.tsx`

```tsx
import TurnoverPredictor from "@/components/TurnoverPredictor";

// ... dans votre composant, après avoir chargé l'employé

return (
  <MainLayout>
    {/* Informations existantes de l'employé */}
    
    {/* Ajouter le prédicteur */}
    <div className="mt-6">
      <TurnoverPredictor
        employeeData={{
          date_of_birth: employee.date_of_birth,
          hire_date: employee.hire_date,
          contract_type: employee.contract_type || "CDI",
        }}
      />
    </div>
  </MainLayout>
);
```

### Option 2: Page d'édition d'employé

**Fichier:** `frontend/app/employees/[id]/edit/page.tsx`

```tsx
import TurnoverPredictor from "@/components/TurnoverPredictor";

// Dans votre formulaire d'édition

<form onSubmit={handleSubmit}>
  {/* Champs existants du formulaire */}
  
  {/* Ajouter après les champs de base */}
  <div className="mt-8">
    <TurnoverPredictor
      employeeData={{
        date_of_birth: formData.date_of_birth,
        hire_date: formData.hire_date,
        contract_type: formData.contract_type,
      }}
    />
  </div>
</form>
```

### Option 3: Modal standalone

```tsx
import { useState } from "react";
import TurnoverPredictor from "@/components/TurnoverPredictor";
import { X, Brain } from "lucide-react";

function EmployeeActions({ employee }) {
  const [showPredictor, setShowPredictor] = useState(false);

  return (
    <>
      <button
        onClick={() => setShowPredictor(true)}
        className="bg-purple-600 text-white px-4 py-2 rounded-lg flex items-center gap-2"
      >
        <Brain className="w-5 h-5" />
        Prédire Turnover
      </button>

      {showPredictor && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">
                Prédiction - {employee.first_name} {employee.last_name}
              </h2>
              <button onClick={() => setShowPredictor(false)}>
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <TurnoverPredictor
              employeeData={{
                date_of_birth: employee.date_of_birth,
                hire_date: employee.hire_date,
                contract_type: employee.contract_type,
              }}
            />
          </div>
        </div>
      )}
    </>
  );
}
```

## 🎨 Personnalisation

### Modifier les seuils de risque

Dans `backend/ml/predict_turnover.py`, ligne 126-136:

```python
# Modifier les pourcentages
if probability < 0.30:  # Changez 0.30 pour ajuster "Faible"
    risk_level = "Faible"
elif probability < 0.60:  # Changez 0.60 pour ajuster "Moyen"
    risk_level = "Moyen"
else:
    risk_level = "Élevé"
```

### Ajouter d'autres niveaux

```python
if probability < 0.20:
    risk_level = "Très Faible"
    risk_emoji = "🟢"
elif probability < 0.40:
    risk_level = "Faible"
    risk_emoji = "🟡"
elif probability < 0.60:
    risk_level = "Moyen"
    risk_emoji = "🟠"
elif probability < 0.80:
    risk_level = "Élevé"
    risk_emoji = "🔴"
else:
    risk_level = "Critique"
    risk_emoji = "🔴"
```

Puis ajustez les couleurs dans le composant React:

```tsx
const getRiskBadgeColor = (level: string) => {
  switch (level.toLowerCase()) {
    case "très faible":
      return "bg-emerald-100 text-emerald-800 border-emerald-300";
    case "faible":
      return "bg-green-100 text-green-800 border-green-300";
    case "moyen":
      return "bg-yellow-100 text-yellow-800 border-yellow-300";
    case "élevé":
      return "bg-orange-100 text-orange-800 border-orange-300";
    case "critique":
      return "bg-red-100 text-red-800 border-red-300";
    default:
      return "bg-gray-100 text-gray-800 border-gray-300";
  }
};
```

## 🔍 Débogage

### Erreur: "Modèle introuvable"

```powershell
# Vérifiez le chemin
Get-Item "C:\Users\wdaoud\Documents\Models\turnover_model.pkl"

# Si le fichier est ailleurs, modifiez dans predict_turnover.py:
MODEL_PATH = Path(r"VOTRE\NOUVEAU\CHEMIN\turnover_model.pkl")
```

### Erreur: "Feature mismatch"

Le modèle attend exactement ces 10 features dans cet ordre:
```python
['age', 'anciennete_annees', 'total_jours_absence', 'nb_absences', 
 'duree_presence_jours', 'sexe_Féminin', 'sexe_Masculin',
 'type_contrat_CDD', 'type_contrat_CDI', 'type_contrat_Inconnu']
```

Si votre modèle utilise des features différentes, créez `turnover_features.pkl`:

```python
import joblib

features = ['vos', 'features', 'dans', 'le', 'bon', 'ordre']
joblib.dump(features, "C:/Users/wdaoud/Documents/Models/turnover_features.pkl")
```

### Tester avec curl

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/hr-analytics/predict-turnover" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date_naissance": "1990-05-15",
    "date_embauche": "2018-03-01",
    "sexe": "Masculin",
    "type_contrat": "CDI",
    "total_jours_absence": 12,
    "nb_absences": 3
  }'
```

## 📊 Comparaison avec le modèle existant

Votre application a déjà un système de prédiction dans `predictive_scoring.py` qui utilise `turnover_model_real.pkl`. Voici les différences:

| Aspect | Ancien modèle (XGBoost) | Nouveau modèle (Gradient Boosting) |
|--------|-------------------------|-----------------------------------|
| **Emplacement** | `backend/ml/models/turnover_model_real.pkl` | `C:\Users\wdaoud\Documents\Models\turnover_model.pkl` |
| **Features** | 7 features (sexe_code, is_cdi, taux_absenteisme) | 10 features (sexe one-hot, type_contrat one-hot) |
| **Endpoint** | `/predictive-scoring/ml/{employee_id}` | `/predict-turnover` |
| **Usage** | Chargement automatique depuis DB | Formulaire manuel |
| **SHAP** | ✅ Explainability incluse | ❌ Pas de SHAP |

Vous pouvez garder les deux ou migrer vers un seul modèle selon vos besoins.

## ✅ Checklist d'intégration

- [ ] Modèles présents dans `C:\Users\wdaoud\Documents\Models\`
- [ ] Backend redémarré (uvicorn reload automatique)
- [ ] Endpoint testé avec PowerShell/curl
- [ ] Composant React ajouté à une page
- [ ] Test dans le navigateur avec un employé réel
- [ ] Vérification du badge coloré (🟢🟡🔴)
- [ ] Ajout du champ `sexe` à votre table `employees` (si manquant)

## 💡 Améliorations futures

1. **Batch prediction**: Prédire pour tous les employés actifs
2. **Export CSV**: Télécharger les prédictions
3. **Dashboard**: Vue d'ensemble des risques de turnover
4. **Alertes**: Notifications pour les employés à haut risque
5. **Historique**: Tracker l'évolution du risque dans le temps
6. **Re-training**: Interface pour ré-entraîner le modèle

## 📞 Support

Si vous rencontrez des problèmes:
1. Vérifiez les logs FastAPI dans le terminal uvicorn
2. Vérifiez la console du navigateur (F12)
3. Testez l'endpoint directement avec PowerShell
4. Vérifiez que les chemins des fichiers sont corrects
