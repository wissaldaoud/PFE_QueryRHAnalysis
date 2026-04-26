/**
 * Code Snippets - Design System Components
 * Copy-paste ready examples for common patterns
 */

// ============================================
// 1. MODERN GRADIENT HEADER
// ============================================

export function GradientHeader() {
  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-violet-600 to-purple-700">
      {/* Decorative orbs */}
      <div className="absolute inset-0">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-500/30 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-500/30 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto px-6 py-12">
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 bg-white/10 backdrop-blur-sm rounded-2xl">
            <Brain className="w-8 h-8 text-white" strokeWidth={2} />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">
              Votre Titre
            </h1>
            <p className="text-indigo-100 text-lg">
              Votre sous-titre
            </p>
          </div>
        </div>

        {/* Stats Pills */}
        <div className="flex flex-wrap gap-3">
          <div className="px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20">
            <p className="text-sm text-white font-medium flex items-center gap-2">
              <Users className="w-4 h-4" />
              1,234 employés
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================
// 2. ALERT BANNERS (Success, Warning, Error)
// ============================================

export function AlertBanner({ type, title, message }: {
  type: 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
}) {
  const config = {
    success: {
      bg: 'bg-emerald-50 dark:bg-emerald-900/20',
      border: 'border-emerald-200 dark:border-emerald-800/50',
      icon: 'text-emerald-600 dark:text-emerald-400',
      iconBg: 'bg-emerald-100 dark:bg-emerald-900/30',
      title: 'text-emerald-900 dark:text-emerald-300',
      text: 'text-emerald-700 dark:text-emerald-400',
      Icon: CheckCircle2,
    },
    warning: {
      bg: 'bg-amber-50 dark:bg-amber-900/20',
      border: 'border-amber-200 dark:border-amber-800/50',
      icon: 'text-amber-600 dark:text-amber-400',
      iconBg: 'bg-amber-100 dark:bg-amber-900/30',
      title: 'text-amber-900 dark:text-amber-300',
      text: 'text-amber-700 dark:text-amber-400',
      Icon: AlertCircle,
    },
    error: {
      bg: 'bg-rose-50 dark:bg-rose-900/20',
      border: 'border-rose-200 dark:border-rose-800/50',
      icon: 'text-rose-600 dark:text-rose-400',
      iconBg: 'bg-rose-100 dark:bg-rose-900/30',
      title: 'text-rose-900 dark:text-rose-300',
      text: 'text-rose-700 dark:text-rose-400',
      Icon: AlertTriangle,
    },
    info: {
      bg: 'bg-blue-50 dark:bg-blue-900/20',
      border: 'border-blue-200 dark:border-blue-800/50',
      icon: 'text-blue-600 dark:text-blue-400',
      iconBg: 'bg-blue-100 dark:bg-blue-900/30',
      title: 'text-blue-900 dark:text-blue-300',
      text: 'text-blue-700 dark:text-blue-400',
      Icon: Info,
    },
  }[type];

  const { Icon } = config;

  return (
    <div className={`${config.bg} border-2 ${config.border} rounded-2xl p-6`}>
      <div className="flex items-start gap-4">
        <div className={`p-2 ${config.iconBg} rounded-lg`}>
          <Icon className={`w-5 h-5 ${config.icon}`} />
        </div>
        <div>
          <p className={`font-semibold ${config.title} mb-1`}>{title}</p>
          <p className={`text-sm ${config.text}`}>{message}</p>
        </div>
      </div>
    </div>
  );
}

// Usage:
// <AlertBanner type="success" title="Succès" message="Analyse terminée avec succès" />

// ============================================
// 3. MODERN INPUT FIELD
// ============================================

export function InputField({ label, icon: Icon, ...props }: {
  label: string;
  icon?: LucideIcon;
  type?: string;
  placeholder?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}) {
  return (
    <div>
      <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
        {label}
      </label>
      <div className="relative">
        {Icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
            <Icon className="w-5 h-5" strokeWidth={2} />
          </div>
        )}
        <input
          {...props}
          className={`
            w-full ${Icon ? 'pl-11' : 'pl-4'} pr-4 py-3
            bg-slate-50 dark:bg-slate-800
            border-2 border-slate-200 dark:border-slate-700
            rounded-xl
            text-slate-900 dark:text-white
            placeholder:text-slate-400
            focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500
            transition-all duration-200
          `}
        />
      </div>
    </div>
  );
}

// Usage:
// <InputField label="Nom" icon={User} placeholder="John Doe" value={name} onChange={setName} />

// ============================================
// 4. SELECT DROPDOWN (Modern)
// ============================================

export function SelectField({ label, options, value, onChange }: {
  label: string;
  options: { value: string; label: string }[];
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div>
      <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
        {label}
      </label>
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className={`
            w-full px-4 py-3
            bg-slate-50 dark:bg-slate-800
            border-2 border-slate-200 dark:border-slate-700
            rounded-xl
            text-slate-900 dark:text-white
            focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500
            transition-all duration-200
            appearance-none
            cursor-pointer
          `}
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" />
      </div>
    </div>
  );
}

// ============================================
// 5. BUTTON VARIANTS
// ============================================

export function ButtonPrimary({ children, loading, ...props }: {
  children: React.ReactNode;
  loading?: boolean;
  disabled?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      {...props}
      disabled={loading || props.disabled}
      className={`
        px-6 py-3
        bg-gradient-to-r from-indigo-600 to-violet-600
        text-white font-semibold
        rounded-xl
        hover:from-indigo-700 hover:to-violet-700
        disabled:opacity-50 disabled:cursor-not-allowed
        transition-all duration-200
        flex items-center justify-center gap-2
        shadow-lg shadow-indigo-500/30
        hover:shadow-xl hover:shadow-indigo-500/50
      `}
    >
      {loading ? (
        <>
          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          Chargement...
        </>
      ) : (
        children
      )}
    </button>
  );
}

