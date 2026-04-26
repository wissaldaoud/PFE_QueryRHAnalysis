'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import MainLayout from '@/components/MainLayout';
import {
  Users,
  Search,
  Plus,
  Edit,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Filter,
  Download,
  Building2,
  Mail,
  Phone,
  MoreVertical,
  Eye,
  UserCheck,
  UserX,
} from 'lucide-react';

interface Employee {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  job_title?: string;
  department?: {
    id: number;
    name: string;
  };
  hire_date: string;
  employment_status: string;
  salary?: number;
}

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: string;
}

export default function EmployeesPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const departmentFilter = searchParams.get('department');
  
  const [user, setUser] = useState<User | null>(null);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalEmployees, setTotalEmployees] = useState(0);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [employeeToDelete, setEmployeeToDelete] = useState<Employee | null>(null);
  const [activeDropdown, setActiveDropdown] = useState<number | null>(null);

  const itemsPerPage = 10;

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');

    if (!token) {
      router.push('/login');
      return;
    }

    if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);
      
      // Les employés simples ne peuvent pas voir la liste des employés
      if (parsedUser.role === 'employee') {
        router.push('/dashboard');
        return;
      }
    }

    fetchEmployees(token);
  }, [router, currentPage, searchTerm, statusFilter, departmentFilter]);

  const fetchEmployees = async (token: string) => {
    setLoading(true);
    try {
      let url = `http://127.0.0.1:8000/api/v1/employees?skip=${
        (currentPage - 1) * itemsPerPage
      }&limit=${itemsPerPage}`;

      if (searchTerm) {
        url += `&search=${encodeURIComponent(searchTerm)}`;
      }
      if (statusFilter !== 'all') {
        url += `&status=${statusFilter}`;
      }
      if (departmentFilter) {
        url += `&department_id=${departmentFilter}`;
      }

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        localStorage.removeItem('access_token');
        router.push('/login');
        return;
      }

      if (response.ok) {
        const data = await response.json();
        if (Array.isArray(data)) {
          setEmployees(data);
          setTotalEmployees(data.length);
          setTotalPages(Math.ceil(data.length / itemsPerPage));
        } else {
          setEmployees(data.items || data);
          setTotalEmployees(data.total || data.length);
          setTotalPages(Math.ceil((data.total || data.length) / itemsPerPage));
        }
      } else {
        setEmployees([]);
        setTotalEmployees(0);
        setTotalPages(1);
      }
    } catch (err) {
      console.error('Error fetching employees:', err);
      setEmployees([]);
      setTotalEmployees(0);
      setTotalPages(1);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!employeeToDelete) return;

    const token = localStorage.getItem('access_token');
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/employees/${employeeToDelete.id}`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        setEmployees(employees.filter((e) => e.id !== employeeToDelete.id));
        setShowDeleteModal(false);
        setEmployeeToDelete(null);
      }
    } catch (err) {
      console.error('Error deleting employee:', err);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-700';
      case 'inactive':
        return 'bg-gray-100 text-gray-700';
      case 'on_leave':
        return 'bg-orange-100 text-orange-700';
      case 'terminated':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'active':
        return 'Actif';
      case 'inactive':
        return 'Inactif';
      case 'on_leave':
        return 'En congé';
      case 'terminated':
        return 'Terminé';
      default:
        return status;
    }
  };

  const canEdit = user?.role === 'admin' || user?.role === 'hr_manager';

  const stats = [
    {
      title: 'Total Employés',
      value: totalEmployees,
      icon: Users,
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-500',
    },
    {
      title: 'Actifs',
      value: employees.filter((e) => e.employment_status === 'active').length,
      icon: UserCheck,
      bgColor: 'bg-green-50',
      iconColor: 'text-green-500',
    },
    {
      title: 'En congé',
      value: employees.filter((e) => e.employment_status === 'on_leave').length,
      icon: UserX,
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-500',
    },
  ];

  return (
    <MainLayout>
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Employés</h1>
            <p className="text-gray-500 mt-1">
              Gérez les informations de vos employés
            </p>
          </div>
          {canEdit && (
            <Link
              href="/employees/new"
              className="mt-4 sm:mt-0 inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-[#E31837] to-[#c41530] text-white rounded-xl font-medium hover:shadow-lg transition-all"
            >
              <Plus className="w-5 h-5" />
              Nouvel employé
            </Link>
          )}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        {stats.map((stat, index) => (
          <div
            key={index}
            className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex items-center gap-4"
          >
            <div className={`p-3 rounded-xl ${stat.bgColor}`}>
              <stat.icon className={`w-6 h-6 ${stat.iconColor}`} />
            </div>
            <div>
              <p className="text-sm text-gray-500">{stat.title}</p>
              <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher par nom, email, département..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837]"
            />
          </div>

          {/* Status Filter */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-gray-500">
              <Filter className="h-5 w-5" />
              <span className="text-sm font-medium hidden sm:inline">Statut:</span>
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837] bg-white"
            >
              <option value="all">Tous</option>
              <option value="active">Actif</option>
              <option value="inactive">Inactif</option>
              <option value="on_leave">En congé</option>
              <option value="terminated">Terminé</option>
            </select>
          </div>

          {/* Export Button */}
          <button className="inline-flex items-center gap-2 px-4 py-2.5 border border-gray-200 rounded-xl text-gray-600 hover:bg-gray-50 transition">
            <Download className="h-5 w-5" />
            <span className="hidden sm:inline">Exporter</span>
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center">
            <div className="w-12 h-12 border-4 border-[#E31837] border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="mt-4 text-gray-500">Chargement des employés...</p>
          </div>
        ) : employees.length === 0 ? (
          <div className="p-12 text-center">
            <Users className="h-16 w-16 text-gray-300 mx-auto" />
            <p className="mt-4 text-gray-500 font-medium">Aucun employé trouvé</p>
            <p className="text-sm text-gray-400 mt-1">
              Essayez de modifier vos filtres de recherche
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50 border-b border-gray-100">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Employé
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Département
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Poste
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Statut
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Date d'embauche
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {employees.map((employee) => (
                  <tr
                    key={employee.id}
                    className="hover:bg-gray-50/50 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-4">
                        <div className="h-11 w-11 flex-shrink-0 bg-gradient-to-br from-[#E31837] to-[#c41530] rounded-xl flex items-center justify-center shadow-sm">
                          <span className="text-white font-semibold text-sm">
                            {employee.first_name[0]}
                            {employee.last_name[0]}
                          </span>
                        </div>
                        <div>
                          <div className="text-sm font-semibold text-gray-900">
                            {employee.first_name} {employee.last_name}
                          </div>
                          <div className="text-sm text-gray-500 flex items-center gap-1">
                            <Mail className="h-3 w-3" />
                            {employee.email}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <Building2 className="h-4 w-4 text-gray-400" />
                        {employee.department?.name || 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-700">
                        {employee.job_title || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex px-3 py-1 text-xs font-medium rounded-full ${getStatusBadge(
                          employee.employment_status
                        )}`}
                      >
                        {getStatusLabel(employee.employment_status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(employee.hire_date).toLocaleDateString('fr-FR', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <div className="relative inline-block">
                        <button
                          onClick={() =>
                            setActiveDropdown(
                              activeDropdown === employee.id ? null : employee.id
                            )
                          }
                          className="p-2 hover:bg-gray-100 rounded-lg transition"
                        >
                          <MoreVertical className="h-5 w-5 text-gray-400" />
                        </button>

                        {activeDropdown === employee.id && (
                          <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-100 py-2 z-10">
                            <Link
                              href={`/employees/${employee.id}`}
                              className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                            >
                              <Eye className="h-4 w-4" />
                              Voir le profil
                            </Link>
                            {canEdit && (
                              <>
                                <Link
                                  href={`/employees/${employee.id}/edit`}
                                  className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                                >
                                  <Edit className="h-4 w-4" />
                                  Modifier
                                </Link>
                                <button
                                  onClick={() => {
                                    setEmployeeToDelete(employee);
                                    setShowDeleteModal(true);
                                    setActiveDropdown(null);
                                  }}
                                  className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 w-full"
                                >
                                  <Trash2 className="h-4 w-4" />
                                  Supprimer
                                </button>
                              </>
                            )}
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Affichage de{' '}
              <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> à{' '}
              <span className="font-medium">
                {Math.min(currentPage * itemsPerPage, totalEmployees)}
              </span>{' '}
              sur <span className="font-medium">{totalEmployees}</span> employés
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                <ChevronLeft className="h-5 w-5 text-gray-600" />
              </button>
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const pageNum = i + 1;
                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`px-3.5 py-2 rounded-lg text-sm font-medium transition ${
                      currentPage === pageNum
                        ? 'bg-[#E31837] text-white'
                        : 'hover:bg-gray-50 text-gray-600'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="p-2 border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                <ChevronRight className="h-5 w-5 text-gray-600" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Delete Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl">
            <div className="flex items-center gap-4 mb-4">
              <div className="p-3 bg-red-100 rounded-xl">
                <Trash2 className="h-6 w-6 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900">
                Confirmer la suppression
              </h3>
            </div>
            <p className="text-gray-600 mb-6">
              Êtes-vous sûr de vouloir supprimer{' '}
              <span className="font-semibold text-gray-900">
                {employeeToDelete?.first_name} {employeeToDelete?.last_name}
              </span>{' '}
              ? Cette action est irréversible.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowDeleteModal(false);
                  setEmployeeToDelete(null);
                }}
                className="px-5 py-2.5 border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-50 font-medium transition"
              >
                Annuler
              </button>
              <button
                onClick={handleDelete}
                className="px-5 py-2.5 bg-red-600 text-white rounded-xl hover:bg-red-700 font-medium transition"
              >
                Supprimer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Click outside to close dropdown */}
      {activeDropdown && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setActiveDropdown(null)}
        />
      )}
    </MainLayout>
  );
}


