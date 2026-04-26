# Intégration Qlik Sense - QueryHrAnalysis.qvf

## Configuration requise

### 1. Qlik Sense Desktop
- Qlik Sense Desktop doit être installé et en cours d'exécution
- Par défaut, il écoute sur `http://localhost:4848`
- L'application **QueryHrAnalysis.qvf** doit être présente dans Qlik Sense Desktop

### 2. Configuration CORS (Important !)

Pour permettre à votre frontend Next.js d'accéder à Qlik Sense Desktop, vous devez configurer CORS :

#### Option 1 : Désactiver CORS dans Qlik Desktop (Développement uniquement)
1. Fermez Qlik Sense Desktop
2. Éditez le fichier `Settings.ini` :
   - Chemin Windows : `C:\Users\[VotreNom]\AppData\Local\Programs\Qlik\Sense\Engine\Settings.ini`
3. Ajoutez ces lignes dans la section `[Settings]` :
   ```ini
   EnableWebSocketCrossOriginRequests=1
   AllowOrigin=*
   ```
4. Redémarrez Qlik Sense Desktop

#### Option 2 : Utiliser un proxy (Production)
Configurez un proxy qui ajoute les en-têtes CORS appropriés.

### 3. Accéder à l'application

Une fois configuré :
1. Démarrez Qlik Sense Desktop
2. Assurez-vous que **QueryHrAnalysis.qvf** est ouvert dans Qlik
3. Allez sur : `http://localhost:3002/qlik` dans votre application

## Utilisation de l'intégration

### Page créée : `/qlik`

La page utilise **Qlik Capability APIs** pour :
- Charger l'application QueryHrAnalysis.qvf
- Afficher les sélections courantes
- Permettre l'interaction avec les visualisations
- Ouvrir l'application complète dans Qlik Sense

### Fonctionnalités disponibles

1. **Visualisations embarquées** : Les graphiques Qlik sont intégrés dans la page
2. **Sélections interactives** : Cliquez sur les éléments pour filtrer
3. **Barre de sélections** : Voir et gérer les filtres actifs
4. **Lien vers Qlik Hub** : Bouton pour ouvrir l'app complète

### Personnalisation

Pour ajouter des visualisations spécifiques de votre application :

1. Ouvrez `frontend/app/qlik/page.tsx`
2. Dans la fonction `initializeQlik`, ajoutez vos objets Qlik :

```typescript
// Exemple : Ajouter un graphique spécifique
app.visualization.create(
  'QV01', // ID de votre objet dans Qlik
  [],
  { noInteraction: false }
).then((vis: any) => {
  const container = document.getElementById('chart-container-1');
  if (container) vis.show(container);
});
```

3. Pour trouver les IDs des objets :
   - Ouvrez QueryHrAnalysis.qvf dans Qlik Sense Desktop
   - En mode édition, cliquez sur un graphique
   - L'ID apparaît dans les propriétés

## Dépannage

### "Impossible de se connecter à Qlik Sense Desktop"
- Vérifiez que Qlik Desktop est bien démarré
- Vérifiez l'URL : `http://localhost:4848`
- Testez l'accès dans le navigateur : `http://localhost:4848/hub`

### "CORS error"
- Suivez la configuration CORS ci-dessus
- Redémarrez Qlik Desktop après modification

### "Application introuvable"
- Vérifiez le nom exact : **QueryHrAnalysis.qvf**
- L'application doit être dans : `Documents\Qlik\Sense\Apps\`

### Les visualisations ne s'affichent pas
- Ouvrez la console navigateur (F12)
- Vérifiez les erreurs JavaScript
- Assurez-vous que l'application contient des feuilles et objets

## Architecture de l'intégration

```
Frontend Next.js (localhost:3002)
    ↓
Qlik Capability APIs (require.js)
    ↓
Qlik Sense Desktop (localhost:4848)
    ↓
QueryHrAnalysis.qvf
```

## Complémentarité avec le Moteur de Requêtes

- **Moteur de Requêtes** (`/query`) : Questions ad-hoc, exports rapides, requêtes SQL
- **Dashboards Qlik** (`/qlik`) : Visualisations riches, drill-down, analyse exploratoire

Les deux outils se complètent pour offrir une solution d'analytics complète !

## URLs importantes

- Frontend : `http://localhost:3002`
- Page Qlik : `http://localhost:3002/qlik`
- Page Requêtes : `http://localhost:3002/query`
- Qlik Desktop Hub : `http://localhost:4848/hub`
- Qlik App directe : `http://localhost:4848/sense/app/QueryHrAnalysis.qvf`

## Prochaines étapes recommandées

1. Identifier les visualisations clés de votre app Qlik
2. Ajouter leurs IDs dans le code pour les embarquer
3. Créer des layouts personnalisés
4. Ajouter des filtres prédéfinis pour l'utilisateur
5. Synchroniser avec le Moteur de Requêtes (ex: lancer une requête depuis Qlik)
