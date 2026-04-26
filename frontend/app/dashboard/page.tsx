'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import MainLayout from '@/components/MainLayout';
import {
  Users,
  Calendar,
  TrendingUp,
  Clock,
  UserCheck,
  Building2,
  ArrowUpRight,
  ArrowDownRight,
  Briefcase,
  CalendarDays,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react';

interface Stats {
  total_employees: number;
  active_employees: number;
  departments_count: number;
  turnover_rate: number;
  avg_tenure_years: number;
}

interface User {
  id: number;
  username: string;
  full_name: string;
  role: string;
  email: string;
}

interface LeaveBalance {
  annual_total: number;
  annual_used: number;
  annual_remaining: number;
  sick_used: number;
}

interface Leave {
  id: number;
  leave_type: string;
  start_date: string;
  end_date: string;
  status: string;
  reason: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [pendingLeaves, setPendingLeaves] = useState(0);
  const [leaveBalance, setLeaveBalance] = useState<LeaveBalance | null>(null);
  const [myLeaves, setMyLeaves] = useState<Leave[]>([]);

  const isEmployee = user?.role === 'employee';

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
      
      // Si c'est un employé, charger ses données personnelles
      if (parsedUser.role === 'employee') {
        fetchMyLeaveBalance(token);
        fetchMyLeaves(token);
        setLoading(false);
      } else {
        // Manager, HR, Admin: charger les stats globales/équipe
        fetchStats(token);
        // Les pending_leaves sont déjà dans dashboard-stats, pas besoin d'appel séparé
      }
    }
  }, [router]);

  const fetchStats = async (token: string) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/analytics/dashboard-stats', {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('📊 Stats reçues:', data);
        setStats({
          total_employees: data.total_employees || 0,
          active_employees: data.active_employees || 0,
          departments_count: data.departments_count || 0,
          turnover_rate: data.turnover_rate || 0,
          avg_tenure_years: data.avg_tenure_years || 0,
        });
        
        // Si c'est un manager ou HR, récupérer les congés en attente depuis la réponse
        if (data.pending_leaves !== undefined) {
          setPendingLeaves(data.pending_leaves);
        }
      } else {
        console.error('❌ Erreur fetch stats:', response.status);
      }
    } catch (err) {
      console.error('❌ Erreur catch stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingLeaves = async (token: string) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/leaves/?status=pending', {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setPendingLeaves(data.total);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchMyLeaveBalance = async (token: string) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/leaves/balance', {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setLeaveBalance(data);
      } else {
        // Valeurs par défaut
        setLeaveBalance({
          annual_total: 22,
          annual_used: 5,
          annual_remaining: 17,
          sick_used: 2,
        });
      }
    } catch (err) {
      setLeaveBalance({
        annual_total: 22,
        annual_used: 5,
        annual_remaining: 17,
        sick_used: 2,
      });
    }
  };

  const fetchMyLeaves = async (token: string) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/leaves/', {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setMyLeaves(data.items || data.slice(0, 5));
      }
    } catch (err) {
      console.error(err);
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

  // ============================================
  // DASHBOARD EMPLOYÉ (vue personnelle uniquement)
  // ============================================
  if (isEmployee) {
    const getStatusColor = (status: string) => {
      switch (status) {
        case 'approved': return 'bg-green-100 text-green-700';
        case 'rejected': return 'bg-red-100 text-red-700';
        case 'pending': return 'bg-orange-100 text-orange-700';
        default: return 'bg-gray-100 text-gray-700';
      }
    };

    const getStatusLabel = (status: string) => {
      switch (status) {
        case 'approved': return 'Approuvé';
        case 'rejected': return 'Refusé';
        case 'pending': return 'En attente';
        default: return status;
      }
    };

    const getLeaveTypeLabel = (type: string) => {
      switch (type) {
        case 'annual': return 'Congé annuel';
        case 'sick': return 'Congé maladie';
        case 'unpaid': return 'Sans solde';
        case 'maternity': return 'Maternité';
        case 'paternity': return 'Paternité';
        default: return type;
      }
    };

    return (
      <MainLayout>
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Bonjour, {user?.full_name || user?.username} 👋
          </h1>
          <p className="text-gray-500 mt-1">
            Bienvenue sur votre espace personnel
          </p>
        </div>

        {/* Solde de congés */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Congés restants</p>
                <p className="text-4xl font-bold text-[#E31837] mt-2">
                  {leaveBalance?.annual_remaining || 0}
                </p>
                <p className="text-sm text-gray-400 mt-1">jours disponibles</p>
              </div>
              <div className="p-4 rounded-xl bg-red-50">
                <CalendarDays className="w-8 h-8 text-[#E31837]" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Congés utilisés</p>
                <p className="text-4xl font-bold text-gray-900 mt-2">
                  {leaveBalance?.annual_used || 0}
                </p>
                <p className="text-sm text-gray-400 mt-1">sur {leaveBalance?.annual_total || 22} jours</p>
              </div>
              <div className="p-4 rounded-xl bg-blue-50">
                <CheckCircle className="w-8 h-8 text-blue-500" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">Congés maladie</p>
                <p className="text-4xl font-bold text-gray-900 mt-2">
                  {leaveBalance?.sick_used || 0}
                </p>
                <p className="text-sm text-gray-400 mt-1">jours pris cette année</p>
              </div>
              <div className="p-4 rounded-xl bg-orange-50">
                <AlertCircle className="w-8 h-8 text-orange-500" />
              </div>
            </div>
          </div>
        </div>

        {/* Actions rapides employé */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions rapides</h2>
              <div className="space-y-3">
                <a
                  href="/leaves/new"
                  className="flex items-center gap-4 p-4 rounded-xl bg-gradient-to-r from-[#E31837] to-[#c41530] text-white hover:opacity-90 transition-opacity"
                >
                  <Calendar className="w-6 h-6" />
                  <span className="font-medium">Demander un congé</span>
                  <ArrowUpRight className="w-5 h-5 ml-auto" />
                </a>
                <a
                  href="/leaves"
                  className="flex items-center gap-4 p-4 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors"
                >
                  <Clock className="w-5 h-5 text-gray-600" />
                  <span className="font-medium text-gray-700">Voir mes congés</span>
                  <ArrowUpRight className="w-4 h-4 text-gray-400 ml-auto" />
                </a>
                <a
                  href="/settings"
                  className="flex items-center gap-4 p-4 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors"
                >
                  <Users className="w-5 h-5 text-gray-600" />
                  <span className="font-medium text-gray-700">Mon profil</span>
                  <ArrowUpRight className="w-4 h-4 text-gray-400 ml-auto" />
                </a>
              </div>
            </div>

            {/* Progress bar congés */}
            <div className="bg-gradient-to-br from-[#E31837] to-[#c41530] rounded-2xl p-6 shadow-lg mt-6 text-white">
              <h3 className="text-sm font-medium opacity-80">Utilisation des congés</h3>
              <div className="mt-4">
                <div className="flex justify-between text-sm mb-2">
                  <span>Utilisé: {leaveBalance?.annual_used || 0}j</span>
                  <span>Total: {leaveBalance?.annual_total || 22}j</span>
                </div>
                <div className="h-3 bg-white/20 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-white rounded-full transition-all duration-500"
                    style={{ width: `${((leaveBalance?.annual_used || 0) / (leaveBalance?.annual_total || 22)) * 100}%` }}
                  />
                </div>
                <p className="text-sm mt-3 opacity-80">
                  Il vous reste <strong>{leaveBalance?.annual_remaining || 0} jours</strong> à prendre
                </p>
              </div>
            </div>
          </div>

          {/* Mes demandes de congés */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-gray-900">Mes demandes de congés</h2>
                <a href="/leaves" className="text-sm text-[#E31837] font-medium hover:underline">
                  Voir tout
                </a>
              </div>

              {myLeaves.length > 0 ? (
                <div className="space-y-4">
                  {myLeaves.slice(0, 5).map((leave) => (
                    <div
                      key={leave.id}
                      className="flex items-center gap-4 p-4 rounded-xl bg-gray-50"
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        leave.status === 'approved' ? 'bg-green-100' :
                        leave.status === 'rejected' ? 'bg-red-100' : 'bg-orange-100'
                      }`}>
                        {leave.status === 'approved' && <CheckCircle className="w-5 h-5 text-green-500" />}
                        {leave.status === 'rejected' && <XCircle className="w-5 h-5 text-red-500" />}
                        {leave.status === 'pending' && <Clock className="w-5 h-5 text-orange-500" />}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{getLeaveTypeLabel(leave.leave_type)}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(leave.start_date).toLocaleDateString('fr-FR')} - {new Date(leave.end_date).toLocaleDateString('fr-FR')}
                        </p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(leave.status)}`}>
                        {getStatusLabel(leave.status)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Aucune demande de congé</p>
                  <a
                    href="/leaves/new"
                    className="inline-block mt-4 px-4 py-2 bg-[#E31837] text-white rounded-lg hover:bg-[#c41530] transition-colors"
                  >
                    Faire une demande
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      </MainLayout>
    );
  }

  // ============================================
  // DASHBOARD ADMIN/HR/MANAGER (vue complète)
  // ============================================

  const statCards = [
    {
      title: 'Total Employés',
      value: stats?.total_employees ?? 0,
      icon: Users,
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-500',
      change: '+12%',
      changeType: 'up',
    },
    {
      title: 'Employés Actifs',
      value: stats?.active_employees ?? 0,
      icon: UserCheck,
      bgColor: 'bg-green-50',
      iconColor: 'text-green-500',
      change: '+5%',
      changeType: 'up',
    },
    {
      title: 'Congés en attente',
      value: pendingLeaves,
      icon: Clock,
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-500',
      change: pendingLeaves > 0 ? 'À traiter' : 'Aucun',
      changeType: 'neutral',
    },
    
  ];

  // Actions rapides personnalisées selon le rôle
  const getQuickActions = () => {
    switch(user?.role) {
      case 'admin':
        return [
          { title: 'Gérer les comptes', href: '/admin/accounts', icon: Users, color: 'bg-red-500' },
          { title: 'Gérer employés', href: '/employees', icon: Briefcase, color: 'bg-blue-500' },
          { title: 'Voir Analytics', href: '/analytics', icon: TrendingUp, color: 'bg-purple-500' },
        ];
      case 'hr_manager':
        return [
          { title: 'Affecter employés', href: '/hr/assign', icon: UserCheck, color: 'bg-indigo-500' },
          { title: 'Gérer congés', href: '/leaves', icon: Calendar, color: 'bg-green-500' },
          { title: 'Nouvel employé', href: '/employees/new', icon: Users, color: 'bg-blue-500' },
          { title: 'Voir Analytics', href: '/analytics', icon: TrendingUp, color: 'bg-purple-500' },
        ];
      case 'manager':
        return [
          { title: 'Mon équipe', href: '/employees', icon: Users, color: 'bg-blue-500' },
          { title: 'Congés équipe', href: '/leaves', icon: Calendar, color: 'bg-green-500' },
          { title: 'Mes statistiques', href: '/analytics', icon: TrendingUp, color: 'bg-purple-500' },
        ];
      case 'analyst':
        return [
          { title: 'Analytics Avancés', href: '/analytics', icon: TrendingUp, color: 'bg-purple-500' },
          { title: 'Prédictions ML', href: '/ml/predictions', icon: TrendingUp, color: 'bg-pink-500' },
          { title: 'Rapports', href: '/reports', icon: Briefcase, color: 'bg-orange-500' },
        ];
      default:
        return [
          { title: 'Voir Analytics', href: '/analytics', icon: TrendingUp, color: 'bg-purple-500' },
        ];
    }
  };

  const quickActions = getQuickActions();

  // Titre personnalisé selon le rôle
  const getDashboardTitle = () => {
    switch(user?.role) {
      case 'admin': return 'Tableau de bord Administrateur';
      case 'hr_manager': return 'Tableau de bord RH';
      case 'manager': return 'Tableau de bord Manager';
      case 'analyst': return 'Tableau de bord Analytics';
      default: return 'Tableau de bord HR Analytics';
    }
  };

  return (
    <MainLayout>
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Bonjour, {user?.full_name || user?.username} 👋
        </h1>
        <p className="text-gray-500 mt-1">
          {getDashboardTitle()}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat, index) => (
          <div
            key={index}
            className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-500">{stat.title}</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stat.value}</p>
                <div className="flex items-center gap-1 mt-2">
                  {stat.changeType === 'up' && (
                    <ArrowUpRight className="w-4 h-4 text-green-500" />
                  )}
                  {stat.changeType === 'down' && (
                    <ArrowDownRight className="w-4 h-4 text-red-500" />
                  )}
                  <span className={`text-sm ${
                    stat.changeType === 'up' ? 'text-green-500' :
                    stat.changeType === 'down' ? 'text-red-500' : 'text-gray-500'
                  }`}>
                    {stat.change}
                  </span>
                </div>
              </div>
              <div className={`p-3 rounded-xl ${stat.bgColor}`}>
                <stat.icon className={`w-6 h-6 ${stat.iconColor}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Two column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions rapides</h2>
            <div className="space-y-3">
              {quickActions.map((action, index) => (
                <a
                  key={index}
                  href={action.href}
                  className="flex items-center gap-4 p-4 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors group"
                >
                  <div className={`p-2 rounded-lg ${action.color}`}>
                    <action.icon className="w-5 h-5 text-white" />
                  </div>
                  <span className="font-medium text-gray-700 group-hover:text-gray-900">
                    {action.title}
                  </span>
                  <ArrowUpRight className="w-4 h-4 text-gray-400 ml-auto group-hover:text-gray-600" />
                </a>
              ))}
            </div>
          </div>

          {/* Section spéciale pour HR Manager */}
          {user?.role === 'hr_manager' && (
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 shadow-lg mt-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <UserCheck className="w-6 h-6" />
                <h3 className="text-lg font-semibold">Espace RH</h3>
              </div>
              <p className="text-sm opacity-90 mb-4">
                Gérez les affectations des nouveaux employés et validez les demandes de congés
              </p>
              <a
                href="/hr/assign"
                className="inline-flex items-center gap-2 px-4 py-2 bg-white text-indigo-600 rounded-lg hover:bg-indigo-50 transition-colors font-medium"
              >
                <Users className="w-4 h-4" />
                Affecter des employés
              </a>
            </div>
          )}

          {/* Section spéciale pour Manager */}
          {user?.role === 'manager' && (
            <div className="bg-gradient-to-br from-blue-500 to-cyan-600 rounded-2xl p-6 shadow-lg mt-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <Users className="w-6 h-6" />
                <h3 className="text-lg font-semibold">Mon Équipe</h3>
              </div>
              <p className="text-sm opacity-90 mb-4">
                {stats?.active_employees || 0} employés sous votre responsabilité
              </p>
              {pendingLeaves > 0 && (
                <div className="flex items-center gap-2 mb-4 p-3 bg-white/20 rounded-lg">
                  <AlertCircle className="w-5 h-5" />
                  <span className="text-sm font-medium">{pendingLeaves} demande{pendingLeaves > 1 ? 's' : ''} de congé à valider</span>
                </div>
              )}
              <a
                href="/leaves"
                className="inline-flex items-center gap-2 px-4 py-2 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium"
              >
                <Calendar className="w-4 h-4" />
                Gérer les congés
              </a>
            </div>
          )}

          {/* Section spéciale pour Admin */}
          {user?.role === 'admin' && (
            <div className="bg-gradient-to-br from-red-500 to-pink-600 rounded-2xl p-6 shadow-lg mt-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <Building2 className="w-6 h-6" />
                <h3 className="text-lg font-semibold">Administration</h3>
              </div>
              <p className="text-sm opacity-90 mb-4">
                Accès complet à toutes les fonctionnalités du système
              </p>
              <a
                href="/admin/accounts"
                className="inline-flex items-center gap-2 px-4 py-2 bg-white text-red-600 rounded-lg hover:bg-red-50 transition-colors font-medium"
              >
                <UserCheck className="w-4 h-4" />
                Gérer les comptes
              </a>
            </div>
          )}

          {/* Section spéciale pour Analyst */}
          {user?.role === 'analyst' && (
            <div className="bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl p-6 shadow-lg mt-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <TrendingUp className="w-6 h-6" />
                <h3 className="text-lg font-semibold">Analytics & ML</h3>
              </div>
              <p className="text-sm opacity-90 mb-4">
                Explorez les données RH et les prédictions de turnover
              </p>
              <a
                href="/analytics"
                className="inline-flex items-center gap-2 px-4 py-2 bg-white text-purple-600 rounded-lg hover:bg-purple-50 transition-colors font-medium"
              >
                <TrendingUp className="w-4 h-4" />
                Voir Analytics
              </a>
            </div>
          )}
        </div>
      

        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">
                {user?.role === 'manager' ? 'Congés de mon équipe' : 'Activité récente'}
              </h2>
              <a href="/leaves" className="text-sm text-[#E31837] font-medium hover:underline">
                Voir tout
              </a>
            </div>

            <div className="space-y-3">
              {pendingLeaves > 0 ? (
                <div className="flex items-center gap-4 p-4 rounded-xl bg-orange-50 border border-orange-100">
                  <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                    <Clock className="w-5 h-5 text-orange-500" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">{pendingLeaves} demande{pendingLeaves > 1 ? 's' : ''} en attente</p>
                    <p className="text-sm text-gray-500">
                      {user?.role === 'manager' ? 'Validation requise pour votre équipe' : 'Nécessite une validation'}
                    </p>
                  </div>
                  <a
                    href="/leaves"
                    className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors text-sm font-medium"
                  >
                    Traiter
                  </a>
                </div>
              ) : (
                <div className="text-center py-8">
                  <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-3" />
                  <p className="text-gray-500">Aucune demande en attente</p>
                  <p className="text-sm text-gray-400 mt-1">Tout est à jour !</p>
                </div>
              )}

              {user?.role === 'hr_manager' && (
                <a
                  href="/hr/assign"
                  className="flex items-center gap-4 p-4 rounded-xl bg-indigo-50 border border-indigo-100 hover:bg-indigo-100 transition-colors"
                >
                  <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center">
                    <UserCheck className="w-5 h-5 text-indigo-500" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Affectation des employés</p>
                    <p className="text-sm text-gray-500">Assigner les nouveaux employés à leurs départements</p>
                  </div>
                  <ArrowUpRight className="w-5 h-5 text-indigo-500" />
                </a>
              )}

              {user?.role === 'analyst' && (
                <a
                  href="/analytics"
                  className="flex items-center gap-4 p-4 rounded-xl bg-purple-50 border border-purple-100 hover:bg-purple-100 transition-colors"
                >
                  <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-purple-500" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-gray-900">Rapport analytique disponible</p>
                    <p className="text-sm text-gray-500">Consultez les dernières analyses RH</p>
                  </div>
                  <ArrowUpRight className="w-5 h-5 text-purple-500" />
                </a>
              )}
            </div>
           
          </div>

          {/* Department Overview - Seulement pour Admin et HR */}
          {(user?.role === 'admin' || user?.role === 'hr_manager') && (
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mt-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">Répartition par département</h2>
              <div className="space-y-4">
                {[
                  { name: 'Développement', count: 45, color: 'bg-blue-500', percent: 30 },
                  { name: 'Marketing', count: 28, color: 'bg-green-500', percent: 19 },
                  { name: 'RH', count: 15, color: 'bg-purple-500', percent: 10 },
                  { name: 'Finance', count: 22, color: 'bg-orange-500', percent: 15 },
                  { name: 'Commercial', count: 40, color: 'bg-pink-500', percent: 26 },
                ].map((dept, index) => (
                  <div key={index}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">{dept.name}</span>
                      <span className="text-sm text-gray-500">{dept.count} employés</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${dept.color} rounded-full transition-all duration-500`}
                        style={{ width: `${dept.percent}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}


