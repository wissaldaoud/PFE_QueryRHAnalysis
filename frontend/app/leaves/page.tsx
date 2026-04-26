'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import MainLayout from '@/components/MainLayout';
import LeaveCalendar from '@/components/LeaveCalendar';
import {
  Calendar,
  Plus,
  Filter,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Eye,
  Search,
  CalendarDays,
  Hourglass,
  CalendarCheck,
  CalendarX,
  LayoutGrid,
  List,
} from 'lucide-react';

interface LeaveRequest {
  id: number;
  employee_id: number;
  employee_name?: string;
  leave_type: 'annual' | 'sick' | 'unpaid';
  start_date: string;
  end_date: string;
  days_requested: number;
  reason?: string;
  status: 'pending' | 'manager_approved' | 'hr_approved' | 'rejected' | 'cancelled';
  approver_name?: string;
  manager_approver_name?: string;
  hr_approver_name?: string;
  rejection_reason?: string;
  created_at: string;
}

const leaveTypeConfig: Record<string, { label: string; color: string; bgColor: string }> = {
  annual: { label: 'Congé Annuel', color: 'text-blue-700', bgColor: 'bg-blue-100' },
  sick: { label: 'Maladie', color: 'text-orange-700', bgColor: 'bg-orange-100' },
  unpaid: { label: 'Sans Solde', color: 'text-gray-700', bgColor: 'bg-gray-100' },
};

const statusConfig: Record<string, { label: string; color: string; bgColor: string; icon: React.ElementType }> = {
  pending: { label: 'En attente Manager', color: 'text-amber-700', bgColor: 'bg-amber-100', icon: Clock },
  manager_approved: { label: 'Approuvé Manager (En attente RH)', color: 'text-blue-700', bgColor: 'bg-blue-100', icon: Hourglass },
  hr_approved: { label: 'Approuvé (Final)', color: 'text-green-700', bgColor: 'bg-green-100', icon: CheckCircle },
  rejected: { label: 'Refusé', color: 'text-red-700', bgColor: 'bg-red-100', icon: XCircle },
  cancelled: { label: 'Annulé', color: 'text-gray-700', bgColor: 'bg-gray-100', icon: AlertCircle },
};

