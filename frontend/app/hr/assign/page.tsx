'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import MainLayout from '@/components/MainLayout';
import { Users, Building2, UserCheck, Briefcase, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface Employee {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  employee_code: string;
  job_title?: string;
  department_id?: number;
  manager_id?: number;
  hire_date: string;
}

interface Department {
  id: number;
  name: string;
  code: string;
}

interface Manager {
  id: number;
  first_name: string;
  last_name: string;
  employee_code: string;
}

export default function AssignEmployeesPage() {
  const router = useRouter();
  const [unassignedEmployees, setUnassignedEmployees] = useState<Employee[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [managers, setManagers] = useState<Manager[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [assignData, setAssignData] = useState({
    department_id: '',
    manager_id: '',
    job_title: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');

    if (!token) {
      router.push('/login');
      return;
    }

    if (userData) {
      const user = JSON.parse(userData);
      // Vérifier que c'est un RH ou Admin
      if (!['hr_manager', 'admin'].includes(user.role)) {
        router.push('/dashboard');
        return;
      }
    }

    fetchData(token);
  }, [router]);

  const fetchData = async (token: string) => {
    setLoading(true);
    try {
      // Récupérer les employés non-affectés
      const empRes = await fetch('http://127.0.0.1:8000/api/v1/employees/unassigned', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (empRes.ok) {
        const empData = await empRes.json();
        setUnassignedEmployees(empData);
      }

      // Récupérer les départements
      const deptRes = await fetch('http://127.0.0.1:8000/api/v1/departments/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (deptRes.ok) {
        const deptData = await deptRes.json();
        setDepartments(deptData);
      }

      // Récupérer les managers disponibles (avec rôle manager/admin et département assigné)
      const managersRes = await fetch('http://127.0.0.1:8000/api/v1/employees/managers', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (managersRes.ok) {
        const managersData = await managersRes.json();
        setManagers(managersData);
      }
    } catch (err) {
      console.error('Erreur chargement:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignClick = (employee: Employee) => {
    setSelectedEmployee(employee);
    setAssignData({
      department_id: employee.department_id?.toString() || '',
      manager_id: employee.manager_id?.toString() || '',
      job_title: employee.job_title || '',
    });
    setShowAssignModal(true);
  };

  const handleAssignSubmit = async () => {
    if (!selectedEmployee) return;

    const token = localStorage.getItem('access_token');
    if (!token) return;

    setSubmitting(true);
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/employees/${selectedEmployee.id}/assign`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            department_id: assignData.department_id ? parseInt(assignData.department_id) : null,
            manager_id: assignData.manager_id ? parseInt(assignData.manager_id) : null,
            job_title: assignData.job_title || null,
          }),
        }
      );

      if (response.ok) {
        setNotification({
          type: 'success',
          message: `Employé ${selectedEmployee.first_name} ${selectedEmployee.last_name} affecté avec succès`,
        });
        setShowAssignModal(false);
        fetchData(token);
        setTimeout(() => setNotification(null), 3000);
      } else {
        const error = await response.json();
        setNotification({
          type: 'error',
          message: error.detail || 'Erreur lors de l\'affectation',
        });
      }
    } catch (err) {
      setNotification({
        type: 'error',
        message: 'Erreur réseau',
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-96">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-[#E31837] border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="mt-4 text-gray-500">Chargement...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      {/* Notification */}
      {notification && (
        <div
          className={`fixed top-4 right-4 z-50 px-6 py-4 rounded-lg shadow-lg flex items-center gap-3 ${
            notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'
          } text-white`}
        >
          {notification.type === 'success' ? (
            <CheckCircle className="w-5 h-5" />
          ) : (
            <XCircle className="w-5 h-5" />
          )}
          <span>{notification.message}</span>
        </div>
      )}

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Affectation des employés</h1>
        <p className="text-gray-500 mt-1">Affecter les nouveaux employés à un département et un manager</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-orange-50">
              <AlertCircle className="w-6 h-6 text-orange-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Non affectés</p>
              <p className="text-3xl font-bold text-gray-900">{unassignedEmployees.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-blue-50">
              <Building2 className="w-6 h-6 text-blue-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Départements</p>
              <p className="text-3xl font-bold text-gray-900">{departments.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-green-50">
              <UserCheck className="w-6 h-6 text-green-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Managers disponibles</p>
              <p className="text-3xl font-bold text-gray-900">{managers.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Liste des employés non-affectés */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Employés à affecter</h2>

        {unassignedEmployees.length > 0 ? (
          <div className="space-y-4">
            {unassignedEmployees.map((employee) => (
              <div
                key={employee.id}
                className="flex items-center justify-between p-4 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#E31837] to-[#c41530] flex items-center justify-center text-white font-bold">
                    {employee.first_name[0]}{employee.last_name[0]}
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">
                      {employee.first_name} {employee.last_name}
                    </p>
                    <p className="text-sm text-gray-500">{employee.email}</p>
                    <p className="text-xs text-gray-400">Code: {employee.employee_code}</p>
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <div className="flex items-center gap-2 mb-1">
                      <Building2 className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600">
                        {employee.department_id ? '✓ Département' : '⚠️ Sans département'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <UserCheck className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600">
                        {employee.manager_id ? '✓ Manager' : '⚠️ Sans manager'}
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={() => handleAssignClick(employee)}
                    className="px-4 py-2 bg-[#E31837] text-white rounded-lg hover:bg-[#c41530] transition-colors font-medium"
                  >
                    Affecter
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Tous les employés ont été affectés !</p>
          </div>
        )}
      </div>

      {/* Modal d'affectation */}
      {showAssignModal && selectedEmployee && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-8 max-w-lg w-full shadow-2xl">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">
              Affecter {selectedEmployee.first_name} {selectedEmployee.last_name}
            </h3>

            <div className="space-y-4 mb-6">
              {/* Département */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Département *
                </label>
                <select
                  value={assignData.department_id}
                  onChange={(e) => setAssignData({ ...assignData, department_id: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent"
                >
                  <option value="">Sélectionner un département</option>
                  {departments.map((dept) => (
                    <option key={dept.id} value={dept.id}>
                      {dept.name} ({dept.code})
                    </option>
                  ))}
                </select>
              </div>

              {/* Manager */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Manager (optionnel)
                </label>
                <select
                  value={assignData.manager_id}
                  onChange={(e) => setAssignData({ ...assignData, manager_id: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent"
                >
                  <option value="">Sélectionner un manager</option>
                  {managers
                    .filter((m) => m.id !== selectedEmployee.id)
                    .map((manager) => (
                      <option key={manager.id} value={manager.id}>
                        {manager.first_name} {manager.last_name} ({manager.employee_code})
                      </option>
                    ))}
                </select>
              </div>

              {/* Poste */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Titre du poste
                </label>
                <input
                  type="text"
                  value={assignData.job_title}
                  onChange={(e) => setAssignData({ ...assignData, job_title: e.target.value })}
                  placeholder="Ex: Développeur, Assistant RH..."
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setShowAssignModal(false)}
                disabled={submitting}
                className="flex-1 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                Annuler
              </button>
              <button
                onClick={handleAssignSubmit}
                disabled={submitting || !assignData.department_id}
                className="flex-1 px-6 py-3 bg-[#E31837] text-white rounded-lg hover:bg-[#c41530] transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? 'Affectation...' : 'Affecter'}
              </button>
            </div>
          </div>
        </div>
      )}
    </MainLayout>
  );
}
