"use client";

import { useState, useEffect } from "react";
import { 
  ChevronRight, Home, TrendingDown, User, Calendar, 
  Briefcase, Activity, Clock, ChevronDown, ChevronUp,
  Search, AlertCircle, CheckCircle2, TrendingUp as TrendUp,
  Users, Building2, Gauge, ArrowUpRight, ArrowDownRight
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
  prediction: number;
  turnover_probability: number;
  turnover_probability_percent: number;
  risk_level: string;
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
  const [expandedSection, setExpandedSection] = useState<string>("employee");

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
          birthDate = `${defaultBirthYear}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
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
    return years.toFixed(1);
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getRiskConfig = (level: string) => {
    const configs: Record<string, { color: string; bg: string; dot: string; label: string }> = {
      faible: {
        color: '#065F46',
        bg: '#D1FAE5',
        dot: '#10B981',
        label: 'Risque Faible'
      },
      moyen: {
        color: '#92400E',
        bg: '#FEF3C7',
        dot: '#F59E0B',
        label: 'Risque Moyen'
      },
      élevé: {
        color: '#991B1B',
        bg: '#FEE2E2',
        dot: '#EF4444',
        label: 'Risque Élevé'
      },
    };
    return configs[level.toLowerCase()] || configs.faible;
  };

  const toggleSection = (section: string) => {
    setExpandedSection(expandedSection === section ? "" : section);
  };

  return (
    <MainLayout>
      <div className="min-h-screen bg-[#F4F6F9]" style={{ fontFamily: "'Inter', sans-serif" }}>
        {/* Professional Header with Breadcrumb */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-6 py-4">
            {/* Breadcrumb */}
            <div className="flex items-center text-sm text-gray-500 mb-3">
              <Home className="w-4 h-4" />
              <ChevronRight className="w-4 h-4 mx-2" />
              <span>Analytics RH</span>
              <ChevronRight className="w-4 h-4 mx-2" />
              <span className="text-[#1E3A5F] font-medium">Analyse Prédictive du Turnover</span>
            </div>

            {/* Title Section */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4 border-l-4 border-[#C0392B] pl-4">
                <div className="p-2.5 bg-gradient-to-br from-[#1E3A5F] to-[#2C5282] rounded-lg">
                  <TrendingDown className="w-6 h-6 text-white" strokeWidth={2.5} />
                </div>
                <div>
                  <h1 className="text-2xl font-semibold text-[#1E3A5F] tracking-tight">
                    Analyse Prédictive du Turnover
                  </h1>
                  <p className="text-sm text-gray-600 mt-0.5">
                    Modèle de Machine Learning • Prédiction en temps réel
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="px-3 py-1.5 bg-gray-100 rounded-lg text-xs font-medium text-gray-700">
                  <Users className="w-3.5 h-3.5 inline mr-1.5" />
                  {employees.length} employés
                </div>
                <div className="px-3 py-1.5 bg-green-50 rounded-lg text-xs font-medium text-green-700">
                  <CheckCircle2 className="w-3.5 h-3.5 inline mr-1.5" />
                  Modèle actif
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content - Two Column Layout */}
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            
            {/* Left Column - Form (55%) */}
            <div className="lg:col-span-7 space-y-5">
              
              {/* Employee Selection Card */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                {/* Collapsible Header */}
                <button
                  onClick={() => toggleSection("employee")}
                  className="w-full px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors border-b border-gray-100"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-1 h-8 bg-[#C0392B] rounded-full" />
                    <User className="w-5 h-5 text-[#1E3A5F]" />
                    <div className="text-left">
                      <h3 className="text-xs font-semibold text-[#1E3A5F] uppercase tracking-wider">
                        Sélection Employé
                      </h3>
                      <p className="text-xs text-gray-500 mt-0.5">Rechercher et sélectionner</p>
                    </div>
                  </div>
                  {expandedSection === "employee" ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </button>

                {/* Content */}
                {expandedSection === "employee" && (
                  <div className="p-5 space-y-4">
                    {/* Search */}
                    <div className="relative">
                      <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                        Rechercher un employé
                      </label>
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                          type="text"
                          placeholder={loadingEmployees ? "Chargement..." : `Rechercher parmi ${employees.length} employés...`}
                          value={searchTerm}
                          onChange={(e) => {
                            setSearchTerm(e.target.value);
                            setShowDropdown(true);
                          }}
                          onFocus={() => setShowDropdown(true)}
                          onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
                          disabled={loadingEmployees}
                          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1E3A5F] focus:border-transparent transition-shadow text-sm"
                        />
                      </div>

                      {/* Dropdown */}
                      {showDropdown && !loadingEmployees && filteredEmployees.length > 0 && (
                        <div className="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-80 overflow-y-auto">
                          {filteredEmployees.slice(0, 50).map((emp) => (
                            <div
                              key={emp.id}
                              onClick={() => selectEmployee(emp)}
                              className="px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0 transition-colors"
                            >
                              <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-gradient-to-br from-[#1E3A5F] to-[#2C5282] rounded-lg flex items-center justify-center">
                                  <span className="text-white text-sm font-semibold">
                                    {getInitials(emp.full_name)}
                                  </span>
                                </div>
                                <div className="flex-1">
                                  <p className="font-medium text-gray-900 text-sm">{emp.full_name}</p>
                                  <p className="text-xs text-gray-500">
                                    {emp.employee_code} • {emp.department_name || "N/A"}
                                  </p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Selected Employee Profile Card */}
                    {selectedEmployee && (
                      <div className="mt-4 p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg border border-gray-200">
                        <div className="flex items-start space-x-4">
                          <div className="w-16 h-16 bg-gradient-to-br from-[#1E3A5F] to-[#2C5282] rounded-xl flex items-center justify-center shadow-lg">
                            <span className="text-white text-xl font-bold">
                              {getInitials(selectedEmployee.full_name)}
                            </span>
                          </div>
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900 mb-1">{selectedEmployee.full_name}</h4>
                            <div className="flex flex-wrap gap-2 mb-2">
                              <span className="px-2 py-0.5 bg-white rounded text-xs font-medium text-gray-700 border border-gray-200">
                                ID: {selectedEmployee.employee_code}
                              </span>
                              {selectedEmployee.department_name && (
                                <span className="px-2 py-0.5 bg-blue-50 rounded text-xs font-medium text-blue-700 border border-blue-200">
                                  <Building2 className="w-3 h-3 inline mr-1" />
                                  {selectedEmployee.department_name}
                                </span>
                              )}
                            </div>
                            {formData.date_embauche && (
                              <div className="grid grid-cols-2 gap-2 text-xs">
                                <div>
                                  <span className="text-gray-500">Âge:</span>
                                  <span className="ml-1 font-semibold text-gray-900">
                                    {calculateAge(formData.date_naissance)} ans
                                  </span>
                                </div>
                                <div>
                                  <span className="text-gray-500">Ancienneté:</span>
                                  <span className="ml-1 font-semibold text-gray-900">
                                    {calculateAnciennete(formData.date_embauche)} ans
                                  </span>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Parameters Card */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <button
                  onClick={() => toggleSection("parameters")}
                  className="w-full px-5 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors border-b border-gray-100"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-1 h-8 bg-[#2C5282] rounded-full" />
                    <Activity className="w-5 h-5 text-[#1E3A5F]" />
                    <div className="text-left">
                      <h3 className="text-xs font-semibold text-[#1E3A5F] uppercase tracking-wider">
                        Paramètres d'Analyse
                      </h3>
                      <p className="text-xs text-gray-500 mt-0.5">Ajuster les données</p>
                    </div>
                  </div>
                  {expandedSection === "parameters" ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </button>

                {expandedSection === "parameters" && (
                  <form onSubmit={handleSubmit} className="p-5 space-y-4">
                    <div>
                      <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                        Sexe
                      </label>
                      <select
                        value={formData.sexe}
                        onChange={(e) => setFormData({ ...formData, sexe: e.target.value })}
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1E3A5F] focus:border-transparent transition-shadow text-sm"
                      >
                        <option value="Masculin">Masculin</option>
                        <option value="Féminin">Féminin</option>
                      </select>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                          Jours d'absence
                        </label>
                        <input
                          type="number"
                          min="0"
                          value={formData.total_jours_absence}
                          onChange={(e) =>
                            setFormData({ ...formData, total_jours_absence: e.target.value })
                          }
                          className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1E3A5F] focus:border-transparent transition-shadow text-sm"
                        />
                      </div>

                      <div>
                        <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-2">
                          Nb. absences
                        </label>
                        <input
                          type="number"
                          min="0"
                          value={formData.nb_absences}
                          onChange={(e) =>
                            setFormData({ ...formData, nb_absences: e.target.value })
                          }
                          className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1E3A5F] focus:border-transparent transition-shadow text-sm"
                        />
                      </div>
                    </div>

                    {usingDefaultBirthDate && (
                      <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-start space-x-2">
                        <AlertCircle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                        <p className="text-xs text-amber-800">
                          Date de naissance absente - âge estimé à 35 ans
                        </p>
                      </div>
                    )}

                    <button
                      type="submit"
                      disabled={loading || !selectedEmployee}
                      className="w-full mt-4 py-3.5 px-4 bg-gradient-to-r from-[#1E3A5F] to-[#2C5282] text-white font-semibold rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center"
                    >
                      {loading ? (
                        <>
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Analyse en cours...
                        </>
                      ) : (
                        <>
                          <Gauge className="w-5 h-5 mr-2" />
                          Lancer l'Analyse Prédictive
                        </>
                      )}
                    </button>
                  </form>
                )}
              </div>
            </div>

            {/* Right Column - Results (45%) - Sticky */}
            <div className="lg:col-span-5">
              <div className="sticky top-6 space-y-5">
                
                {/* Error Alert */}
                {error && (
                  <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold text-red-900 text-sm">Erreur</h4>
                      <p className="text-sm text-red-700 mt-1">{error}</p>
                    </div>
                  </div>
                )}

                {/* Prediction Result */}
                {result && (
                  <>
                    {/* Gauge Chart Card */}
                    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-shadow duration-300">
                      <div className="text-center">
                        <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-4">
                          Probabilité de Turnover
                        </h3>
                        
                        {/* Animated Gauge/Arc */}
                        <div className="relative w-48 h-24 mx-auto mb-4">
                          <svg className="w-full h-full" viewBox="0 0 200 100">
                            {/* Background arc */}
                            <path
                              d="M 20 90 A 80 80 0 0 1 180 90"
                              fill="none"
                              stroke="#E5E7EB"
                              strokeWidth="20"
                              strokeLinecap="round"
                            />
                            {/* Color zones */}
                            <path
                              d="M 20 90 A 80 80 0 0 1 95 18"
                              fill="none"
                              stroke="#10B981"
                              strokeWidth="20"
                              strokeLinecap="round"
                              opacity="0.3"
                            />
                            <path
                              d="M 95 18 A 80 80 0 0 1 105 18"
                              fill="none"
                              stroke="#F59E0B"
                              strokeWidth="20"
                              strokeLinecap="round"
                              opacity="0.3"
                            />
                            <path
                              d="M 105 18 A 80 80 0 0 1 180 90"
                              fill="none"
                              stroke="#EF4444"
                              strokeWidth="20"
                              strokeLinecap="round"
                              opacity="0.3"
                            />
                            {/* Value arc */}
                            <path
                              d={`M 20 90 A 80 80 0 0 1 ${20 + (160 * result.turnover_probability_percent / 100)} ${90 - (80 * Math.sin((Math.PI * result.turnover_probability_percent / 100)))}`}
                              fill="none"
                              stroke={result.turnover_probability_percent < 30 ? "#10B981" : result.turnover_probability_percent < 60 ? "#F59E0B" : "#EF4444"}
                              strokeWidth="20"
                              strokeLinecap="round"
                              style={{ 
                                transition: 'all 1s ease-out',
                                filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))'
                              }}
                            />
                            {/* Needle */}
                            <circle cx="100" cy="90" r="8" fill="#1E3A5F" />
                          </svg>
                        </div>

                        {/* Value Display */}
                        <div className="mb-4">
                          <div className="text-5xl font-bold text-[#1E3A5F] mb-1">
                            {result.turnover_probability_percent.toFixed(1)}%
                          </div>
                          <div className="text-sm text-gray-600">
                            Probabilité de départ
                          </div>
                        </div>

                        {/* Status Badge */}
                        <div className="inline-flex items-center px-4 py-2 rounded-full"
                          style={{ 
                            backgroundColor: getRiskConfig(result.risk_level).bg,
                            color: getRiskConfig(result.risk_level).color
                          }}
                        >
                          <div className="w-2 h-2 rounded-full mr-2"
                            style={{ backgroundColor: getRiskConfig(result.risk_level).dot }}
                          />
                          <span className="text-sm font-semibold">
                            {getRiskConfig(result.risk_level).label}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* KPI Cards */}
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between mb-2">
                          <Calendar className="w-5 h-5 text-blue-500" />
                          <ArrowUpRight className="w-4 h-4 text-green-500" />
                        </div>
                        <div className="text-2xl font-bold text-gray-900 mb-1">
                          {result.features_used.age}
                        </div>
                        <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Âge (ans)
                        </div>
                      </div>

                      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between mb-2">
                          <Briefcase className="w-5 h-5 text-purple-500" />
                          <ArrowUpRight className="w-4 h-4 text-green-500" />
                        </div>
                        <div className="text-2xl font-bold text-gray-900 mb-1">
                          {result.features_used.anciennete_annees.toFixed(1)}
                        </div>
                        <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Ancienneté (ans)
                        </div>
                      </div>

                      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between mb-2">
                          <Activity className="w-5 h-5 text-orange-500" />
                          {result.features_used.total_jours_absence > 10 ? (
                            <ArrowDownRight className="w-4 h-4 text-red-500" />
                          ) : (
                            <ArrowUpRight className="w-4 h-4 text-green-500" />
                          )}
                        </div>
                        <div className="text-2xl font-bold text-gray-900 mb-1">
                          {result.features_used.total_jours_absence}
                        </div>
                        <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Jours absences
                        </div>
                      </div>

                      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between mb-2">
                          <Clock className="w-5 h-5 text-teal-500" />
                          {result.features_used.nb_absences > 5 ? (
                            <ArrowDownRight className="w-4 h-4 text-red-500" />
                          ) : (
                            <ArrowUpRight className="w-4 h-4 text-green-500" />
                          )}
                        </div>
                        <div className="text-2xl font-bold text-gray-900 mb-1">
                          {result.features_used.nb_absences}
                        </div>
                        <div className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Nb. absences
                        </div>
                      </div>
                    </div>

                    {/* Additional Metrics */}
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
                      <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
                        Indicateurs Utilisés
                      </h4>
                      <div className="space-y-2">
                        {Object.entries(result.features_used).map(([key, value]) => (
                          <div key={key} className="flex justify-between items-center text-sm py-1.5 border-b border-gray-100 last:border-0">
                            <span className="text-gray-600">{key.replace(/_/g, ' ')}</span>
                            <span className="font-semibold text-gray-900">
                              {typeof value === 'number' ? value.toFixed(2) : value}
                            </span>
                          </div>
                        ))}
                      </div>
                      <div className="mt-4 pt-3 border-t border-gray-200">
                        <p className="text-xs text-gray-500 flex items-center">
                          <Clock className="w-3 h-3 mr-1.5" />
                          Analysé le {new Date(result.computed_at).toLocaleString('fr-FR')}
                        </p>
                      </div>
                    </div>
                  </>
                )}

                {/* Empty State */}
                {!result && !error && !loading && (
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Gauge className="w-8 h-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      Prêt pour l'analyse
                    </h3>
                    <p className="text-sm text-gray-600">
                      Sélectionnez un employé et lancez l'analyse pour voir les résultats
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
