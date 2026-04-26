'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import MainLayout from '@/components/MainLayout';
import { Calendar, ChevronLeft, Send, AlertCircle, User, CalendarDays } from 'lucide-react';

interface Employee {
  id: number;
  first_name: string;
  last_name: string;
  employee_code: string;
}

interface UserData {
  id: number;
  role: string;
  employee_id?: number;
  full_name?: string;
}

export default function NewLeavePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [currentUser, setCurrentUser] = useState<UserData | null>(null);
  const [canSelectEmployee, setCanSelectEmployee] = useState(false);
  
  const [formData, setFormData] = useState({
    employee_id: '',
    leave_type: 'annual',
    start_date: '',
    end_date: '',
    reason: '',
  });

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userData = localStorage.getItem('user');
    
    if (!token) {
      router.push('/login');
      return;
    }

    if (userData) {
      const user = JSON.parse(userData);
      setCurrentUser(user);
      
      // Seuls HR, Admin et Manager peuvent sélectionner un employé
      const canSelect = ['admin', 'hr_manager', 'manager'].includes(user.role);
      setCanSelectEmployee(canSelect);
      
      // Si c'est un employé, on utilise son employee_id
      if (!canSelect && user.employee_id) {
        setFormData(prev => ({ ...prev, employee_id: String(user.employee_id) }));
      }
    }

    fetchEmployees();
  }, []);

  const fetchEmployees = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch('http://127.0.0.1:8000/api/v1/employees?limit=100', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setEmployees(data);
      }
    } catch (error) {
      console.error('Error fetching employees:', error);
    }
  };

  const calculateDays = () => {
    if (!formData.start_date || !formData.end_date) return 0;
    const start = new Date(formData.start_date);
    const end = new Date(formData.end_date);
    const diff = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    return diff > 0 ? diff : 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');
      // Si c'est un employé, ne pas envoyer employee_id (le backend utilise celui de l'utilisateur)
      const url = canSelectEmployee 
        ? `http://127.0.0.1:8000/api/v1/leaves/?employee_id=${formData.employee_id}`
        : 'http://127.0.0.1:8000/api/v1/leaves/';
        
      const res = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          leave_type: formData.leave_type,
          start_date: formData.start_date,
          end_date: formData.end_date,
          reason: formData.reason || null,
        }),
      });

      if (res.ok) {
        setSuccess(true);
        setTimeout(() => {
          router.push('/leaves');
        }, 2000);
      } else {
        const data = await res.json();
        setError(data.detail || 'Erreur lors de la création');
      }
    } catch (error) {
      setError('Erreur de connexion au serveur');
    } finally {
      setLoading(false);
    }
  };

  const today = new Date().toISOString().split('T')[0];

  return (
    <MainLayout>
      {/* Page Header */}
      <div className="mb-8">
        <button
          onClick={() => router.push('/leaves')}
          className="flex items-center gap-2 text-gray-500 hover:text-gray-700 mb-4 transition"
        >
          <ChevronLeft className="w-5 h-5" />
          <span>Retour aux congés</span>
        </button>
        <div className="flex items-center gap-3">
          <div className="p-3 bg-gradient-to-br from-[#E31837] to-[#c41530] rounded-xl shadow-sm">
            <CalendarDays className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Nouvelle Demande</h1>
            <p className="text-gray-500">Remplissez le formulaire pour soumettre votre demande de congé</p>
          </div>
        </div>
      </div>

      <div className="max-w-3xl">
        {success ? (
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Send className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-xl font-bold text-green-800 mb-2">Demande envoyée !</h2>
            <p className="text-green-600">Votre demande de congé a été soumise avec succès.</p>
            <p className="text-sm text-green-500 mt-2">Redirection en cours...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8">
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                <p className="text-red-700">{error}</p>
              </div>
            )}

            {/* Employee Selection - Only for HR/Admin/Manager */}
            {canSelectEmployee ? (
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Employé *
                </label>
                <select
                  required
                  value={formData.employee_id}
                  onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837] bg-white"
                >
                  <option value="">Sélectionner un employé</option>
                  {employees.map((emp) => (
                    <option key={emp.id} value={emp.id}>
                      {emp.first_name} {emp.last_name} ({emp.employee_code})
                    </option>
                  ))}
                </select>
              </div>
            ) : (
              <div className="mb-6 p-4 bg-blue-50 border border-blue-100 rounded-xl">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <User className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-blue-600">Demande pour :</p>
                    <p className="font-semibold text-blue-800">{currentUser?.full_name || 'Vous'}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Leave Type */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type de congé *
              </label>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { value: 'annual', label: 'Congé Annuel', desc: 'Congés payés', color: 'blue' },
                  { value: 'sick', label: 'Maladie', desc: 'Arrêt maladie', color: 'orange' },
                  { value: 'unpaid', label: 'Sans Solde', desc: 'Non rémunéré', color: 'gray' },
                ].map((type) => (
                  <label
                    key={type.value}
                    className={`
                      relative flex flex-col p-4 border-2 rounded-xl cursor-pointer transition
                      ${formData.leave_type === type.value 
                        ? 'border-[#E31837] bg-red-50' 
                        : 'border-gray-200 hover:border-gray-300'}
                    `}
                  >
                    <input
                      type="radio"
                      name="leave_type"
                      value={type.value}
                      checked={formData.leave_type === type.value}
                      onChange={(e) => setFormData({ ...formData, leave_type: e.target.value })}
                      className="sr-only"
                    />
                    <span className="font-medium text-gray-900">{type.label}</span>
                    <span className="text-sm text-gray-500">{type.desc}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date de début *
                </label>
                <input
                  type="date"
                  required
                  min={today}
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date de fin *
                </label>
                <input
                  type="date"
                  required
                  min={formData.start_date || today}
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837]"
                />
              </div>
            </div>

            {/* Days Summary */}
            {calculateDays() > 0 && (
              <div className="mb-6 p-4 bg-gradient-to-r from-[#E31837]/10 to-[#c41530]/10 border border-[#E31837]/20 rounded-xl">
                <p className="text-[#E31837]">
                  <span className="font-bold text-3xl">{calculateDays()}</span>
                  <span className="ml-2 text-lg">jour{calculateDays() > 1 ? 's' : ''} de congé demandé{calculateDays() > 1 ? 's' : ''}</span>
                </p>
              </div>
            )}

            {/* Reason */}
            <div className="mb-8">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Motif (optionnel)
              </label>
              <textarea
                rows={4}
                value={formData.reason}
                onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                placeholder="Précisez le motif de votre demande..."
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837] resize-none"
              />
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-4">
              <button
                type="button"
                onClick={() => router.push('/leaves')}
                className="px-6 py-3 border border-gray-200 rounded-xl text-gray-700 hover:bg-gray-50 font-medium transition"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={loading || (canSelectEmployee && !formData.employee_id) || !formData.start_date || !formData.end_date}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-[#E31837] to-[#c41530] text-white rounded-xl hover:shadow-lg font-medium transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Envoi...
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    Soumettre la demande
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </MainLayout>
  );
}


