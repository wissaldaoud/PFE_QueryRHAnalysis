import Link from "next/link";
import { Users, TrendingUp, Calendar, BarChart3 } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Query HR Analytics Online
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Plateforme interactive pour requêtes RH et indicateurs intelligents
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Dashboard Cards */}
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
            {/* Card 1: Total Employees */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Users className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Total Employés
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        0
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Card 2: Turnover Rate */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <TrendingUp className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Taux de Turnover
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        0%
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Card 3: Attendance */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Calendar className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Taux de Présence
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        0%
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            {/* Card 4: Departments */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <BarChart3 className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Départements
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        0
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <Link
              href="/employees"
              className="bg-white p-6 shadow rounded-lg hover:shadow-lg transition-shadow"
            >
              <h3 className="text-lg font-medium text-gray-900">
                Gestion des Employés
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Consulter et gérer les données des employés
              </p>
            </Link>

            <Link
              href="/analytics"
              className="bg-white p-6 shadow rounded-lg hover:shadow-lg transition-shadow"
            >
              <h3 className="text-lg font-medium text-gray-900">
                Analyse & Prédictions
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Visualiser les indicateurs et prédictions IA
              </p>
            </Link>

            <Link
              href="/reports"
              className="bg-white p-6 shadow rounded-lg hover:shadow-lg transition-shadow"
            >
              <h3 className="text-lg font-medium text-gray-900">
                Rapports Qlik
              </h3>
              <p className="mt-2 text-sm text-gray-500">
                Accéder aux tableaux de bord Qlik Sense
              </p>
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}


