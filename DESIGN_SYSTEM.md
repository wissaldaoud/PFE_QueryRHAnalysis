# 🎨 Design System - Application RH Turnover Prediction

## 📋 Vue d'ensemble

Ce document présente le système de design complet pour votre application de prédiction du turnover. Inspiré des meilleurs SaaS modernes (Stripe, Notion, Linear), ce design system assure une expérience utilisateur professionnelle et cohérente.

---

## 🎨 Palette de Couleurs

### Couleurs Principales

```typescript
const colors = {
  // Primaire (Indigo) - Actions, CTAs, Navigation
  primary: {
    50: '#eef2ff',
    100: '#e0e7ff',
    500: '#6366f1',  // Main
    600: '#4f46e5',  // Hover
    700: '#4338ca',
  },

  // Neutre (Slate) - Interface générale
  slate: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a',
    950: '#020617',
  },

  // Succès (Emerald) - Risque faible, validation
  success: {
    50: '#ecfdf5',
    100: '#d1fae5',
    500: '#10b981',
    600: '#059669',
  },

  // Warning (Amber) - Risque moyen, attention
  warning: {
    50: '#fffbeb',
    100: '#fef3c7',
    500: '#f59e0b',
    600: '#d97706',
  },

  // Danger (Rose) - Risque élevé, erreurs
  danger: {
    50: '#fff1f2',
    100: '#ffe4e6',
    500: '#f43f5e',
    600: '#e11d48',
  },

  // Accent (Violet) - Highlights spéciaux
  accent: {
    50: '#faf5ff',
    100: '#f3e8ff',
    500: '#8b5cf6',
    600: '#7c3aed',
  },
};
```

### Utilisation

- **Primaire**: Boutons d'action, liens, badges actifs
- **Neutre**: Textes, bordures, backgrounds, cards
- **Succès**: Indicateurs positifs, risque faible
- **Warning**: Alertes, risque moyen
- **Danger**: Erreurs, risque élevé
- **Accent**: Features spéciales, ML/IA

---

## ✏️ Typographie

### Police Système

Utiliser la stack système native pour des performances optimales:

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 
             'Helvetica Neue', 'Ubuntu', sans-serif;
