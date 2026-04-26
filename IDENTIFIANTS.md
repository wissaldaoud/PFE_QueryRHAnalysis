# 🔑 IDENTIFIANTS DE CONNEXION

## Comptes vérifiés et fonctionnels

### 1. Compte Administrateur
- **Email:** admin@soprahr.com
- **Mot de passe:** admin123456789
- **Rôle:** admin

### 2. Compte Employé (pour tester workflow)
- **Email:** fatima.alaoui@soprahr.com
- **Mot de passe:** password123
- **Rôle:** employee

### 3. Compte Manager
- **Email:** karim.alaoui@soprahr.com
- **Mot de passe:** password123
- **Rôle:** manager

---

## ⚠️ Points importants

1. **Utilisez l'EMAIL COMPLET** comme identifiant (pas le username)
2. **Pas d'espaces** avant ou après l'email/mot de passe
3. **Sensible à la casse** - respectez les majuscules/minuscules
4. L'URL du frontend est: http://localhost:3000
5. L'URL du backend est: http://127.0.0.1:8000

---

## 🧪 Test de connexion

Pour tester si un compte fonctionne, vous pouvez utiliser cette commande PowerShell:

```powershell
C:\Users\wdaoud\Desktop\test\backend\env\Scripts\python.exe -c "import httpx; r = httpx.post('http://127.0.0.1:8000/api/v1/auth/login', data={'username':'admin@soprahr.com','password':'admin123456789'}); print('Status:', r.status_code); print(r.json() if r.status_code == 200 else r.text)"
```

---

## 🔄 Workflow de test des congés

1. Connectez-vous en tant qu'**employé** (fatima.alaoui@soprahr.com)
2. Créez une demande de congé
3. Déconnectez-vous
4. Connectez-vous en tant qu'**admin** (admin@soprahr.com)
5. Approuvez la demande en tant que Manager
6. Approuvez la demande en tant que RH
