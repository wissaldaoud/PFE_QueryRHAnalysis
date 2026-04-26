/**
 * EXEMPLE D'INTÉGRATION - Page d'édition d'employé avec prédiction de turnover
 * 
 * Ce fichier montre comment ajouter le composant TurnoverPredictor
 * à la page d'édition d'un employé existant.
 * 
 * Pour intégrer: Copiez les sections marquées "NOUVEAU" dans votre 
 * fichier frontend/app/employees/[id]/edit/page.tsx
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import MainLayout from "@/components/MainLayout";
// ========== NOUVEAU: Import du composant ==========
import TurnoverPredictor from "@/components/TurnoverPredictor";
// ===================================================
import {
  ArrowLeft,
  User,
  Mail,
  Phone,
  Calendar,
  Building2,
  Briefcase,
  DollarSign,
  Save,
  FileText,
  MapPin,
  AlertTriangle,
  CheckCircle,
  Loader2,
  Trash2,
} from "lucide-react";

interface Department {
  id: number;
  name: string;
}

interface Employee {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  date_of_birth: string | null;
  hire_date: string;
  job_title: string | null;
  department_id: number | null;
  salary: number | null;
  employment_status: string;
  address?: string | null;
  emergency_contact_name?: string | null;
  emergency_contact_phone?: string | null;
  contract_type?: string | null;
  notes?: string | null;
}

export default function EditEmployeePage() {
  const router = useRouter();
  const params = useParams();
  const employeeId = params.id;

  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const [formData, setFormData] = useState({
    employee_code: "",
    first_name: "",
    last_name: "",
    email: "",
    phone: "",
    date_of_birth: "",
    hire_date: "",
    job_title: "",
    department_id: "",
    salary: "",
    employment_status: "active",
    address: "",
    emergency_contact_name: "",
    emergency_contact_phone: "",
    contract_type: "CDI",
    notes: "",
  });

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const userData = localStorage.getItem("user");

    if (!token) {
      router.push("/login");
      return;
    }

    if (userData) {
      const user = JSON.parse(userData);
      if (user.role === "employee") {
        router.push("/dashboard");
        return;
      }
    }

    fetchEmployee();
    fetchDepartments();
  }, [employeeId, router]);

  const fetchEmployee = async () => {
    const token = localStorage.getItem("access_token");
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/employees/${employeeId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data: Employee = await response.json();
        setFormData({
          employee_code: data.employee_code || "",
          first_name: data.first_name || "",
          last_name: data.last_name || "",
          email: data.email || "",
          phone: data.phone || "",
          date_of_birth: data.date_of_birth || "",
          hire_date: data.hire_date || "",
          job_title: data.job_title || "",
          department_id: data.department_id?.toString() || "",
          salary: data.salary?.toString() || "",
          employment_status: data.employment_status || "active",
          address: data.address || "",
          emergency_contact_name: data.emergency_contact_name || "",
          emergency_contact_phone: data.emergency_contact_phone || "",
          contract_type: data.contract_type || "CDI",
          notes: data.notes || "",
        });
      } else {
        setError("Erreur lors du chargement de l'employé");
      }
    } catch (err) {
      setError("Erreur de connexion au serveur");
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartments = async () => {
    const token = localStorage.getItem("access_token");
    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/departments", {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setDepartments(data);
      }
    } catch (err) {
      console.error("Error fetching departments:", err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // ... votre code de soumission existant
  };

  const handleDelete = async () => {
    // ... votre code de suppression existant
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex justify-center items-center min-h-screen">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href={`/employees/${employeeId}`}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-800">
                Modifier Employé
              </h1>
              <p className="text-gray-600">
                {formData.first_name} {formData.last_name}
              </p>
            </div>
          </div>
        </div>

        {/* Formulaire principal */}
        <form onSubmit={handleSubmit}>
          {/* ... Vos sections de formulaire existantes ... */}
          
          {/* Informations personnelles */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <User className="w-5 h-5" />
              Informations Personnelles
            </h2>
            {/* ... vos champs ... */}
          </div>

          {/* Informations professionnelles */}
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Briefcase className="w-5 h-5" />
              Informations Professionnelles
            </h2>
            {/* ... vos champs ... */}
          </div>

          {/* ========== NOUVEAU: Section Prédiction de Turnover ========== */}
          {formData.date_of_birth && formData.hire_date && (
            <div className="mb-6">
              <TurnoverPredictor
                employeeData={{
                  date_of_birth: formData.date_of_birth,
                  hire_date: formData.hire_date,
                  contract_type: formData.contract_type,
                }}
              />
            </div>
          )}
          {/* ============================================================= */}

          {/* Messages d'erreur/succès */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800">Employé mis à jour avec succès!</p>
            </div>
          )}

          {/* Boutons d'action */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={saving}
              className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center justify-center gap-2"
            >
              {saving ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Enregistrement...
                </>
              ) : (
                <>
                  <Save className="w-5 h-5" />
                  Enregistrer
                </>
              )}
            </button>

            <button
              type="button"
              onClick={() => setShowDeleteModal(true)}
              className="px-6 py-3 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 flex items-center gap-2"
            >
              <Trash2 className="w-5 h-5" />
              Supprimer
            </button>
          </div>
        </form>
      </div>
    </MainLayout>
  );
}
