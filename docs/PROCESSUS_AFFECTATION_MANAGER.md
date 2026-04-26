# 📋 Processus d'Affectation d'Équipe au Manager

## 🎯 Vue d'Ensemble

Dans votre application HR Analytics, l'affectation d'employés à un manager se fait via le champ **`manager_id`** dans la table `employees`.

---

## 🏗️ Architecture du Modèle

### Modèle Employee (Self-Referential)

```sql
employees
├── id (Primary Key)
├── first_name
├── last_name
├── email
├── department_id  → Département de l'employé
└── manager_id     → Référence à employees.id (son manager)
```

**Exemple concret** :
```
┌─────────────────────────────────────────┐
│ KARIM (Manager)                         │
│ - employee_id: 269                      │
│ - manager_id: NULL  ← Pas de manager    │
└─────────────────────────────────────────┘
           ↑
           │ manager_id = 269
           │
┌─────────────────────────────────────────┐
│ FATIMA (Employée)                       │
│ - employee_id: 2                        │
│ - manager_id: 269  ← Rapporte à Karim  │
└─────────────────────────────────────────┘
```

---

## 🔧 Méthodes d'Affectation

### **Méthode 1: Lors de la Création d'un Nouvel Employé**

**Endpoint**: `POST /api/v1/employees/`

```json
{
  "first_name": "Mohamed",
  "last_name": "Bennani",
  "email": "mohamed.bennani@soprahr.com",
  "phone": "+212 6 12 34 56 78",
  "hire_date": "2026-02-23",
  "department_id": 5,
  "manager_id": 269,  ← Assigner Karim comme manager dès la création
  "position": "Développeur",
  "salary": 12000,
  "employment_status": "active"
}
```

✅ **Résultat** : Mohamed est automatiquement ajouté à l'équipe de Karim

---

### **Méthode 2: Modification d'un Employé Existant**

**Endpoint**: `PUT /api/v1/employees/{employee_id}`

```json
{
  "manager_id": 269  ← Changer/Assigner le manager
}
```

**Exemple Python** :
```python
import httpx

# Se connecter
token_response = httpx.post(
    "http://127.0.0.1:8000/api/v1/auth/login",
    data={"username": "admin@soprahr.com", "password": "admin123456789"}
)
token = token_response.json()["access_token"]

# Assigner l'employé ID 10 à Karim (manager_id 269)
response = httpx.put(
    "http://127.0.0.1:8000/api/v1/employees/10",
    headers={"Authorization": f"Bearer {token}"},
    json={"manager_id": 269}
)

print(response.status_code)  # 200 si succès
```

---

### **Méthode 3: Via SQL Direct (Migration de données)**

**Script SQL** :
```sql
-- Assigner plusieurs employés à Karim d'un coup
UPDATE employees 
SET manager_id = 269 
WHERE id IN (2, 5, 10, 15, 20);

-- Assigner tous les employés d'un département à un manager
UPDATE employees 
SET manager_id = 269 
WHERE department_id = 5 AND manager_id IS NULL;

-- Vérifier l'équipe de Karim
SELECT id, first_name, last_name, email, manager_id
FROM employees
WHERE manager_id = 269;
```

---

### **Méthode 4: Via l'Interface Web** (Si implémentée)

1. Aller sur http://localhost:3000/employees
2. Cliquer sur un employé
3. Cliquer "✏️ Modifier"
4. Dans le champ "Manager", sélectionner "Karim Alaoui"
5. Cliquer "Sauvegarder"

---

## 📊 Impact sur le Dashboard et les Fonctionnalités

### 1️⃣ **Dashboard du Manager**

Quand Karim se connecte :
```
📊 Dashboard - Karim (Manager)
┌────────────────────────────────┐
│ Total Employés:  1             │  ← Fatima
│ Employés Actifs: 1             │
│ Congés en attente: 3           │  ← Demandes de Fatima
│ Départements: 1                │
└────────────────────────────────┘
```

**Code Backend** (déjà implémenté) :
```python
# backend/app/api/v1/endpoints/analytics.py (ligne 60-90)

# Trouver tous les employés qui reportent à ce manager
team_employees = db.query(Employee).filter(
    Employee.manager_id == current_user.employee_id
).all()

team_ids = [emp.id for emp in team_employees]
team_count = len(team_employees)
```

---

### 2️⃣ **Gestion des Congés**

**Filtrage automatique** :
- Manager voit **SEULEMENT** les demandes de congé de son équipe
- Basé sur `manager_id` de l'employé

```python
# backend/app/api/v1/endpoints/leaves.py (ligne 156-195)

# Récupérer l'équipe du manager
team_employees = db.query(Employee.id).filter(
    Employee.manager_id == current_user.employee_id  ← Filtrage par manager
).all()

employee_ids_filter = [emp.id for emp in team_employees]

# Filtrer les congés
leaves = query.filter(
    LeaveRequest.employee_id.in_(employee_ids_filter)
).all()
```

---

### 3️⃣ **Notifications**

Les notifications sont envoyées **automatiquement** au bon manager :

