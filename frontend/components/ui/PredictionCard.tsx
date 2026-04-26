/**
 * Prediction Card Component - Hero Result Display
 * Design System pour affichage des résultats de prédiction
 */

import { AlertTriangle, CheckCircle2, AlertCircle } from "lucide-react";

interface PredictionCardProps {
  probability: number;
  riskLevel: "faible" | "moyen" | "élevé";
  prediction: 0 | 1;
  className?: string;
}

const riskConfig = {
  faible: {
    label: "Risque Faible",
    emoji: "✅",
    gradient: "from-emerald-500 to-teal-500",
    bgGradient: "from-emerald-50 to-teal-50 dark:from-emerald-950/30 dark:to-teal-950/30",
    border: "border-emerald-200 dark:border-emerald-800/50",
    icon: CheckCircle2,
    iconColor: "text-emerald-600 dark:text-emerald-400",
    textColor: "text-emerald-900 dark:text-emerald-100",
    badgeBg: "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300",
  },
  moyen: {
    label: "Risque Moyen",
    emoji: "⚠️",
    gradient: "from-amber-500 to-orange-500",
    bgGradient: "from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30",
    border: "border-amber-200 dark:border-amber-800/50",
    icon: AlertCircle,
    iconColor: "text-amber-600 dark:text-amber-400",
    textColor: "text-amber-900 dark:text-amber-100",
    badgeBg: "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300",
  },
  élevé: {
    label: "Risque Élevé",
    emoji: "🚨",
    gradient: "from-rose-500 to-red-500",
    bgGradient: "from-rose-50 to-red-50 dark:from-rose-950/30 dark:to-red-950/30",
    border: "border-rose-200 dark:border-rose-800/50",
    icon: AlertTriangle,
    iconColor: "text-rose-600 dark:text-rose-400",
    textColor: "text-rose-900 dark:text-rose-100",
    badgeBg: "bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300",
  },
};

export default function PredictionCard({
  probability,
  riskLevel,
  prediction,
  className = "",
}: PredictionCardProps) {
  const config = riskConfig[riskLevel];
  const Icon = config.icon;

  return (
    <div
      className={`
        relative overflow-hidden
        rounded-2xl border-2 ${config.border}
        bg-gradient-to-br ${config.bgGradient}
        p-8
        transition-all duration-500
        hover:shadow-2xl hover:shadow-slate-300/50 dark:hover:shadow-black/50
        ${className}
      `}
    >
      {/* Decorative gradient orb */}
      <div
        className={`
          absolute -top-20 -right-20 w-64 h-64 
          bg-gradient-to-br ${config.gradient} 
          rounded-full blur-3xl opacity-10
        `}
      />

      <div className="relative z-10">
        {/* Header avec emoji et badge */}
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-4">
            <div
              className={`
                text-5xl
                animate-bounce-subtle
              `}
            >
              {config.emoji}
            </div>
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
                Résultat de l'Analyse
              </p>
              <h2 className={`text-2xl font-bold ${config.textColor}`}>
                {config.label}
              </h2>
            </div>
          </div>

          {/* Icon badge */}
          <div
            className={`
              p-3 rounded-xl
              ${config.badgeBg}
              transition-transform duration-300 hover:scale-110
            `}
          >
            <Icon className={`w-6 h-6 ${config.iconColor}`} strokeWidth={2.5} />
          </div>
        </div>

        {/* Probabilité - Grand affichage */}
        <div className="mb-6">
          <div className="flex items-baseline gap-2">
            <span className={`text-6xl font-bold tracking-tight ${config.textColor}`}>
              {probability.toFixed(1)}
            </span>
            <span className={`text-3xl font-semibold ${config.textColor} opacity-70`}>
              %
            </span>
          </div>
          <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mt-2">
            Probabilité de départ
          </p>
        </div>

        {/* Barre de progression */}
        <div className="mb-6">
          <div className="h-3 bg-white/50 dark:bg-slate-800/50 rounded-full overflow-hidden backdrop-blur-sm">
            <div
              className={`
                h-full rounded-full
                bg-gradient-to-r ${config.gradient}
                transition-all duration-1000 ease-out
              `}
              style={{ width: `${probability}%` }}
            />
          </div>
        </div>

        {/* Prédiction binaire */}
        <div
          className={`
            flex items-center gap-3 px-4 py-3 rounded-lg
            bg-white/70 dark:bg-slate-800/70 backdrop-blur-sm
            border ${config.border}
          `}
        >
          <div
            className={`
              w-2 h-2 rounded-full
              bg-gradient-to-r ${config.gradient}
              animate-pulse
            `}
          />
          <p className={`text-sm font-semibold ${config.textColor}`}>
            {prediction === 1 ? (
              <span>L'employé présente des signes de départ potentiel</span>
            ) : (
              <span>L'employé devrait rester dans l'organisation</span>
            )}
          </p>
        </div>

        {/* Timestamp subtil */}
        <div className="mt-6 pt-4 border-t border-slate-200/50 dark:border-slate-700/50">
          <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
            <span className="inline-block w-1 h-1 bg-current rounded-full animate-pulse" />
            Analyse générée par le modèle Gradient Boosting
          </p>
        </div>
      </div>

      {/* Subtle shine effect on hover */}
      <div className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/10 to-white/0 opacity-0 hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
    </div>
  );
}

// Add to global CSS for bounce-subtle animation
// @keyframes bounce-subtle {
//   0%, 100% { transform: translateY(0); }
//   50% { transform: translateY(-5px); }
// }
// .animate-bounce-subtle {
//   animation: bounce-subtle 2s ease-in-out infinite;
// }
