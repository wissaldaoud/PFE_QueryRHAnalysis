"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import MainLayout from "@/components/MainLayout";
import {
  User,
  Mail,
  Phone,
  Lock,
  Bell,
  Shield,
  Eye,
  EyeOff,
  Save,
  CheckCircle,
  AlertTriangle,
  Loader2,
  Key,
  Globe,
  Moon,
  Sun,
  Palette,
} from "lucide-react";

interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_2fa_enabled: boolean;
}

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  // Profile form
  const [profileForm, setProfileForm] = useState({
    full_name: "",
    email: "",
    phone: "",
  });

  // Password form
  const [passwordForm, setPasswordForm] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);

  // Notifications settings
  const [notifications, setNotifications] = useState({
    email_notifications: true,
    leave_reminders: true,
    system_alerts: true,
    weekly_reports: false,
  });

  // Appearance
  const [theme, setTheme] = useState("light");
  const [language, setLanguage] = useState("fr");

  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/auth/me", {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
        setProfileForm({
          full_name: data.full_name || "",
          email: data.email || "",
          phone: data.phone || "",
        });
      }
    } catch (err) {
      console.error("Erreur:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    const token = localStorage.getItem("access_token");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/auth/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(profileForm),
      });

      if (response.ok) {
        setSuccess("Profil mis à jour avec succès !");
        fetchUserProfile();
      } else {
        const data = await response.json();
        throw new Error(data.detail || "Erreur lors de la mise à jour");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setError("Les mots de passe ne correspondent pas");
      setSaving(false);
      return;
    }

    if (passwordForm.new_password.length < 8) {
      setError("Le mot de passe doit contenir au moins 8 caractères");
      setSaving(false);
      return;
    }

    const token = localStorage.getItem("access_token");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/auth/change-password",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            current_password: passwordForm.current_password,
            new_password: passwordForm.new_password,
          }),
        }
      );

      if (response.ok) {
        setSuccess("Mot de passe modifié avec succès !");
        setPasswordForm({
          current_password: "",
          new_password: "",
          confirm_password: "",
        });
      } else {
        const data = await response.json();
        throw new Error(data.detail || "Erreur lors du changement de mot de passe");
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case "admin":
        return "bg-purple-100 text-purple-800";
      case "hr_manager":
        return "bg-blue-100 text-blue-800";
      case "manager":
        return "bg-green-100 text-green-800";
      case "analyst":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case "admin":
        return "Administrateur";
      case "hr_manager":
        return "Responsable RH";
      case "manager":
        return "Manager";
      case "analyst":
        return "Analyste";
      default:
        return "Employé";
    }
  };

  if (loading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-96">
          <Loader2 className="h-8 w-8 animate-spin text-[#E31837]" />
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Paramètres</h1>
          <p className="text-gray-600 mt-1">
            Gérez vos préférences et paramètres de compte
          </p>
        </div>

        {/* Success/Error Messages */}
        {success && (
          <div className="bg-green-50 border border-green-200 rounded-2xl p-4 flex items-center gap-3">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="text-green-700 font-medium">{success}</span>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-4 flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-red-500" />
            <span className="text-red-700">{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Profile Card */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="bg-gradient-to-r from-[#E31837] to-[#c41530] px-6 py-8 text-center">
                <div className="w-20 h-20 rounded-full bg-white/20 flex items-center justify-center mx-auto mb-4">
                  <span className="text-3xl font-bold text-white">
                    {user?.full_name?.charAt(0).toUpperCase() || "U"}
                  </span>
                </div>
                <h2 className="text-xl font-semibold text-white">
                  {user?.full_name}
                </h2>
                <p className="text-white/80 text-sm mt-1">{user?.email}</p>
                <span
                  className={`inline-block mt-3 px-3 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(
                    user?.role || ""
                  )}`}
                >
                  {getRoleLabel(user?.role || "")}
                </span>
              </div>

              <div className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center gap-3 text-gray-600">
                    <Shield className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium">Authentification 2FA</p>
                      <p className="text-xs text-gray-500">
                        {user?.is_2fa_enabled ? "Activée" : "Désactivée"}
                      </p>
                    </div>
                    <span
                      className={`ml-auto w-3 h-3 rounded-full ${
                        user?.is_2fa_enabled ? "bg-green-500" : "bg-gray-300"
                      }`}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Settings Forms */}
          <div className="lg:col-span-2 space-y-6">
            {/* Profile Settings */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <User className="h-5 w-5 text-[#E31837]" />
                  Informations du profil
                </h3>
              </div>

              <form onSubmit={handleProfileSubmit} className="p-6">
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nom complet
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <User className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type="text"
                        value={profileForm.full_name}
                        onChange={(e) =>
                          setProfileForm({ ...profileForm, full_name: e.target.value })
                        }
                        className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Email
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Mail className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type="email"
                        value={profileForm.email}
                        onChange={(e) =>
                          setProfileForm({ ...profileForm, email: e.target.value })
                        }
                        className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent"
                      />
                    </div>
                  </div>

                  <div className="sm:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Téléphone
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Phone className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type="tel"
                        value={profileForm.phone}
                        onChange={(e) =>
                          setProfileForm({ ...profileForm, phone: e.target.value })
                        }
                        placeholder="+212 6 12 34 56 78"
                        className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-6 flex justify-end">
                  <button
                    type="submit"
                    disabled={saving}
                    className="inline-flex items-center px-5 py-2.5 bg-gradient-to-r from-[#E31837] to-[#c41530] text-white rounded-xl hover:from-[#c41530] hover:to-[#a11228] disabled:opacity-50 transition-all font-medium"
                  >
                    {saving ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4 mr-2" />
                    )}
                    Enregistrer
                  </button>
                </div>
              </form>
            </div>

            {/* Password Settings */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Key className="h-5 w-5 text-[#E31837]" />
                  Changer le mot de passe
                </h3>
              </div>

              <form onSubmit={handlePasswordSubmit} className="p-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Mot de passe actuel
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Lock className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type={showCurrentPassword ? "text" : "password"}
                        value={passwordForm.current_password}
                        onChange={(e) =>
                          setPasswordForm({
                            ...passwordForm,
                            current_password: e.target.value,
                          })
                        }
                        className="block w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent"
                      />
                      <button
                        type="button"
                        onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      >
                        {showCurrentPassword ? (
                          <EyeOff className="h-5 w-5 text-gray-400" />
                        ) : (
                          <Eye className="h-5 w-5 text-gray-400" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Nouveau mot de passe
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Lock className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type={showNewPassword ? "text" : "password"}
                        value={passwordForm.new_password}
                        onChange={(e) =>
                          setPasswordForm({
                            ...passwordForm,
                            new_password: e.target.value,
                          })
                        }
                        className="block w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent"
                      />
                      <button
                        type="button"
                        onClick={() => setShowNewPassword(!showNewPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center"
                      >
                        {showNewPassword ? (
                          <EyeOff className="h-5 w-5 text-gray-400" />
                        ) : (
                          <Eye className="h-5 w-5 text-gray-400" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Confirmer le mot de passe
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Lock className="h-5 w-5 text-gray-400" />
                      </div>
                      <input
                        type="password"
                        value={passwordForm.confirm_password}
                        onChange={(e) =>
                          setPasswordForm({
                            ...passwordForm,
                            confirm_password: e.target.value,
                          })
                        }
                        className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-6 flex justify-end">
                  <button
                    type="submit"
                    disabled={saving}
                    className="inline-flex items-center px-5 py-2.5 bg-gradient-to-r from-[#E31837] to-[#c41530] text-white rounded-xl hover:from-[#c41530] hover:to-[#a11228] disabled:opacity-50 transition-all font-medium"
                  >
                    {saving ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Key className="h-4 w-4 mr-2" />
                    )}
                    Changer le mot de passe
                  </button>
                </div>
              </form>
            </div>

            {/* Notifications Settings */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Bell className="h-5 w-5 text-[#E31837]" />
                  Notifications
                </h3>
              </div>

              <div className="p-6 space-y-4">
                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="font-medium text-gray-900">Notifications par email</p>
                    <p className="text-sm text-gray-500">
                      Recevoir des notifications par email
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() =>
                      setNotifications({
                        ...notifications,
                        email_notifications: !notifications.email_notifications,
                      })
                    }
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      notifications.email_notifications
                        ? "bg-[#E31837]"
                        : "bg-gray-200"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        notifications.email_notifications
                          ? "translate-x-6"
                          : "translate-x-1"
                      }`}
                    />
                  </button>
                </label>

                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="font-medium text-gray-900">Rappels de congés</p>
                    <p className="text-sm text-gray-500">
                      Rappels pour les demandes de congés en attente
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() =>
                      setNotifications({
                        ...notifications,
                        leave_reminders: !notifications.leave_reminders,
                      })
                    }
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      notifications.leave_reminders ? "bg-[#E31837]" : "bg-gray-200"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        notifications.leave_reminders
                          ? "translate-x-6"
                          : "translate-x-1"
                      }`}
                    />
                  </button>
                </label>

                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="font-medium text-gray-900">Alertes système</p>
                    <p className="text-sm text-gray-500">
                      Notifications importantes du système
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() =>
                      setNotifications({
                        ...notifications,
                        system_alerts: !notifications.system_alerts,
                      })
                    }
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      notifications.system_alerts ? "bg-[#E31837]" : "bg-gray-200"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        notifications.system_alerts
                          ? "translate-x-6"
                          : "translate-x-1"
                      }`}
                    />
                  </button>
                </label>

                <label className="flex items-center justify-between cursor-pointer">
                  <div>
                    <p className="font-medium text-gray-900">Rapports hebdomadaires</p>
                    <p className="text-sm text-gray-500">
                      Recevoir un résumé hebdomadaire par email
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() =>
                      setNotifications({
                        ...notifications,
                        weekly_reports: !notifications.weekly_reports,
                      })
                    }
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      notifications.weekly_reports ? "bg-[#E31837]" : "bg-gray-200"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        notifications.weekly_reports
                          ? "translate-x-6"
                          : "translate-x-1"
                      }`}
                    />
                  </button>
                </label>
              </div>
            </div>

            {/* Appearance Settings */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-100">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Palette className="h-5 w-5 text-[#E31837]" />
                  Apparence
                </h3>
              </div>

              <div className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Thème
                  </label>
                  <div className="grid grid-cols-3 gap-3">
                    <button
                      onClick={() => setTheme("light")}
                      className={`flex items-center justify-center gap-2 p-3 rounded-xl border-2 transition-all ${
                        theme === "light"
                          ? "border-[#E31837] bg-red-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <Sun className="h-5 w-5" />
                      <span className="text-sm font-medium">Clair</span>
                    </button>
                    <button
                      onClick={() => setTheme("dark")}
                      className={`flex items-center justify-center gap-2 p-3 rounded-xl border-2 transition-all ${
                        theme === "dark"
                          ? "border-[#E31837] bg-red-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <Moon className="h-5 w-5" />
                      <span className="text-sm font-medium">Sombre</span>
                    </button>
                    <button
                      onClick={() => setTheme("auto")}
                      className={`flex items-center justify-center gap-2 p-3 rounded-xl border-2 transition-all ${
                        theme === "auto"
                          ? "border-[#E31837] bg-red-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <Palette className="h-5 w-5" />
                      <span className="text-sm font-medium">Auto</span>
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Langue
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Globe className="h-5 w-5 text-gray-400" />
                    </div>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent appearance-none bg-white"
                    >
                      <option value="fr">Français</option>
                      <option value="en">English</option>
                      <option value="ar">العربية</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}


