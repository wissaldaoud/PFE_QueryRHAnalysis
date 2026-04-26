# 🏖️ Gestion des Congés et Chevauchement d'Équipe

## 📋 Vue d'ensemble

Le système de gestion des congés intègre une **validation automatique** pour éviter que trop d'employés de la même équipe soient absents simultanément.

---

## 🔄 Processus de validation à deux niveaux

### 1️⃣ Création de la demande (Employé)
- L'employé crée une demande de congé
- **Validation automatique** avant soumission :
  - ✅ Solde de congés suffisant
  - ✅ Délai de prévenance respecté (14 jours pour congés annuels)
  - ✅ Effectif minimum garanti dans l'équipe
  - ✅ Période non bloquée
- Si une règle n'est pas respectée → **Demande REFUSÉE immédiatement**
- Statut : `pending` (En attente manager)

### 2️⃣ Approbation Manager
- Le manager reçoit une notification
- Voit les **avertissements** (collègues déjà en congé)
- Peut approuver ou refuser
- Si approuvé → Statut : `manager_approved` (En attente RH)

### 3️⃣ Validation finale RH
- Le RH reçoit une notification
- Valide ou rejette la demande
- Si approuvé → Statut : `hr_approved` (Congé confirmé)

---

## ⚠️ Détection automatique du chevauchement

### Comment ça fonctionne ?

Quand un employé demande un congé, le système :

1. **Identifie son équipe** (par département)
2. **Cherche les congés** déjà approuvés ou en attente sur la même période
3. **Calcule l'effectif restant** si la demande est approuvée
4. **Applique la règle d'effectif minimum**

### Règles d'effectif minimum

Le système refuse automatiquement si :

```
Effectif présent < MAX(2 personnes, 40% de l'équipe)
```

**Exemples concrets :**

| Taille équipe | Minimum requis | Calcul |
|---------------|----------------|--------|
| 3 personnes   | 2 personnes    | max(2, 3×40%=1.2) = 2 |
| 5 personnes   | 2 personnes    | max(2, 5×40%=2) = 2 |
| 10 personnes  | 4 personnes    | max(2, 10×40%=4) = 4 |
| 20 personnes  | 8 personnes    | max(2, 20×40%=8) = 8 |

### Exemple de scénario

**Département RH - 5 employés**
- Ahmed, Sara, Mohamed, Fatima, Karim

**Chronologie :**
1. Sara demande congé du 3 au 7 mars → ✅ Approuvé (4 restent)
2. Mohamed demande congé du 5 au 9 mars → ✅ Approuvé avec avertissement (3 restent)
3. Ahmed demande congé du 6 au 8 mars → ❌ **REFUSÉ**
   - Seulement 2 personnes resteraient (Fatima, Karim)
   - Minimum requis : 2 personnes
   - Message : "Effectif minimum non garanti. L'équipe a 5 personnes, 2 déjà en congé..."

---

## 👥 Affectation des équipes

### Méthode 1 : Par Département (Actuellement utilisée)

**Principe :**
- Tous les employés d'un même **département** forment une équipe
- La validation de chevauchement se fait au niveau du département

**Comment affecter un employé à un département :**

1. Allez sur **Employés** : `http://localhost:3000/employees`
2. Cliquez sur un employé
3. Cliquez sur **Modifier**
4. Dans la section "Informations professionnelles", sélectionnez le **Département**
5. Enregistrez

**Exemple :**
```
Département : Ressources Humaines
├── Ahmed Bennani (RH Manager)
├── Sara El Amrani (Analyste RH)
└── Mohamed Tazi (Assistant RH)

→ Ces 3 personnes forment une équipe
→ Au moins 2 doivent rester présentes si l'un demande congé
```

### Méthode 2 : Par Manager (Disponible mais non activée)

**Principe :**
- Les employés avec le même `manager_id` forment une sous-équipe
- Permet plusieurs équipes au sein d'un même département

**Configuration requise :**
- Ajouter le champ "Manager" dans le formulaire d'édition employé
- Le manager doit lui-même être enregistré comme employé

