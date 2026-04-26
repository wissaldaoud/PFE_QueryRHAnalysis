"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import MainLayout from "@/components/MainLayout";
import {
  Upload,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ArrowLeft,
  TrendingUp,
  Award,
  BookOpen,
  Briefcase,
  Trophy,
  Medal,
  Sparkles,
} from "lucide-react";

interface RankedCV {
  rank: number;
  filename: string;
  overall_score: number;
  skills_score: number;
  experience_score: number;
  category_match_score: number;
  education_score: number;
  matching_skills: string[];
  missing_required_skills: string[];
  missing_preferred_skills: string[];
  recommendations: string[];
  predicted_category: string;
  job_category: string;
}

interface CVRankingResponse {
  success: boolean;
  total_uploaded: number;
  total_ranked: number;
  failed_files: string[];
  ranked_cvs: RankedCV[];
  best_cv: RankedCV | null;
}

const JOB_TEMPLATES = [
  {
    id: "dev-backend",
    name: "Développeur Backend Python",
    title: "Développeur Backend Python Senior",
    description: "Développement et maintenance d'API REST, architecture microservices, optimisation performances",
    required_skills: "Python, FastAPI, PostgreSQL, Docker, Git",
    preferred_skills: "AWS, Kubernetes, Redis, Machine Learning",
    required_education: "Licence Informatique, Ingénieur",
    experience: "3",
  },
  {
    id: "dev-fullstack",
    name: "Développeur Full Stack",
    title: "Développeur Full Stack",
    description: "Développement d'applications web complètes, frontend et backend, déploiement",
    required_skills: "JavaScript, React, Node.js, SQL, Git",
    preferred_skills: "TypeScript, Next.js, MongoDB, Docker",
    required_education: "Licence Informatique",
    experience: "2",
  },
  {
    id: "data-scientist",
    name: "Data Scientist",
    title: "Data Scientist",
    description: "Analyse de données, modélisation ML, visualisation, déploiement en production",
    required_skills: "Python, Machine Learning, Pandas, NumPy, scikit-learn",
    preferred_skills: "TensorFlow, PyTorch, SQL, Spark, AWS",
    required_education: "Master en Data Science, Ingénieur",
    experience: "3",
  },
  {
    id: "devops",
    name: "Ingénieur DevOps",
    title: "Ingénieur DevOps",
    description: "Automatisation déploiements, infrastructure as code, monitoring, sécurité",
    required_skills: "Docker, Kubernetes, CI/CD, Linux, Git",
    preferred_skills: "AWS, Terraform, Ansible, Monitoring, Python",
    required_education: "Ingénieur, Master Informatique",
    experience: "3",
  },
  {
    id: "custom",
    name: "✏️ Personnalisé (saisie manuelle)",
    title: "",
    description: "",
    required_skills: "",
    preferred_skills: "",
    required_education: "",
    experience: "3",
  },
];

