"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import MainLayout from "@/components/MainLayout";
import { 
  Upload, 
  FileText, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  ArrowLeft,
  TrendingUp,
  Award,
  BookOpen,
  Briefcase
} from "lucide-react";

interface MatchResult {
  success: boolean;
  job_offer_id: number;
  job_title: string;
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

interface JobOffer {
  id: number;
  title: string;
  description: string;
  category: string;
  required_skills: string[];
  preferred_skills: string[];
  required_education: string[];
  required_experience_years: number;
  location: string;
  salary_range: string;
}

export default function CVMatchingPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.id as string;
  
  const [job, setJob] = useState<JobOffer | null>(null);
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  useEffect(() => {
    fetchJobDetails();
  }, [jobId]);

  const fetchJobDetails = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/cv-matching/jobs/${jobId}`);
      if (!response.ok) throw new Error("Offre non trouvée");
      const data = await response.json();
      setJob(data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError("");
    }
  };

  const handleUploadAndMatch = async () => {
    if (!selectedFile) {
      setError("Veuillez sélectionner un fichier CV");
      return;
    }

    setLoading(true);
    setError("");
    setMatchResult(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(
        `http://localhost:8000/api/v1/cv-matching/upload-and-match/${jobId}`,
        {
          method: "POST",
          body: formData
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Erreur lors du matching");
      }

