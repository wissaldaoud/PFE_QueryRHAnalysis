"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import MainLayout from "@/components/MainLayout";
import {
  Users,
  CheckCircle,
  XCircle,
  Clock,
  Search,
  Mail,
  Calendar,
  AlertTriangle,
  UserCheck,
  UserX,
  Loader2,
  RefreshCw,
  Shield,
} from "lucide-react";

interface PendingAccount {
  id: number;
  email: string;
  username: string;
  full_name: string;
  created_at: string;
}

interface User {
  id: number;
  role: string;
}

export default function AdminAccountsPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [pendingAccounts, setPendingAccounts] = useState<PendingAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<PendingAccount | null>(null);
  const [rejectReason, setRejectReason] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState("employee");

  const roleOptions = [
    { value: "employee", label: "Employé", description: "Accès basique : congés, profil" },
    { value: "manager", label: "Manager", description: "Gestion d'équipe, validation congés" },
    { value: "hr_manager", label: "Responsable RH", description: "Gestion complète RH" },
    { value: "analyst", label: "Analyste", description: "Accès aux rapports et statistiques" },
  ];

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const userData = localStorage.getItem("user");

    if (!token) {
      router.push("/login");
      return;
    }

    if (userData) {
      const parsedUser = JSON.parse(userData);
      setUser(parsedUser);

      // Only admin and hr_manager can access this page
      if (!["admin", "hr_manager"].includes(parsedUser.role)) {
        router.push("/dashboard");
        return;
      }
    }

    fetchPendingAccounts(token);
  }, [router]);

  const fetchPendingAccounts = async (token: string) => {
    setLoading(true);
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/auth/pending-accounts",
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPendingAccounts(data.items || []);
      }
    } catch (err) {
      console.error("Erreur chargement comptes:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (account: PendingAccount) => {
    setSelectedAccount(account);
    setSelectedRole("employee");
    setShowApproveModal(true);
  };

  const confirmApprove = async () => {
    if (!selectedAccount) return;
    
    const token = localStorage.getItem("access_token");
    if (!token) return;

    setActionLoading(selectedAccount.id);
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/auth/approve-account",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ 
            user_id: selectedAccount.id,
            role: selectedRole 
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        const roleLabel = roleOptions.find(r => r.value === selectedRole)?.label || "Employé";
        setSuccessMessage(`✅ Compte de ${selectedAccount.full_name} approuvé en tant que ${roleLabel} !`);
        setPendingAccounts((prev) => prev.filter((a) => a.id !== selectedAccount.id));
        setShowApproveModal(false);
        setSelectedAccount(null);
        setTimeout(() => setSuccessMessage(""), 3000);
      }
    } catch (err) {
      console.error("Erreur approbation:", err);
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async () => {
    if (!selectedAccount) return;

    const token = localStorage.getItem("access_token");
    if (!token) return;

    setActionLoading(selectedAccount.id);
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/auth/reject-account",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: selectedAccount.id,
            reason: rejectReason,
          }),
        }
      );

      if (response.ok) {
        setSuccessMessage(`❌ Compte de ${selectedAccount.full_name} refusé`);
        setPendingAccounts((prev) =>
          prev.filter((a) => a.id !== selectedAccount.id)
        );
        setShowRejectModal(false);
        setSelectedAccount(null);
        setRejectReason("");
        setTimeout(() => setSuccessMessage(""), 3000);
      }
    } catch (err) {
      console.error("Erreur refus:", err);
    } finally {
      setActionLoading(null);
    }
  };

  const filteredAccounts = pendingAccounts.filter(
    (account) =>
      account.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      account.username.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "N/A";
    const date = new Date(dateStr);
    return date.toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "long",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <MainLayout>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <div className="w-10 h-10 bg-amber-100 rounded-xl flex items-center justify-center">
                <Clock className="w-5 h-5 text-amber-600" />
              </div>
              Comptes en attente
            </h1>
            <p className="text-gray-500 mt-1">
              Validez ou refusez les nouvelles demandes d'inscription
            </p>
          </div>

          <button
            onClick={() => fetchPendingAccounts(localStorage.getItem("access_token") || "")}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Actualiser
          </button>
        </div>
      </div>

      {/* Success Message */}
      {successMessage && (
        <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-xl">
          {successMessage}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">En attente</p>
              <p className="text-3xl font-bold text-amber-600 mt-1">
                {pendingAccounts.length}
              </p>
            </div>
            <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center">
              <Clock className="w-6 h-6 text-amber-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Action requise</p>
              <p className="text-3xl font-bold text-[#E31837] mt-1">
                {pendingAccounts.length > 0 ? "Oui" : "Non"}
              </p>
            </div>
            <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-[#E31837]" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total utilisateurs</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">-</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Rechercher par nom, email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837]"
          />
        </div>
      </div>

      {/* Accounts List */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        {loading ? (
          <div className="p-12 text-center">
            <Loader2 className="w-8 h-8 animate-spin text-[#E31837] mx-auto mb-4" />
            <p className="text-gray-500">Chargement des comptes...</p>
          </div>
        ) : filteredAccounts.length === 0 ? (
          <div className="p-12 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Aucun compte en attente
            </h3>
            <p className="text-gray-500">
              Tous les comptes ont été traités. Revenez plus tard.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {filteredAccounts.map((account) => (
              <div
                key={account.id}
                className="p-6 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-[#E31837] to-[#c41530] rounded-full flex items-center justify-center text-white font-semibold text-lg">
                      {account.full_name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")
                        .substring(0, 2)
                        .toUpperCase()}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">
                        {account.full_name}
                      </h3>
                      <div className="flex items-center gap-4 mt-1">
                        <span className="flex items-center gap-1 text-sm text-gray-500">
                          <Mail className="w-4 h-4" />
                          {account.email}
                        </span>
                        <span className="text-sm text-gray-400">
                          @{account.username}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 text-xs text-gray-400 mt-1">
                        <Calendar className="w-3 h-3" />
                        Inscrit le {formatDate(account.created_at)}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium">
                      En attente
                    </span>

                    <button
                      onClick={() => handleApprove(account)}
                      disabled={actionLoading === account.id}
                      className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-xl transition-colors disabled:opacity-50"
                    >
                      {actionLoading === account.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <UserCheck className="w-4 h-4" />
                      )}
                      Approuver
                    </button>

                    <button
                      onClick={() => {
                        setSelectedAccount(account);
                        setShowRejectModal(true);
                      }}
                      disabled={actionLoading === account.id}
                      className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-xl transition-colors disabled:opacity-50"
                    >
                      <UserX className="w-4 h-4" />
                      Refuser
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Approve Modal with Role Selection */}
      {showApproveModal && selectedAccount && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <UserCheck className="w-5 h-5 text-green-500" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Approuver le compte
                </h3>
                <p className="text-sm text-gray-500">
                  {selectedAccount.full_name}
                </p>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                <Shield className="w-4 h-4 inline mr-1" />
                Choisir le rôle
              </label>
              <div className="space-y-2">
                {roleOptions.map((role) => (
                  <label
                    key={role.value}
                    className={`flex items-center p-3 border rounded-xl cursor-pointer transition-all ${
                      selectedRole === role.value
                        ? "border-[#E31837] bg-red-50"
                        : "border-gray-200 hover:border-gray-300"
                    }`}
                  >
                    <input
                      type="radio"
                      name="role"
                      value={role.value}
                      checked={selectedRole === role.value}
                      onChange={(e) => setSelectedRole(e.target.value)}
                      className="sr-only"
                    />
                    <div className={`w-4 h-4 rounded-full border-2 mr-3 flex items-center justify-center ${
                      selectedRole === role.value
                        ? "border-[#E31837]"
                        : "border-gray-300"
                    }`}>
                      {selectedRole === role.value && (
                        <div className="w-2 h-2 rounded-full bg-[#E31837]" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{role.label}</p>
                      <p className="text-xs text-gray-500">{role.description}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowApproveModal(false);
                  setSelectedAccount(null);
                }}
                className="flex-1 px-4 py-3 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors font-medium"
              >
                Annuler
              </button>
              <button
                onClick={confirmApprove}
                disabled={actionLoading === selectedAccount.id}
                className="flex-1 px-4 py-3 bg-green-500 text-white rounded-xl hover:bg-green-600 transition-colors font-medium flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {actionLoading === selectedAccount.id ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <UserCheck className="w-4 h-4" />
                )}
                Confirmer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && selectedAccount && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <UserX className="w-5 h-5 text-red-500" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Refuser le compte
                </h3>
                <p className="text-sm text-gray-500">
                  {selectedAccount.full_name}
                </p>
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Motif du refus (optionnel)
              </label>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                rows={3}
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837]"
                placeholder="Indiquez la raison du refus..."
              />
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setSelectedAccount(null);
                  setRejectReason("");
                }}
                className="flex-1 px-4 py-3 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors font-medium"
              >
                Annuler
              </button>
              <button
                onClick={handleReject}
                disabled={actionLoading === selectedAccount.id}
                className="flex-1 px-4 py-3 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors font-medium flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {actionLoading === selectedAccount.id ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <UserX className="w-4 h-4" />
                )}
                Confirmer le refus
              </button>
            </div>
          </div>
        </div>
      )}
    </MainLayout>
  );
}


