"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Eye, EyeOff, Lock, Mail, Users, BarChart3, Shield, Zap, Key } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [totpCode, setTotpCode] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [requires2FA, setRequires2FA] = useState(false);
  const [loading, setLoading] = useState(false);
  const [keycloakLoading, setKeycloakLoading] = useState(false);
  const [error, setError] = useState("");

  // Handle Keycloak callback
  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');
    
    if (code && state) {
      handleKeycloakCallback(code, state);
    }
  }, [searchParams]);

  const handleKeycloakCallback = async (code: string, state: string) => {
    setKeycloakLoading(true);
    setError("");
    
    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/auth/keycloak/callback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          code,
          state,
          redirect_uri: window.location.origin + "/login"
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Erreur de connexion Keycloak");
      }

      localStorage.setItem("access_token", data.access_token);
      if (data.refresh_token) {
        localStorage.setItem("refresh_token", data.refresh_token);
      }
      if (data.user) {
        localStorage.setItem("user", JSON.stringify(data.user));
      }
      
      // Clear URL params and redirect
      window.history.replaceState({}, document.title, "/login");
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Erreur de connexion Keycloak");
      window.history.replaceState({}, document.title, "/login");
    } finally {
      setKeycloakLoading(false);
    }
  };

  const handleKeycloakLogin = async () => {
    setKeycloakLoading(true);
    setError("");
    
    try {
      const redirectUri = window.location.origin + "/login";
      const response = await fetch(
        `http://127.0.0.1:8000/api/v1/auth/keycloak/login?redirect_uri=${encodeURIComponent(redirectUri)}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Erreur Keycloak");
      }

      // Redirect to Keycloak login page
      window.location.href = data.authorization_url;
    } catch (err: any) {
      setError(err.message || "Erreur de connexion Keycloak");
      setKeycloakLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const formData = new URLSearchParams();
      formData.append("username", email.trim());
      formData.append("password", password);

      console.log("Tentative de connexion avec:", email.trim());

      const response = await fetch("http://127.0.0.1:8000/api/v1/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        if (data.detail === "2FA_REQUIRED" || data.requires_2fa) {
          setRequires2FA(true);
          setLoading(false);
          return;
        }
        console.error("Erreur de connexion:", data);
        // Améliorer le message d'erreur
        let errorMsg = data.detail || "Erreur de connexion";
        if (response.status === 401) {
          errorMsg = "Email ou mot de passe incorrect. Vérifiez vos identifiants.";
        }
        throw new Error(errorMsg);
      }

      localStorage.setItem("access_token", data.access_token);
      if (data.refresh_token) {
        localStorage.setItem("refresh_token", data.refresh_token);
      }
      localStorage.setItem("user", JSON.stringify(data.user));
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Erreur de connexion");
    } finally {
      setLoading(false);
    }
  };

  const handleLogin2FA = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/auth/login/2fa", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
          totp_code: totpCode,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Code 2FA invalide");
      }

      localStorage.setItem("access_token", data.access_token);
      if (data.refresh_token) {
        localStorage.setItem("refresh_token", data.refresh_token);
      }
      localStorage.setItem("user", JSON.stringify(data.user));
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Erreur de connexion");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Hero Section (SOPRAHR Style) */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-[#E31837] via-[#C41230] to-[#8B0D24] relative overflow-hidden">
        {/* Decorative circles */}
        <div className="absolute top-20 left-20 w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/3 w-32 h-32 bg-white/10 rounded-full blur-2xl"></div>
        
        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center px-12 text-white">
          {/* Logo */}
          <div className="mb-12">
            <div className="flex items-center space-x-3">
              <img 
                src="/logo.png" 
                alt="Sopra HR Logo"
                className="h-16 w-auto"
              />
              <div>
                <h1 className="text-2xl font-bold">Query HR Analytics</h1>
                <p className="text-white/70 text-sm">Plateforme d'analyse RH</p>
              </div>
            </div>
          </div>

          {/* Main Title */}
          <h2 className="text-4xl lg:text-5xl font-bold leading-tight mb-6">
            Accélérez la<br />
            transformation<br />
            <span className="text-white/90">digitale des RH</span>
          </h2>

          <p className="text-lg text-white/80 mb-12 max-w-md">
            Plateforme intelligente pour requêtes RH, analytics avancés et indicateurs de performance en temps réel.
          </p>

          {/* Features */}
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5" />
              </div>
              <span className="text-white/90">Gestion des employés centralisée</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5" />
              </div>
              <span className="text-white/90">Analytics et KPIs en temps réel</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5" />
              </div>
              <span className="text-white/90">Prédictions ML intelligentes</span>
            </div>
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5" />
              </div>
              <span className="text-white/90">Sécurité enterprise (2FA, RBAC)</span>
            </div>
          </div>
        </div>

        {/* Bottom decoration */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-white/30 to-transparent"></div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center bg-gray-50 px-6 py-12">
        <div className="w-full max-w-md">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="inline-flex items-center justify-center">
              <img 
                src="/logo.png" 
                alt="Sopra HR Logo"
                className="h-12 w-auto"
              />
            </div>
          </div>

          {/* Welcome Text */}
          <div className="text-center lg:text-left mb-8">
            <h2 className="text-2xl font-bold text-gray-900">
              {requires2FA ? "Vérification 2FA" : "Bienvenue"}
            </h2>
            <p className="mt-2 text-gray-600">
              {requires2FA
                ? "Entrez le code de votre application d'authentification"
                : "Connectez-vous à votre espace RH"}
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 bg-red-50 border-l-4 border-[#E31837] text-red-700 px-4 py-3 rounded-r-lg">
              <p className="text-sm">{error}</p>
            </div>
          )}

          {/* Login Form */}
          {!requires2FA ? (
            <form onSubmit={handleLogin} className="space-y-6">
              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Adresse email
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="block w-full pl-12 pr-4 py-3.5 border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent transition-all duration-200"
                    placeholder="votre.email@soprahr.com"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Mot de passe
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-gray-400" />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    autoComplete="current-password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="block w-full pl-12 pr-12 py-3.5 border border-gray-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent transition-all duration-200"
                    placeholder="••••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600 transition"
                  >
                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                  </button>
                </div>
              </div>

              {/* Remember & Forgot */}
              <div className="flex items-center justify-between">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="w-4 h-4 rounded border-gray-300 text-[#E31837] focus:ring-[#E31837]"
                  />
                  <span className="ml-2 text-sm text-gray-600">Se souvenir de moi</span>
                </label>
                <a href="#" className="text-sm text-[#E31837] hover:text-[#C41230] font-medium transition">
                  Mot de passe oublié ?
                </a>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full flex justify-center items-center py-4 px-4 border border-transparent rounded-xl text-base font-semibold text-white bg-[#E31837] hover:bg-[#C41230] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#E31837] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-red-500/30 hover:shadow-red-500/40"
              >
                {loading ? (
                  <div className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Connexion en cours...
                  </div>
                ) : (
                  "Se connecter"
                )}
              </button>

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-gray-50 text-gray-500">ou</span>
                </div>
              </div>

              {/* Keycloak SSO Button */}
              <button
                type="button"
                onClick={handleKeycloakLogin}
                disabled={keycloakLoading}
                className="w-full flex justify-center items-center py-4 px-4 border-2 border-[#4A90A4] rounded-xl text-base font-semibold text-[#4A90A4] bg-white hover:bg-[#4A90A4] hover:text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#4A90A4] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {keycloakLoading ? (
                  <div className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Connexion SSO...
                  </div>
                ) : (
                  <>
                    <Key className="w-5 h-5 mr-2" />
                    Se connecter avec Keycloak SSO
                  </>
                )}
              </button>
            </form>
          ) : (
            /* 2FA Form */
            <form onSubmit={handleLogin2FA} className="space-y-6">
              <div>
                <label htmlFor="totp" className="block text-sm font-medium text-gray-700 mb-2">
                  Code d'authentification
                </label>
                <p className="text-xs text-gray-500 mb-4">
                  Entrez le code à 6 chiffres de Google Authenticator
                </p>
                <input
                  id="totp"
                  name="totp"
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]{6}"
                  maxLength={6}
                  required
                  value={totpCode}
                  onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, ""))}
                  className="block w-full px-4 py-4 border border-gray-300 rounded-xl text-center text-3xl tracking-[0.5em] font-mono placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-[#E31837] focus:border-transparent transition-all duration-200"
                  placeholder="000000"
                />
              </div>

              <div className="flex space-x-4">
                <button
                  type="button"
                  onClick={() => {
                    setRequires2FA(false);
                    setTotpCode("");
                    setError("");
                  }}
                  className="flex-1 py-3.5 px-4 border-2 border-gray-300 rounded-xl text-sm font-semibold text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-300 transition-all duration-200"
                >
                  Retour
                </button>
                <button
                  type="submit"
                  disabled={loading || totpCode.length !== 6}
                  className="flex-1 py-3.5 px-4 border border-transparent rounded-xl text-sm font-semibold text-white bg-[#E31837] hover:bg-[#C41230] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#E31837] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  {loading ? "Vérification..." : "Vérifier"}
                </button>
              </div>
            </form>
          )}

          {/* Register Link */}
          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Pas encore de compte ?{" "}
              <a href="/register" className="text-[#E31837] font-medium hover:underline">
                Créer un compte
              </a>
            </p>
          </div>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-center text-xs text-gray-500">
              © 2026 Sopra HR Software - Tous droits réservés
            </p>
            <p className="text-center text-xs text-gray-400 mt-1">
              Query HR Analytics Online - Projet PFE
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}


