# Intégration Qlik Sense - Guide rapide

## 🚀 Démarrage rapide

### 1. Tester la connexion Qlik

Avant tout, testez que Qlik Sense Desktop est accessible :

```bash
# Ouvrez ce fichier dans votre navigateur :
http://localhost:3002/qlik-test.html
```

Ce test vérifiera :
- ✅ Connexion au serveur Qlik (localhost:4848)
- ✅ Chargement des bibliothèques Qlik
- ✅ Configuration CORS
- ✅ Accès à QueryHrAnalysis.qvf

### 2. Accéder à la page Qlik

Une fois les tests passés :

```
http://localhost:3002/qlik
```

## 📁 Fichiers créés

### Pages
- `/app/qlik/page.tsx` - Page principale d'intégration Qlik Sense

### Configuration
- `/lib/qlik-objects-config.ts` - Configuration des objets Qlik
- `/types/qlik.d.ts` - Types TypeScript pour Qlik APIs

### Documentation
- `/docs/QLIK_INTEGRATION.md` - Guide complet d'intégration
- `/public/qlik-test.html` - Page de test de connexion

### Navigation
- `/components/MainLayout.tsx` - Ajout du lien "Dashboards Qlik"

## ⚙️ Configuration CORS (Important !)

Pour que l'intégration fonctionne, configurez CORS dans Qlik Desktop :

1. **Fermez Qlik Sense Desktop**

2. **Éditez Settings.ini** :
   - Chemin : `C:\Users\[VotreNom]\AppData\Local\Programs\Qlik\Sense\Engine\Settings.ini`

3. **Ajoutez dans [Settings]** :
   ```ini
   EnableWebSocketCrossOriginRequests=1
   AllowOrigin=*
   ```

4. **Redémarrez Qlik Sense Desktop**

## 🎯 Personnalisation

### Ajouter vos propres visualisations

1. Ouvrez `QueryHrAnalysis.qvf` dans Qlik Desktop
2. Identifiez les IDs de vos graphiques (mode édition → propriétés)
3. Modifiez `/lib/qlik-objects-config.ts` :

```typescript
export const QLIK_OBJECTS = {
  monGraphique: {
    id: 'QV01', // Votre ID réel
    containerId: 'mon-graphique-container',
    title: 'Mon Graphique',
  },
};
```

4. Utilisez dans `/app/qlik/page.tsx` :

```typescript
import { loadAllVisualizations } from '@/lib/qlik-objects-config';

// Dans votre code :
const visualizations = await loadAllVisualizations(app);
```

## 🔍 Débogage

### Problème : "Impossible de se connecter"

**Vérifications :**
- [ ] Qlik Desktop démarré ?
- [ ] Accessible sur http://localhost:4848/hub ?
- [ ] App QueryHrAnalysis.qvf existe ?

**Solution :**
```bash
# Testez l'accès manuel :
curl http://localhost:4848/hub
```

### Problème : "CORS error"

**Solution :**
Suivez les instructions de configuration CORS ci-dessus

### Problème : "Application introuvable"

**Vérifications :**
- [ ] Nom exact : `QueryHrAnalysis.qvf`
- [ ] Emplacement : `Documents\Qlik\Sense\Apps\`

### Problème : "Visualisations vides"

**Solution :**
Ouvrez la console (F12) et vérifiez :
- Les IDs des objets sont corrects
- L'application contient des données
- Pas d'erreurs JavaScript

## 📊 Complémentarité des outils

| Fonctionnalité | Moteur de Requêtes | Dashboards Qlik |
|----------------|-------------------|-----------------|
| Questions ad-hoc | ✅ | ❌ |
| Requêtes SQL | ✅ | ❌ |
| Export rapide | ✅ | ⚠️ |
| Visualisations riches | ⚠️ | ✅ |
| Drill-down | ❌ | ✅ |
| Analyse exploratoire | ⚠️ | ✅ |

**Recommandation :** Utilisez les deux !
- **Moteur de Requêtes** pour les questions rapides et exports
- **Dashboards Qlik** pour l'analyse visuelle approfondie

## 🌐 URLs importantes

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3002 |
| Page Qlik | http://localhost:3002/qlik |
| Page Requêtes | http://localhost:3002/query |
| Test Qlik | http://localhost:3002/qlik-test.html |
| Qlik Hub | http://localhost:4848/hub |
| Qlik App | http://localhost:4848/sense/app/QueryHrAnalysis.qvf |

## 📚 Documentation complète

Pour plus de détails, consultez :
- `/docs/QLIK_INTEGRATION.md` - Guide complet
- `/lib/qlik-objects-config.ts` - Exemples de code

## 🆘 Support

En cas de problème :
1. Lancez le test : http://localhost:3002/qlik-test.html
2. Vérifiez la console navigateur (F12)
3. Consultez `/docs/QLIK_INTEGRATION.md`

## ✨ Prochaines étapes

- [ ] Tester la connexion avec qlik-test.html
- [ ] Configurer CORS si nécessaire
- [ ] Accéder à /qlik
- [ ] Identifier vos graphiques dans QueryHrAnalysis.qvf
- [ ] Personnaliser les visualisations dans qlik-objects-config.ts
- [ ] Créer des layouts personnalisés
