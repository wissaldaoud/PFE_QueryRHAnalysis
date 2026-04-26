"use client";

import { useState, useEffect } from "react";
import MainLayout from "@/components/MainLayout";
import { useRouter } from "next/navigation";
import { 
  Plus, 
  Briefcase, 
  MapPin, 
  DollarSign, 
  Calendar, 
  Trash2,
  Search,
  FileText,
  Upload,
  X
} from "lucide-react";

interface JobOffer {
  id: number;
  title: string;
  description: string;
  category: string | null;
  required_skills: string[];
  preferred_skills: string[];
  required_education: string[];
  required_experience_years: number | null;
  location: string | null;
  salary_range: string | null;
  contract_type: string | null;
  department: string | null;
  is_active: boolean;
  created_at: string;
}

export default function JobOffersPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<JobOffer[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  
  const [newJob, setNewJob] = useState({
    title: "",
    description: "",
    category: "",
    required_skills: [] as string[],
    preferred_skills: [] as string[],
    required_education: [] as string[],
    required_experience_years: null as number | null,
    location: "",
    salary_range: "",
    contract_type: "CDI",
    department: ""
  });
  
  const [skillInput, setSkillInput] = useState("");
  const [educationInput, setEducationInput] = useState("");

  useEffect(() => {
    fetchJobs();
    fetchCategories();
  }, [selectedCategory]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        active_only: "true",
        limit: "100"
      });
      if (selectedCategory) {
        params.append("category", selectedCategory);
      }
      
      const response = await fetch(`http://localhost:8000/api/v1/cv-matching/jobs?${params}`);
      if (!response.ok) throw new Error("Erreur chargement offres");
      const data = await response.json();
      setJobs(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/cv-matching/categories");
      if (!response.ok) throw new Error("Erreur chargement catégories");
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (err: any) {
      console.error("Erreur catégories:", err);
    }
  };

  const handleCreateJob = async () => {
    try {
      setError("");
      setSuccess("");
      
      if (!newJob.title || !newJob.description) {
        setError("Titre et description sont requis");
        return;
      }

      const response = await fetch("http://localhost:8000/api/v1/cv-matching/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newJob)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Erreur création offre");
      }

      setSuccess("Offre créée avec succès!");
      setShowCreateDialog(false);
      fetchJobs();
      
      // Reset form
      setNewJob({
        title: "",
        description: "",
        category: "",
        required_skills: [],
        preferred_skills: [],
        required_education: [],
        required_experience_years: null,
        location: "",
        salary_range: "",
        contract_type: "CDI",
        department: ""
      });
      
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDeleteJob = async (jobId: number) => {
    if (!confirm("Êtes-vous sûr de vouloir désactiver cette offre?")) return;
    
    try {
      const response = await fetch(`http://localhost:8000/api/v1/cv-matching/jobs/${jobId}`, {
        method: "DELETE"
      });
      
      if (!response.ok) throw new Error("Erreur suppression");
      setSuccess("Offre désactivée");
      fetchJobs();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const addSkill = () => {
    if (!skillInput.trim()) return;
    setNewJob({...newJob, required_skills: [...newJob.required_skills, skillInput.trim()]});
    setSkillInput("");
  };

  const removeSkill = (index: number) => {
    setNewJob({
      ...newJob, 
      required_skills: newJob.required_skills.filter((_, i) => i !== index)
    });
  };

  const addEducation = () => {
    if (!educationInput.trim()) return;
    setNewJob({...newJob, required_education: [...newJob.required_education, educationInput.trim()]});
    setEducationInput("");
  };

  const removeEducation = (index: number) => {
    setNewJob({
      ...newJob, 
      required_education: newJob.required_education.filter((_, i) => i !== index)
    });
  };

  const filteredJobs = jobs.filter(job =>
    job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    job.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    job.department?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <MainLayout>
      <div className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Offres d'Emploi</h1>
            <p className="text-gray-600 mt-1">Gérez les offres et matchez les CV</p>
          </div>
          
          <button
            onClick={() => setShowCreateDialog(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Nouvelle Offre
          </button>
        </div>

        {/* Alerts */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        {/* Filters */}
        <div className="flex gap-4 items-center">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher une offre..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <select
            className="border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="">Toutes les catégories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        {/* Loading */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Chargement des offres...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredJobs.map((job) => (
              <div key={job.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-800">{job.title}</h3>
                    {job.category && (
                      <span className="inline-block mt-2 px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">{job.category}</span>
                    )}
                  </div>
                  <button
                    onClick={() => handleDeleteJob(job.id)}
                    className="text-red-600 hover:text-red-700 p-1"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>

                <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                  {job.description}
                </p>

                <div className="space-y-2 text-sm text-gray-600">
                  {job.location && (
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4" />
                      {job.location}
                    </div>
                  )}

                  {job.salary_range && (
                    <div className="flex items-center gap-2">
                      <DollarSign className="h-4 w-4" />
                      {job.salary_range}
                    </div>
                  )}

                  {job.required_experience_years && (
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      {job.required_experience_years} ans d'expérience
                    </div>
                  )}

                  {job.contract_type && (
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4" />
                      {job.contract_type}
                    </div>
                  )}
                </div>

                {job.required_skills && job.required_skills.length > 0 && (
                  <div className="mt-4">
                    <p className="text-xs text-gray-500 mb-2">Compétences requises:</p>
                    <div className="flex flex-wrap gap-1">
                      {job.required_skills.slice(0, 5).map((skill, i) => (
                        <span key={i} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                          {skill}
                        </span>
                      ))}
                      {job.required_skills.length > 5 && (
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-500 rounded">
                          +{job.required_skills.length - 5}
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {job.required_education && job.required_education.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs text-gray-500 mb-2">🎓 Formation requise:</p>
                    <div className="flex flex-wrap gap-1">
                      {job.required_education.map((edu, i) => (
                        <span key={i} className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded">
                          {edu}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <button
                  onClick={() => router.push(`/cv-matching/${job.id}`)}
                  className="mt-4 w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Upload className="h-4 w-4" />
                  Matcher un CV
                </button>
              </div>
            ))}
          </div>
        )}

        {!loading && filteredJobs.length === 0 && (
          <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
            <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Aucune offre trouvée</p>
          </div>
        )}

        {/* Create Dialog */}
        {showCreateDialog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
             <div className="p-6 border-b flex justify-between items-center">
                <div>
                  <h2 className="text-xl font-bold">Créer une Offre d'Emploi</h2>
                  <p className="text-gray-600 text-sm mt-1">Remplissez les informations requises</p>
                </div>
                <button onClick={() => setShowCreateDialog(false)} className="text-gray-500 hover:text-gray-700">
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Titre *</label>
                  <input
                    type="text"
                    value={newJob.title}
                    onChange={(e) => setNewJob({...newJob, title: e.target.value})}
                    placeholder="Ex: Data Scientist Senior"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
                  <textarea
                    value={newJob.description}
                    onChange={(e) => setNewJob({...newJob, description: e.target.value})}
                    placeholder="Description détaillée du poste..."
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Catégorie</label>
                    <select
                      value={newJob.category}
                      onChange={(e) => setNewJob({...newJob, category: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Sélectionner...</option>
                      {categories.map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Années d'expérience</label>
                    <input
                      type="number"
                      value={newJob.required_experience_years || ""}
                      onChange={(e) => setNewJob({
                        ...newJob, 
                        required_experience_years: e.target.value ? parseFloat(e.target.value) : null
                      })}
                      placeholder="Ex: 3"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Compétences Requises</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={skillInput}
                      onChange={(e) => setSkillInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                      placeholder="Ex: Python, SQL..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      type="button"
                      onClick={addSkill}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {newJob.required_skills.map((skill, i) => (
                      <span key={i} className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                        {skill}
                        <button onClick={() => removeSkill(i)} className="ml-1 hover:text-blue-900">×</button>
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">🎓 Formation Requise</label>
                  <div className="flex gap-2 mb-2">
                    <input
                      type="text"
                      value={educationInput}
                      onChange={(e) => setEducationInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addEducation())}
                      placeholder="Ex: Master en Informatique, Licence..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      type="button"
                      onClick={addEducation}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                      <Plus className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {newJob.required_education.map((edu, i) => (
                      <span key={i} className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                        {edu}
                        <button onClick={() => removeEducation(i)} className="ml-1 hover:text-green-900">×</button>
                      </span>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Localisation</label>
                    <input
                      type="text"
                      value={newJob.location}
                      onChange={(e) => setNewJob({...newJob, location: e.target.value})}
                      placeholder="Ex: Paris"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Salaire</label>
                    <input
                      type="text"
                      value={newJob.salary_range}
                      onChange={(e) => setNewJob({...newJob, salary_range: e.target.value})}
                      placeholder="Ex: 40000-60000 EUR"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>

              <div className="p-6 border-t flex justify-end gap-3">
                <button
                  onClick={() => setShowCreateDialog(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  onClick={handleCreateJob}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Créer l'Offre
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}