```

### Hiérarchie

```typescript
const typography = {
  // Headers
  h1: 'text-4xl md:text-5xl font-bold tracking-tight',
  h2: 'text-3xl md:text-4xl font-bold tracking-tight',
  h3: 'text-2xl md:text-3xl font-semibold tracking-tight',
  h4: 'text-xl md:text-2xl font-semibold',
  h5: 'text-lg font-semibold',

  // Body
  bodyLarge: 'text-lg',
  body: 'text-base',
  bodySmall: 'text-sm',
  caption: 'text-xs',

  // Poids
  regular: 'font-normal',    // 400
  medium: 'font-medium',     // 500
  semibold: 'font-semibold', // 600
  bold: 'font-bold',         // 700
};
```

### Règles d'utilisation

1. **Headers (h1-h3)**: Toujours en `font-bold` ou `font-semibold`
2. **Body**: `font-normal` ou `font-medium` pour emphase
3. **Labels/Inputs**: `font-medium` (500) pour meilleure lisibilité
4. **Line-height**: 
   - Headers: `leading-tight` (1.25)
   - Body: `leading-normal` (1.5)
   - Captions: `leading-relaxed` (1.625)

---

## 📏 Système d'Espacement

### Scale Tailwind (recommandé)

```typescript
const spacing = {
  xs: '0.5rem',   // 8px  - gaps serrés
  sm: '0.75rem',  // 12px - spacing compact
  md: '1rem',     // 16px - spacing standard
  lg: '1.5rem',   // 24px - sections
  xl: '2rem',     // 32px - grandes sections
  '2xl': '3rem',  // 48px - hero sections
};
```

### Padding Cards

```typescript
const cardPadding = {
  compact: 'p-4',      // Petites cards/badges
  default: 'p-6',      // Cards standards
  comfortable: 'p-8',  // Cards importantes
  spacious: 'p-10',    // Hero cards
};
```

### Gaps & Grids

```css
/* Grids modernes */
.grid-auto-fit {
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

.grid-auto-fill {
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}

/* Gaps standards */
gap-4    /* 16px - KPI grids */
gap-6    /* 24px - Content grids */
gap-8    /* 32px - Section spacing */
```

---

## 🎴 Composants

### 1. KPI Card

**Utilisation**: Affichage métriques clés (âge, ancienneté, absences)

```tsx
<KPICard
  title="Âge"
  value="32 ans"
  subtitle="Calculé depuis date de naissance"
  icon={Calendar}
  variant="default"
  trend={{ value: 5, direction: "up" }}
/>
```

**Variants disponibles**:
- `default`: Neutre (slate)
- `success`: Vert (emerald)
- `warning`: Orange (amber)
- `danger`: Rouge (rose)
- `info`: Bleu (indigo)

**Features**:
- Hover effect (lift + shadow)
- Icon avec animation scale
- Trend badge optionnel
- Gradient overlay subtil

### 2. Prediction Card

**Utilisation**: Résultat principal de prédiction

```tsx
<PredictionCard
  probability={23.5}
  riskLevel="moyen"
  prediction={1}
/>
```

**Features**:
- Gradient background dynamique selon risque
- Barre de progression animée
- Emoji + icon badge
- Glow effect sur hover
- Decorative orb background

### 3. Employee Selector

**Utilisation**: Sélection employé avec recherche

```tsx
<EmployeeSelector
  employees={employees}
  selectedEmployee={selectedEmployee}
  onSelect={handleEmployeeSelect}
  loading={loading}
/>
```

**Features**:
- Combobox moderne avec dropdown
- Recherche en temps réel
- Avatar badges
- Department tags
- Check indicator pour sélection
- Empty state personnalisé

---

## 🎭 Micro-interactions

### Hover States

```css
/* Cards */
hover:shadow-xl hover:-translate-y-0.5
transition-all duration-300

/* Boutons */
hover:scale-105 active:scale-95
transition-transform duration-200

/* Links */
hover:text-indigo-600 hover:underline
underline-offset-2
```

### Loading States

```tsx
// Spinner moderne
<div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />

// Skeleton
<div className="h-4 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
```

### Transitions

```css
/* Standard */
transition-all duration-200 ease-out

/* Smooth */
transition-all duration-300 ease-in-out

/* Slow (backgrounds) */
transition-all duration-500 ease-in-out
```

---

## 🌓 Dark Mode

### Stratégie

Utiliser les classes `dark:` de Tailwind pour tous les éléments:

```tsx
// ✅ BON
className="bg-white dark:bg-slate-900 text-slate-900 dark:text-white"

// ❌ MAUVAIS
className="bg-white text-black"
```

### Palette Dark Mode

```typescript
const darkColors = {
  background: {
    primary: 'slate-950',   // Body
    secondary: 'slate-900', // Cards
    tertiary: 'slate-800',  // Inputs
  },
  text: {
    primary: 'white',
    secondary: 'slate-300',
    tertiary: 'slate-400',
    muted: 'slate-500',
  },
  borders: 'slate-700',
};
```

### Best Practices

1. **Contraste**: Toujours tester lisibilité en dark mode
2. **Ombres**: Utiliser `shadow-black/50` au lieu de `shadow-slate-300`
3. **Opacité**: Préférer `/50`, `/30`, `/20` pour subtilité
4. **Gradients**: Ajuster luminosité (-950 au lieu de -50)

---

## 📐 Layout & Grids

### Page Structure

```tsx
<MainLayout>
  <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
    {/* Hero Header */}
    <header className="bg-gradient-to-br from-indigo-600 to-purple-700 py-12">
      {/* ... */}
    </header>

    {/* Content */}
    <main className="max-w-7xl mx-auto px-6 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sidebar */}
        <aside className="lg:col-span-1 space-y-6">
          {/* ... */}
        </aside>

        {/* Main Content */}
        <section className="lg:col-span-2 space-y-6">
          {/* ... */}
        </section>
      </div>
    </main>
  </div>
</MainLayout>
```

### Responsive Breakpoints

```typescript
const breakpoints = {
  sm: '640px',   // Mobile landscape
  md: '768px',   // Tablet
  lg: '1024px',  // Desktop
  xl: '1280px',  // Large desktop
  '2xl': '1536px', // Extra large
};
```

### Grid Layouts

```tsx
// KPIs (2 cols mobile, 4 cols desktop)
<div className="grid grid-cols-2 md:grid-cols-4 gap-4">

// Content (1 col mobile, 2 cols desktop)
<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

// Dashboard (1 col mobile, 3 cols desktop)
<div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
```

---

## 🎯 Hiérarchie Visuelle

### Priorité 1: Résultat de Prédiction

- Taille: Grande (h-auto, pas de limite)
- Position: Premier élément visible
- Style: Card avec gradient, emoji, large value
- Ombres: `shadow-2xl`

### Priorité 2: KPIs Clés

- Taille: Moyenne (h-fit)
- Position: Grid 2x2 ou 4x1
- Style: Cards propres, icons colorés
- Ombres: `shadow-xl`

### Priorité 3: Détails/Paramètres

- Taille: Standard
- Position: Sidebar ou bottom
- Style: Cards compactes
- Ombres: `shadow-lg`

### Priorité 4: Metadata

- Taille: Petite (text-xs)
- Position: Footer de cards
- Style: Text muted
- Ombres: None

---

## 🔧 Installation & Intégration

### 1. Importer le CSS custom

Dans `app/globals.css`:

```css
@import '../styles/design-system.css';
```

### 2. Remplacer la page turnover

Option A - Remplacer complètement:
```bash
# Backup
mv app/turnover/page.tsx app/turnover/page.old.tsx

# Utiliser nouvelle version
mv app/turnover/page-modern.tsx app/turnover/page.tsx
```

Option B - Tester en parallèle:
```tsx
// Dans navigation, ajouter:
{ name: 'Turnover v2', href: '/turnover-modern', icon: TrendingDown }
```

### 3. Vérifier les dépendances

Assurez-vous d'avoir lucide-react:

```bash
npm install lucide-react
```

### 4. Tester Dark Mode

Dans votre `ThemeToggle` component, vérifier que la classe `dark` est bien ajoutée à `<html>`.

---

## 📱 Responsive Design

### Mobile First

Toujours commencer par mobile, puis ajouter breakpoints:

```tsx
// ✅ BON
<div className="text-sm md:text-base lg:text-lg">

// ❌ MAUVAIS
<div className="lg:text-lg md:text-base text-sm">
```

### Touch Targets

Minimums recommandés:
- Boutons: `min-h-[44px]` (44px Apple HIG)
- Links: `min-h-[40px]`
- Inputs: `min-h-[48px]`

### Spacing Mobile

```tsx
// Desktop: p-8
// Mobile: p-6
className="p-6 lg:p-8"

// Desktop: gap-8
// Mobile: gap-4
className="gap-4 lg:gap-8"
```

---

## ♿ Accessibilité

### Focus States

Toujours visible:

```css
focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:ring-offset-2
```

### ARIA Labels

```tsx
<button aria-label="Lancer l'analyse prédictive">
  <Sparkles className="w-5 h-5" />
</button>
```

### Contraste

Minimum WCAG AA:
- Texte normal: 4.5:1
- Large texte: 3:1
- UI components: 3:1

### Keyboard Navigation

Tous les éléments interactifs doivent être navigables au clavier (tab, enter, espace).

---

## 🚀 Performance

### Optimisations

1. **Images**: Utiliser Next.js `<Image>` avec lazy loading
2. **Animations**: Préférer `transform` et `opacity` (GPU)
3. **Fonts**: Utiliser system fonts (pas de web fonts)
4. **CSS**: Minimiser les classes custom, utiliser Tailwind

### Bundle Size

```bash
# Analyser
npm run build -- --analyze

# Composants à code-split si gros
const HeavyChart = dynamic(() => import('./HeavyChart'), { ssr: false })
```

---

## 📚 Ressources

### Inspirations

- **Stripe**: Typographie, spacing
- **Linear**: Micro-interactions, animations
- **Notion**: Dark mode, hiérarchie
- **Vercel**: Gradients, ombres

### Outils

- **Tailwind Docs**: https://tailwindcss.com
- **Lucide Icons**: https://lucide.dev
- **Coolors**: Palette generator
- **Contrast Checker**: WebAIM

---

## 🎓 Best Practices Résumé

### ✅ À FAIRE

- Utiliser le design system (couleurs, spacing)
- Ajouter hover states partout
- Tester dark mode systématiquement
- Mobile-first approach
- Composants réutilisables
- Transitions subtiles (200-300ms)
- Focus states visibles
- Loading states clairs

### ❌ À ÉVITER

- Couleurs hors palette
- Animations trop longues (>500ms)
- Text trop petit (<12px)
- Padding inconsistant
- Couleurs flashy/aggressive
- Trop de gradients
- Oublier dark mode
- Ignorer responsive

---

## 🔄 Migration Progressive

Pour migrer progressivement votre app:

1. **Phase 1**: Importer design-system.css
2. **Phase 2**: Créer composants UI (KPICard, etc.)
3. **Phase 3**: Refondre page par page
4. **Phase 4**: Uniformiser sidebar/layout
5. **Phase 5**: Audit final accessibilité

---

## 💬 Support

Pour questions ou améliorations, référez-vous à:
- Ce document
- Code source des composants (`components/ui/*`)
- Page exemple (`turnover/page-modern.tsx`)

**Créé avec ❤️ pour un dashboard RH professionnel**
