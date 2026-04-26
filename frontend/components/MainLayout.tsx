'use client';

import { ReactNode, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import {
  LayoutDashboard,
  Users,
  Calendar,
  Building2,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
  Search,
  ChevronDown,
  TrendingDown,
  User,
  UserCheck,
  Database,
} from 'lucide-react';
import NotificationBell from './NotificationBell';
import ThemeToggle from './ThemeToggle';

interface LayoutProps {
  children: ReactNode;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Moteur de Requêtes', href: '/query', icon: Database, highlight: true },
{ name: 'Prédiction Turnover', href: '/turnover', icon: TrendingDown, roles: ['admin', 'hr_manager', 'analyst', 'manager'] },
  { name: 'Employés', href: '/employees', icon: Users, roles: ['admin', 'hr_manager', 'manager'] },
  { name: 'Congés', href: '/leaves', icon: Calendar },
  { name: 'Départements', href: '/departments', icon: Building2, roles: ['admin', 'hr_manager', 'manager'] },
  { name: 'Analytics', href: '/analytics', icon: BarChart3, roles: ['admin', 'hr_manager', 'analyst'] },
  { name: 'Comptes en attente', href: '/admin/accounts', icon: UserCheck, roles: ['admin', 'hr_manager'] },
];

export default function MainLayout({ children }: LayoutProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  // Get user from localStorage (client-side only)
  const getUserData = () => {
    if (typeof window !== 'undefined') {
      const userData = localStorage.getItem('user');
      return userData ? JSON.parse(userData) : null;
    }
    return null;
  };

  const user = getUserData();

  const handleLogout = () => {
    // Clear local storage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    
    // Redirect to login page
    router.push('/login');
  };

  const getRoleBadge = (role: string) => {
    const badges: Record<string, { label: string; color: string }> = {
      admin: { label: 'Administrateur', color: 'bg-red-100 text-red-700' },
      hr_manager: { label: 'RH Manager', color: 'bg-blue-100 text-blue-700' },
      manager: { label: 'Manager', color: 'bg-purple-100 text-purple-700' },
      analyst: { label: 'Analyste', color: 'bg-green-100 text-green-700' },
      employee: { label: 'Employé', color: 'bg-gray-100 text-gray-700' },
    };
    return badges[role] || badges.employee;
  };

  const filteredNav = navigation.filter(item => {
    if (!item.roles) return true;
    return user && item.roles.includes(user.role);
  });

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-64 bg-white dark:bg-gray-800 shadow-xl transform transition-transform duration-300 ease-in-out
          lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-6 border-b dark:border-gray-700">
          <Link href="/dashboard" className="flex items-center gap-2">
            <img 
              src="/logo.png" 
              alt="Sopra HR Logo"
              className="h-10 w-auto"
            />
          </Link>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            <X className="w-5 h-5 dark:text-white" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {filteredNav.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200
                  ${isActive
                    ? 'bg-gradient-to-r from-[#E31837] to-[#c41530] text-white shadow-lg shadow-red-200 dark:shadow-red-900/30'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
                  }
                `}
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Bottom section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
          <Link
            href="/settings"
            className="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-600 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white transition-all"
          >
            <Settings className="w-5 h-5" />
            <span className="font-medium">Paramètres</span>
          </Link>
        </div>
      </aside>

      {/* Main content area */}
      <div className="lg:pl-64">
        {/* Top header */}
        <header className="sticky top-0 z-30 h-16 bg-white dark:bg-gray-800 border-b dark:border-gray-700 flex items-center justify-between px-4 lg:px-8 transition-colors duration-300">
          {/* Left side */}
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
            >
              <Menu className="w-5 h-5 dark:text-white" />
            </button>

            {/* Search bar */}
            <div className="hidden md:flex items-center gap-2 bg-gray-100 dark:bg-gray-700 rounded-xl px-4 py-2 w-80">
              <Search className="w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher..."
                className="bg-transparent border-none outline-none text-sm w-full dark:text-white dark:placeholder-gray-400"
              />
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-4">
            {/* Theme Toggle */}
            <ThemeToggle />

            {/* Notifications */}
            <NotificationBell />

            {/* User menu */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-3 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition"
              >
                <div className="w-9 h-9 bg-gradient-to-br from-[#E31837] to-[#c41530] rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.full_name || user?.username}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{getRoleBadge(user?.role).label}</p>
                </div>
                <ChevronDown className="w-4 h-4 text-gray-400" />
              </button>

              {/* Dropdown */}
              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-xl shadow-lg border dark:border-gray-700 py-2 z-50">
                  <div className="px-4 py-3 border-b dark:border-gray-700">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.email}</p>
                    <span className={`inline-flex items-center px-2 py-0.5 mt-1 rounded-full text-xs font-medium ${getRoleBadge(user?.role).color}`}>
                      {getRoleBadge(user?.role).label}
                    </span>
                  </div>
                  <Link
                    href="/profile"
                    className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <User className="w-4 h-4" />
                    Mon profil
                  </Link>
                  <Link
                    href="/settings"
                    className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <Settings className="w-4 h-4" />
                    Paramètres
                  </Link>
                  <hr className="my-2 dark:border-gray-700" />
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 w-full"
                  >
                    <LogOut className="w-4 h-4" />
                    Déconnexion
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