export default function LeavesPage() {
  const router = useRouter();
  const [leaves, setLeaves] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalLeaves, setTotalLeaves] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [userRole, setUserRole] = useState<string>('');
  const [viewMode, setViewMode] = useState<'list' | 'calendar'>('list');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');

    if (!token) {
      router.push('/login');
      return;
    }

    if (user) {
      const userData = JSON.parse(user);
      setUserRole(userData.role);
    }

    fetchLeaves();
  }, [currentPage, statusFilter, typeFilter]);

  const fetchLeaves = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      let url = `http://127.0.0.1:8000/api/v1/leaves?page=${currentPage}&page_size=10`;

      if (statusFilter) url += `&status=${statusFilter}`;
      if (typeFilter) url += `&leave_type=${typeFilter}`;

      const res = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (res.ok) {
        const data = await res.json();
        setLeaves(data.items);
        setTotalPages(data.total_pages);
        setTotalLeaves(data.total);
      } else {
        setLeaves([]);
        setTotalLeaves(0);
      }
    } catch (error) {
      console.error('Error fetching leaves:', error);
      setLeaves([]);
      setTotalLeaves(0);
    } finally {
      setLoading(false);
    }
  };

  const handleManagerApprove = async (id: number) => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`http://localhost:8000/api/v1/leaves/${id}/manager-approve`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (res.ok) {
        alert('Demande approuvée par le manager!');
        fetchLeaves();
      } else {
        const error = await res.json();
        alert(`Erreur: ${error.detail || 'Impossible d\'approuver'}`);
      }
    } catch (error) {
      console.error('Error approving leave:', error);
      alert('Erreur lors de l\'approbation');
    }
  };

  const handleManagerReject = async (id: number) => {
    const reason = prompt('Motif du refus:');
    if (!reason) return;

    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`http://localhost:8000/api/v1/leaves/${id}/manager-reject`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ rejection_reason: reason }),
      });

      if (res.ok) {
        alert('Demande rejetée par le manager.');
        fetchLeaves();
      } else {
        const error = await res.json();
        alert(`Erreur: ${error.detail || 'Impossible de rejeter'}`);
      }
    } catch (error) {
      console.error('Error rejecting leave:', error);
      alert('Erreur lors du rejet');
    }
  };

  const handleHRApprove = async (id: number) => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`http://localhost:8000/api/v1/leaves/${id}/hr-approve`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (res.ok) {
        alert('Demande approuvée par RH (final)!');
        fetchLeaves();
      } else {
        const error = await res.json();
        alert(`Erreur: ${error.detail || 'Impossible d\'approuver'}`);
      }
    } catch (error) {
      console.error('Error approving leave (HR):', error);
      alert('Erreur lors de l\'approbation RH');
    }
  };

  const handleHRReject = async (id: number) => {
    const reason = prompt('Motif du refus (RH):');
    if (!reason) return;

    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`http://localhost:8000/api/v1/leaves/${id}/hr-reject`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ rejection_reason: reason }),
      });

      if (res.ok) {
        alert('Demande rejetée par RH.');
        fetchLeaves();
      } else {
        const error = await res.json();
        alert(`Erreur: ${error.detail || 'Impossible de rejeter'}`);
      }
    } catch (error) {
      console.error('Error rejecting leave (HR):', error);
      alert('Erreur lors du rejet RH');
    }
  };

  const canApprove = ['admin', 'hr_manager', 'manager'].includes(userRole);

  const pendingCount = leaves.filter((l) => l.status === 'pending').length;
  const managerApprovedCount = leaves.filter((l) => l.status === 'manager_approved').length;
  const approvedCount = leaves.filter((l) => l.status === 'hr_approved').length;
  const rejectedCount = leaves.filter((l) => l.status === 'rejected').length;

  const stats = [
    {
      title: 'En attente Manager',
      value: pendingCount,
      icon: Hourglass,
      bgColor: 'bg-amber-50',
      iconColor: 'text-amber-500',
    },
    {
      title: 'En attente RH',
      value: managerApprovedCount,
      icon: Clock,
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-500',
    },
    {
      title: 'Approuvés',
      value: approvedCount,
      icon: CalendarCheck,
      bgColor: 'bg-green-50',
      iconColor: 'text-green-500',
    },
    {
      title: 'Refusés',
      value: rejectedCount,
      icon: CalendarX,
      bgColor: 'bg-red-50',
      iconColor: 'text-red-500',
    },
  ];

  return (
    <MainLayout>
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Gestion des Congés</h1>
            <p className="text-gray-500 dark:text-gray-400 mt-1">
              Consultez et gérez les demandes de congés
            </p>
          </div>
          <div className="flex items-center gap-3 mt-4 sm:mt-0">
            {/* Toggle View Mode */}
            <div className="flex items-center bg-gray-100 dark:bg-gray-700 rounded-xl p-1">
              <button
                onClick={() => setViewMode('list')}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
                  viewMode === 'list' 
                    ? 'bg-white dark:bg-gray-600 shadow-sm text-gray-900 dark:text-white' 
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                }`}
              >
                <List className="w-4 h-4" />
                <span className="text-sm font-medium hidden sm:inline">Liste</span>
              </button>
              <button
                onClick={() => setViewMode('calendar')}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
                  viewMode === 'calendar' 
                    ? 'bg-white dark:bg-gray-600 shadow-sm text-gray-900 dark:text-white' 
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                }`}
              >
                <LayoutGrid className="w-4 h-4" />
                <span className="text-sm font-medium hidden sm:inline">Calendrier</span>
              </button>
            </div>
            <Link
              href="/leaves/new"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-[#E31837] to-[#c41530] text-white rounded-xl font-medium hover:shadow-lg transition-all"
            >
              <Plus className="w-5 h-5" />
              <span className="hidden sm:inline">Nouvelle demande</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat, index) => (
          <div
            key={index}
            className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm border border-gray-100 dark:border-gray-700"
          >
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl ${stat.bgColor} dark:bg-opacity-20`}>
                <stat.icon className={`w-6 h-6 ${stat.iconColor}`} />
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Calendar View */}
      {viewMode === 'calendar' && (
        <div className="mb-8">
          <LeaveCalendar 
            leaves={leaves.map(l => ({
              id: l.id,
              employee_name: l.employee_name || `Employé #${l.employee_id}`,
              leave_type: l.leave_type,
              start_date: l.start_date,
              end_date: l.end_date,
              status: l.status,
            }))} 
          />
        </div>
      )}

      {/* List View */}
      {viewMode === 'list' && (
        <>
          {/* Filters */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow-sm border border-gray-100 dark:border-gray-700 mb-6">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher par employé..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837]"
            />
          </div>

          {/* Filters */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-gray-500">
              <Filter className="h-5 w-5" />
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837] bg-white"
            >
              <option value="">Tous les statuts</option>
              <option value="pending">En attente</option>
              <option value="approved">Approuvés</option>
              <option value="rejected">Refusés</option>
              <option value="cancelled">Annulés</option>
            </select>

            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837] bg-white"
            >
              <option value="">Tous les types</option>
              <option value="annual">Congé Annuel</option>
              <option value="sick">Maladie</option>
              <option value="unpaid">Sans Solde</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center">
            <div className="w-12 h-12 border-4 border-[#E31837] border-t-transparent rounded-full animate-spin mx-auto"></div>
            <p className="mt-4 text-gray-500">Chargement des demandes...</p>
          </div>
        ) : leaves.length === 0 ? (
          <div className="p-12 text-center">
            <Calendar className="h-16 w-16 text-gray-300 mx-auto" />
            <p className="mt-4 text-gray-500 font-medium">
              Aucune demande de congé trouvée
            </p>
            <p className="text-sm text-gray-400 mt-1">
              Les demandes apparaîtront ici une fois créées
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
                    Type
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Période
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Durée
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Statut
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {leaves.map((leave) => {
                  const StatusIcon = statusConfig[leave.status]?.icon || Clock;
                  return (
                    <tr
                      key={leave.id}
                      className="hover:bg-gray-50/50 transition-colors"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 bg-gradient-to-br from-[#E31837] to-[#c41530] rounded-xl flex items-center justify-center shadow-sm">
                            <span className="text-white font-semibold text-sm">
                              {(leave.employee_name || 'E')
                                .split(' ')
                                .map((n) => n[0])
                                .join('')
                                .slice(0, 2)}
                            </span>
                          </div>
                          <div>
                            <p className="font-semibold text-gray-900">
                              {leave.employee_name || `Employé #${leave.employee_id}`}
                            </p>
                            <p className="text-xs text-gray-500">
                              Demandé le{' '}
                              {new Date(leave.created_at).toLocaleDateString('fr-FR')}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${
                            leaveTypeConfig[leave.leave_type]?.bgColor
                          } ${leaveTypeConfig[leave.leave_type]?.color}`}
                        >
                          {leaveTypeConfig[leave.leave_type]?.label}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {new Date(leave.start_date).toLocaleDateString('fr-FR', {
                              day: 'numeric',
                              month: 'short',
                            })}
                          </p>
                          <p className="text-xs text-gray-500">
                            →{' '}
                            {new Date(leave.end_date).toLocaleDateString('fr-FR', {
                              day: 'numeric',
                              month: 'short',
                              year: 'numeric',
                            })}
                          </p>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-1">
                          <span className="text-xl font-bold text-gray-900">
                            {leave.days_requested}
                          </span>
                          <span className="text-sm text-gray-500">
                            jour{leave.days_requested > 1 ? 's' : ''}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ${
                            statusConfig[leave.status]?.bgColor
                          } ${statusConfig[leave.status]?.color}`}
                        >
                          <StatusIcon className="w-3.5 h-3.5" />
                          {statusConfig[leave.status]?.label}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => router.push(`/leaves/${leave.id}`)}
                            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition"
                            title="Voir détails"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          {/* Manager: peut approuver/rejeter si status = pending */}
                          {(userRole === 'manager' || userRole === 'hr_manager' || userRole === 'admin') && leave.status === 'pending' && (
                            <>
                              <button
                                onClick={() => handleManagerApprove(leave.id)}
                                className="px-3 py-1.5 text-xs bg-blue-100 text-blue-700 hover:bg-blue-200 rounded-lg transition font-medium"
                                title="Approuver (Manager)"
                              >
                                ✓ Manager
                              </button>
                              <button
                                onClick={() => handleManagerReject(leave.id)}
                                className="px-3 py-1.5 text-xs bg-red-100 text-red-700 hover:bg-red-200 rounded-lg transition font-medium"
                                title="Refuser (Manager)"
                              >
                                ✗ Refuser
                              </button>
                            </>
                          )}
                          {/* RH: peut approuver/rejeter si status = manager_approved */}
                          {(userRole === 'hr_manager' || userRole === 'admin') && leave.status === 'manager_approved' && (
                            <>
                              <button
                                onClick={() => handleHRApprove(leave.id)}
                                className="px-3 py-1.5 text-xs bg-green-100 text-green-700 hover:bg-green-200 rounded-lg transition font-medium"
                                title="Approuver final (RH)"
                              >
                                ✓ RH (Final)
                              </button>
                              <button
                                onClick={() => handleHRReject(leave.id)}
                                className="px-3 py-1.5 text-xs bg-red-100 text-red-700 hover:bg-red-200 rounded-lg transition font-medium"
                                title="Refuser (RH)"
                              >
                                ✗ Refuser
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Page <span className="font-medium">{currentPage}</span> sur{' '}
              <span className="font-medium">{totalPages}</span>
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                <ChevronLeft className="w-5 h-5 text-gray-600 dark:text-gray-300" />
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
                        : 'hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300'
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="p-2 border border-gray-200 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                <ChevronRight className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </button>
            </div>
          </div>
        )}
      </div>
        </>
      )}
    </MainLayout>
  );
}