export function ButtonSecondary({ children, ...props }: {
  children: React.ReactNode;
  onClick?: () => void;
}) {
  return (
    <button
      {...props}
      className={`
        px-6 py-3
        bg-white dark:bg-slate-800
        border-2 border-slate-200 dark:border-slate-700
        text-slate-900 dark:text-white
        font-semibold
        rounded-xl
        hover:border-slate-300 dark:hover:border-slate-600
        hover:bg-slate-50 dark:hover:bg-slate-700
        transition-all duration-200
        flex items-center justify-center gap-2
      `}
    >
      {children}
    </button>
  );
}

export function ButtonGhost({ children, ...props }: {
  children: React.ReactNode;
  onClick?: () => void;
}) {
  return (
    <button
      {...props}
      className={`
        px-4 py-2
        text-slate-600 dark:text-slate-400
        font-medium
        rounded-lg
        hover:bg-slate-100 dark:hover:bg-slate-800
        hover:text-slate-900 dark:hover:text-white
        transition-all duration-200
      `}
    >
      {children}
    </button>
  );
}

// ============================================
// 6. STAT CARD (Simple metrics)
// ============================================

export function StatCard({ label, value, icon: Icon, trend }: {
  label: string;
  value: string | number;
  icon: LucideIcon;
  trend?: { value: number; up: boolean };
}) {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 hover:shadow-lg transition-shadow duration-300">
      <div className="flex items-start justify-between mb-4">
        <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg">
          <Icon className="w-5 h-5 text-slate-600 dark:text-slate-400" />
        </div>
        {trend && (
          <span className={`text-xs font-medium px-2 py-1 rounded-md ${
            trend.up 
              ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400'
              : 'bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-400'
          }`}>
            {trend.up ? '↑' : '↓'} {trend.value}%
          </span>
        )}
      </div>
      <p className="text-2xl font-bold text-slate-900 dark:text-white mb-1">
        {value}
      </p>
      <p className="text-sm text-slate-600 dark:text-slate-400">
        {label}
      </p>
    </div>
  );
}

// ============================================
// 7. BADGE COMPONENT
// ============================================

export function Badge({ children, variant = 'default' }: {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
}) {
  const variants = {
    default: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300',
    success: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400',
    warning: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400',
    danger: 'bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-400',
    info: 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400',
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-semibold ${variants[variant]}`}>
      {children}
    </span>
  );
}

// ============================================
// 8. EMPTY STATE
// ============================================

export function EmptyState({ icon: Icon, title, description, action }: {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-700 p-12 text-center">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-800 mb-4">
        <Icon className="w-8 h-8 text-slate-400" />
      </div>
      <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
        {title}
      </h3>
      <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md mx-auto mb-6">
        {description}
      </p>
      {action}
    </div>
  );
}

// ============================================
// 9. PROGRESS BAR
// ============================================

export function ProgressBar({ value, max = 100, variant = 'indigo' }: {
  value: number;
  max?: number;
  variant?: 'indigo' | 'emerald' | 'amber' | 'rose';
}) {
  const percentage = (value / max) * 100;
  
  const gradients = {
    indigo: 'from-indigo-500 to-violet-500',
    emerald: 'from-emerald-500 to-teal-500',
    amber: 'from-amber-500 to-orange-500',
    rose: 'from-rose-500 to-red-500',
  };

  return (
    <div className="w-full">
      <div className="flex justify-between text-sm mb-2">
        <span className="font-medium text-slate-700 dark:text-slate-300">Progression</span>
        <span className="font-semibold text-slate-900 dark:text-white">{value}/{max}</span>
      </div>
      <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full bg-gradient-to-r ${gradients[variant]} transition-all duration-500 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

// ============================================
// 10. SKELETON LOADERS
// ============================================

export function SkeletonCard() {
  return (
    <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="w-12 h-12 bg-slate-200 dark:bg-slate-800 rounded-lg animate-pulse" />
        <div className="w-16 h-6 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
      </div>
      <div className="w-24 h-8 bg-slate-200 dark:bg-slate-800 rounded animate-pulse mb-2" />
      <div className="w-32 h-4 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
    </div>
  );
}

export function SkeletonText({ lines = 3 }: { lines?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 bg-slate-200 dark:bg-slate-800 rounded animate-pulse"
          style={{ width: i === lines - 1 ? '60%' : '100%' }}
        />
      ))}
    </div>
  );
}

// ============================================
// 11. TOOLTIP (Simple hover)
// ============================================

export function Tooltip({ children, text }: {
  children: React.ReactNode;
  text: string;
}) {
  return (
    <div className="group relative inline-block">
      {children}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1.5 bg-slate-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-200 whitespace-nowrap">
        {text}
        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-slate-900" />
      </div>
    </div>
  );
}

// Usage:
// <Tooltip text="Cliquez pour analyser">
//   <button>Analyser</button>
// </Tooltip>

// ============================================
// 12. MODAL (Simple)
// ============================================

export function Modal({ isOpen, onClose, title, children }: {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl max-w-lg w-full p-6 animate-in fade-in slide-in-from-top-4 duration-200">
        <div className="flex items-start justify-between mb-4">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            {title}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-slate-500" />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

// ============================================
// EXPORT ALL
// ============================================

export {
  GradientHeader,
  AlertBanner,
  InputField,
  SelectField,
  ButtonPrimary,
  ButtonSecondary,
  ButtonGhost,
  StatCard,
  Badge,
  EmptyState,
  ProgressBar,
  SkeletonCard,
  SkeletonText,
  Tooltip,
  Modal,
};
