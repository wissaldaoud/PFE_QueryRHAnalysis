"use client";

import { useState, useEffect } from "react";
import {
  Loader2, AlertCircle, Calendar, Briefcase, Activity,
  TrendingUp, Search, CheckCircle, BarChart3, Users,
  Shield, Clock, UserCheck, ChevronRight
} from "lucide-react";
import MainLayout from "@/components/MainLayout";

interface Employee {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  full_name: string;
  date_of_birth?: string;
  hire_date: string;
  contract_type?: string;
  employment_status: string;
  department_name?: string;
}

interface PredictionResult {
  success: boolean;
  prediction: number;
  score: number;
  probabilite: number;
  niveau: string;
  couleur: string;
  recommandation: string;
  features_used: any;
  model_path: string;
  computed_at: string;
  details: any;
}

/* ─── Gauge SVG ──────────────────────────────────────────────────────────── */
function GaugeChart({ percent, riskLevel }: { percent: number; riskLevel: string }) {
  const safePercent = typeof percent === 'number' && !isNaN(percent) ? percent : 0;
  const radius = 70;
  const stroke = 12;
  const normalizedRadius = radius - stroke / 2;
  const circumference = Math.PI * normalizedRadius; // half circle
  const progress = Math.min(Math.max(safePercent / 100, 0), 1);
  const offset = circumference * (1 - progress);

  const color =
    safePercent < 30 ? "#10b981" :
    safePercent < 60 ? "#f59e0b" :
    "#ef4444";

  const trackColor = "#e5e7eb";

  return (
    <div className="flex flex-col items-center">
      <svg width="180" height="100" viewBox="0 0 180 100">
        {/* Track */}
        <path
          d={`M ${stroke / 2} 90 A ${normalizedRadius} ${normalizedRadius} 0 0 1 ${180 - stroke / 2} 90`}
          fill="none"
          stroke={trackColor}
          strokeWidth={stroke}
          strokeLinecap="round"
        />
        {/* Progress */}
        <path
          d={`M ${stroke / 2} 90 A ${normalizedRadius} ${normalizedRadius} 0 0 1 ${180 - stroke / 2} 90`}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${circumference} ${circumference}`}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 1s ease, stroke 0.5s ease" }}
        />
        {/* Zone labels */}
        <text x="14" y="96" fontSize="9" fill="#9ca3af" fontFamily="sans-serif">0%</text>
        <text x="82" y="18" fontSize="9" fill="#9ca3af" fontFamily="sans-serif" textAnchor="middle">50%</text>
        <text x="158" y="96" fontSize="9" fill="#9ca3af" fontFamily="sans-serif" textAnchor="end">100%</text>
      </svg>
      <div className="text-center -mt-4">
        <div className="text-4xl font-black" style={{ color, fontFamily: "'DM Mono', monospace" }}>
          {safePercent.toFixed(1)}%
        </div>
        <div className="text-xs text-gray-400 mt-0.5 font-medium tracking-widest uppercase">Probabilité</div>
      </div>
    </div>
  );
}

/* ─── KPI Card ───────────────────────────────────────────────────────────── */
function KpiCard({
  label, value, unit, color, icon: Icon
}: { label: string; value: string | number; unit?: string; color: string; icon: any }) {
  const colors: Record<string, string> = {
    blue:   "bg-blue-50   border-blue-200   text-blue-700",
    green:  "bg-green-50  border-green-200  text-green-700",
    orange: "bg-orange-50 border-orange-200 text-orange-700",
    purple: "bg-purple-50 border-purple-200 text-purple-700",
    slate:  "bg-slate-50  border-slate-200  text-slate-700",
  };
  const cls = colors[color] ?? colors.slate;

  return (
    <div className={`rounded-xl border p-4 ${cls.split(" ").slice(0, 2).join(" ")} flex items-start gap-3`}>
      <div className={`p-2 rounded-lg ${cls.split(" ").slice(0, 1).join(" ")} border ${cls.split(" ")[1]}`}>
        <Icon className={`w-4 h-4 ${cls.split(" ")[2]}`} />
      </div>
      <div>
        <p className={`text-xs font-semibold tracking-wide uppercase ${cls.split(" ")[2]} opacity-70`}>{label}</p>
        <p className={`text-2xl font-black ${cls.split(" ")[2]}`}>
          {value}<span className="text-sm font-medium ml-1 opacity-70">{unit}</span>
        </p>
      </div>
    </div>
  );
}

/* ─── Risk Badge ─────────────────────────────────────────────────────────── */
function RiskBadge({ level }: { level: string }) {
  const lower = level.toLowerCase();
  if (lower === "faible")
    return (
      <span className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-emerald-100 text-emerald-700 border border-emerald-200 font-semibold text-sm">
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        Risque Faible
      </span>
    );
  if (lower === "moyen")
    return (
      <span className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-amber-100 text-amber-700 border border-amber-200 font-semibold text-sm">
        <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
        Risque Moyen
      </span>
    );
  return (
    <span className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full bg-red-100 text-red-700 border border-red-200 font-semibold text-sm">
      <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
      Risque Élevé
    </span>
  );
}

/* ─── Section Header ─────────────────────────────────────────────────────── */
function SectionHeader({
  icon: Icon, label, color
}: { icon: any; label: string; color: "blue" | "green" | "orange" }) {
  const map = {
    blue:   "bg-blue-100   text-blue-600   border-blue-300",
    green:  "bg-green-100  text-green-600  border-green-300",
    orange: "bg-orange-100 text-orange-600 border-orange-300",
  };
  const [bg, text] = map[color].split(" ");
  return (
    <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${bg} border ${map[color].split(" ")[2]} mb-4`}>
      <Icon className={`w-4 h-4 ${text}`} />
      <span className={`text-sm font-semibold ${text}`}>{label}</span>
    </div>
  );
}

