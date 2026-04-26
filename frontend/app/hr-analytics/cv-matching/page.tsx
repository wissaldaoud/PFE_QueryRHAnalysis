"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createPortal } from "react-dom";
import MainLayout from "@/components/MainLayout";
import { 
  ArrowLeft, 
  Briefcase,
  Sparkles,
  CheckCircle,
  XCircle,
  AlertCircle,
  Award,
  TrendingUp,
  TrendingDown,
  Target,
  Lightbulb,
  UserCheck,
  AlertTriangle,
  GraduationCap,
  Clock,
  Zap
} from "lucide-react";

interface CVData {
  skills: string[];
  experiences: string[];
  job_titles: string[];
  education: string[];
  years_of_experience: number;
  full_text?: string;
}

interface JobOffer {
  required_skills: string[];
  preferred_skills: string[];
  required_education: string[];
  job_title: string;
  description: string;
  required_experience_years: number;
}

interface MatchingResult {
  overall_score: number;
  skills_score: number;
  experience_score: number;
  title_score: number;
  education_score: number;
  matching_skills: string[];
  missing_required_skills: string[];
  missing_preferred_skills: string[];
  recommendations: string[];
}

// Offres d'emploi pré-définies
const JOB_TEMPLATES = [
  {
    id: "dev-backend",
    name: "Développeur Backend Python",
    requiredSkills: "Python, FastAPI, PostgreSQL, Docker, Git",
    preferredSkills: "AWS, Kubernetes, Redis, Machine Learning",
    requiredEducation: "Licence Informatique, Ingénieur",
    title: "Développeur Backend Python Senior",
    description: "Développement et maintenance d'API REST, architecture microservices, optimisation performances",
    experience: "3"
  },
  {
    id: "dev-fullstack",
    name: "Développeur Full Stack",
    requiredSkills: "JavaScript, React, Node.js, SQL, Git",
    preferredSkills: "TypeScript, Next.js, MongoDB, Docker",
    requiredEducation: "Licence Informatique",
    title: "Développeur Full Stack",
    description: "Développement d'applications web complètes, frontend et backend, déploiement",
    experience: "2"
  },
  {
    id: "data-scientist",
    name: "Data Scientist",
    requiredSkills: "Python, Machine Learning, Pandas, NumPy, scikit-learn",
    preferredSkills: "TensorFlow, PyTorch, SQL, Spark, AWS",
    requiredEducation: "Master en Data Science, Ingénieur",
    title: "Data Scientist",
    description: "Analyse de données, modélisation ML, visualisation, déploiement en production",
    experience: "3"
  },
  {
    id: "devops",
    name: "Ingénieur DevOps",
    requiredSkills: "Docker, Kubernetes, CI/CD, Linux, Git",
    preferredSkills: "AWS, Terraform, Ansible, Monitoring, Python",
    requiredEducation: "Ingénieur, Master Informatique",
    title: "Ingénieur DevOps",
    description: "Automatisation déploiements, infrastructure as code, monitoring, sécurité",
    experience: "3"
  },
  {
    id: "custom",
    name: "✏️ Personnalisé (saisie manuelle)",
    requiredSkills: "",
    preferredSkills: "",
    requiredEducation: "",
    title: "",
    description: "",
    experience: "3"
  }
];

