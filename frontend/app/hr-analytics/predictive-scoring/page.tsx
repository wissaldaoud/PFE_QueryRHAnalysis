"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import MainLayout from "@/components/MainLayout";
import { ArrowLeft, RefreshCw } from "lucide-react";

interface KeyFactor {
  feature: string;
  shap_value: number;
  direction: string;
}

interface PredictiveScore {
  employee_id: number;
  employee_name: string;
  churn_risk_score: number;
  churn_risk_percent: number;
  risk_level: string;
  action_priority: string;
  performance_score: number;
  engagement_score: number;
  prediction_confidence: number;
  key_factors: KeyFactor[];
  recommendations: string[];
  features_used: any;
  model_version: string;
  computed_at: string;
}

interface EmployeeFromDB {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  full_name: string;
  job_title: string | null;
  department_name: string | null;
  department_id: number | null;
  hire_date: string;
  tenure_months: number;
  employment_status: string;
  email: string | null;
}

// ── Helpers ──────────────────────────────────────────────────────

function getRiskConfig(level: string) {
  const u = level.toUpperCase();
  if (u === "ÉLEVÉ" || u === "ELEVE")
    return {
      short: "ÉLEVÉ",
      context: "Des signaux d'alerte significatifs ont été détectés sur ce profil.",
      textClass: "text-red-700 dark:text-red-400",
      bgClass: "bg-red-50 dark:bg-red-950/20",
      borderClass: "border-red-200 dark:border-red-800/50",
    };
  if (u === "MOYEN")
    return {
      short: "MODÉRÉ",
      context: "Ce profil mérite une attention particulière dans les prochaines semaines.",
      textClass: "text-amber-700 dark:text-amber-400",
      bgClass: "bg-amber-50 dark:bg-amber-950/20",
      borderClass: "border-amber-200 dark:border-amber-800/50",
    };
  return {
    short: "STABLE",
    context: "Aucun signal préoccupant détecté. Situation sous contrôle.",
    textClass: "text-emerald-700 dark:text-emerald-400",
    bgClass: "bg-emerald-50 dark:bg-emerald-950/20",
    borderClass: "border-emerald-200 dark:border-emerald-800/50",
  };
}

// ── Sub-components ───────────────────────────────────────────────

