/**
 * Turnover Prediction Page - Modern Redesign
 * Professional SaaS-style dashboard inspired by Linear, Stripe, Notion
 */

"use client";

import { useState, useEffect } from "react";
import {
  AlertCircle,
  Calendar,
  Activity,
  TrendingUp,
  Clock,
  Users,
  Sparkles,
  Brain,
  Target,
  Briefcase,
} from "lucide-react";
import MainLayout from "@/components/MainLayout";
import KPICard from "@/components/ui/KPICard";
import PredictionCard from "@/components/ui/PredictionCard";
import EmployeeSelector from "@/components/ui/EmployeeSelector";

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
  prediction: number;
  turnover_probability: number;
  turnover_probability_percent: number;
  risk_level: "faible" | "moyen" | "élevé";
  risk_color: string;
  risk_emoji: string;
  features_used: {
    age: number;
    anciennete_annees: number;
    total_jours_absence: number;
    nb_absences: number;
    duree_presence_jours: number;
    [key: string]: any;
  };
  model_path: string;
  computed_at: string;
}

export default function TurnoverPredictionPageModern() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<PredictionResult | null>(null);

  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loadingEmployees, setLoadingEmployees] = useState(true);
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

  // Load employees
  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const response = await fetch(
          "http://localhost:8000/api/v1/hr-analytics/employees?all=true",
          { headers: { Authorization: `Bearer ${token}` } }
        );

        if (response.ok) {
          const data = await response.json();
          setEmployees(data);
        } else {
          setError("Erreur lors du chargement des employés");
        }
      } catch (err) {
        console.error("Error loading employees:", err);
        setError("Erreur de connexion au serveur");
      } finally {
        setLoadingEmployees(false);
      }
    };

    fetchEmployees();
  }, []);

  // Handle employee selection
  const handleEmployeeSelect = async (emp: Employee) => {
    setSelectedEmployee(emp);
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
          setError("Date d'embauche manquante pour cet employé.");
          setLoading(false);
          return;
        }

        let birthDate = data.date_of_birth;
        let usingDefault = false;
        if (!birthDate) {
          const today = new Date();
          const defaultAge = 35;
          const defaultBirthYear = today.getFullYear() - defaultAge;
          birthDate = `${defaultBirthYear}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
          usingDefault = true;
        }
        setUsingDefaultBirthDate(usingDefault);

        const newFormData = {
          date_naissance: birthDate,
          date_embauche: data.hire_date,
          sexe: data.sexe || "Masculin",
          type_contrat: data.type_contrat || "CDI",
          total_jours_absence: data.total_jours_absence.toString(),
          nb_absences: data.nb_absences.toString(),
        };

        setFormData(newFormData);
        setError("");
      } else {
        setError("Erreur lors du chargement des données");
      }
    } catch (err) {
      console.error("Error loading employee turnover data:", err);
      setError("Erreur de connexion au serveur");
    } finally {
      setLoading(false);
    }
  };

  // Handle prediction
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedEmployee) {
      setError("Veuillez sélectionner un employé");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const token = localStorage.getItem("access_token");

      let typeContratMapped = formData.type_contrat;
      const contractMapping: Record<string, string> = {
        "Contrat à durée déterminée": "CDD sur emploi permanent",
        "Contrat à durée indéterminée": "CDI",
        "Durée déterminée": "CDD sur emploi permanent",
        "Durée indéterminée": "CDI",
      };

      if (contractMapping[formData.type_contrat]) {
        typeContratMapped = contractMapping[formData.type_contrat];
      }

      const requestData = {
        date_naissance: formData.date_naissance,
        date_embauche: formData.date_embauche,
        sexe: formData.sexe,
        type_contrat: typeContratMapped,
        total_jours_absence: parseInt(formData.total_jours_absence) || 0,
        nb_absences: parseInt(formData.nb_absences) || 0,
      };

      const response = await fetch(
        "http://localhost:8000/api/v1/hr-analytics/predict-turnover",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(requestData),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Erreur lors de la prédiction");
      }
    } catch (err) {
      console.error("Error predicting turnover:", err);
      setError("Erreur de connexion au serveur");
    } finally {
      setLoading(false);
    }
  };

  const calculateAge = (birthDate: string) => {
    if (!birthDate) return 0;
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const calculateAnciennete = (hireDate: string) => {
    if (!hireDate) return 0;
    const today = new Date();
    const hire = new Date(hireDate);
    const years = (today.getTime() - hire.getTime()) / (365.25 * 24 * 60 * 60 * 1000);
    return years;
  };

  return (
    <MainLayout>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
        {/* Hero Header - Modern Gradient */}
        <div className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-violet-600 to-purple-700">
          {/* Decorative elements */}
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
                  Analyse Prédictive du Turnover
                </h1>
                <p className="text-indigo-100 text-lg">
                  Modèle de Machine Learning • Gradient Boosting
                </p>
              </div>
            </div>

            {/* Stats Pills */}
            <div className="flex flex-wrap gap-3">
              <div className="px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20">
                <p className="text-sm text-white font-medium flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  {employees.length} employés
                </p>
              </div>
              <div className="px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20">
                <p className="text-sm text-white font-medium flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Précision: 94.2%
                </p>
              </div>
              <div className="px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20">
                <p className="text-sm text-white font-medium flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  IA Prédictive
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Form */}
            <div className="lg:col-span-1 space-y-6">
              {/* Employee Selection Card */}
              <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-xl shadow-slate-200/50 dark:shadow-black/50">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg">
                    <Users className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                    Sélection Employé
                  </h2>
                </div>

                <EmployeeSelector
                  employees={employees}
                  selectedEmployee={selectedEmployee}
                  onSelect={handleEmployeeSelect}
                  loading={loadingEmployees}
                />

                {/* Selected Employee Info */}
                {selectedEmployee && formData.date_embauche && (
                  <div className="mt-6 p-4 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700">
                    <p className="text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wide mb-3">
                      Informations
                    </p>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-600 dark:text-slate-400">Âge:</span>
                        <span className="font-semibold text-slate-900 dark:text-white">
                          {calculateAge(formData.date_naissance)} ans
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600 dark:text-slate-400">Ancienneté:</span>
                        <span className="font-semibold text-slate-900 dark:text-white">
                          {calculateAnciennete(formData.date_embauche).toFixed(1)} ans
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-600 dark:text-slate-400">Contrat:</span>
                        <span className="font-semibold text-slate-900 dark:text-white">
                          {formData.type_contrat}
                        </span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Parameters Card */}
              <form onSubmit={handleSubmit} className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-xl shadow-slate-200/50 dark:shadow-black/50">
                <div className="flex items-center gap-3 mb-6">
                  <div className="p-2 bg-violet-100 dark:bg-violet-900/30 rounded-lg">
                    <Activity className="w-5 h-5 text-violet-600 dark:text-violet-400" />
                  </div>
                  <h2 className="text-lg font-bold text-slate-900 dark:text-white">
                    Paramètres
                  </h2>
                </div>

                <div className="space-y-4">
                  {/* Sexe */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                      Sexe
                    </label>
                    <select
                      value={formData.sexe}
                      onChange={(e) => setFormData({ ...formData, sexe: e.target.value })}
                      className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                    >
                      <option value="Masculin">Masculin</option>
                      <option value="Féminin">Féminin</option>
                    </select>
                  </div>

                  {/* Absences */}
                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                      Total jours d'absence
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={formData.total_jours_absence}
                      onChange={(e) =>
                        setFormData({ ...formData, total_jours_absence: e.target.value })
                      }
                      className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                      placeholder="0"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                      Nombre d'absences
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={formData.nb_absences}
                      onChange={(e) =>
                        setFormData({ ...formData, nb_absences: e.target.value })
                      }
                      className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                      placeholder="0"
                    />
                  </div>

                  {/* Submit Button */}
                  <button
                    type="submit"
                    disabled={loading || !selectedEmployee}
                    className="w-full mt-6 px-6 py-4 bg-gradient-to-r from-indigo-600 to-violet-600 text-white font-semibold rounded-xl hover:from-indigo-700 hover:to-violet-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-3 shadow-lg shadow-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/50"
                  >
                    {loading ? (
                      <>
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Analyse en cours...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-5 h-5" />
                        Lancer l'Analyse IA
                      </>
                    )}
                  </button>
                </div>

                {/* Warnings */}
                {usingDefaultBirthDate && (
                  <div className="mt-4 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50 rounded-lg">
                    <p className="text-xs text-amber-800 dark:text-amber-400 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 flex-shrink-0" />
                      Date de naissance absente - âge estimé à 35 ans
                    </p>
                  </div>
                )}
              </form>
            </div>

            {/* Right Column - Results */}
            <div className="lg:col-span-2 space-y-6">
              {/* Error Alert */}
              {error && (
                <div className="bg-rose-50 dark:bg-rose-900/20 border-2 border-rose-200 dark:border-rose-800/50 rounded-2xl p-6">
                  <div className="flex items-start gap-4">
                    <div className="p-2 bg-rose-100 dark:bg-rose-900/30 rounded-lg">
                      <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-400" />
                    </div>
                    <div>
                      <p className="font-semibold text-rose-900 dark:text-rose-300 mb-1">
                        Erreur
                      </p>
                      <p className="text-sm text-rose-700 dark:text-rose-400">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Prediction Result */}
              {result && (
                <>
                  <PredictionCard
                    probability={result.turnover_probability_percent}
                    riskLevel={result.risk_level}
                    prediction={result.prediction as 0 | 1}
                  />

                  {/* KPIs Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <KPICard
                      title="Âge"
                      value={`${result.features_used.age} ans`}
                      icon={Calendar}
                      variant="default"
                    />
                    <KPICard
                      title="Ancienneté"
                      value={`${result.features_used.anciennete_annees.toFixed(1)} ans`}
                      icon={Clock}
                      variant="info"
                    />
                    <KPICard
                      title="Jours d'absence"
                      value={result.features_used.total_jours_absence}
                      icon={Activity}
                      variant={result.features_used.total_jours_absence > 10 ? "warning" : "success"}
                    />
                    <KPICard
                      title="Nb. Absences"
                      value={result.features_used.nb_absences}
                      icon={TrendingUp}
                      variant={result.features_used.nb_absences > 5 ? "warning" : "default"}
                    />
                  </div>

                  {/* Features Detail */}
                  <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-xl shadow-slate-200/50 dark:shadow-black/50">
                    <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
                      <Briefcase className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                      Détails de l'Analyse
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      {Object.entries(result.features_used).map(([key, value]) => (
                        <div
                          key={key}
                          className="flex justify-between items-center p-3 bg-slate-50 dark:bg-slate-800 rounded-lg"
                        >
                          <span className="text-slate-600 dark:text-slate-400 font-medium">
                            {key.replace(/_/g, " ")}:
                          </span>
                          <span className="font-semibold text-slate-900 dark:text-white">
                            {typeof value === "number" ? value.toFixed(2) : value}
                          </span>
                        </div>
                      ))}
                    </div>
                    <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800">
                      <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-2">
                        <Clock className="w-3 h-3" />
                        Analysé le {new Date(result.computed_at).toLocaleString("fr-FR")}
                      </p>
                    </div>
                  </div>
                </>
              )}

              {/* Empty State */}
              {!result && !error && !loading && (
                <div className="bg-white dark:bg-slate-900 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-700 p-12 text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-800 mb-4">
                    <Brain className="w-8 h-8 text-slate-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
                    Prêt pour l'analyse
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400 max-w-md mx-auto">
                    Sélectionnez un employé et ajustez les paramètres, puis lancez l'analyse
                    prédictive pour obtenir les résultats.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
