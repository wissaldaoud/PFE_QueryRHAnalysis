"use client";

import { useState, useEffect } from "react";
import { Loader2, AlertCircle, Calendar, Briefcase, Activity, TrendingUp, Search, Database, CheckCircle, BarChart3, Users } from "lucide-react";
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
  prediction: number;
  turnover_probability: number;
  turnover_probability_percent: number;
  risk_level: string;
  risk_color: string;
  risk_emoji: string;
  features_used: any;
  model_path: string;
  computed_at: string;
}

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
        console.log("🔄 Chargement des employés...");
        const token = localStorage.getItem("access_token");
        console.log("Token présent:", token ? "Oui" : "Non");
        
        const response = await fetch(
          "http://localhost:8000/api/v1/hr-analytics/employees?all=true",
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );

        console.log("Response status:", response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log("✅ Employés chargés:", data.length, "employés");
          console.log("Premier employé:", data[0]);
          setEmployees(data);
        } else {
          const errorText = await response.text();
          console.error("❌ Erreur HTTP:", response.status, errorText);
          setError("Erreur lors du chargement des employés");
        }
      } catch (err) {
        console.error("❌ Error loading employees:", err);
        setError("Erreur de connexion au serveur");
      } finally {
        setLoadingEmployees(false);
      }
    };

    fetchEmployees();
  }, []);

  const filteredEmployees = employees.filter((emp) => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      emp.full_name?.toLowerCase().includes(search) ||
      emp.first_name?.toLowerCase().includes(search) ||
      emp.last_name?.toLowerCase().includes(search) ||
      emp.employee_code?.toLowerCase().includes(search) ||
      emp.id.toString().includes(search)
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
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        
        console.log("📊 Données reçues de l'API:", data);
        
        if (!data.hire_date) {
          setError(
            `⚠️ Date d'embauche manquante pour cet employé.\n` +
            `Veuillez compléter le profil de l'employé dans la base de données.`
          );
          setLoading(false);
          return;
        }
        
        let birthDate = data.date_of_birth;
        let usingDefault = false;
        if (!birthDate) {
          const today = new Date();
          const defaultAge = 35;
          const defaultBirthYear = today.getFullYear() - defaultAge;
          birthDate = `${defaultBirthYear}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
          console.log(`⚠️ Date de naissance manquante, utilisation âge par défaut: ${defaultAge} ans`);
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
        
        console.log("✅ Formulaire pré-rempli:", newFormData);
        setFormData(newFormData);
        
        setError("");
      } else {
        try {
          const errorData = await response.json();
          const errorMessage = errorData.detail || `Erreur HTTP ${response.status}`;
          console.error("❌ Erreur API:", response.status, errorMessage);
          
          if (response.status === 401) {
            setError(
              "⚠️ Session expirée ou token invalide.\n" +
              "Veuillez vous reconnecter à l'application."
            );
            setTimeout(() => {
              window.location.href = "/login";
            }, 2000);
          } else {
            setError(`Erreur: ${errorMessage}`);
          }
        } catch {
          console.error("❌ Erreur HTTP:", response.status);
          if (response.status === 401) {
            setError("⚠️ Session expirée. Veuillez vous reconnecter.");
            setTimeout(() => {
              window.location.href = "/login";
            }, 2000);
          } else {
            setError(`Erreur lors du chargement des données (${response.status})`);
          }
        }
      }
    } catch (err) {
      console.error("Error loading employee turnover data:", err);
      setError("Erreur de connexion au serveur");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedEmployee) {
      setError("Veuillez sélectionner un employé");
      return;
    }

    if (!formData.date_embauche) {
      setError("Date d'embauche manquante - veuillez recharger");
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

  const getRiskBadgeColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "faible":
        return "bg-green-100 text-green-800 border-green-300";
      case "moyen":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "élevé":
        return "bg-red-100 text-red-800 border-red-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
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
    return years.toFixed(1);
  };

  return (
    <MainLayout>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-600 to-red-700 text-white py-8 shadow-md">
          <div className="max-w-6xl mx-auto px-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold">Analyse Prédictive du Turnover</h1>
              </div>
              <div className="hidden md:flex items-center gap-2 bg-white/10 px-4 py-2 rounded-lg backdrop-blur-sm">
                <BarChart3 className="w-5 h-5" />
                <span className="text-sm font-medium">Analyse RH</span>
              </div>
            </div>
          </div>
        </div>

        {/* Contenu principal */}
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Formulaire */}
            <div className="bg-white rounded-xl shadow-md p-8 border border-gray-200">
              {/* Sélection d'employé */}
              <div className="mb-6">
                <div className="flex items-center gap-3 mb-4 pb-3 border-b border-gray-200">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Users className="w-5 h-5 text-blue-600" />
                  </div>
                  <h2 className="text-xl font-semibold text-gray-800">
                    Sélection de l'employé
                  </h2>
                </div>

                {/* Champ de recherche */}
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    type="text"
                    placeholder={
                      loadingEmployees
                        ? "Chargement..."
                        : employees.length === 0
                        ? "Aucun employé trouvé"
                        : `Rechercher parmi ${employees.length} employés...`
                    }
                    value={searchTerm}
                    onChange={(e) => {
                      setSearchTerm(e.target.value);
                      setShowDropdown(true);
                    }}
                    onFocus={() => setShowDropdown(true)}
                    onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
                    disabled={loadingEmployees || employees.length === 0}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100"
                  />

                  {!loadingEmployees && employees.length === 0 && !error && (
                    <div className="mt-3 text-sm text-orange-600 bg-orange-50 border border-orange-200 rounded-lg p-3">
                      ⚠️ Aucun employé trouvé dans la base de données. Vérifiez votre connexion.
                    </div>
                  )}

                  {/* Dropdown des employés */}
                  {showDropdown && !loadingEmployees && filteredEmployees.length > 0 && (
                    <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-80 overflow-y-auto">
                      {filteredEmployees.slice(0, 50).map((emp) => (
                        <div
                          key={emp.id}
                          onClick={() => selectEmployee(emp)}
                          className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0 transition-colors"
                        >
                          <div className="flex justify-between items-center">
                            <div>
                              <p className="font-semibold text-gray-800">
                                {emp.full_name}
                              </p>
                              <p className="text-sm text-gray-500">
                                {emp.employee_code} • {emp.department_name || "N/A"}
                              </p>
                            </div>
                            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded font-medium">
                              {emp.employee_code}
                            </span>
                          </div>
                        </div>
                      ))}
                      {filteredEmployees.length > 50 && (
                        <div className="px-4 py-2 text-sm text-gray-500 text-center">
                          +{filteredEmployees.length - 50} autres... Affinez votre recherche
                        </div>
                      )}
                    </div>
                  )}

                  {showDropdown &&
                    searchTerm &&
                    filteredEmployees.length === 0 &&
                    !loadingEmployees && (
                      <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg p-4 text-center">
                        <p className="text-gray-500">
                          Aucun employé trouvé pour "{searchTerm}"
                        </p>
                      </div>
                    )}
                </div>

                {/* Badge employé sélectionné */}
                {selectedEmployee && (
                  <div className="mt-3 flex items-center gap-2 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-3">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <div className="flex-1">
                      <p className="text-sm font-semibold text-green-800">
                        Employé sélectionné
                      </p>
                      <p className="text-xs text-green-600">
                        {selectedEmployee.full_name} • {selectedEmployee.employee_code}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Formulaire de données - LECTURE SEULE */}
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Note explicative */}
                {selectedEmployee && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-semibold text-blue-900">
                        Données calculées automatiquement
                      </p>
                      <p className="text-xs text-blue-700 mt-1">
                        Toutes les informations sont chargées depuis la base de données. Aucune saisie manuelle requise.
                      </p>
                    </div>
                  </div>
                )}

                {/* Informations personnelles */}
                <div className="space-y-4">
                  <div className="bg-blue-50 px-3 py-2 rounded-lg border-l-4 border-blue-500">
                    <h3 className="text-sm font-semibold text-blue-900 flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      Informations personnelles
                    </h3>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Date de naissance
                        {usingDefaultBirthDate && (
                          <span className="ml-2 text-xs bg-orange-100 text-orange-700 px-2 py-0.5 rounded">
                            Âge par défaut: 35 ans
                          </span>
                        )}
                      </label>
                      <input
                        type="date"
                        value={formData.date_naissance}
                        disabled
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 cursor-not-allowed"
                      />
                      {formData.date_naissance && (
                        <p className="text-xs text-gray-500 mt-1">
                         Âge: {calculateAge(formData.date_naissance)} ans (auto-calculé)
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Sexe
                      </label>
                      <input
                        type="text"
                        value={formData.sexe}
                        disabled
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 cursor-not-allowed"
                      />
                    </div>
                  </div>
                </div>

                {/* Informations professionnelles */}
                <div className="space-y-4">
                  <div className="bg-green-50 px-3 py-2 rounded-lg border-l-4 border-green-500">
                    <h3 className="text-sm font-semibold text-green-900 flex items-center gap-2">
                      <Briefcase className="w-4 h-4" />
                      Informations professionnelles
                    </h3>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Date d'embauche
                      </label>
                      <input
                        type="date"
                        value={formData.date_embauche}
                        disabled
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 cursor-not-allowed"
                      />
                      {formData.date_embauche && (
                        <p className="text-xs text-gray-500 mt-1">
                          Ancienneté: {calculateAnciennete(formData.date_embauche)} ans (auto-calculée)
                        </p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Type de contrat
                      </label>
                      <input
                        type="text"
                        value={formData.type_contrat}
                        disabled
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 cursor-not-allowed"
                      />
                    </div>
                  </div>
                </div>

                {/* Absences */}
                <div className="space-y-4">
                  <div className="bg-orange-50 px-3 py-2 rounded-lg border-l-4 border-orange-500">
                    <h3 className="text-sm font-semibold text-orange-900 flex items-center gap-2">
                      <Activity className="w-4 h-4" />
                      Absences
                    </h3>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nombre d'absences
                      </label>
                      <input
                        type="number"
                        value={formData.nb_absences}
                        disabled
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 cursor-not-allowed"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Total jours d'absence
                      </label>
                      <input
                        type="number"
                        value={formData.total_jours_absence}
                        disabled
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50 cursor-not-allowed"
                      />
                    </div>
                  </div>

                  {/* Note absences */}
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                    <p className="text-xs text-gray-600">
                      📊 <strong>Absences calculées depuis les congés approuvés</strong> dans la base de données
                    </p>
                  </div>
                </div>

                {/* Bouton */}
                <button
                  type="submit"
                  disabled={loading || !selectedEmployee}
                  className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-4 rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 font-semibold text-lg transition-all shadow-lg hover:shadow-xl"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-6 h-6 animate-spin" />
                      Analyse en cours...
                    </>
                  ) : (
                    <>
                      <TrendingUp className="w-6 h-6" />
                      Prédire le Turnover
                    </>
                  )}
                </button>
              </form>
            </div>

            {/* Résultats */}
            <div>
              {/* Erreur */}
              {error && (
                <div className="bg-gradient-to-r from-red-50 to-rose-50 border-l-4 border-red-500 rounded-lg p-6 mb-6 shadow-sm">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-red-100 rounded-lg">
                      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-red-900 mb-1">Erreur</h3>
                      <p className="text-sm text-red-700 whitespace-pre-line">{error}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Résultat */}
              {result && (
                <div className="space-y-6">
                  {/* Carte principale */}
                  <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-200">
                    <div className="text-center">
                      {/* Score */}
                      <div className="inline-flex items-center justify-center w-40 h-40 rounded-full bg-gradient-to-br from-blue-50 to-blue-100 mb-4 shadow-inner">
                        <div className="text-center">
                          <div className="text-5xl font-bold text-blue-700">
                            {result.turnover_probability_percent.toFixed(1)}%
                          </div>
                          <div className="text-xs text-blue-600 mt-1 font-medium">
                            Probabilité
                          </div>
                        </div>
                      </div>

                      {/* Niveau de risque */}
                      <div className={`inline-block px-6 py-2 rounded-full border-2 font-semibold mb-4 ${getRiskBadgeColor(result.risk_level)}`}>
                        Risque {result.risk_level}
                      </div>

                      {/* Prédiction */}
                      <div className="mt-4">
                        {result.prediction === 1 ? (
                          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                            <p className="text-red-800 font-semibold">
                              ⚠️ Risque de départ élevé
                            </p>
                          </div>
                        ) : (
                          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <p className="text-green-800 font-semibold">
                              ✅ Devrait rester dans l'entreprise
                            </p>
                          </div>
                        )}
                      </div>

                      {/* Info employé */}
                      {selectedEmployee && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <p className="text-sm text-gray-600 flex items-center justify-center gap-2">
                            <Users className="w-4 h-4" />
                            <span className="font-medium">{selectedEmployee.full_name}</span>
                            <span className="text-gray-400">•</span>
                            <span className="text-gray-500">{selectedEmployee.employee_code}</span>
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Features utilisées */}
                  <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                      <Activity className="w-5 h-5 text-blue-600" />
                      Indicateurs utilisés
                    </h3>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                        <p className="text-xs text-blue-600 mb-1 font-medium">Âge</p>
                        <p className="text-2xl font-bold text-blue-900">
                          {result.features_used.age} ans
                        </p>
                      </div>

                      <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4 border border-green-200">
                        <p className="text-xs text-green-600 mb-1 font-medium">Ancienneté</p>
                        <p className="text-2xl font-bold text-green-900">
                          {result.features_used.anciennete_annees.toFixed(1)} ans
                        </p>
                      </div>

                      <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-4 border border-orange-200">
                        <p className="text-xs text-orange-600 mb-1 font-medium">Nb absences</p>
                        <p className="text-2xl font-bold text-orange-900">
                          {result.features_used.nb_absences}
                        </p>
                      </div>

                      <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4 border border-purple-200">
                        <p className="text-xs text-purple-600 mb-1 font-medium">Jours absence</p>
                        <p className="text-2xl font-bold text-purple-900">
                          {result.features_used.total_jours_absence}
                        </p>
                      </div>

                      <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg p-4 col-span-2 border border-gray-200">
                        <p className="text-xs text-gray-600 mb-1 font-medium">Durée de présence</p>
                        <p className="text-2xl font-bold text-gray-900">
                          {result.features_used.duree_presence_jours} jours
                        </p>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="flex items-center gap-2 text-xs text-gray-500 mb-1">
                        <BarChart3 className="w-3 h-3" />
                        <span>Modèle: {result.model_path.split("\\").pop()}</span>
                      </div>
                      <p className="text-xs text-gray-500">
                        Calculé le: {new Date(result.computed_at).toLocaleString("fr-FR")}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* État vide */}
              {!result && !error && (
                <div className="bg-white rounded-2xl shadow-lg p-12 text-center border border-gray-200">
                  <div className="w-20 h-20 mx-auto mb-4 bg-blue-50 rounded-full flex items-center justify-center">
                    <BarChart3 className="w-10 h-10 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">
                    {selectedEmployee
                      ? "Prêt pour l'analyse"
                      : "Sélectionnez un employé"}
                  </h3>
                  <p className="text-gray-500 text-sm">
                    {selectedEmployee
                      ? "Cliquez sur le bouton pour lancer la prédiction"
                      : "Les données seront chargées automatiquement depuis la base de données"}
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
