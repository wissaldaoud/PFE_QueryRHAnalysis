"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import MainLayout from "@/components/MainLayout";
import { 
  ArrowLeft, 
  GraduationCap,
  Sparkles,
  TrendingUp,
  Award,
  Clock
} from "lucide-react";

interface TrainingCourse {
  id: string;
  title: string;
  description: string;
  skills_taught: string[];
  duration_hours: number;
  level: string;
}

interface TrainingRecommendation {
  course: TrainingCourse;
  relevance_score: number;
  reason: string;
  skills_to_gain: string[];
  priority: string;
}

export default function TrainingRecommendationPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<TrainingRecommendation[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Employee Form State
  const [employeeId, setEmployeeId] = useState("");
  const [currentSkills, setCurrentSkills] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [yearsExp, setYearsExp] = useState("2");
  const [department, setDepartment] = useState("IT");
  const [careerGoals, setCareerGoals] = useState("");

  // Catalog de formations pré-définies
  const TRAINING_CATALOG = [
    {
      id: "ML101",
      title: "Introduction au Machine Learning",
      description: "Apprenez les bases du ML avec Python, scikit-learn et TensorFlow. Projets pratiques inclus.",
      skills_taught: "Machine Learning, Python, scikit-learn, TensorFlow, Data Analysis",
      duration_hours: "40",
      level: "Intermédiaire"
    },
    {
      id: "FASTAPI",
      title: "Développement API avec FastAPI",
      description: "Créez des API REST performantes avec FastAPI, PostgreSQL et Docker.",
      skills_taught: "FastAPI, Python, REST API, PostgreSQL, Docker",
      duration_hours: "24",
      level: "Intermédiaire"
    },
    {
      id: "REACT",
      title: "React et Next.js Avancé",
      description: "Maîtrisez React 18 et Next.js 14 pour des applications web modernes.",
      skills_taught: "React, Next.js, TypeScript, Tailwind CSS, Server Components",
      duration_hours: "32",
      level: "Intermédiaire"
    },
    {
      id: "K8S",
      title: "Kubernetes et DevOps",
      description: "Déploiement et orchestration de containers avec Kubernetes sur AWS et Azure.",
      skills_taught: "Kubernetes, Docker, AWS, Azure, CI/CD, Terraform",
      duration_hours: "40",
      level: "Avancé"
    },
    {
      id: "DATA",
      title: "Data Science avec Python",
      description: "Analyse de données, visualisation et statistiques avec Pandas, NumPy et Matplotlib.",
      skills_taught: "Python, Pandas, NumPy, Matplotlib, Statistics, Data Analysis",
      duration_hours: "36",
      level: "Débutant"
    },
    {
      id: "SECURITY",
      title: "Sécurité des Applications Web",
      description: "Protégez vos applications contre les vulnérabilités OWASP Top 10.",
      skills_taught: "Security, OWASP, Penetration Testing, JWT, OAuth2",
      duration_hours: "28",
      level: "Intermédiaire"
    }
  ];

  const [courses, setCourses] = useState(TRAINING_CATALOG);

  const loadExample = () => {
    setEmployeeId("EMP001");
    setCurrentSkills("Python, SQL, Git");
    setJobTitle("Développeur Junior");
    setYearsExp("1.5");
    setDepartment("IT");
    setCareerGoals("Devenir expert en Machine Learning et Data Science");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setRecommendations([]);

    const requestData = {
      employee: {
        id: employeeId,
        current_skills: currentSkills.split(",").map(s => s.trim()).filter(s => s),
        job_title: jobTitle,
        years_of_experience: parseFloat(yearsExp) || 0,
        department: department,
        career_goals: careerGoals
      },
      courses: courses.map(c => ({
        id: c.id,
        title: c.title,
        description: c.description,
        skills_taught: c.skills_taught.split(",").map(s => s.trim()).filter(s => s),
        duration_hours: parseInt(c.duration_hours) || 0,
        level: c.level
      }))
    };

    try {
      const response = await fetch("http://localhost:8000/api/v1/hr-analytics/training-recommendation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setRecommendations(data.data.recommendations || []);
    } catch (err: any) {
      setError(err.message || "Une erreur est survenue");
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toUpperCase()) {
      case "HAUTE": return "text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30";
      case "MOYENNE": return "text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/30";
      case "BASSE": return "text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/30";
      default: return "text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-800";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "text-green-600";
    if (score >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  return (
    <MainLayout>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 dark:from-gray-900 dark:to-gray-800">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => router.back()}
                  className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                >
                  <ArrowLeft className="h-6 w-6 text-gray-600 dark:text-gray-300" />
                </button>
                <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl">
                  <GraduationCap className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Recommandation de Formations
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Formations personnalisées basées sur le profil
                  </p>
                </div>
              </div>
              <button
                onClick={loadExample}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
              >
                Charger un exemple
              </button>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            {/* Form Section */}
            <div className="space-y-6">
              {/* Employee Profile */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <span className="mr-2">👤</span> Profil Employé
                </h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      ID Employé
                    </label>
                    <input
                      type="text"
                      value={employeeId}
                      onChange={(e) => setEmployeeId(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="EMP001"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Compétences actuelles (virgules)
                    </label>
                    <input
                      type="text"
                      value={currentSkills}
                      onChange={(e) => setCurrentSkills(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Python, SQL, Git..."
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Poste actuel
                      </label>
                      <input
                        type="text"
                        value={jobTitle}
                        onChange={(e) => setJobTitle(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        placeholder="Développeur"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Années d'exp
                      </label>
                      <input
                        type="number"
                        step="0.5"
                        value={yearsExp}
                        onChange={(e) => setYearsExp(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Département
                    </label>
                    <select
                      value={department}
                      onChange={(e) => setDepartment(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value="IT">IT</option>
                      <option value="RH">RH</option>
                      <option value="Finance">Finance</option>
                      <option value="Marketing">Marketing</option>
                      <option value="Ventes">Ventes</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Objectifs de carrière
                    </label>
                    <textarea
                      value={careerGoals}
                      onChange={(e) => setCareerGoals(e.target.value)}
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Devenir expert en..."
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg 
                             hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed
                             font-semibold flex items-center justify-center space-x-2 shadow-lg"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Analyse en cours...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-5 w-5" />
                        <span>Obtenir Recommandations</span>
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* Course Catalog Info */}
              <div className="bg-purple-50 dark:bg-purple-900/20 rounded-xl p-4 border-2 border-purple-200 dark:border-purple-800">
                <h3 className="font-semibold text-purple-900 dark:text-purple-200 mb-2 flex items-center">
                  <Award className="w-5 h-5 mr-2" />
                  📚 Catalogue de {courses.length} formations disponibles
                </h3>
                <p className="text-sm text-purple-700 dark:text-purple-300">
                  L'IA sélectionnera les formations les plus pertinentes selon votre profil et objectifs.
                </p>
              </div>
            </div>

            {/* Results Section */}
            <div className="space-y-6">
              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-xl p-4">
                  <p className="text-red-700 dark:text-red-300">❌ {error}</p>
                </div>
              )}

              {recommendations.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                    <TrendingUp className="mr-2 h-6 w-6 text-purple-600" />
                    Top {recommendations.length} Formations Recommandées
                  </h2>

                  <div className="space-y-4">
                    {recommendations.map((rec, index) => (
                      <div
                        key={rec.course.id}
                        className="border-2 border-purple-200 dark:border-purple-800 rounded-lg p-4 
                                hover:border-purple-400 dark:hover:border-purple-600 transition-all hover:shadow-md"
                      >
                        {/* Header */}
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-start space-x-3">
                            <div className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full 
                                          flex items-center justify-center font-bold">
                              {index + 1}
                            </div>
                            <div>
                              <h3 className="font-semibold text-lg text-gray-900 dark:text-white">
                                {rec.course.title}
                              </h3>
                              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                {rec.course.description}
                              </p>
                            </div>
                          </div>
                        </div>

                        {/* Metrics */}
                        <div className="grid grid-cols-3 gap-3 mb-3">
                          <div className="text-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
                            <div className={`text-2xl font-bold ${getScoreColor(rec.relevance_score)}`}>
                              {(rec.relevance_score * 100).toFixed(0)}%
                            </div>
                            <div className="text-xs text-gray-600 dark:text-gray-400">Pertinence</div>
                          </div>
                          
                          <div className="text-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
                            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400 flex items-center justify-center">
                              <Clock className="w-5 h-5 mr-1" />
                              {rec.course.duration_hours}h
                            </div>
                            <div className="text-xs text-gray-600 dark:text-gray-400">Durée</div>
                          </div>

                          <div className="text-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
                            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getPriorityColor(rec.priority)}`}>
                              {rec.priority}
                            </div>
                            <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">Priorité</div>
                          </div>
                        </div>

                        {/* Reason */}
                        <div className="mb-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                          <p className="text-sm text-blue-900 dark:text-blue-200">
                            <strong>💡 Pourquoi cette formation :</strong> {rec.reason}
                          </p>
                        </div>

                        {/* Skills to Gain */}
                        {rec.skills_to_gain && rec.skills_to_gain.length > 0 && (
                          <div>
                            <p className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-2">
                              ✨ Compétences à acquérir :
                            </p>
                            <div className="flex flex-wrap gap-2">
                              {rec.skills_to_gain.map((skill, idx) => (
                                <span
                                  key={idx}
                                  className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 
                                           rounded-full text-xs font-medium"
                                >
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Level Badge */}
                        <div className="mt-3 flex items-center justify-between">
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            Niveau : <span className="font-semibold">{rec.course.level}</span>
                          </span>
                          <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 
                                          text-sm font-medium transition-colors">
                            S'inscrire
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {!loading && recommendations.length === 0 && !error && (
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center">
                  <GraduationCap className="h-24 w-24 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400 text-lg">
                    Remplissez le formulaire pour obtenir des recommandations personnalisées
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