export default function CVRankingPage() {
  const router = useRouter();

  // Job form
  const [selectedTemplate, setSelectedTemplate] = useState("custom");
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [requiredSkills, setRequiredSkills] = useState("");
  const [preferredSkills, setPreferredSkills] = useState("");
  const [requiredEducation, setRequiredEducation] = useState("");
  const [requiredExp, setRequiredExp] = useState("3");

  // Files
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  // Results
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rankingResult, setRankingResult] = useState<CVRankingResponse | null>(null);
  const [selectedCV, setSelectedCV] = useState<RankedCV | null>(null);

  const handleTemplateChange = (id: string) => {
    setSelectedTemplate(id);
    const t = JOB_TEMPLATES.find((t) => t.id === id);
    if (t) {
      setJobTitle(t.title);
      setJobDescription(t.description);
      setRequiredSkills(t.required_skills);
      setPreferredSkills(t.preferred_skills);
      setRequiredEducation(t.required_education);
      setRequiredExp(t.experience);
    }
  };

  const handleFilesSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFiles(Array.from(e.target.files || []));
    setError(null);
    setRankingResult(null);
    setSelectedCV(null);
  };

  const handleRankCVs = async () => {
    if (selectedFiles.length === 0) {
      setError("Veuillez sélectionner au moins un fichier CV");
      return;
    }
    if (!jobTitle || !jobDescription || !requiredSkills) {
      setError("Veuillez remplir le titre, la description et les compétences requises");
      return;
    }

    setLoading(true);
    setError(null);
    setRankingResult(null);
    setSelectedCV(null);

    try {
      const formData = new FormData();
      selectedFiles.forEach((f) => formData.append("files", f));
      formData.append("title", jobTitle);
      formData.append("description", jobDescription);
      formData.append("required_skills", JSON.stringify(
        requiredSkills.split(",").map((s) => s.trim()).filter(Boolean)
      ));
      formData.append("preferred_skills", JSON.stringify(
        preferredSkills.split(",").map((s) => s.trim()).filter(Boolean)
      ));
      formData.append("required_education", JSON.stringify(
        requiredEducation.split(",").map((s) => s.trim()).filter(Boolean)
      ));
      formData.append("required_experience_years", requiredExp);

      const response = await fetch("http://localhost:8000/api/v1/cv-ranking/rank", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Erreur lors du ranking");
      }

      const result: CVRankingResponse = await response.json();
      setRankingResult(result);
      if (result.ranked_cvs.length > 0) setSelectedCV(result.ranked_cvs[0]);
    } catch (err: any) {
      setError(err.message || "Une erreur est survenue");
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 75) return "text-green-600";
    if (score >= 50) return "text-orange-600";
    return "text-red-600";
  };

  const getScoreBg = (score: number) => {
    if (score >= 75) return "bg-green-100";
    if (score >= 50) return "bg-orange-100";
    return "bg-red-100";
  };

  const getScoreLabel = (score: number) => {
    if (score >= 75) return "Excellent Match";
    if (score >= 50) return "Bon Match";
    if (score >= 25) return "Match Partiel";
    return "Faible Match";
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="h-5 w-5 text-yellow-500" />;
    if (rank === 2) return <Medal className="h-5 w-5 text-gray-400" />;
    if (rank === 3) return <Medal className="h-5 w-5 text-amber-600" />;
    return <span className="text-sm font-bold text-gray-500">#{rank}</span>;
  };

  const getRankBorder = (cv: RankedCV) => {
    if (selectedCV?.filename === cv.filename) return "border-blue-500 bg-blue-50 dark:bg-blue-900/20";
    if (cv.rank === 1) return "border-yellow-400 bg-yellow-50 dark:bg-yellow-900/10";
    return "border-gray-200 bg-white dark:bg-gray-800 hover:border-gray-300";
  };

  return (
    <MainLayout>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 dark:from-gray-900 dark:to-gray-800">

        {/* Header */}
        <div className="bg-white dark:bg-gray-800 shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center space-x-4">
              <button onClick={() => router.back()} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                <ArrowLeft className="h-6 w-6 text-gray-600 dark:text-gray-300" />
              </button>
              <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl">
                <Trophy className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">CV Ranking avec IA</h1>
                <p className="text-sm text-gray-600 dark:text-gray-300">Classez plusieurs CVs contre une offre d'emploi</p>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

            {/* ===== FORMULAIRE ===== */}
            <div className="space-y-6">

              {/* Upload CVs */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <span className="mr-2">📄</span> Uploader plusieurs CVs
                </h2>
                <div className="border-2 border-dashed border-purple-300 dark:border-purple-700 rounded-lg p-8 text-center hover:border-purple-400 transition-colors">
                  <input type="file" accept=".pdf,.docx,.doc" multiple onChange={handleFilesSelect} className="hidden" id="cvs-upload" />
                  <label htmlFor="cvs-upload" className="cursor-pointer">
                    <Upload className="h-12 w-12 mx-auto text-purple-400 mb-4" />
                    {selectedFiles.length > 0 ? (
                      <div>
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">{selectedFiles.length} fichier(s) sélectionné(s)</p>
                        <div className="mt-2 max-h-32 overflow-y-auto space-y-1">
                          {selectedFiles.map((f, i) => (
                            <p key={i} className="text-xs text-gray-500">{f.name} ({(f.size / 1024).toFixed(1)} KB)</p>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div>
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Cliquez pour sélectionner plusieurs CVs</p>
                        <p className="text-xs text-gray-500 mt-1">PDF, DOCX — Maximum 50 fichiers</p>
                      </div>
                    )}
                  </label>
                </div>
              </div>

              {/* Offre d'emploi */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <span className="mr-2">💼</span> Offre d'Emploi
                </h2>

                {/* Template */}
                <div className="mb-6 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border-2 border-purple-200 dark:border-purple-800">
                  <label className="block text-sm font-semibold text-purple-900 dark:text-purple-200 mb-2 flex items-center">
                    <Sparkles className="w-4 h-4 mr-2" />
                    🚀 Sélectionner un poste type (gain de temps)
                  </label>
                  <select
                    value={selectedTemplate}
                    onChange={(e) => handleTemplateChange(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-purple-300 dark:border-purple-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-medium focus:ring-2 focus:ring-purple-500 cursor-pointer"
                  >
                    {JOB_TEMPLATES.map((t) => (
                      <option key={t.id} value={t.id}>{t.name}</option>
                    ))}
                  </select>
                  <p className="mt-2 text-xs text-purple-700 dark:text-purple-300">
                    💡 Sélectionnez un poste type pour remplir automatiquement les champs
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Titre du poste *</label>
                    <input type="text" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Ex: Développeur Backend Python" />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Description *</label>
                    <textarea value={jobDescription} onChange={(e) => setJobDescription(e.target.value)} rows={3}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Description du poste..." />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Compétences requises * (virgules)</label>
                    <input type="text" value={requiredSkills} onChange={(e) => setRequiredSkills(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Python, FastAPI, Docker..." />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Compétences préférées (virgules)</label>
                    <input type="text" value={preferredSkills} onChange={(e) => setPreferredSkills(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="AWS, Kubernetes..." />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">🎓 Formation requise (virgules)</label>
                    <input type="text" value={requiredEducation} onChange={(e) => setRequiredEducation(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Master Informatique, Ingénieur..." />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Expérience requise (années)</label>
                    <input type="number" step="0.5" value={requiredExp} onChange={(e) => setRequiredExp(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
                  </div>

                  {error && (
                    <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
                      <p className="text-red-800 dark:text-red-200 text-sm">{error}</p>
                    </div>
                  )}

                  <button onClick={handleRankCVs} disabled={loading}
                    className="w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center">
                    {loading ? (
                      <>
                        <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        Analyse en cours...
                      </>
                    ) : (
                      <>
                        <TrendingUp className="h-5 w-5 mr-2" />
                        Lancer le Ranking
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* ===== RÉSULTATS ===== */}
            <div className="space-y-6">
              {!rankingResult && !loading && (
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center">
                  <Trophy className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400">
                    Uploadez des CVs, remplissez l'offre et lancez le ranking
                  </p>
                </div>
              )}

              {rankingResult && (
                <>
                  {/* Résumé */}
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 flex items-center gap-6 text-sm">
                    <span className="text-gray-600 dark:text-gray-400">
                      <strong className="text-gray-900 dark:text-white">{rankingResult.total_uploaded}</strong> uploadé(s)
                    </span>
                    <span className="text-gray-600 dark:text-gray-400">
                      <strong className="text-green-600">{rankingResult.total_ranked}</strong> analysé(s)
                    </span>
                    {rankingResult.failed_files.length > 0 && (
                      <span className="text-red-600">
                        <strong>{rankingResult.failed_files.length}</strong> échoué(s): {rankingResult.failed_files.join(", ")}
                      </span>
                    )}
                  </div>

                  {/* Classement + Détail */}
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

                    {/* Classement */}
                    <div className="lg:col-span-1 space-y-3">
                      <h2 className="text-lg font-bold text-gray-800 dark:text-white">🏆 Classement</h2>
                      {rankingResult.ranked_cvs.map((cv) => (
                        <button key={cv.filename} onClick={() => setSelectedCV(cv)}
                          className={`w-full text-left border-2 rounded-lg p-4 transition-colors ${getRankBorder(cv)}`}>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              {getRankIcon(cv.rank)}
                              <span className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate max-w-[120px]">
                                {cv.filename}
                              </span>
                            </div>
                            <span className={`text-sm font-bold ${getScoreColor(cv.overall_score)}`}>
                              {cv.overall_score.toFixed(1)}%
                            </span>
                          </div>
                          <div className="mt-2 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                            <div className={`h-2 rounded-full ${cv.overall_score >= 75 ? "bg-green-600" : cv.overall_score >= 50 ? "bg-orange-600" : "bg-red-600"}`}
                              style={{ width: `${cv.overall_score}%` }}></div>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">{getScoreLabel(cv.overall_score)}</p>
                        </button>
                      ))}
                    </div>

                    {/* Détail */}
                    {selectedCV && (
                      <div className="lg:col-span-2 space-y-4">
                        <h2 className="text-lg font-bold text-gray-800 dark:text-white">Détail — {selectedCV.filename}</h2>

                        {/* Score global */}
                        <div className={`border-2 rounded-lg p-6 ${getScoreBg(selectedCV.overall_score)}`}>
                          <div className="flex justify-between items-start">
                            <div>
                              <h3 className="text-xl font-bold">Score Global</h3>
                              <p className="text-gray-600">{getScoreLabel(selectedCV.overall_score)}</p>
                            </div>
                            <div className={`text-4xl font-bold ${getScoreColor(selectedCV.overall_score)}`}>
                              {selectedCV.overall_score.toFixed(1)}%
                            </div>
                          </div>
                          <div className="mt-4 bg-gray-200 rounded-full h-4">
                            <div className={`h-4 rounded-full ${selectedCV.overall_score >= 75 ? "bg-green-600" : selectedCV.overall_score >= 50 ? "bg-orange-600" : "bg-red-600"}`}
                              style={{ width: `${selectedCV.overall_score}%` }}></div>
                          </div>
                        </div>

                        {/* Scores détaillés */}
                        <div className="grid grid-cols-2 gap-4">
                          {[
                            { label: "Compétences", score: selectedCV.skills_score, icon: Award },
                            { label: "Expérience", score: selectedCV.experience_score, icon: Briefcase },
                            { label: "Catégorie", score: selectedCV.category_match_score, icon: TrendingUp, extra: selectedCV.predicted_category },
                            { label: "Éducation", score: selectedCV.education_score, icon: BookOpen },
                          ].map(({ label, score, icon: Icon, extra }) => (
                            <div key={label} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                              <div className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                <Icon className="h-4 w-4" />{label}
                              </div>
                              <div className={`text-2xl font-bold ${getScoreColor(score)}`}>{score.toFixed(1)}%</div>
                              <div className="mt-2 bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                                <div className="h-2 rounded-full bg-purple-600" style={{ width: `${score}%` }}></div>
                              </div>
                              {extra && <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">Prédit: {extra}</p>}
                            </div>
                          ))}
                        </div>

                        {/* Compétences */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                            <h3 className="text-base font-bold flex items-center gap-2 mb-4">
                              <CheckCircle2 className="h-5 w-5 text-green-600" />Compétences Correspondantes
                            </h3>
                            {selectedCV.matching_skills.length > 0 ? (
                              <div className="flex flex-wrap gap-2">
                                {selectedCV.matching_skills.map((skill, i) => (
                                  <span key={i} className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">{skill}</span>
                                ))}
                              </div>
                            ) : (
                              <p className="text-gray-500 text-sm">Aucune compétence correspondante</p>
                            )}
                          </div>

                          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                            <h3 className="text-base font-bold flex items-center gap-2 mb-4">
                              <XCircle className="h-5 w-5 text-red-600" />Compétences Manquantes
                            </h3>
                            {selectedCV.missing_required_skills.length > 0 ? (
                              <div className="flex flex-wrap gap-2">
                                {selectedCV.missing_required_skills.map((skill, i) => (
                                  <span key={i} className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm">{skill}</span>
                                ))}
                              </div>
                            ) : (
                              <p className="text-green-600 text-sm font-medium">✓ Toutes les compétences requises sont présentes</p>
                            )}
                            {selectedCV.missing_preferred_skills.length > 0 && (
                              <div className="mt-4">
                                <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">Compétences préférées manquantes:</p>
                                <div className="flex flex-wrap gap-2">
                                  {selectedCV.missing_preferred_skills.map((skill, i) => (
                                    <span key={i} className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-sm">{skill}</span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Recommandations */}
                        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-6">
                          <h3 className="text-base font-bold flex items-center gap-2 mb-4">
                            <AlertCircle className="h-5 w-5" />Recommandations
                          </h3>
                          <ul className="space-y-2">
                            {selectedCV.recommendations.map((rec, i) => (
                              <li key={i} className="flex items-start gap-2">
                                <span className="text-purple-600 mt-1">•</span>
                                <span className="text-gray-700 dark:text-gray-300">{rec}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}