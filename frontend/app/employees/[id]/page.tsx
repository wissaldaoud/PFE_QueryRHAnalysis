'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import MainLayout from '@/components/MainLayout';
import {
  User,
  Mail,
  Phone,
  Building2,
  Calendar,
  Briefcase,
  MapPin,
  Edit,
  ArrowLeft,
  Clock,
  DollarSign,
  FileText,
  Award,
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
  address?: string;
  date_of_birth?: string;
  emergency_contact?: string;
  contract_type?: string;
}

interface LeaveBalance {
  annual_total: number;
  annual_used: number;
  annual_remaining: number;
  sick_used: number;
}

export default function EmployeeProfilePage() {
  const router = useRouter();
  const params = useParams();
  const employeeId = params.id as string;

  const [employee, setEmployee] = useState<Employee | null>(null);
  const [leaveBalance, setLeaveBalance] = useState<LeaveBalance | null>(null);
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState<string>('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');

    if (!token) {
      router.push('/login');
      return;
    }

    if (userData) {
      const user = JSON.parse(userData);
      setUserRole(user.role);
      
      // Les employés simples ne peuvent pas voir les profils des autres
      if (user.role === 'employee') {
        router.push('/dashboard');
        return;
      }
    }

    fetchEmployee(token);
    fetchLeaveBalance(token);
  }, [employeeId, router]);

  const fetchEmployee = async (token: string) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/employees/${employeeId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setEmployee(data);
      }
    } catch (err) {
      console.error('Error fetching employee:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchLeaveBalance = async (token: string) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/leaves/balance/${employeeId}`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setLeaveBalance(data);
      }
    } catch (err) {
      console.error('Error fetching leave balance:', err);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return { label: 'Actif', color: 'bg-green-100 text-green-700' };
      case 'inactive':
        return { label: 'Inactif', color: 'bg-gray-100 text-gray-700' };
      case 'on_leave':
        return { label: 'En congé', color: 'bg-orange-100 text-orange-700' };
      case 'terminated':
        return { label: 'Terminé', color: 'bg-red-100 text-red-700' };
      default:
        return { label: status, color: 'bg-gray-100 text-gray-700' };
    }
  };

  const canEdit = userRole === 'admin' || userRole === 'hr_manager';

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-96">
          <div className="w-12 h-12 border-4 border-[#E31837] border-t-transparent rounded-full animate-spin"></div>
        </div>
      </MainLayout>
    );
  }

  if (!employee) {
    return (
      <MainLayout>
        <div className="text-center py-12">
          <p className="text-gray-500">Employé non trouvé</p>
        </div>
      </MainLayout>
    );
  }

  const status = getStatusBadge(employee.employment_status);

  return (
    <MainLayout>
      {/* Back Button */}
      <button
        onClick={() => router.push('/employees')}
        className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-6 transition"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>Retour aux employés</span>
      </button>

      {/* Profile Header */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 bg-gradient-to-br from-[#E31837] to-[#c41530] rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-white text-2xl font-bold">
                {employee.first_name[0]}
                {employee.last_name[0]}
              </span>
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold text-gray-900">
                  {employee.first_name} {employee.last_name}
                </h1>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${status.color}`}>
                  {status.label}
                </span>
              </div>
              <p className="text-gray-500 mt-1">{employee.job_title}</p>
              <p className="text-sm text-gray-400 mt-1">
                Code: {employee.employee_code}
              </p>
            </div>
          </div>

          {canEdit && (
            <button
              onClick={() => router.push(`/employees/${employeeId}/edit`)}
              className="mt-4 sm:mt-0 inline-flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition"
            >
              <Edit className="w-4 h-4" />
              Modifier
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Contact Info */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Informations de contact
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                <Mail className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">Email</p>
                  <p className="text-sm font-medium text-gray-900">{employee.email}</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                <Phone className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">Téléphone</p>
                  <p className="text-sm font-medium text-gray-900">
                    {employee.phone || 'Non renseigné'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                <MapPin className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">Adresse</p>
                  <p className="text-sm font-medium text-gray-900">
                    {employee.address || 'Non renseignée'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                <Phone className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">Contact urgence</p>
                  <p className="text-sm font-medium text-gray-900">
                    {employee.emergency_contact || 'Non renseigné'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Employment Info */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Informations professionnelles
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                <Building2 className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">Département</p>
                  <p className="text-sm font-medium text-gray-900">
                    {employee.department?.name || 'Non assigné'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                <Briefcase className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">Poste</p>
                  <p className="text-sm font-medium text-gray-900">
                    {employee.job_title || 'Non renseigné'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                <Calendar className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">Date d'embauche</p>
                  <p className="text-sm font-medium text-gray-900">
                    {new Date(employee.hire_date).toLocaleDateString('fr-FR', {
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric',
                    })}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                <FileText className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">Type de contrat</p>
                  <p className="text-sm font-medium text-gray-900">
                    {employee.contract_type || 'CDI'}
                  </p>
                </div>
              </div>
              {canEdit && employee.salary && (
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                  <DollarSign className="w-5 h-5 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">Salaire annuel</p>
                    <p className="text-sm font-medium text-gray-900">
                      {employee.salary.toLocaleString('fr-FR')} MAD
                    </p>
                  </div>
                </div>
              )}
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                <Clock className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-xs text-gray-500">Ancienneté</p>
                  <p className="text-sm font-medium text-gray-900">
                    {Math.floor(
                      (new Date().getTime() - new Date(employee.hire_date).getTime()) /
                        (1000 * 60 * 60 * 24 * 365)
                    )}{' '}
                    ans
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Leave Balance */}
          {leaveBalance && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Solde de congés
              </h2>
              
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-600">Congés annuels</span>
                  <span className="text-sm font-medium">
                    {leaveBalance.annual_remaining}/{leaveBalance.annual_total} jours
                  </span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-[#E31837] to-[#c41530] rounded-full"
                    style={{
                      width: `${
                        (leaveBalance.annual_remaining / leaveBalance.annual_total) * 100
                      }%`,
                    }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 bg-green-50 rounded-xl text-center">
                  <p className="text-2xl font-bold text-green-700">
                    {leaveBalance.annual_remaining}
                  </p>
                  <p className="text-xs text-green-600">Restants</p>
                </div>
                <div className="p-3 bg-orange-50 rounded-xl text-center">
                  <p className="text-2xl font-bold text-orange-700">
                    {leaveBalance.annual_used}
                  </p>
                  <p className="text-xs text-orange-600">Utilisés</p>
                </div>
              </div>

              <div className="mt-4 p-3 bg-blue-50 rounded-xl">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-blue-700">Maladie utilisés</span>
                  <span className="font-medium text-blue-800">
                    {leaveBalance.sick_used} jours
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Quick Actions */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Actions rapides
            </h2>
            <div className="space-y-2">
              <button
                onClick={() => router.push(`/leaves/new?employee=${employeeId}`)}
                className="w-full flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition text-left"
              >
                <Calendar className="w-5 h-5 text-[#E31837]" />
                <span className="text-sm font-medium text-gray-700">
                  Demander un congé
                </span>
              </button>
              <button
                onClick={() => router.push(`/leaves?employee=${employeeId}`)}
                className="w-full flex items-center gap-3 p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition text-left"
              >
                <FileText className="w-5 h-5 text-blue-500" />
                <span className="text-sm font-medium text-gray-700">
                  Historique des congés
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