      const result = await response.json();
      setMatchResult(result);
    } catch (err: any) {
      setError(err.message);
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

  return (
    <MainLayout>
      <div className="container mx-auto p-6 space-y-6">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-800"
        >
          <ArrowLeft className="h-4 w-4" />
          Retour
        </button>

        {job && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h1 className="text-2xl font-bold text-gray-800">{job.title}</h1>
            <div className="mt-2 flex items-center gap-4 text-sm text-gray-600">
              {job.category && <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">{job.category}</span>}
              {job.location && <span>{job.location}</span>}
              {job.salary_range && <span>• {job.salary_range}</span>}
            </div>
            
            <p className="text-gray-700 mt-4 mb-4">{job.description}</p>
            
            {job.required_skills && job.required_skills.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium mb-2">Compétences requises:</p>
                <div className="flex flex-wrap gap-2">
                  {job.required_skills.map((skill, i) => (
                    <span key={i} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">{skill}</span>
                  ))}
                </div>
              </div>
            )}

            {job.preferred_skills && job.preferred_skills.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium mb-2">Compétences préférées:</p>
                <div className="flex flex-wrap gap-2">
                  {job.preferred_skills.map((skill, i) => (
                    <span key={i} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">{skill}</span>
                  ))}
                </div>
              </div>
            )}

            {job.required_education && job.required_education.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium mb-2">🎓 Formation requise:</p>
                <div className="flex flex-wrap gap-2">
                  {job.required_education.map((edu, i) => (
                    <span key={i} className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded">{edu}</span>
                  ))}
                </div>
              </div>
            )}

            {job.required_experience_years && (
              <div className="mt-4">
                <p className="text-sm font-medium mb-2">Expérience requise:</p>
                <p className="text-sm text-gray-700">{job.required_experience_years} années</p>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-2">Uploader votre CV</h2>
          <p className="text-gray-600 text-sm mb-4">Formats acceptés: PDF, DOCX</p>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors">
            <input
              type="file"
              accept=".pdf,.docx,.doc"
              onChange={handleFileSelect}
              className="hidden"
              id="cv-upload"
            />
            <label htmlFor="cv-upload" className="cursor-pointer">
              <Upload className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              {selectedFile ? (
                <div>
                  <p className="text-sm font-medium text-gray-700">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {(selectedFile.size / 1024).toFixed(2)} KB
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-sm font-medium text-gray-700">
                    Cliquez pour sélectionner un CV
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    ou glissez-déposez votre fichier ici
                  </p>
                </div>
              )}
            </label>
          </div>

          <button
            onClick={handleUploadAndMatch}
            disabled={!selectedFile || loading}
            className="mt-4 w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Analyse en cours...
              </>
            ) : (
              <>
                <FileText className="h-4 w-4" />
                Analyser le CV
              </>
            )}
          </button>
        </div>

        {matchResult && (
          <>
            <div className={`border-2 rounded-lg p-6 ${getScoreBg(matchResult.overall_score)}`}>
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-bold">Score Global</h2>
                  <p className="text-gray-600">{getScoreLabel(matchResult.overall_score)}</p>
                </div>
                <div className={`text-4xl font-bold ${getScoreColor(matchResult.overall_score)}`}>
                  {matchResult.overall_score.toFixed(1)}%
                </div>
              </div>
              <div className="mt-4 bg-gray-200 rounded-full h-4">
                <div
                  className={`h-4 rounded-full ${matchResult.overall_score >= 75 ? 'bg-green-600' : matchResult.overall_score >= 50 ? 'bg-orange-600' : 'bg-red-600'}`}
                  style={{ width: `${matchResult.overall_score}%` }}
                ></div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                  <Award className="h-4 w-4" />
                  Compétences
                </div>
                <div className={`text-2xl font-bold ${getScoreColor(matchResult.skills_score)}`}>
                  {matchResult.skills_score.toFixed(1)}%
                </div>
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-blue-600"
                    style={{ width: `${matchResult.skills_score}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                  <Briefcase className="h-4 w-4" />
                  Expérience
                </div>
                <div className={`text-2xl font-bold ${getScoreColor(matchResult.experience_score)}`}>
                  {matchResult.experience_score.toFixed(1)}%
                </div>
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-blue-600"
                    style={{ width: `${matchResult.experience_score}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                  <TrendingUp className="h-4 w-4" />
                  Catégorie
                </div>
                <div className={`text-2xl font-bold ${getScoreColor(matchResult.category_match_score)}`}>
                  {matchResult.category_match_score.toFixed(1)}%
                </div>
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-blue-600"
                    style={{ width: `${matchResult.category_match_score}%` }}
                  ></div>
                </div>
                <p className="text-xs text-gray-600 mt-2">
                  Prédit: {matchResult.predicted_category}
                </p>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                  <BookOpen className="h-4 w-4" />
                  Éducation
                </div>
                <div className={`text-2xl font-bold ${getScoreColor(matchResult.education_score)}`}>
                  {matchResult.education_score.toFixed(1)}%
                </div>
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div
                    className="h-2 rounded-full bg-blue-600"
                    style={{ width: `${matchResult.education_score}%` }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-bold flex items-center gap-2 mb-4">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  Compétences Correspondantes
                </h3>
                {matchResult.matching_skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {matchResult.matching_skills.map((skill, i) => (
                      <span key={i} className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">Aucune compétence correspondante</p>
                )}
              </div>

              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-bold flex items-center gap-2 mb-4">
                  <XCircle className="h-5 w-5 text-red-600" />
                  Compétences Manquantes
                </h3>
                {matchResult.missing_required_skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {matchResult.missing_required_skills.map((skill, i) => (
                      <span key={i} className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p className="text-green-600 text-sm font-medium">
                    ✓ Toutes les compétences requises sont présentes
                  </p>
                )}

                {matchResult.missing_preferred_skills.length > 0 && (
                  <div className="mt-4">
                    <p className="text-xs text-gray-600 mb-2">Compétences préférées manquantes:</p>
                    <div className="flex flex-wrap gap-2">
                      {matchResult.missing_preferred_skills.map((skill, i) => (
                        <span key={i} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-bold flex items-center gap-2 mb-4">
                <AlertCircle className="h-5 w-5" />
                Recommandations
              </h3>
              <ul className="space-y-2">
                {matchResult.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-blue-600 mt-1">•</span>
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}
      </div>
    </MainLayout>
  );
}