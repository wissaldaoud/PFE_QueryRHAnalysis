"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import MainLayout from "@/components/MainLayout";
import { 
  Briefcase, 
  GraduationCap, 
  BarChart3,
  Sparkles
} from "lucide-react";

export default function HRAnalyticsPage() {
  const router = useRouter();

  const features = [
    {
      id: "cv-matching",
      title: "CV Matching",
      description: "Comparez automatiquement un CV avec une offre d'emploi grâce à l'IA",
      icon: Briefcase,
      color: "from-blue-500 to-cyan-500",
      route: "/hr-analytics/cv-matching",
      features: [
        "Analyse sémantique avec NLP",
        "Score de correspondance détaillé",
        "Identification des compétences manquantes",
        "Recommandations personnalisées"
      ]
    },
    {
      id: "training",
      title: "Recommandation de Formation",
      description: "Suggérez les meilleures formations adaptées aux employés",
      icon: GraduationCap,
      color: "from-purple-500 to-pink-500",
      route: "/hr-analytics/training-recommendation",
      features: [
        "Analyse du skill gap",
        "Top 5 formations personnalisées",
        "Priorisation intelligente",
        "Alignement avec objectifs carrière"
      ]
    },
    {
      id: "scoring",
      title: "Scoring Prédictif",
      description: "Prédisez le churn, la performance et l'engagement des employés",
      icon: BarChart3,
      color: "from-orange-500 to-red-500",
      route: "/hr-analytics/predictive-scoring",
      features: [
        "Risque de départ (churn)",
        "Score de performance",
        "Niveau d'engagement",
        "Recommandations RH actionnables"
      ]
    }
  ];

  return (
    <MainLayout>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        {/* Header */}
        <div className="bg-white dark:bg-gray-800 shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl">
                <Sparkles className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  HR Analytics Avancé
                </h1>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-300">
                  Propulsé par Intelligence Artificielle et Machine Learning
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          {/* Description */}
          <div className="mb-10 text-center">
            <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-3">
              Optimisez vos décisions RH avec l'IA
            </h2>
            <p className="text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
              Notre plateforme utilise des modèles de Machine Learning avancés pour vous aider
              dans le recrutement, la formation et la prévention du turnover.
            </p>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => (
              <div
                key={feature.id}
                className="group bg-white dark:bg-gray-800 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 overflow-hidden cursor-pointer transform hover:-translate-y-2"
                onClick={() => router.push(feature.route)}
              >
                {/* Card Header with Gradient */}
                <div className={`bg-gradient-to-r ${feature.color} p-6`}>
                  <feature.icon className="h-12 w-12 text-white mb-4" />
                  <h3 className="text-2xl font-bold text-white">
                    {feature.title}
                  </h3>
                </div>

                {/* Card Body */}
                <div className="p-6">
                  <p className="text-gray-600 dark:text-gray-300 mb-6">
                    {feature.description}
                  </p>

                  {/* Features List */}
                  <ul className="space-y-3">
                    {feature.features.map((item, idx) => (
                      <li
                        key={idx}
                        className="flex items-center text-sm text-gray-700 dark:text-gray-400"
                      >
                        <svg
                          className="h-5 w-5 text-green-500 mr-3 flex-shrink-0"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                        {item}
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <button className="mt-6 w-full py-3 px-4 bg-gray-900 dark:bg-gray-700 text-white rounded-lg hover:bg-gray-800 dark:hover:bg-gray-600 transition-colors duration-200 font-medium">
                    Commencer →
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Tech Stack Badge */}
          <div className="mt-16 text-center">
            <div className="inline-flex items-center space-x-2 px-6 py-3 bg-white dark:bg-gray-800 rounded-full shadow-lg">
              <Sparkles className="h-5 w-5 text-indigo-500" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Propulsé par Sentence Transformers, PyTorch & FastAPI
              </span>
            </div>
          </div>

          {/* Stats Section */}
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg text-center">
              <div className="text-4xl font-bold text-indigo-600 dark:text-indigo-400">
                98%
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Précision du CV Matching
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg text-center">
              <div className="text-4xl font-bold text-purple-600 dark:text-purple-400">
                Top 5
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Formations recommandées
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg text-center">
              <div className="text-4xl font-bold text-orange-600 dark:text-orange-400">
                85%
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                Prédiction du churn
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
