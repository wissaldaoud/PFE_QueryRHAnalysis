"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Eye,
  EyeOff,
  Lock,
  Mail,
  User,
  Users,
  BarChart3,
  Shield,
  Zap,
  CheckCircle,
  ArrowRight,
  Loader2,
} from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    username: "",
    password: "",
    confirmPassword: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError("");
  };

  const validateForm = () => {
    if (!formData.fullName.trim()) {
      setError("Le nom complet est requis");
      return false;
    }
    if (!formData.email.trim()) {
      setError("L'email est requis");
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      setError("Format d'email invalide");
      return false;
    }
    if (!formData.username.trim()) {
      setError("Le nom d'utilisateur est requis");
      return false;
    }
    if (formData.username.length < 3) {
      setError("Le nom d'utilisateur doit contenir au moins 3 caractères");
      return false;
    }
    if (formData.password.length < 8) {
      setError("Le mot de passe doit contenir au moins 8 caractères");
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      setError("Les mots de passe ne correspondent pas");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: formData.email,
          username: formData.username,
          password: formData.password,
          full_name: formData.fullName,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Erreur lors de l'inscription");
      }

      setSuccess(true);
    } catch (err: any) {
      setError(err.message || "Erreur lors de l'inscription");
    } finally {
      setLoading(false);
    }
  };

  // Page de succès
  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 px-4">
        <div className="max-w-md w-full bg-white rounded-3xl shadow-xl p-8 text-center">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-10 h-10 text-green-500" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Inscription réussie ! 🎉
          </h2>
          <p className="text-gray-600 mb-6">
            Votre compte a été créé avec succès. Un administrateur va examiner votre demande.
            Vous recevrez un email dès que votre compte sera activé.
          </p>
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
            <p className="text-amber-800 text-sm">
              ⏳ <strong>Statut:</strong> En attente de validation
            </p>
          </div>
          <Link
            href="/login"
            className="inline-flex items-center gap-2 bg-[#E31837] text-white px-6 py-3 rounded-xl hover:bg-[#c41530] transition-colors font-medium"
          >
            Retour à la connexion
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Hero Section with SOPRAHR Official Image (60% width) */}
      <div className="hidden lg:flex lg:w-[60%] relative overflow-hidden">
        {/* Background Image - Image officielle SOPRAHR */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `url('https://www.soprahr.com/images/librariesprovider2/soprahr/news-2021/home.jpg?sfvrsn=fc36eadc_24')`,
          }}
        />
        
        {/* Gradient Overlay - SOPRAHR Red */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#E31837]/90 via-[#E31837]/70 to-transparent" />
        
        {/* Content */}
        <div className="relative z-10 flex flex-col justify-between h-full px-12 py-12 text-white">
          {/* Logo SOPRAHR Officiel */}
          <div>
            <img 
              src="https://www.soprahr.com/images/default-source/logos/logo-soprahr.png" 
              alt="Sopra HR Logo"
              className="h-12 brightness-0 invert"
              onError={(e) => {
                const target = e.currentTarget as HTMLImageElement;
                target.style.display = 'none';
              }}
            />
          </div>

          {/* Main Content */}
          <div>
            {/* Main Title */}
            <h2 className="text-4xl lg:text-5xl font-bold leading-tight mb-6">
              Accélérez la<br />
              transformation<br />
              <span className="text-white/90">digitale des RH</span>
            </h2>

            <p className="text-lg text-white/90 mb-8 max-w-md">
              Créez votre compte pour accéder à Query HR Analytics 
              et bénéficiez d'outils modernes pour la gestion RH.
            </p>

            {/* Features */}
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
                  <Users className="w-5 h-5" />
                </div>
                <span className="text-white/90">Gestion des employés centralisée</span>
              </div>
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
                  <BarChart3 className="w-5 h-5" />
                </div>
                <span className="text-white/90">Analytics et KPIs en temps réel</span>
              </div>
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
                  <Shield className="w-5 h-5" />
                </div>
                <span className="text-white/90">Sécurité et conformité RGPD</span>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="text-white/70 text-sm">
            © 2026 Sopra HR Software - Groupe Sopra Steria
          </div>
        </div>
      </div>

      {/* Right Side - Registration Form (40% width, more compact) */}
      <div className="w-full lg:w-[40%] flex items-center justify-center bg-gray-50 px-6 py-8">
        <div className="w-full max-w-sm">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-6">
            <div className="inline-flex items-center space-x-3">
              <div className="w-10 h-10 bg-[#E31837] rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">HR</span>
              </div>
              <div className="text-left">
                <h1 className="text-lg font-bold text-gray-900">Query HR Analytics</h1>
                <p className="text-gray-500 text-xs">by SOPRAHR</p>
              </div>
            </div>
          </div>

          {/* Welcome Text */}
          <div className="text-center lg:text-left mb-6">
            <h2 className="text-xl font-bold text-gray-900">Créer un compte</h2>
            <p className="mt-1 text-gray-600 text-sm">
              Remplissez le formulaire pour demander un accès
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 bg-red-50 border-l-4 border-[#E31837] text-red-700 px-3 py-2 rounded-r-lg">
              <p className="text-sm">{error}</p>
            </div>
          )}

          {/* Registration Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom complet
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-4 w-4 text-gray-400" />
                </div>
                <input
                  type="text"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837] transition-colors bg-white"
                  placeholder="Ahmed Bennani"
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Adresse email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-4 w-4 text-gray-400" />
                </div>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837] transition-colors bg-white"
                  placeholder="ahmed.bennani@company.com"
                />
              </div>
            </div>

            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nom d'utilisateur
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span className="text-gray-400 font-medium text-sm">@</span>
                </div>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837] transition-colors bg-white"
                  placeholder="ahmed.bennani"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mot de passe
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 text-gray-400" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-10 py-2.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837] transition-colors bg-white"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-4 w-4 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
              <p className="mt-0.5 text-xs text-gray-500">Min. 8 caractères</p>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirmer le mot de passe
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 text-gray-400" />
                </div>
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-10 py-2.5 text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-[#E31837]/20 focus:border-[#E31837] transition-colors bg-white"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4 text-gray-400 hover:text-gray-600" />
                  ) : (
                    <Eye className="h-4 w-4 text-gray-400 hover:text-gray-600" />
                  )}
                </button>
              </div>
            </div>

            {/* Terms */}
            <div className="flex items-start">
              <input
                type="checkbox"
                id="terms"
                required
                className="mt-1 h-4 w-4 text-[#E31837] border-gray-300 rounded focus:ring-[#E31837]"
              />
              <label htmlFor="terms" className="ml-2 text-sm text-gray-600">
                J'accepte les{" "}
                <a href="#" className="text-[#E31837] hover:underline">
                  conditions d'utilisation
                </a>{" "}
                et la{" "}
                <a href="#" className="text-[#E31837] hover:underline">
                  politique de confidentialité
                </a>
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-[#E31837] to-[#c41530] text-white py-2.5 px-4 rounded-lg font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2 disabled:opacity-70 shadow-lg shadow-red-500/25 text-sm"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Inscription en cours...
                </>
              ) : (
                <>
                  Créer mon compte
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-gray-50 text-gray-500">
                Déjà inscrit ?
              </span>
            </div>
          </div>

          {/* Login Link */}
          <Link
            href="/login"
            className="block w-full text-center py-3 px-4 border-2 border-gray-200 rounded-xl text-gray-700 font-medium hover:bg-gray-100 hover:border-gray-300 transition-colors"
          >
            Se connecter
          </Link>

          {/* Info Box */}
          <div className="mt-8 bg-blue-50 border border-blue-100 rounded-xl p-4">
            <p className="text-sm text-blue-800">
              <strong>ℹ️ Note:</strong> Après inscription, votre compte devra être 
              validé par un administrateur avant que vous puissiez vous connecter.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}