export default function CVMatchingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<MatchingResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showAlert, setShowAlert] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Monter le composant côté client
  useEffect(() => {
    setMounted(true);
  }, []);

  // Surveiller l'état de la popup
  useEffect(() => {
    // Popup active quand showAlert et result sont présents
  }, [showAlert, result, mounted]);

  // CV Form State
  const [skills, setSkills] = useState("");
  const [experiences, setExperiences] = useState("");
  const [jobTitles, setJobTitles] = useState("");
  const [education, setEducation] = useState("");
  const [yearsExp, setYearsExp] = useState("3");

  // Job Offer Form State
  const [selectedTemplate, setSelectedTemplate] = useState("custom");
  const [requiredSkills, setRequiredSkills] = useState("");
  const [preferredSkills, setPreferredSkills] = useState("");
  const [requiredEducation, setRequiredEducation] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [requiredExp, setRequiredExp] = useState("3");

  // Upload CV State
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [cvFullText, setCvFullText] = useState("");
  const [uploadMode, setUploadMode] = useState<"manual" | "upload">("manual");

  // Handle job template selection
  const handleTemplateChange = (templateId: string) => {
    setSelectedTemplate(templateId);
    const template = JOB_TEMPLATES.find(t => t.id === templateId);
    
    if (template) {
      setRequiredSkills(template.requiredSkills);
      setPreferredSkills(template.preferredSkills);
      setRequiredEducation(template.requiredEducation);
      setJobTitle(template.title);
      setJobDescription(template.description);
      setRequiredExp(template.experience);
    }
  };

  // Handle CV file upload
  const handleCvUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setCvFile(file);
    setLoading(true);
    setError(null);
    
    try {
      // Call backend API to parse the CV
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch("http://localhost:8000/api/v1/hr-analytics/parse-cv", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Fill form with extracted data
      const extracted = data.extracted_data;
      
      if (extracted.skills && extracted.skills.length > 0) {
        setSkills(extracted.skills.join(", "));
      }
      
      if (extracted.experiences && extracted.experiences.length > 0) {
        setExperiences(extracted.experiences.join("\n"));
      }
      
      if (extracted.job_titles && extracted.job_titles.length > 0) {
        setJobTitles(extracted.job_titles.join("\n"));
      }
      
      if (extracted.education && extracted.education.length > 0) {
        setEducation(extracted.education.join("\n"));
      }
      
      if (extracted.years_of_experience) {
        setYearsExp(extracted.years_of_experience.toString());
      }
      
      setCvFullText(data.text);
      
      alert(`✅ CV "${file.name}" analysé avec succès !\n\n${data.message}\n\nVérifiez et complétez les informations extraites.`);
      
    } catch (err: any) {
      setError(err.message || "Erreur lors du parsing du CV");
      alert(`❌ Erreur: ${err.message}\n\nEssayez un autre format de fichier.`);
    } finally {
      setLoading(false);
    }
  };

  // Example data
  const loadExample = () => {
    setSkills("Python, FastAPI, Machine Learning, SQL, Docker, Pandas, Git");
    setExperiences("Développeur Backend avec 3 ans d'expérience en Python et FastAPI\nCréation d'APIs RESTful et microservices\nDéveloppement de modèles ML pour prédiction");
    setJobTitles("Développeur Backend Python\nData Scientist Junior");
    setEducation("Master en Informatique et Data Science\nLicence en Mathématiques Appliquées");
    setYearsExp("3.5");
    
    setRequiredSkills("Python, FastAPI, PostgreSQL, Docker, Machine Learning");
    setPreferredSkills("Kubernetes, MLflow, React, CI/CD");
    setRequiredEducation("Master en Informatique, Ingénieur");
    setJobTitle("Senior Backend Developer - ML Platform");
    setJobDescription("Développement d'une plateforme ML avec Python, FastAPI, et Docker. Responsabilité de créer des APIs pour modèles ML en production.");
    setRequiredExp("3");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const cvData: CVData = {
      skills: skills.split(",").map(s => s.trim()).filter(s => s),
      experiences: experiences.split("\n").filter(s => s.trim()),
      job_titles: jobTitles.split("\n").filter(s => s.trim()),
      education: education.split("\n").filter(s => s.trim()),
      years_of_experience: parseFloat(yearsExp) || 0,
      full_text: cvFullText || undefined
    };

    const jobData: JobOffer = {
      required_skills: requiredSkills.split(",").map(s => s.trim()).filter(s => s),
      preferred_skills: preferredSkills.split(",").map(s => s.trim()).filter(s => s),
      required_education: requiredEducation.split(",").map(s => s.trim()).filter(s => s),
      job_title: jobTitle.trim(),
      description: jobDescription.trim(),
      required_experience_years: parseFloat(requiredExp) || 0
    };

    try {
      const response = await fetch("http://localhost:8000/api/v1/hr-analytics/cv-matching", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cv: cvData, job_offer: jobData })
      });

      if (!response.ok) {
        throw new Error(`Erreur ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      const resultData = data.data || data;
      
      setResult(resultData);
      
      // Déclencher la popup immédiatement
      setShowAlert(true);
    } catch (err: any) {
      setError(err.message || "Une erreur est survenue");
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return "text-green-600";
    if (score >= 0.6) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 0.8) return "bg-green-100 dark:bg-green-900/30";
    if (score >= 0.6) return "bg-yellow-100 dark:bg-yellow-900/30";
    return "bg-red-100 dark:bg-red-900/30";
  };

  // Get match level based on score
  const getMatchLevel = (score: number) => {
    if (score >= 0.8) return {
      label: "Excellent Match",
      icon: Award,
      color: "text-green-600",
      bgColor: "bg-green-50 dark:bg-green-900/20",
      borderColor: "border-green-500",
      description: "Profil hautement qualifié"
    };
    if (score >= 0.6) return {
      label: "Good Match",
      icon: Target,
      color: "text-orange-600",
      bgColor: "bg-orange-50 dark:bg-orange-900/20",
      borderColor: "border-orange-500",
      description: "Profil solide avec quelques points à vérifier"
    };
    return {
      label: "Weak Match",
      icon: AlertTriangle,
      color: "text-red-600",
      bgColor: "bg-red-50 dark:bg-red-900/20",
      borderColor: "border-red-500",
      description: "Profil nécessitant des améliorations"
    };
  };

  // Generate AI-like summary
  const generateAISummary = (result: MatchingResult) => {
    const scorePercent = Math.round(result.overall_score * 100);
    const skillsPercent = Math.round(result.skills_score * 100);
    const expPercent = Math.round(result.experience_score * 100);
    const eduPercent = Math.round(result.education_score * 100);
    
    let summary = `Ce candidat présente une correspondance ${result.overall_score >= 0.8 ? 'excellente' : result.overall_score >= 0.6 ? 'bonne' : 'modérée'} avec le poste (${scorePercent}%). `;
    
    // Skills analysis
    if (skillsPercent >= 80) {
      summary += "Les compétences techniques sont très bien alignées. ";
    } else if (skillsPercent >= 60) {
      summary += "Les compétences techniques sont solides, mais certaines compétences clés manquent. ";
    } else {
      summary += "Les compétences techniques nécessitent un renforcement significatif. ";
    }
    
    // Experience analysis
    if (expPercent >= 80) {
      summary += "L'expérience est excellente et parfaitement adaptée. ";
    } else if (expPercent >= 60) {
      summary += "L'expérience est correcte mais pourrait être plus approfondie. ";
    } else {
      summary += "L'expérience est limitée pour ce niveau de poste. ";
    }
    
    // Missing skills
    if (result.missing_required_skills.length > 0) {
      const topMissing = result.missing_required_skills.slice(0, 2).join(" et ");
      summary += `L'ajout d'expérience en ${topMissing} améliorerait considérablement le profil.`;
    }
    
    return summary;
  };

  // Get HR recommendation
  const getHRRecommendation = (result: MatchingResult) => {
    const score = result.overall_score;
    
    if (score >= 0.8) {
      return [
        { type: "success", text: "Candidat fortement recommandé pour un entretien" },
        { type: "info", text: "Prioriser pour un processus de recrutement rapide" },
        { type: "success", text: "Profil aligné avec les besoins du poste" }
      ];
    } else if (score >= 0.6) {
      return [
        { type: "warning", text: "Candidat qualifié, entretien recommandé" },
        { type: "info", text: "Vérifier l'expérience pratique lors de l'entretien" },
        { type: "warning", text: "Évaluer les compétences manquantes en détail" }
      ];
    } else {
      return [
        { type: "error", text: "Profil en dessous des attentes pour ce poste" },
        { type: "warning", text: "Formation ou expérience supplémentaire nécessaire" },
        { type: "info", text: "Envisager pour un poste de niveau inférieur" }
      ];
    }
  };

  // Composant Popup séparé
  const PopupAlert = () => {
    if (!showAlert || !result || !mounted) return null;

    const popupContent = (
      <div 
        className="fixed inset-0 bg-black bg-opacity-60 z-[99999] flex items-center justify-center p-4" 
        style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, margin: 0 }}
        onClick={(e) => {
          if (e.target === e.currentTarget) {
            setShowAlert(false);
          }
        }}
      >
        <div 
          className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full p-6 relative transform scale-100" 
          style={{ 
            animation: 'bounce-in 0.5s ease-out',
            maxHeight: '90vh',
            overflowY: 'auto'
          }}
        >
          {/* Icon */}
          <div className="flex justify-center mb-4">
            {result.overall_score >= 0.8 ? (
              <div className="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                <Award className="w-12 h-12 text-green-600" />
              </div>
            ) : result.overall_score >= 0.6 ? (
              <div className="w-20 h-20 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center">
                <Target className="w-12 h-12 text-orange-600" />
              </div>
            ) : (
              <div className="w-20 h-20 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
                <AlertTriangle className="w-12 h-12 text-red-600" />
              </div>
            )}
          </div>

          {/* Message */}
          <h3 className={`text-2xl font-bold text-center mb-3 ${
            result.overall_score >= 0.8 ? 'text-green-600' :
            result.overall_score >= 0.6 ? 'text-orange-600' : 'text-red-600'
          }`}>
            {result.overall_score >= 0.8 ? '✅ Excellent Profil !' :
             result.overall_score >= 0.6 ? '⚠️ Bon Profil' : '❌ Profil Faible'}
          </h3>
          
          <p className="text-center text-gray-700 dark:text-gray-300 mb-2 text-lg font-semibold">
            Score Global : {Math.round(result.overall_score * 100)}%
          </p>

          <div className={`p-4 rounded-lg mb-4 ${
            result.overall_score >= 0.8 ? 'bg-green-50 dark:bg-green-900/20 border border-green-200' :
            result.overall_score >= 0.6 ? 'bg-orange-50 dark:bg-orange-900/20 border border-orange-200' :
            'bg-red-50 dark:bg-red-900/20 border border-red-200'
          }`}>
            <p className="text-sm text-gray-800 dark:text-gray-200 leading-relaxed">
              {result.overall_score >= 0.8 ? (
                <>🎯 <strong>Recommandation :</strong> Candidat hautement qualifié. Processus de recrutement prioritaire recommandé.</>
              ) : result.overall_score >= 0.6 ? (
                <>💼 <strong>Recommandation :</strong> Candidat qualifié. Entretien recommandé pour évaluer l'expérience pratique.</>
              ) : (
                <>⚠️ <strong>Recommandation :</strong> Profil nécessite des améliorations. Envisager pour un poste de niveau inférieur ou formation supplémentaire.</>
              )}
            </p>
          </div>

          {/* Stats rapides */}
          <div className="grid grid-cols-3 gap-2 mb-4">
            <div className="text-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
              <div className="text-xs text-gray-500 dark:text-gray-400">Compétences</div>
              <div className={`font-bold ${result.skills_score >= 0.8 ? 'text-green-600' : result.skills_score >= 0.6 ? 'text-orange-600' : 'text-red-600'}`}>
                {Math.round(result.skills_score * 100)}%
              </div>
            </div>
            <div className="text-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
              <div className="text-xs text-gray-500 dark:text-gray-400">Expérience</div>
              <div className={`font-bold ${result.experience_score >= 0.8 ? 'text-green-600' : result.experience_score >= 0.6 ? 'text-orange-600' : 'text-red-600'}`}>
                {Math.round(result.experience_score * 100)}%
              </div>
            </div>
            <div className="text-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
              <div className="text-xs text-gray-500 dark:text-gray-400">Formation</div>
              <div className={`font-bold ${
                result.education_score === 0 ? 'text-gray-400' :
                result.education_score >= 0.8 ? 'text-green-600' : 
                result.education_score >= 0.6 ? 'text-orange-600' : 'text-red-600'
              }`}>
                {result.education_score === 0 ? 'N/A' : `${Math.round(result.education_score * 100)}%`}
              </div>
            </div>
          </div>

          {/* Boutons */}
          <div className="flex gap-3">
            <button
              onClick={() => setShowAlert(false)}
              className="flex-1 px-4 py-2.5 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              Fermer
            </button>
            <button
              onClick={() => {
                setShowAlert(false);
                window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });
              }}
              className={`flex-1 px-4 py-2.5 text-white rounded-lg transition-colors font-medium ${
                result.overall_score >= 0.8 ? 'bg-green-600 hover:bg-green-700' :
                result.overall_score >= 0.6 ? 'bg-orange-600 hover:bg-orange-700' :
                'bg-red-600 hover:bg-red-700'
              }`}
            >
              Voir Détails
            </button>
          </div>
        </div>
      </div>
    );

    // Utiliser createPortal pour rendre en dehors du DOM parent
    return createPortal(popupContent, document.body);
  };

  return (
    <MainLayout>
      {/* Popup via Portal */}
      <PopupAlert />

      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-gray-900 dark:to-gray-800">
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
                <div className="p-3 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-xl">
                  <Briefcase className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    CV Matching avec IA
                  </h1>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    Analyse sémantique avancée avec NLP
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={loadExample}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
                >
                  Charger un exemple
                </button>
                <button
                  onClick={() => {
                    // Créer un résultat de test
                    const testResult: MatchingResult = {
                      overall_score: 0.85,
                      skills_score: 0.9,
                      experience_score: 0.8,
                      title_score: 0.85,
                      education_score: 0.8,
                      matching_skills: ["Python", "FastAPI"],
                      missing_required_skills: [],
                      missing_preferred_skills: ["AWS"],
                      recommendations: ["Test"]
                    };
                    setResult(testResult);
                    setShowAlert(true);
                  }}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
                >
                  🧪 Test Popup
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          
         
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Form Section */}
            <div className="space-y-6">
              {/* CV Section */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <span className="mr-2">📄</span> Données du CV
                </h2>

                {/* Upload CV Section */}
                <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-dashed border-blue-300 dark:border-blue-700">
                  <div className="flex items-center justify-between mb-3">
                    <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      📎 Option 1 : Uploader un CV (fichier texte)
                    </label>
                  </div>
                  
                  <input
                    type="file"
                    accept=".txt,.pdf,.doc,.docx"
                    onChange={handleCvUpload}
                    className="block w-full text-sm text-gray-500 dark:text-gray-400
                      file:mr-4 file:py-2 file:px-4
                      file:rounded-lg file:border-0
                      file:text-sm file:font-semibold
                      file:bg-blue-600 file:text-white
                      hover:file:bg-blue-700
                      file:cursor-pointer cursor-pointer"
                  />
                  
                  {cvFile && (
                    <div className="mt-3 flex items-center text-sm text-green-700 dark:text-green-400">
                      <CheckCircle className="h-4 w-4 mr-2" />
                      <span>Fichier chargé : {cvFile.name}</span>
                    </div>
                  )}
                  
                  <p className="mt-2 text-xs text-gray-600 dark:text-gray-400">
                    💡 Formats acceptés : .txt, .pdf, .doc, .docx (extraction automatique pour .txt)
                  </p>
                </div>

                {/* Full CV Text Area */}
                {cvFullText && (
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Texte complet du CV (vérifiez et éditez si nécessaire)
                    </label>
                    <textarea
                      value={cvFullText}
                      onChange={(e) => setCvFullText(e.target.value)}
                      rows={6}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                      placeholder="Le contenu du CV apparaîtra ici..."
                    />
                  </div>
                )}

                <div className="mb-4 text-center text-sm font-medium text-gray-500 dark:text-gray-400">
                  — OU saisir manuellement —
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Compétences (séparées par des virgules)
                    </label>
                    <input
                      type="text"
                      value={skills}
                      onChange={(e) => setSkills(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Python, FastAPI, ML..."
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Expériences (une par ligne)
                    </label>
                    <textarea
                      value={experiences}
                      onChange={(e) => setExperiences(e.target.value)}
                      rows={4}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="3 ans de développement Backend..."
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Postes précédents (un par ligne)
                    </label>
                    <textarea
                      value={jobTitles}
                      onChange={(e) => setJobTitles(e.target.value)}
                      rows={2}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Développeur Backend"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Formation (une par ligne)
                    </label>
                    <textarea
                      value={education}
                      onChange={(e) => setEducation(e.target.value)}
                      rows={2}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Master en Informatique"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Années d'expérience
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
                </form>
              </div>

              {/* Job Offer Section */}
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <span className="mr-2">💼</span> Offre d'Emploi
                </h2>
                
                {/* Template Selector */}
                <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border-2 border-blue-200 dark:border-blue-800">
                  <label className="block text-sm font-semibold text-blue-900 dark:text-blue-200 mb-2 flex items-center">
                    <Sparkles className="w-4 h-4 mr-2" />
                    🚀 Sélectionner un poste type (gain de temps)
                  </label>
                  <select
                    value={selectedTemplate}
                    onChange={(e) => handleTemplateChange(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-blue-300 dark:border-blue-600 rounded-lg 
                             bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-medium
                             focus:ring-2 focus:ring-blue-500 focus:border-transparent
                             cursor-pointer hover:border-blue-400"
                  >
                    {JOB_TEMPLATES.map((template) => (
                      <option key={template.id} value={template.id}>
                        {template.name}
                      </option>
                    ))}
                  </select>
                  <p className="mt-2 text-xs text-blue-700 dark:text-blue-300">
                    💡 Sélectionnez un poste type pour remplir automatiquement les champs, ou choisissez "Personnalisé"
                  </p>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Titre du poste
                    </label>
                    <input
                      type="text"
                      value={jobTitle}
                      onChange={(e) => setJobTitle(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Senior Backend Developer"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Compétences requises (virgules)
                    </label>
                    <input
                      type="text"
                      value={requiredSkills}
                      onChange={(e) => setRequiredSkills(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Python, FastAPI..."
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Compétences préférées (virgules)
                    </label>
                    <input
                      type="text"
                      value={preferredSkills}
                      onChange={(e) => setPreferredSkills(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Docker, Kubernetes..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      🎓 Formation requise (virgules)
                    </label>
                    <input
                      type="text"
                      value={requiredEducation}
                      onChange={(e) => setRequiredEducation(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Master en Informatique, Ingénieur..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Description du poste
                    </label>
                    <textarea
                      value={jobDescription}
                      onChange={(e) => setJobDescription(e.target.value)}
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      placeholder="Développement d'APIs..."
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Expérience requise (années)
                    </label>
                    <input
                      type="number"
                      step="0.5"
                      value={requiredExp}
                      onChange={(e) => setRequiredExp(e.target.value)}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      required
                    />
                  </div>

                  <button
                    onClick={handleSubmit}
                    disabled={loading}
                    className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-lg hover:from-blue-700 hover:to-cyan-700 transition-colors duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
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
                        <Sparkles className="h-5 w-5 mr-2" />
                        Analyser le CV
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Results Section */}
            <div className="lg:sticky lg:top-4 h-fit">
              {error && (
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 mb-6">
                  <p className="text-red-800 dark:text-red-200">{error}</p>
                </div>
              )}

              {result && (
                <div className="space-y-5">
                  {/* Global Match Score Card */}
                  <div className={`rounded-xl shadow-lg p-6 border-l-4 ${getMatchLevel(result.overall_score).borderColor} ${getMatchLevel(result.overall_score).bgColor}`}>
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          {(() => {
                            const MatchIcon = getMatchLevel(result.overall_score).icon;
                            return <MatchIcon className={`w-6 h-6 ${getMatchLevel(result.overall_score).color}`} />;
                          })()}
                          <h3 className={`text-xl font-bold ${getMatchLevel(result.overall_score).color}`}>
                            {getMatchLevel(result.overall_score).label}
                          </h3>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {getMatchLevel(result.overall_score).description}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className={`text-4xl font-bold ${getMatchLevel(result.overall_score).color}`}>
                          {Math.round(result.overall_score * 100)}%
                        </div>
                        <p className="text-xs text-gray-500 mt-1">Score Global</p>
                      </div>
                    </div>
                    
                    {/* Progress bar */}
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                      <div
                        className={`h-full transition-all duration-500 ${result.overall_score >= 0.8 ? 'bg-green-500' : result.overall_score >= 0.6 ? 'bg-orange-500' : 'bg-red-500'}`}
                        style={{ width: `${result.overall_score * 100}%` }}
                      />
                    </div>
                  </div>

                  {/* AI Summary Card */}
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl shadow-md p-5 border border-blue-200 dark:border-blue-800">
                    <div className="flex items-start space-x-3">
                      <div className="p-2 bg-blue-500 rounded-lg">
                        <Zap className="w-5 h-5 text-white" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-2 flex items-center">
                          Analyse IA
                          <span className="ml-2 px-2 py-0.5 bg-blue-500 text-white text-xs rounded-full">AUTO</span>
                        </h4>
                        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                          {generateAISummary(result)}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Detailed Scores with Icons */}
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-5">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                      <Target className="w-5 h-5 mr-2 text-blue-500" />
                      Évaluation Détaillée
                    </h3>
                    <div className="space-y-4">
                      {[
                        { label: "Compétences Techniques", score: result.skills_score, icon: Zap },
                        { label: "Expérience Professionnelle", score: result.experience_score, icon: Clock },
                        { label: "Adéquation du Poste", score: result.title_score, icon: Briefcase },
                        { label: "Formation Académique", score: result.education_score, icon: GraduationCap, isEducation: true }
                      ].map((item) => {
                        const ItemIcon = item.icon;
                        const scorePercent = Math.round(item.score * 100);
                        const isNA = item.isEducation && item.score === 0;
                        
                        return (
                          <div key={item.label} className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center space-x-2">
                                <ItemIcon className="w-4 h-4 text-gray-500" />
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{item.label}</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                {isNA ? (
                                  <span className="text-sm font-semibold text-gray-400">Non Disponible</span>
                                ) : (
                                  <>
                                    {scorePercent >= 80 ? (
                                      <CheckCircle className="w-4 h-4 text-green-500" />
                                    ) : scorePercent >= 60 ? (
                                      <AlertCircle className="w-4 h-4 text-orange-500" />
                                    ) : (
                                      <XCircle className="w-4 h-4 text-red-500" />
                                    )}
                                    <span className={`text-sm font-bold ${getScoreColor(item.score)}`}>
                                      {scorePercent}%
                                    </span>
                                  </>
                                )}
                              </div>
                            </div>
                            {!isNA && (
                              <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                                <div
                                  className={`h-2 rounded-full transition-all duration-500 ${
                                    item.score >= 0.8 ? 'bg-green-500' : 
                                    item.score >= 0.6 ? 'bg-orange-500' : 'bg-red-500'
                                  }`}
                                  style={{ width: `${item.score * 100}%` }}
                                />
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Skills Analysis - Grouped */}
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-5">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                      <Lightbulb className="w-5 h-5 mr-2 text-yellow-500" />
                      Analyse des Compétences
                    </h3>
                    
                    {/* Core Skills */}
                    {result.matching_skills.length > 0 && (
                      <div className="mb-4">
                        <div className="flex items-center mb-2">
                          <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                          <h4 className="text-sm font-semibold text-green-700 dark:text-green-400">
                            Compétences Maîtrisées ({result.matching_skills.length})
                          </h4>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {result.matching_skills.map((skill, idx) => (
                            <span
                              key={idx}
                              className="px-3 py-1.5 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded-lg text-sm font-medium border border-green-300 dark:border-green-700"
                            >
                              ✓ {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Missing Required Skills */}
                    {result.missing_required_skills.length > 0 && (
                      <div className="mb-4">
                        <div className="flex items-center mb-2">
                          <XCircle className="w-4 h-4 text-red-500 mr-2" />
                          <h4 className="text-sm font-semibold text-red-700 dark:text-red-400">
                            Compétences Requises Manquantes ({result.missing_required_skills.length})
                          </h4>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {result.missing_required_skills.map((skill, idx) => (
                            <span
                              key={idx}
                              className="px-3 py-1.5 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 rounded-lg text-sm font-medium border border-red-300 dark:border-red-700"
                            >
                              ✗ {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Missing Preferred Skills */}
                    {result.missing_preferred_skills.length > 0 && (
                      <div>
                        <div className="flex items-center mb-2">
                          <AlertCircle className="w-4 h-4 text-orange-500 mr-2" />
                          <h4 className="text-sm font-semibold text-orange-700 dark:text-orange-400">
                            Compétences Préférées Manquantes ({result.missing_preferred_skills.length})
                          </h4>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {result.missing_preferred_skills.map((skill, idx) => (
                            <span
                              key={idx}
                              className="px-3 py-1.5 bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300 rounded-lg text-sm border border-orange-200 dark:border-orange-800"
                            >
                              ⚠ {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* HR Decision Support */}
                  <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-5 border-t-4 border-blue-500">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                      <UserCheck className="w-5 h-5 mr-2 text-blue-500" />
                      Recommandation RH
                    </h3>
                    <div className="space-y-3">
                      {getHRRecommendation(result).map((rec, idx) => (
                        <div
                          key={idx}
                          className={`flex items-start space-x-3 p-3 rounded-lg ${
                            rec.type === 'success' ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800' :
                            rec.type === 'warning' ? 'bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800' :
                            rec.type === 'info' ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800' :
                            'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
                          }`}
                        >
                          {rec.type === 'success' ? (
                            <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                          ) : rec.type === 'warning' ? (
                            <AlertTriangle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
                          ) : rec.type === 'info' ? (
                            <Lightbulb className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                          ) : (
                            <XCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                          )}
                          <p className={`text-sm font-medium ${
                            rec.type === 'success' ? 'text-green-800 dark:text-green-200' :
                            rec.type === 'warning' ? 'text-orange-800 dark:text-orange-200' :
                            rec.type === 'info' ? 'text-blue-800 dark:text-blue-200' :
                            'text-red-800 dark:text-red-200'
                          }`}>
                            {rec.text}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Technical Recommendations */}
                  {result.recommendations.length > 0 && (
                    <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl shadow-md p-5 border border-purple-200 dark:border-purple-800">
                      <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-100 mb-3 flex items-center">
                        <Lightbulb className="w-5 h-5 mr-2" />
                        Points d'Amélioration Suggérés
                      </h3>
                      <ul className="space-y-2">
                        {result.recommendations.map((rec, idx) => (
                          <li
                            key={idx}
                            className="text-sm text-purple-800 dark:text-purple-200 flex items-start"
                          >
                            <TrendingUp className="w-4 h-4 mr-2 flex-shrink-0 mt-0.5" />
                            <span>{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {!result && !error && !loading && (
                <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center">
                  <Sparkles className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    Remplissez le formulaire et cliquez sur "Analyser le CV" pour voir les résultats
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
