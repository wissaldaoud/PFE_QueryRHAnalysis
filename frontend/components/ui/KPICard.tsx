/**
 * KPI Card Component - Design System
 * Style inspiré de Linear/Stripe pour dashboards professionnels
 */

import { LucideIcon } from "lucide-react";
import { ReactNode } from "react";

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: {
    value: number;
    direction: "up" | "down";
  };
  variant?: "default" | "success" | "warning" | "danger" | "info";
  className?: string;
}

const variantStyles = {
  default: {
    container: "bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700",
    icon: "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300",
    value: "text-slate-900 dark:text-white",
    title: "text-slate-600 dark:text-slate-400",
  },
  success: {
    container: "bg-white dark:bg-slate-800 border-emerald-200 dark:border-emerald-800/50",
    icon: "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400",
    value: "text-emerald-600 dark:text-emerald-400",
    title: "text-slate-600 dark:text-slate-400",
  },
  warning: {
    container: "bg-white dark:bg-slate-800 border-amber-200 dark:border-amber-800/50",
    icon: "bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400",
    value: "text-amber-600 dark:text-amber-400",
    title: "text-slate-600 dark:text-slate-400",
  },
  danger: {
    container: "bg-white dark:bg-slate-800 border-rose-200 dark:border-rose-800/50",
    icon: "bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400",
    value: "text-rose-600 dark:text-rose-400",
    title: "text-slate-600 dark:text-slate-400",
  },
  info: {
    container: "bg-white dark:bg-slate-800 border-indigo-200 dark:border-indigo-800/50",
    icon: "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400",
    value: "text-indigo-600 dark:text-indigo-400",
    title: "text-slate-600 dark:text-slate-400",
  },
};

export default function KPICard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = "default",
  className = "",
}: KPICardProps) {
  const styles = variantStyles[variant];

  return (
    <div
      className={`
        group relative overflow-hidden
        rounded-xl border
        ${styles.container}
        p-6
        transition-all duration-300
        hover:shadow-lg hover:shadow-slate-200/50 dark:hover:shadow-black/50
        hover:-translate-y-0.5
        ${className}
      `}
    >
      {/* Subtle gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent via-transparent to-slate-50/50 dark:to-slate-900/30 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

      <div className="relative z-10 flex items-start justify-between">
        <div className="flex-1">
          {/* Title */}
          <p className={`text-sm font-medium ${styles.title} mb-3`}>
            {title}
          </p>

          {/* Value */}
          <div className="flex items-baseline gap-3 mb-2">
            <p className={`text-3xl font-semibold tracking-tight ${styles.value}`}>
              {value}
            </p>

            {/* Trend Badge */}
            {trend && (
              <span
                className={`
                  inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium
                  ${
                    trend.direction === "up"
                      ? "bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400"
                      : "bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-400"
                  }
                `}
              >
                <span>{trend.direction === "up" ? "↑" : "↓"}</span>
                <span>{Math.abs(trend.value)}%</span>
              </span>
            )}
          </div>

          {/* Subtitle */}
          {subtitle && (
            <p className="text-sm text-slate-500 dark:text-slate-400">
              {subtitle}
            </p>
          )}
        </div>

        {/* Icon */}
        {Icon && (
          <div
            className={`
              rounded-lg p-3
              ${styles.icon}
              transition-transform duration-300
              group-hover:scale-110
            `}
          >
            <Icon className="w-5 h-5" strokeWidth={2} />
          </div>
        )}
      </div>

      {/* Bottom accent line - subtle animation on hover */}
      <div
        className={`
          absolute bottom-0 left-0 right-0 h-0.5
          bg-gradient-to-r from-transparent via-current to-transparent
          opacity-0 group-hover:opacity-20
          transition-opacity duration-500
          ${styles.value}
        `}
      />
    </div>
  );
}