/* ─── Read-only field ────────────────────────────────────────────────────── */
function ReadonlyField({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">{label}</label>
      <div className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-800 font-medium text-sm select-none">
        {value || "—"}
      </div>
      {hint && <p className="text-xs text-gray-400 mt-1 pl-1">{hint}</p>}
    </div>
  );
}

/* ─── Page ───────────────────────────────────────────────────────────────── */
export default function TurnoverPredictionPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<PredictionResult | null>(null);

  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loadingEmployees, setLoadingEmployees] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [usingDefaultBirthDate, setUsingDefaultBirthDate] = useState(false);

  const [formData, setFormData] = useState({
    date_naissance: "",
    date_embauche: "",
    sexe: "Masculin",
    type_contrat: "CDI",
    total_jours_absence: "0",
    nb_absences: "0",
  });

  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const response = await fetch(
          "http://localhost:8000/api/v1/employees?limit=1000",
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (response.ok) {
          const data = await response.json();
          setEmployees(data);
        } else {
          setError("Erreur lors du chargement des employés");
        }
      } catch {
        setError("Erreur de connexion au serveur");
      } finally {
        setLoadingEmployees(false);
      }
    };
    fetchEmployees();
  }, []);

  const filteredEmployees = employees.filter((emp) => {
    if (!searchTerm) return true;
    const s = searchTerm.toLowerCase();
    return (
      emp.full_name?.toLowerCase().includes(s) ||
      emp.first_name?.toLowerCase().includes(s) ||
      emp.last_name?.toLowerCase().includes(s) ||
      emp.employee_code?.toLowerCase().includes(s) ||
      emp.id.toString().includes(s)
    );
  });

  const selectEmployee = async (emp: Employee) => {
    setSelectedEmployee(emp);
    setSearchTerm(`${emp.full_name} (${emp.employee_code})`);
    setShowDropdown(false);
    setResult(null);
    setError("");
    setLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(
        `http://localhost:8000/api/v1/employees/${emp.id}/turnover-data`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (response.ok) {
        const data = await response.json();
        if (!data.hire_date) {
          setError("⚠️ Date d'embauche manquante. Veuillez compléter le profil.");
          setLoading(false);
          return;
        }
        let birthDate = data.date_of_birth;
        let usingDefault = false;
        if (!birthDate) {
          const today = new Date();
          const y = today.getFullYear() - 35;
          birthDate = `${y}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
          usingDefault = true;
        }
        setUsingDefaultBirthDate(usingDefault);
        setFormData({
          date_naissance: birthDate,
          date_embauche: data.hire_date,
          sexe: data.sexe || "Masculin",
          type_contrat: data.type_contrat || "CDI",
          total_jours_absence: data.total_jours_absence.toString(),
          nb_absences: data.nb_absences.toString(),
        });
      } else {
        const err = await response.json().catch(() => ({}));
        if (response.status === 401) {
          setError("⚠️ Session expirée. Veuillez vous reconnecter.");
          setTimeout(() => (window.location.href = "/login"), 2000);
        } else {
          setError(`Erreur: ${err.detail || response.status}`);
        }
      }
    } catch {
      setError("Erreur de connexion au serveur");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedEmployee) return setError("Veuillez sélectionner un employé");
    if (!formData.date_embauche) return setError("Date d'embauche manquante");

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const token = localStorage.getItem("access_token");

      const response = await fetch(
        `http://localhost:8000/api/v1/ml/turnover/${selectedEmployee.id}`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        const err = await response.json();
        setError(err.detail || "Erreur lors de la prédiction");
      }
    } catch {
      setError("Erreur de connexion au serveur");
    } finally {
      setLoading(false);
    }
  };

  const calculateAge = (d: string) => {
    if (!d) return 0;
    const today = new Date(), birth = new Date(d);
    let age = today.getFullYear() - birth.getFullYear();
    if (today.getMonth() < birth.getMonth() || (today.getMonth() === birth.getMonth() && today.getDate() < birth.getDate())) age--;
    return age;
  };

  const calculateAnciennete = (d: string) => {
    if (!d) return "0";
    return ((new Date().getTime() - new Date(d).getTime()) / (365.25 * 24 * 60 * 60 * 1000)).toFixed(1);
  };

  const formatDate = (d: string) => {
    if (!d) return "—";
    return new Date(d).toLocaleDateString("fr-FR");
  };

  return (
    <MainLayout>
      <div className="min-h-screen" style={{ background: "#f1f5f9" }}>

        {/* ── Header ── */}
        <div style={{ background: "linear-gradient(135deg, #1e3a5f 0%, #15294a 100%)" }} className="shadow-xl">
          <div className="max-w-6xl mx-auto px-6 py-6">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-blue-300 text-xs mb-3 font-medium tracking-wide">
              <span>Accueil</span>
              <ChevronRight className="w-3 h-3" />
              <span>Ressources Humaines</span>
              <ChevronRight className="w-3 h-3" />
              <span className="text-white">Prédiction Turnover</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="p-3 rounded-xl" style={{ background: "rgba(220,38,38,0.2)", border: "1px solid rgba(220,38,38,0.3)" }}>
                  <TrendingUp className="w-6 h-6 text-red-400" />
                </div>
                <div>
                  <h1 className="text-2xl font-black text-white tracking-tight">
                    Analyse Prédictive du Turnover
                  </h1>
                  <p className="text-blue-300 text-sm mt-0.5">Modèle ML — Prédiction en temps réel</p>
                </div>
              </div>
              <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded-xl text-blue-200 text-sm font-semibold"
                style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.12)" }}>
                <BarChart3 className="w-4 h-4" />
                Analyse RH
              </div>
            </div>
          </div>
        </div>

        {/* ── Main ── */}
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">

            {/* ── LEFT: Form (3/5) ── */}
            <div className="lg:col-span-3 space-y-5">

              {/* Employee selector card */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                <div className="flex items-center gap-3 mb-5">
                  <div className="p-2.5 rounded-xl bg-blue-50 border border-blue-100">
                    <Users className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h2 className="text-base font-bold text-slate-800">Sélection de l'employé</h2>
                    <p className="text-xs text-slate-400">Recherchez par nom ou code employé</p>
                  </div>
                </div>

                {/* Search input */}
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                    {loadingEmployees
                      ? <Loader2 className="w-4 h-4 text-slate-400 animate-spin" />
                      : <Search className="w-4 h-4 text-slate-400" />}
                  </div>
                  <input
                    type="text"
                    placeholder={loadingEmployees ? "Chargement des employés…" : `Rechercher parmi ${employees.length} employés…`}
                    value={searchTerm}
                    onChange={(e) => { setSearchTerm(e.target.value); setShowDropdown(true); }}
                    onFocus={() => setShowDropdown(true)}
                    onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
                    disabled={loadingEmployees || employees.length === 0}
                    className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-slate-50 disabled:text-slate-400 transition-all bg-slate-50"
                  />

                  {/* Dropdown */}
                  {showDropdown && !loadingEmployees && filteredEmployees.length > 0 && (
                    <div className="absolute z-20 w-full mt-2 bg-white border border-slate-200 rounded-xl shadow-xl max-h-72 overflow-y-auto">
                      {filteredEmployees.slice(0, 100).map((emp) => (
                        <div
                          key={emp.id}
                          onClick={() => selectEmployee(emp)}
                          className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-slate-100 last:border-0 transition-colors flex justify-between items-center group"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-600 group-hover:bg-blue-100 group-hover:text-blue-700 transition-colors">
                              {emp.first_name?.[0]}{emp.last_name?.[0]}
                            </div>
                            <div>
                              <p className="font-semibold text-slate-800 text-sm">{emp.full_name}</p>
                              <p className="text-xs text-slate-400">{emp.employee_code} • {emp.department_name || "N/A"}</p>
                            </div>
                          </div>
                          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-lg font-mono font-medium">
                            {emp.employee_code}
                          </span>
                        </div>
                      ))}
                      {filteredEmployees.length > 100 && (
                        <div className="px-4 py-2.5 text-xs text-slate-400 text-center bg-slate-50">
                          +{filteredEmployees.length - 100} autres — affinez votre recherche
                        </div>
                      )}
                    </div>
                  )}

                  {showDropdown && searchTerm && filteredEmployees.length === 0 && !loadingEmployees && (
                    <div className="absolute z-20 w-full mt-2 bg-white border border-slate-200 rounded-xl shadow-xl p-5 text-center">
                      <p className="text-slate-500 text-sm">Aucun résultat pour « {searchTerm} »</p>
                    </div>
                  )}
                </div>

                {/* Selected employee badge */}
                {selectedEmployee && (
                  <div className="mt-3 flex items-center gap-3 bg-emerald-50 border border-emerald-200 rounded-xl p-3.5">
                    <div className="w-9 h-9 rounded-full bg-emerald-100 flex items-center justify-center text-xs font-black text-emerald-700">
                      {selectedEmployee.first_name?.[0]}{selectedEmployee.last_name?.[0]}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-bold text-emerald-800 truncate">{selectedEmployee.full_name}</p>
                      <p className="text-xs text-emerald-600">{selectedEmployee.employee_code} • {selectedEmployee.department_name || "N/A"}</p>
                    </div>
                    <CheckCircle className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                  </div>
                )}

                {/* Auto-load note */}
                {selectedEmployee && (
                  <div className="mt-3 flex items-start gap-2.5 bg-blue-50 border border-blue-100 rounded-xl p-3.5">
                    <AlertCircle className="w-4 h-4 text-blue-500 flex-shrink-0 mt-0.5" />
                    <p className="text-xs text-blue-700 leading-relaxed">
                      <span className="font-bold">Données chargées automatiquement</span> depuis la base de données — aucune saisie manuelle requise.
                    </p>
                  </div>
                )}
              </div>

              {/* Data form card */}
              {selectedEmployee && (
                <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                  <form onSubmit={handleSubmit} className="space-y-6">

                    {/* Personal info */}
                    <div>
                      <SectionHeader icon={Calendar} label="Informations personnelles" color="blue" />
                      <div className="grid grid-cols-2 gap-4">
                        <ReadonlyField
                          label="Date de naissance"
                          value={formatDate(formData.date_naissance)}
                          hint={formData.date_naissance ? `${calculateAge(formData.date_naissance)} ans${usingDefaultBirthDate ? " (valeur par défaut)" : ""}` : undefined}
                        />
                        <ReadonlyField label="Sexe" value={formData.sexe} />
                      </div>
                    </div>

                    {/* Professional info */}
                    <div>
                      <SectionHeader icon={Briefcase} label="Informations professionnelles" color="green" />
                      <div className="grid grid-cols-2 gap-4">
                        <ReadonlyField
                          label="Date d'embauche"
                          value={formatDate(formData.date_embauche)}
                          hint={formData.date_embauche ? `Ancienneté : ${calculateAnciennete(formData.date_embauche)} ans` : undefined}
                        />
                        <ReadonlyField label="Type de contrat" value={formData.type_contrat} />
                      </div>
                    </div>

                    {/* Absences */}
                    <div>
                      <SectionHeader icon={Activity} label="Absences" color="orange" />
                      <div className="grid grid-cols-2 gap-4">
                        <ReadonlyField label="Nombre d'absences" value={formData.nb_absences} />
                        <ReadonlyField label="Total jours d'absence" value={formData.total_jours_absence} />
                      </div>
                      <p className="text-xs text-slate-400 mt-3 flex items-center gap-1.5">
                        <BarChart3 className="w-3 h-3" />
                        Calculé depuis les congés approuvés dans la base de données
                      </p>
                    </div>

                    {/* Submit */}
                    <button
                      type="submit"
                      disabled={loading || !selectedEmployee}
                      style={{ background: "linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 100%)" }}
                      className="w-full text-white px-6 py-4 rounded-xl font-bold text-base flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:opacity-90 shadow-lg hover:shadow-xl active:scale-[0.99]"
                    >
                      {loading ? (
                        <><Loader2 className="w-5 h-5 animate-spin" /> Analyse en cours…</>
                      ) : (
                        <><TrendingUp className="w-5 h-5" /> Lancer la prédiction</>
                      )}
                    </button>
                  </form>
                </div>
              )}
            </div>

            {/* ── RIGHT: Results (2/5) ── */}
            <div className="lg:col-span-2 space-y-5">

              {/* Error */}
              {error && (
                <div className="bg-white border border-red-200 rounded-2xl p-5 shadow-sm">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-red-100 rounded-xl">
                      <AlertCircle className="w-4 h-4 text-red-600" />
                    </div>
                    <div>
                      <p className="text-sm font-bold text-red-800 mb-1">Erreur</p>
                      <p className="text-xs text-red-600 whitespace-pre-line leading-relaxed">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Result card */}
              {result ? (
                <>
                  <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                    <div className="text-center">
                      <GaugeChart
                        percent={result.score || 0}
                        riskLevel={result.niveau}
                      />
                      <div className="mt-4">
                        <RiskBadge level={result.niveau} />
                      </div>

                      {/* Verdict */}
                      <div className="mt-5">
                        {result.prediction === 1 ? (
                          <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
                            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                            <p className="text-sm font-semibold text-red-800 text-left">Risque de départ élevé détecté</p>
                          </div>
                        ) : (
                          <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 flex items-center gap-3">
                            <CheckCircle className="w-5 h-5 text-emerald-500 flex-shrink-0" />
                            <p className="text-sm font-semibold text-emerald-800 text-left">Devrait rester dans l'entreprise</p>
                          </div>
                        )}
                      </div>

                      {selectedEmployee && (
                        <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-center gap-2 text-sm text-slate-500">
                          <UserCheck className="w-4 h-4" />
                          <span className="font-semibold text-slate-700">{selectedEmployee.full_name}</span>
                          <span className="text-slate-300">•</span>
                          <span className="font-mono text-xs">{selectedEmployee.employee_code}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* KPIs */}
                  <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                    <h3 className="text-sm font-bold text-slate-700 uppercase tracking-widest mb-4 flex items-center gap-2">
                      <Activity className="w-4 h-4 text-blue-500" />
                      Indicateurs utilisés
                    </h3>
                    <div className="grid grid-cols-2 gap-3">
                      <KpiCard icon={Users}    label="Âge"           value={result.features_used.age}  unit="ans"  color="blue" />
                      <KpiCard icon={Clock}    label="Ancienneté"    value={result.features_used.anciennete_annees.toFixed(1)} unit="ans" color="green" />
                      <KpiCard icon={Activity} label="Nb absences"   value={result.features_used.nb_absences}            color="orange" />
                      <KpiCard icon={Calendar} label="Jours absence" value={result.features_used.total_jours_absence}    color="purple" />
                    </div>
                    <div className="mt-4 pt-3 border-t border-slate-100 space-y-1">
                      <p className="text-xs text-slate-400 flex items-center gap-1.5">
                        <Shield className="w-3 h-3" />
                        Modèle : {result.model_path.split("\\").pop()}
                      </p>
                      <p className="text-xs text-slate-400">
                        Calculé le {new Date(result.computed_at).toLocaleString("fr-FR")}
                      </p>
                    </div>
                  </div>
                </>
              ) : !error ? (
                /* Empty state */
                <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-10 text-center">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-blue-50 border border-blue-100 flex items-center justify-center">
                    <BarChart3 className="w-8 h-8 text-blue-500" />
                  </div>
                  <h3 className="text-base font-bold text-slate-700 mb-2">
                    {selectedEmployee ? "Prêt pour l'analyse" : "Sélectionnez un employé"}
                  </h3>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    {selectedEmployee
                      ? "Cliquez sur « Lancer la prédiction » pour obtenir l'analyse"
                      : "Les données seront chargées automatiquement depuis la base de données"}
                  </p>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}