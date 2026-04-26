"use client";

import { useEffect, useRef, useState } from "react";
import { BarChart3, TrendingUp, Users, AlertCircle } from "lucide-react";

export default function ReportsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Simulate loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Rapports Qlik Sense
              </h1>
              <p className="mt-2 text-sm text-gray-600">
                Tableaux de bord interactifs et analyses avancées
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <BarChart3 className="h-8 w-8 text-blue-600" />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Instructions Card */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
            <div className="flex items-start">
              <AlertCircle className="h-6 w-6 text-blue-600 mt-1 mr-3 flex-shrink-0" />
              <div>
                <h3 className="text-lg font-semibold text-blue-900 mb-2">
                  Configuration Qlik Sense Requise
                </h3>
                <p className="text-sm text-blue-800 mb-3">
                  Pour afficher les dashboards Qlik Sense, suivez ces étapes :
                </p>
                <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800 ml-2">
                  <li>
                    Créez un compte sur{" "}
                    <a
                      href="https://www.qlik.com/us/trial/qlik-sense-business"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline font-medium"
                    >
                      Qlik Cloud
                    </a>
                  </li>
                  <li>Créez une application "HR Analytics"</li>
                  <li>
                    Exportez les données depuis l'API : GET /api/v1/qlik/employees-export
                  </li>
                  <li>Uploadez les données CSV dans Qlik Sense</li>
                  <li>Créez vos visualisations</li>
                  <li>
                    Configurez l'embedding en ajoutant l'App ID dans les variables
                    d'environnement
                  </li>
                </ol>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <a
              href="http://127.0.0.1:8000/api/v1/qlik/employees-export"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
            >
              <Users className="h-8 w-8 text-green-600 mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Export Employés
              </h3>
              <p className="text-sm text-gray-600">
                Télécharger les données employés au format JSON
              </p>
            </a>

            <a
              href="http://127.0.0.1:8000/api/v1/qlik/departments-summary"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
            >
              <BarChart3 className="h-8 w-8 text-blue-600 mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Résumé Départements
              </h3>
              <p className="text-sm text-gray-600">
                Statistiques agrégées par département
              </p>
            </a>

            <a
              href="http://127.0.0.1:8000/api/v1/qlik/kpi-summary"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
            >
              <TrendingUp className="h-8 w-8 text-purple-600 mb-3" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                KPIs Globaux
              </h3>
              <p className="text-sm text-gray-600">
                Indicateurs clés de performance RH
              </p>
            </a>
          </div>

          {/* Placeholder for Qlik Dashboard */}
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">
                Dashboard Qlik Sense
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Les visualisations Qlik apparaîtront ici une fois configurées
              </p>
            </div>

            {/* Dashboard Container */}
            <div className="p-6">
              {isLoading ? (
                <div className="flex flex-col items-center justify-center py-20">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                  <p className="text-gray-600">Chargement du dashboard...</p>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-20 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                  <BarChart3 className="h-16 w-16 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Dashboard Qlik Non Configuré
                  </h3>
                  <p className="text-sm text-gray-600 text-center max-w-md mb-4">
                    Suivez les instructions ci-dessus pour configurer l'intégration
                    Qlik Sense. Une fois configuré, votre dashboard interactif
                    s'affichera ici.
                  </p>
                  <div className="flex space-x-4">
                    <a
                      href="http://127.0.0.1:8000/docs#/Qlik%20Sense%20Integration"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                      Voir l'API Qlik
                    </a>
                    <a
                      href="https://qlik.com/us/trial"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-white text-blue-600 border border-blue-600 rounded-md hover:bg-blue-50 transition-colors"
                    >
                      Créer compte Qlik
                    </a>
                  </div>
                </div>
              )}

              {/* When Qlik is configured, replace the above with: */}
              {/* 
              <div 
                id="qlik-dashboard-container" 
                style={{ minHeight: "800px" }}
              >
                <!-- Qlik Sense embed will appear here -->
              </div>
              */}
            </div>
          </div>

          {/* Documentation Links */}
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Ressources Utiles
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <a
                href="https://qlik.dev/embed"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center p-3 border border-gray-200 rounded-md hover:border-blue-500 hover:bg-blue-50 transition-colors"
              >
                <div>
                  <p className="font-medium text-gray-900">
                    Documentation Qlik Embedding
                  </p>
                  <p className="text-sm text-gray-600">
                    Guide officiel pour intégrer Qlik Sense
                  </p>
                </div>
              </a>
              <a
                href="http://127.0.0.1:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center p-3 border border-gray-200 rounded-md hover:border-blue-500 hover:bg-blue-50 transition-colors"
              >
                <div>
                  <p className="font-medium text-gray-900">
                    API Documentation
                  </p>
                  <p className="text-sm text-gray-600">
                    Endpoints disponibles pour Qlik
                  </p>
                </div>
              </a>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}