**Exemple d'utilisation :**
```
Département : Développement (10 personnes)
│
├── Équipe Frontend (Manager: Ahmed)
│   ├── Sara
│   ├── Mohamed
│   └── Fatima
│
└── Équipe Backend (Manager: Karim)
    ├── Youssef
    ├── Amina
    └── Hassan

→ Validation séparée pour chaque équipe
```

---

## 🎯 Critères de validation complets

### 1. Solde de congés
- Congés annuels : 30 jours par an
- Congés maladie : Pas de limite
- Congés sans solde : Pas de déduction

### 2. Délai de prévenance
- **Congés annuels** : Minimum 14 jours à l'avance
- **Congés maladie** : Pas de délai (urgent)
- **Congés sans solde** : Recommandé 14 jours

### 3. Effectif minimum d'équipe
- Au moins **40% de l'équipe** OU **2 personnes** doivent rester
- Calculé par département (ou par manager si activé)

### 4. Périodes bloquées
- Fin d'année fiscale (ex: 25 déc - 5 jan)
- Clôture mensuelle (dernier jour du mois)
- Configurable dans le code

### 5. Dates valides
- Date de début doit être dans le futur
- Date de fin après date de début

---

## 🚨 Messages d'erreur et avertissements

### Erreurs bloquantes (Refus automatique)

**Solde insuffisant :**
```
❌ Solde de congés insuffisant.
   Disponible: 5 jours, Demandé: 10 jours
```

**Délai trop court :**
```
❌ Délai de prévenance insuffisant.
   Les congés annuels doivent être demandés au moins 14 jours à l'avance.
   Délai actuel: 7 jours
```

**Effectif minimum non respecté :**
```
❌ Effectif minimum non garanti.
   L'équipe a 5 personnes, 2 déjà en congé sur cette période.
   Minimum requis: 2 personnes présentes,
   Disponibles si approuvé: 2 personnes
```

**Période bloquée :**
```
❌ Période bloquée: Clôture annuelle (25/12 - 05/01).
   Aucun congé n'est autorisé pendant cette période.
```

### Avertissements (Non bloquants)

**Congés simultanés :**
```
⚠️ Congés simultanés: Sara El Amrani, Mohamed Tazi (2 personne(s))
```

**Solde limite :**
```
⚠️ Attention: Vous utilisez 8/10 jours disponibles
```

---

## 📊 Indicateurs et statistiques

Sur la page **Congés**, vous voyez :

- **En attente** : Demandes non encore approuvées par le manager
- **Approuvé Manager** : En attente de validation RH
- **Approuvé (Final)** : Congés confirmés
- **Refusé** : Demandes rejetées

Chaque statut affiche le nombre de demandes.

---

## 🛠️ Configuration avancée

### Modifier les règles d'effectif minimum

Fichier : `backend/app/services/leave_validation_service.py`

```python
class LeaveValidationService:
    # Configuration par défaut
    DEFAULT_MIN_TEAM_PRESENCE_PERCENTAGE = 40  # 40% de l'équipe
    DEFAULT_MIN_TEAM_PRESENCE_COUNT = 2        # 2 personnes minimum
    DEFAULT_ADVANCE_NOTICE_DAYS = 14           # 14 jours de préavis
```

### Ajouter des périodes bloquées

Même fichier, méthode `_get_blocked_periods()` :

```python
blocked_periods = [
    ("Clôture annuelle", date(year, 12, 25), date(year + 1, 1, 5)),
    ("Inventaire", date(year, 6, 30), date(year, 7, 2)),
]
```

---

## 💡 Bonnes pratiques

### Pour les employés
1. ✅ Demandez vos congés **au moins 2 semaines à l'avance**
2. ✅ Vérifiez le calendrier de votre équipe avant de demander
3. ✅ Consultez votre solde de congés régulièrement

### Pour les managers
1. ✅ Consultez les **avertissements** avant d'approuver
2. ✅ Communiquez avec votre équipe sur la planification
3. ✅ Validez ou rejetez rapidement (max 48h)

### Pour les RH
1. ✅ Surveillez les demandes en attente (`manager_approved`)
2. ✅ Vérifiez les tendances de congés par département
3. ✅ Ajustez les règles si nécessaire selon l'activité

---

## 📞 Support

Si vous avez des questions sur :
- La configuration des équipes
- L'activation de la gestion par manager
- La modification des règles de validation

Contactez l'administrateur système.