```python
# backend/app/crud/notification.py

def notify_leave_to_managers(db: Session, leave_request):
    # Récupérer l'employé
    employee = db.query(Employee).filter(
        Employee.id == leave_request.employee_id
    ).first()
    
    if employee and employee.manager_id:
        # Trouver le user associé au manager
        manager_user = db.query(User).filter(
            User.employee_id == employee.manager_id  ← Basé sur manager_id
        ).first()
        
        # Créer la notification
        notification = Notification(
            user_id=manager_user.id,
            type=NotificationType.leave_request,
            message=f"{employee.first_name} a demandé un congé"
        )
```

---

## 🔍 Vérification de l'Affectation

### Via API (Dashboard Stats)

```bash
# Se connecter en tant que Karim
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=karim.alaoui@soprahr.com&password=password123"

# Récupérer les stats (avec le token)
curl http://127.0.0.1:8000/api/v1/analytics/dashboard-stats \
  -H "Authorization: Bearer {TOKEN}"

# Réponse:
{
  "role": "manager",
  "total_employees": 1,          ← 1 employé dans l'équipe
  "active_employees": 1,
  "pending_leaves": 3,
  "departments_count": 1,
  "team_employee_ids": [2]       ← ID de Fatima
}
```

### Via SQL Direct

```sql
-- Voir l'équipe de Karim (employee_id 269)
SELECT 
    e.id,
    e.first_name,
    e.last_name,
    e.email,
    e.job_title,
    e.manager_id,
    m.first_name || ' ' || m.last_name AS manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id
WHERE e.manager_id = 269;

-- Résultat:
-- id | first_name | last_name | email                      | manager_id | manager_name
-- 2  | Fatima     | Alaoui    | fatima.alaoui@soprahr.com  | 269        | Karim Alaoui
```

---

## ⚠️ Règles Importantes

| Règle | Description |
|-------|-------------|
| **1 seul manager** | Un employé ne peut avoir qu'un seul manager à la fois |
| **Plusieurs employés** | Un manager peut avoir plusieurs employés dans son équipe |
| **NULL autorisé** | `manager_id` peut être NULL (pour les top managers ou CEO) |
| **Manager doit exister** | Le `manager_id` doit référencer un `employee.id` valide |
| **Changement possible** | On peut changer le manager d'un employé à tout moment |
| **Cascade** | Si un manager est supprimé, décider : SET NULL ou bloquer |

---

## 🎬 Scénario Complet : Créer une Équipe pour un Manager

### Étape 1: Identifier le Manager

```sql
-- Trouver l'employee_id de Karim
SELECT id, first_name, last_name, email 
FROM employees 
WHERE email = 'karim.alaoui@soprahr.com';

-- Résultat: id = 269
```

### Étape 2: Créer/Assigner des Employés

**Option A - Créer un nouvel employé** :
```bash
POST /api/v1/employees/
{
  "first_name": "Yasmine",
  "last_name": "Bennani",
  "email": "yasmine.bennani@soprahr.com",
  "manager_id": 269,  ← Karim
  ...
}
```

**Option B - Modifier des employés existants** :
```sql
UPDATE employees 
SET manager_id = 269 
WHERE id IN (2, 5, 10, 15);  -- Fatima + 3 autres
```

### Étape 3: Vérifier

```bash
# Karim se connecte
# Dashboard affiche: Total Employés = 4
# Congés: Voit les demandes de Fatima, Yasmine, etc.
```

---

## 📈 Résumé du Flux de Données

```
┌─────────────────────────────────────────────┐
│  1. CRÉATION/MODIFICATION EMPLOYÉ           │
│     manager_id = 269 (Karim)                │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  2. BASE DE DONNÉES                         │
│     employees.manager_id = 269              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  3. DASHBOARD STATS (AUTO)                  │
│     SELECT COUNT(*) WHERE manager_id = 269  │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  4. AFFICHAGE FRONTEND                      │
│     Total Employés: 4                       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  5. CONGÉS FILTRÉS                          │
│     WHERE employee_id IN (equipe_ids)       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  6. NOTIFICATIONS AU MANAGER                │
│     Quand employé demande congé             │
└─────────────────────────────────────────────┘
```

---

## ✅ État Actuel de Votre Système

**Déjà implémenté** :
- ✅ Modèle Employee avec `manager_id`
- ✅ Dashboard stats par rôle (manager voit son équipe)
- ✅ Filtrage des congés par équipe
- ✅ Notifications au bon manager
- ✅ Endpoints API complets
- ✅ Validation hiérarchique (manager/HR)

**État de l'équipe de Karim** :
```
Manager: Karim Alaoui (employee_id: 269)
Équipe: 
  - Fatima Alaoui (employee_id: 2)

Total: 1 employé
```

---

## 📝 Pour Ajouter Plus d'Employés à l'Équipe de Karim

### Script SQL rapide :
```sql
-- Exemple: Assigner 5 employés random à Karim
UPDATE employees 
SET manager_id = 269 
WHERE manager_id IS NULL 
  AND id != 269 
LIMIT 5;
```

### Via l'API :
```python
# Script Python pour assigner en masse
import httpx

token = "..." # Token admin

employee_ids_to_assign = [5, 10, 15, 20, 25]  # IDs à assigner

for emp_id in employee_ids_to_assign:
    httpx.put(
        f"http://127.0.0.1:8000/api/v1/employees/{emp_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"manager_id": 269}
    )
    print(f"✅ Employé {emp_id} assigné à Karim")
```

---

**Dernière mise à jour** : 23 février 2026  
**Version** : 1.0
