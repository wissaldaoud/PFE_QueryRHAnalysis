'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import MainLayout from '@/components/MainLayout';
import {
  Building2,
  Plus,
  Search,
  Edit,
  Trash2,
  Users,
  UserCheck,
  MoreVertical,
  Mail,
  Phone,
  MapPin,
} from 'lucide-react';

interface Department {
  id: number;
  name: string;
  code: string;
  description?: string;
  manager_name?: string;
  manager_email?: string;
  location?: string;
  employee_count: number;
  budget?: number;
  created_at: string;
}

interface User {
  id: number;
  role: string;
}

export default function DepartmentsPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingDept, setEditingDept] = useState<Department | null>(null);
  const [activeDropdown, setActiveDropdown] = useState<number | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: '',
    location: '',
  });

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');

    if (!token) {
      router.push('/login');
      return;
    }

    if (userData) {
      setUser(JSON.parse(userData));
    }

    fetchDepartments(token);
  }, [router]);

  const fetchDepartments = async (token: string) => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/departments', {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setDepartments(data);
      } else {
        console.error('Erreur récupération départements:', response.status);
      }
    } catch (err) {
      console.error('Error fetching departments:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    if (!token) return;

    try {
      const url = editingDept
        ? `http://127.0.0.1:8000/api/v1/departments/${editingDept.id}`
        : 'http://127.0.0.1:8000/api/v1/departments';
      
      const method = editingDept ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        await fetchDepartments(token);
        setShowModal(false);
        setFormData({ name: '', code: '', description: '', location: '' });
        setEditingDept(null);
      } else {
        const error = await response.json();
        alert(error.detail || 'Erreur lors de l\'enregistrement');
      }
    } catch (err) {
      console.error('Erreur:', err);
      alert('Erreur lors de l\'enregistrement du département');
    }
  };

  const handleEdit = (dept: Department) => {
    setEditingDept(dept);
    setFormData({
      name: dept.name,
      code: dept.code,
      description: dept.description || '',
      location: dept.location || '',
    });
    setShowModal(true);
    setActiveDropdown(null);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce département ?')) {
      return;
    }

    const token = localStorage.getItem('access_token');
    if (!token) return;

    setActiveDropdown(null);

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/v1/departments/${id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        await fetchDepartments(token);
      } else {
        const error = await response.json();
        alert(error.detail || 'Erreur lors de la suppression');
      }
    } catch (err) {
      console.error('Erreur:', err);
      alert('Erreur lors de la suppression du département');
    }
  };

  const canEdit = user?.role === 'admin' || user?.role === 'hr_manager';

  const filteredDepartments = departments.filter(
    (dept) =>
      dept.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      dept.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalEmployees = departments.reduce((sum, d) => sum + d.employee_count, 0);

  return (
    <MainLayout>
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Départements</h1>
            <p className="text-gray-500 mt-1">
              Gérez la structure organisationnelle
            </p>
          </div>
          {canEdit && (
            <button
              onClick={() => {
                setEditingDept(null);
                setFormData({ name: '', code: '', description: '', location: '' });
                setShowModal(true);
              }}
              className="mt-4 sm:mt-0 inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-[#E31837] to-[#c41530] text-white rounded-xl font-medium hover:shadow-lg transition-all"
            >
              <Plus className="w-5 h-5" />
              Nouveau département
            </button>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 rounded-xl bg-blue-50">
            <Building2 className="w-6 h-6 text-blue-500" />
          </div>
          <div>
            <p className="text-sm text-gray-500">Total Départements</p>
            <p className="text-2xl font-bold text-gray-900">{departments.length}</p>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 rounded-xl bg-green-50">
            <Users className="w-6 h-6 text-green-500" />
          </div>
          <div>
            <p className="text-sm text-gray-500">Total Employés</p>
            <p className="text-2xl font-bold text-gray-900">{totalEmployees}</p>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex items-center gap-4">
          <div className="p-3 rounded-xl bg-purple-50">
            <UserCheck className="w-6 h-6 text-purple-500" />
          </div>
          <div>
            <p className="text-sm text-gray-500">Moy. par Département</p>
            <p className="text-2xl font-bold text-gray-900">
              {Math.round(totalEmployees / departments.length) || 0}
            </p>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Rechercher un département..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837]"
          />
        </div>
      </div>

      {/* Departments Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="w-12 h-12 border-4 border-[#E31837] border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDepartments.map((dept) => (
            <div
              key={dept.id}
              className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-gradient-to-br from-[#E31837] to-[#c41530] rounded-xl shadow-sm">
                      <Building2 className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{dept.name}</h3>
                      <span className="text-sm text-gray-500">Code: {dept.code}</span>
                    </div>
                  </div>

                  {canEdit && (
                    <div className="relative">
                      <button
                        onClick={() =>
                          setActiveDropdown(activeDropdown === dept.id ? null : dept.id)
                        }
                        className="p-2 hover:bg-gray-100 rounded-lg transition"
                      >
                        <MoreVertical className="w-5 h-5 text-gray-400" />
                      </button>

                      {activeDropdown === dept.id && (
                        <div className="absolute right-0 mt-2 w-40 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-10">
                          <button
                            onClick={() => handleEdit(dept)}
                            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full"
                          >
                            <Edit className="h-4 w-4" />
                            Modifier
                          </button>
                          <button
                            onClick={() => handleDelete(dept.id)}
                            className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 w-full"
                          >
                            <Trash2 className="h-4 w-4" />
                            Supprimer
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {dept.description && (
                  <p className="text-sm text-gray-500 mb-4 line-clamp-2">
                    {dept.description}
                  </p>
                )}

                <div className="space-y-2">
                  {dept.manager_name && (
                    <div className="flex items-center gap-2 text-sm">
                      <UserCheck className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-600">
                        Manager: <strong>{dept.manager_name}</strong>
                      </span>
                    </div>
                  )}
                  {dept.location && (
                    <div className="flex items-center gap-2 text-sm">
                      <MapPin className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-600">{dept.location}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Users className="w-4 h-4 text-gray-400" />
                    <span className="text-sm font-medium text-gray-700">
                      {dept.employee_count} employés
                    </span>
                  </div>
                  <button
                    onClick={() => router.push(`/employees?department=${dept.id}`)}
                    className="text-sm text-[#E31837] font-medium hover:underline"
                  >
                    Voir l'équipe →
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              {editingDept ? 'Modifier le département' : 'Nouveau département'}
            </h3>

            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nom *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837]"
                    placeholder="Ex: Développement"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Code *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.code}
                    onChange={(e) =>
                      setFormData({ ...formData, code: e.target.value.toUpperCase() })
                    }
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837]"
                    placeholder="Ex: DEV"
                    maxLength={5}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
                    }
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837] resize-none"
                    rows={3}
                    placeholder="Description du département..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Localisation
                  </label>
                  <input
                    type="text"
                    value={formData.location}
                    onChange={(e) =>
                      setFormData({ ...formData, location: e.target.value })
                    }
                    className="w-full px-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837]"
                    placeholder="Ex: Bâtiment A - 2ème étage"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingDept(null);
                  }}
                  className="px-5 py-2.5 border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-50 font-medium transition"
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="px-5 py-2.5 bg-gradient-to-r from-[#E31837] to-[#c41530] text-white rounded-xl font-medium hover:shadow-lg transition"
                >
                  {editingDept ? 'Enregistrer' : 'Créer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Click outside to close dropdown */}
      {activeDropdown && (
        <div className="fixed inset-0 z-0" onClick={() => setActiveDropdown(null)} />
      )}
    </MainLayout>
  );
}