function ScoreRing({
  value,
  label,
  strokeClass,
  textClass,
}: {
  value: number;
  label: string;
  strokeClass: string;
  textClass: string;
}) {
  const r = 30;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(Math.max(value, 0), 100);
  const offset = circ * (1 - pct / 100);

  return (
    <div className="flex flex-col items-center py-5 px-3 bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800">
      <p className="text-[11px] font-medium text-neutral-500 dark:text-neutral-400 mb-3 text-center">
        {label}
      </p>
      <div className="relative" style={{ width: 72, height: 72 }}>
        <svg width="72" height="72" style={{ transform: "rotate(-90deg)" }}>
          <circle
            cx="36" cy="36" r={r} fill="none" strokeWidth="5"
            className="stroke-neutral-100 dark:stroke-neutral-800"
          />
          <circle
            cx="36" cy="36" r={r} fill="none" strokeWidth="5"
            strokeDasharray={circ}
            strokeDashoffset={offset}
            strokeLinecap="butt"
            className={strokeClass}
            style={{ transition: "stroke-dashoffset 0.45s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`text-[19px] font-bold tabular-nums leading-none ${textClass}`}>
            {Math.round(pct)}
          </span>
        </div>
      </div>
    </div>
  );
}

function ShapRow({ factor, maxAbs }: { factor: KeyFactor; maxAbs: number }) {
  const isPos = factor.shap_value > 0;
  const pct = Math.min((Math.abs(factor.shap_value) / maxAbs) * 100, 100);

  return (
    <div className="flex items-center gap-2.5 py-[5px]">
      <span
        className="text-[11px] text-neutral-500 dark:text-neutral-400 w-36 text-right truncate shrink-0"
        title={factor.feature}
      >
        {factor.feature}
      </span>
      <div className="flex-1 relative" style={{ height: 12 }}>
        <div className="absolute top-[5px] bottom-[5px] left-1/2 w-px bg-neutral-200 dark:bg-neutral-700" />
        {isPos ? (
          <div
            className="absolute left-1/2 top-[2px] bottom-[2px] bg-red-500"
            style={{ width: `${pct / 2}%` }}
          />
        ) : (
          <div
            className="absolute top-[2px] bottom-[2px] bg-emerald-600 dark:bg-emerald-500"
            style={{ width: `${pct / 2}%`, right: "50%" }}
          />
        )}
      </div>
      <span
        className={`text-[11px] font-mono w-14 text-right shrink-0 tabular-nums ${
          isPos ? "text-red-600 dark:text-red-400" : "text-emerald-700 dark:text-emerald-400"
        }`}
      >
        {isPos ? "+" : ""}
        {factor.shap_value.toFixed(3)}
      </span>
    </div>
  );
}

// ── Page ─────────────────────────────────────────────────────────

export default function PredictiveScoringPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictiveScore | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [employees, setEmployees] = useState<EmployeeFromDB[]>([]);
  const [loadingEmployees, setLoadingEmployees] = useState(true);
  const [employeesError, setEmployeesError] = useState<string | null>(null);
  const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadEmployees();
  }, []);

  async function loadEmployees() {
    setLoadingEmployees(true);
    setEmployeesError(null);
    try {
      // 🔥 Charger TOUS les employés (pas seulement actifs)
      const response = await fetch("http://localhost:8000/api/v1/hr-analytics/employees?all=true");
      if (!response.ok) throw new Error(`Erreur ${response.status}`);
      setEmployees(await response.json());
    } catch (err: any) {
      setEmployeesError(err.message || "Impossible de charger les employés");
    } finally {
      setLoadingEmployees(false);
    }
  }

  async function loadPredictiveScore(employeeId: number) {
    setLoading(true);
    setError(null);
    setSelectedEmployeeId(employeeId);
    setResult(null);
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/hr-analytics/predictive-scoring/ml/${employeeId}`
      );
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `Erreur ${response.status}`);
      }
      setResult(await response.json());
    } catch (err: any) {
      setError(err.message || "Impossible de charger le scoring");
    } finally {
      setLoading(false);
    }
  }

  const filtered = employees.filter((e) => {
    const q = search.toLowerCase();
    return (
      e.full_name.toLowerCase().includes(q) ||
      e.employee_code.toLowerCase().includes(q) ||
      (e.job_title ?? "").toLowerCase().includes(q)
    );
  });

  const riskConfig = result ? getRiskConfig(result.risk_level) : null;
  const shapMaxAbs =
    result?.key_factors?.length
      ? Math.max(...result.key_factors.map((f) => Math.abs(f.shap_value)), 0.001)
      : 0.001;

  return (
    <MainLayout>
      <div className="flex flex-col bg-neutral-50 dark:bg-neutral-950" style={{ height: "100%" }}>

        {/* ── Top bar ──────────────────────────────────────────────── */}
        <header className="h-11 shrink-0 bg-white dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between px-4">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.back()}
              className="text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200 transition-colors"
              aria-label="Retour"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <div className="w-px h-3.5 bg-neutral-200 dark:bg-neutral-700" />
            <span className="text-[13px] font-medium text-neutral-700 dark:text-neutral-200">
              Scoring Prédictif RH
            </span>
          </div>
          {result && (
            <div className="flex items-center gap-2 text-[11px] text-neutral-400">
              <code className="bg-neutral-100 dark:bg-neutral-800 px-1.5 py-0.5 rounded text-[10px] font-mono">
                {result.model_version}
              </code>
              <span>
                Calculé le {new Date(result.computed_at).toLocaleString("fr-FR")}
              </span>
            </div>
          )}
        </header>

        {/* ── Body ─────────────────────────────────────────────────── */}
        <div className="flex flex-1 min-h-0 overflow-hidden">

          {/* ── Sidebar ───────────────────────────────────────────── */}
          <aside className="w-52 shrink-0 bg-white dark:bg-neutral-900 border-r border-neutral-200 dark:border-neutral-800 flex flex-col">

            <div className="px-3.5 py-2.5 border-b border-neutral-100 dark:border-neutral-800 flex items-center justify-between">
              <span className="text-[10px] font-semibold text-neutral-400 uppercase tracking-widest">
                {filtered.length} employés
              </span>
              <button
                onClick={loadEmployees}
                disabled={loadingEmployees}
                className="text-neutral-300 hover:text-neutral-500 dark:hover:text-neutral-400 transition-colors disabled:opacity-40"
                aria-label="Actualiser"
              >
                <RefreshCw className={`w-3 h-3 ${loadingEmployees ? "animate-spin" : ""}`} />
              </button>
            </div>

            <div className="px-2.5 py-2 border-b border-neutral-100 dark:border-neutral-800">
              <input
                type="text"
                placeholder="Filtrer..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full text-xs px-2.5 py-1.5 bg-neutral-50 dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded text-neutral-800 dark:text-neutral-200 placeholder-neutral-400 focus:outline-none focus:ring-1 focus:ring-neutral-300 dark:focus:ring-neutral-600"
              />
            </div>

            <div className="flex-1 overflow-y-auto">
              {loadingEmployees && (
                <div className="p-3 space-y-1.5">
                  {[...Array(7)].map((_, i) => (
                    <div
                      key={i}
                      className="h-9 rounded bg-neutral-100 dark:bg-neutral-800 animate-pulse"
                      style={{ opacity: 1 - i * 0.1 }}
                    />
                  ))}
                </div>
              )}

              {employeesError && (
                <div className="p-4">
                  <p className="text-xs text-red-600 dark:text-red-400 mb-2 leading-relaxed">
                    {employeesError}
                  </p>
                  <button onClick={loadEmployees} className="text-xs underline text-neutral-500">
                    Réessayer
                  </button>
                </div>
              )}

              {!loadingEmployees && !employeesError && filtered.length === 0 && (
                <p className="text-xs text-neutral-400 p-4">Aucun résultat</p>
              )}

              {!loadingEmployees &&
                !employeesError &&
                filtered.map((emp) => {
                  const isSelected = selectedEmployeeId === emp.id;
                  const isActive = emp.employment_status === "active";
                  return (
                    <button
                      key={emp.id}
                      onClick={() => loadPredictiveScore(emp.id)}
                      disabled={loading}
                      className={`w-full flex items-start gap-2 pl-3 pr-2.5 py-2.5 text-left border-l-2 transition-colors duration-100 ${
                        isSelected
                          ? "border-l-neutral-700 dark:border-l-neutral-400 bg-neutral-100 dark:bg-neutral-800"
                          : "border-l-transparent hover:bg-neutral-50 dark:hover:bg-neutral-800/40"
                      } disabled:opacity-40`}
                    >
                      <span
                        className={`w-1.5 h-1.5 rounded-full shrink-0 mt-[5px] ${
                          isActive ? "bg-emerald-400" : "bg-amber-400"
                        }`}
                      />
                      <div className="min-w-0">
                        <p
                          className={`text-[12px] font-medium truncate leading-snug ${
                            isSelected
                              ? "text-neutral-900 dark:text-white"
                              : "text-neutral-700 dark:text-neutral-200"
                          }`}
                        >
                          {emp.full_name}
                        </p>
                        <p className="text-[11px] text-neutral-400 truncate mt-0.5">
                          {emp.job_title || emp.department_name || emp.employee_code}
                        </p>
                      </div>
                    </button>
                  );
                })}
            </div>
          </aside>

          {/* ── Main panel ────────────────────────────────────────── */}
          <main className="flex-1 overflow-y-auto">

            {/* Loading */}
            {loading && (
              <div className="p-6 max-w-2xl space-y-3">
                <div className="h-[88px] rounded-lg bg-neutral-200 dark:bg-neutral-800 animate-pulse" />
                <div className="h-[130px] rounded-lg bg-neutral-200 dark:bg-neutral-800 animate-pulse" />
                <div className="h-48 rounded-lg bg-neutral-200 dark:bg-neutral-800 animate-pulse" />
                <div className="h-36 rounded-lg bg-neutral-200 dark:bg-neutral-800 animate-pulse" />
              </div>
            )}

            {/* Error */}
            {!loading && error && (
              <div className="p-6 max-w-2xl">
                <div className="p-4 rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950/20">
                  <p className="text-sm text-red-700 dark:text-red-400 mb-2">{error}</p>
                  {selectedEmployeeId && (
                    <button
                      onClick={() => loadPredictiveScore(selectedEmployeeId)}
                      className="text-xs text-red-600 underline"
                    >
                      Réessayer
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Empty */}
            {!loading && !result && !error && (
              <div className="h-full flex items-center justify-center">
                <div className="text-center">
                  <p className="text-[13px] font-medium text-neutral-500 dark:text-neutral-400">
                    Sélectionnez un employé
                  </p>
                  <p className="text-xs text-neutral-400 dark:text-neutral-500 mt-1">
                    Le scoring est calculé automatiquement depuis la base RH
                  </p>
                </div>
              </div>
            )}

            {/* Result */}
            {!loading && result && riskConfig && (
              <div className="px-6 py-5 max-w-2xl space-y-4">

                {/* ── Risk + employee header ──────────────────────── */}
                <div
                  className={`rounded-lg border px-5 py-4 ${riskConfig.bgClass} ${riskConfig.borderClass}`}
                >
                  <div className="flex items-start justify-between gap-6">
                    <div>
                      <div className="flex items-center gap-2 mb-1.5">
                        <span
                          className={`text-[10px] font-bold uppercase tracking-widest ${riskConfig.textClass}`}
                        >
                          {riskConfig.short}
                        </span>
                        {result.action_priority && (
                          <>
                            <span className="text-neutral-300 dark:text-neutral-700 select-none">·</span>
                            <span className="text-[10px] text-neutral-500 dark:text-neutral-400">
                              Priorité {result.action_priority}
                            </span>
                          </>
                        )}
                      </div>
                      <h2 className="text-[15px] font-semibold text-neutral-900 dark:text-white leading-snug">
                        {result.employee_name}
                      </h2>
                      <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-1.5 leading-relaxed max-w-sm">
                        {riskConfig.context}
                      </p>
                    </div>
                    <div className="shrink-0 text-right">
                      <p className="text-[10px] text-neutral-400 mb-0.5 whitespace-nowrap">
                        Confiance modèle
                      </p>
                      <p className={`text-[18px] font-bold tabular-nums leading-none ${riskConfig.textClass}`}>
                        {Math.round(result.prediction_confidence * 100)}%
                      </p>
                    </div>
                  </div>
                </div>

                {/* ── Score rings ─────────────────────────────────── */}
                <div>
                  <p className="text-[10px] font-semibold text-neutral-400 uppercase tracking-widest mb-2.5">
                    Indicateurs prédictifs
                  </p>
                  <div className="grid grid-cols-3 gap-3">
                    <ScoreRing
                      value={result.churn_risk_percent}
                      label="Risque départ"
                      strokeClass="stroke-red-500"
                      textClass="text-red-600 dark:text-red-400"
                    />
                    <ScoreRing
                      value={result.performance_score * 100}
                      label="Performance"
                      strokeClass="stroke-blue-500"
                      textClass="text-blue-600 dark:text-blue-400"
                    />
                    <ScoreRing
                      value={result.engagement_score * 100}
                      label="Engagement"
                      strokeClass="stroke-emerald-600"
                      textClass="text-emerald-700 dark:text-emerald-400"
                    />
                  </div>
                </div>

                {/* ── SHAP factors ─────────────────────────────────── */}
                {result.key_factors && result.key_factors.length > 0 && (
                  <div className="bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 px-5 pt-4 pb-3">
                    <p className="text-[10px] font-semibold text-neutral-400 uppercase tracking-widest mb-3">
                      Facteurs explicatifs (SHAP)
                    </p>
                    <div className="divide-y divide-neutral-50 dark:divide-neutral-800/60">
                      {result.key_factors.slice(0, 8).map((f, i) => (
                        <ShapRow key={i} factor={f} maxAbs={shapMaxAbs} />
                      ))}
                    </div>
                    <div className="flex items-center gap-2.5 mt-2 pt-2 border-t border-neutral-100 dark:border-neutral-800">
                      <span className="w-36 shrink-0" />
                      <div className="flex-1 flex justify-between text-[9px] font-mono text-neutral-400 uppercase tracking-wide">
                        <span>← Réduit</span>
                        <span>Augmente →</span>
                      </div>
                      <span className="w-14 shrink-0" />
                    </div>
                  </div>
                )}

                {/* ── Recommendations ──────────────────────────────── */}
                {result.recommendations && result.recommendations.length > 0 && (
                  <div className="bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 px-5 py-4">
                    <p className="text-[10px] font-semibold text-neutral-400 uppercase tracking-widest mb-4">
                      Plan d'action recommandé
                    </p>
                    <ol className="space-y-3">
                      {result.recommendations.map((rec, i) => (
                        <li key={i} className="flex items-start gap-3">
                          <span className="text-[10px] font-mono text-neutral-400 shrink-0 mt-0.5 w-5">
                            {String(i + 1).padStart(2, "0")}.
                          </span>
                          <p className="text-[12px] text-neutral-700 dark:text-neutral-300 leading-relaxed">
                            {rec}
                          </p>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}

                {/* ── Data sources ─────────────────────────────────── */}
                {result.features_used && (
                  <div>
                    <p className="text-[9px] font-semibold text-neutral-400 uppercase tracking-widest mb-2">
                      Données sources
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {Object.entries(result.features_used).map(([k, v]) => (
                        <span
                          key={k}
                          className="text-[10px] font-mono px-2 py-0.5 bg-neutral-100 dark:bg-neutral-800 text-neutral-500 dark:text-neutral-400 rounded"
                        >
                          {k}={String(v)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

              </div>
            )}
          </main>
        </div>
      </div>
    </MainLayout>
  );
}
