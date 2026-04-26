# 🔑 Guide de Configuration Keycloak - Query HR Analytics Online

## 1. Démarrer Keycloak

### Option A: Avec Docker (Recommandé)
```bash
docker-compose -f docker-compose.keycloak.yml up -d
```

### Option B: Sans Docker (Télécharger Keycloak)
1. Télécharger: https://www.keycloak.org/downloads
2. Extraire et exécuter:
```bash
bin/kc.sh start-dev   # Linux/Mac
bin\kc.bat start-dev  # Windows
```

## 2. Accéder à Keycloak

- **URL**: http://localhost:8080
- **Admin Console**: http://localhost:8080/admin
- **Login**: admin / admin

## 3. Créer le Realm "hr-analytics"

1. Cliquer sur "Create Realm"
2. Nom: `hr-analytics`
3. Cliquer "Create"

## 4. Créer le Client "hr-analytics-app"

1. Aller dans: Clients → Create client
2. **Client ID**: `hr-analytics-app`
3. **Client Type**: OpenID Connect
4. Cliquer "Next"

### Configuration du Client:
```
Client authentication: ON
Authorization: ON
Standard flow: ON (Authorization Code Flow)
Direct access grants: ON (Password grant)
```

### Access Settings:
```
Root URL: http://localhost:3000
Home URL: http://localhost:3000
Valid redirect URIs: 
  - http://localhost:3000/*
  - http://localhost:8000/*
  - http://127.0.0.1:3000/*
  - http://127.0.0.1:8000/*
Web origins: 
  - http://localhost:3000
  - http://localhost:8000
```

5. Sauvegarder et aller dans l'onglet "Credentials"
6. Copier le **Client Secret** dans le fichier `.env`:
```
KEYCLOAK_CLIENT_SECRET=votre_client_secret_ici
```

## 5. Créer les Rôles

### Rôles du Realm:
1. Aller dans: Realm roles → Create role
2. Créer ces rôles:
   - `admin` - Administrateur système
   - `hr_manager` - Manager RH
   - `analyst` - Analyste données
   - `employee` - Employé standard

### Rôles du Client (optionnel):
1. Clients → hr-analytics-app → Roles
2. Créer les mêmes rôles si besoin

## 6. Créer des Utilisateurs de Test

1. Aller dans: Users → Add user
2. Créer ces utilisateurs:

### Admin
```
Username: admin.soprahr
Email: admin@soprahr.ma
First name: Admin
Last name: SOPRAHR
Email verified: ON
```
Credentials → Set password: `Admin123!` (Temporary: OFF)
Role mapping → Assign role → admin

### HR Manager
```
Username: rh.manager
Email: rh@soprahr.ma
First name: Fatima
Last name: AMRANI
```
Password: `Manager123!`
Role: hr_manager

### Analyst
```
Username: analyst
Email: analyst@soprahr.ma
First name: Omar
Last name: BENJELLOUN
```
Password: `Analyst123!`
Role: analyst

### Employee
```
Username: employee
Email: employee@soprahr.ma
First name: Ahmed
Last name: TAZI
```
Password: `Employee123!`
Role: employee

## 7. Configuration du Backend

### Mettre à jour .env:
```env
# Keycloak Configuration
KEYCLOAK_SERVER_URL=http://localhost:8080
KEYCLOAK_REALM=hr-analytics
KEYCLOAK_CLIENT_ID=hr-analytics-app
KEYCLOAK_CLIENT_SECRET=votre_secret_ici
```

## 8. Tester l'Authentification

### Via Swagger UI:
1. Aller sur http://localhost:8000/docs
2. Trouver la section "Keycloak SSO 🔑"
3. Tester `/auth/keycloak/config`
4. Tester `/auth/keycloak/login`

### Via cURL:
```bash
# 1. Obtenir la configuration
curl http://localhost:8000/api/v1/auth/keycloak/config

# 2. Login direct (Resource Owner Password Grant)
curl -X POST http://localhost:8080/realms/hr-analytics/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=hr-analytics-app" \
  -d "client_secret=VOTRE_SECRET" \
  -d "username=admin.soprahr" \
  -d "password=Admin123!"
```

## 9. Flux OAuth2 (Frontend)

### Authorization Code Flow:
```javascript
// 1. Rediriger vers Keycloak
const response = await fetch('/api/v1/auth/keycloak/login?redirect_uri=http://localhost:3000/callback');
const { authorization_url, state } = await response.json();
window.location.href = authorization_url;

// 2. Callback (après login Keycloak)
const urlParams = new URLSearchParams(window.location.search);
const code = urlParams.get('code');
const state = urlParams.get('state');

const tokenResponse = await fetch('/api/v1/auth/keycloak/callback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    code: code,
    state: state,
    redirect_uri: 'http://localhost:3000/callback'
  })
});

const { access_token, user } = await tokenResponse.json();
// Stocker le token et les infos utilisateur
```

## 10. Architecture de Sécurité

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│    Frontend     │─────▶│    Keycloak     │◀─────│   Backend API   │
│   (React/Vue)   │      │    (OIDC/SSO)   │      │   (FastAPI)     │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
        │                        │                        │
        │    Authorization       │    Token               │
        │    Code Flow           │    Verification        │
        │                        │                        │
        └────────────────────────┴────────────────────────┘
```

## 11. Points Importants pour le PFE

### Avantages de Keycloak:
- ✅ Open Source (Apache 2.0)
- ✅ SSO Enterprise-grade
- ✅ Support OIDC, OAuth2, SAML 2.0
- ✅ Gestion centralisée des utilisateurs
- ✅ MFA / 2FA intégré
- ✅ Federation d'identités (LDAP, Active Directory)
- ✅ Social Login (Google, Facebook, etc.)
- ✅ Audit Logs intégrés

### Pour la présentation:
1. Montrer la console admin Keycloak
2. Démontrer le flux de login SSO
3. Expliquer le RBAC avec les rôles
4. Montrer les audit logs
5. Parler de la scalabilité (clustering)

## 12. Commandes Utiles

```bash
# Démarrer Keycloak
docker-compose -f docker-compose.keycloak.yml up -d

# Voir les logs
docker logs -f hr-analytics-keycloak

# Arrêter Keycloak
docker-compose -f docker-compose.keycloak.yml down

# Réinitialiser (supprimer les données)
docker-compose -f docker-compose.keycloak.yml down -v
```
