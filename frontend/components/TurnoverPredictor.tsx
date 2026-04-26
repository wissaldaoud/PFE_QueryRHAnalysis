"use client";

import { useState } from "react";
import { TrendingUp, AlertCircle, Loader2, Brain } from "lucide-react";

interface TurnoverPredictorProps {
  employeeData?: {
    date_of_birth?: string;
    hire_date?: string;
    contract_type?: string;
  };
}

interface PredictionResult {
  prediction: number;
  turnover_probability: number;
  turnover_probability_percent: number;
  risk_level: string;
  risk_color: string;
  risk_emoji: string;
  features_used: {
    age: number;
    anciennete_annees: number;
    total_jours_absence: number;
    nb_absences: number;
    duree_presence_jours: number;
    [key: string]: any;
  };
  model_path: string;
  computed_at: string;
}

export default function TurnoverPredictor({ employeeData }: TurnoverPredictorProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [prediction, setPrediction] = useState<PredictionResult | null>(null);
  
  // Champs supplémentaires pour la prédiction
  const [formData, setFormData] = useState({
    sexe: "Masculin",
    total_jours_absence: "0",
    nb_absences: "0",
  });

  const handlePredict = async () => {
    // Validation
    if (!employeeData?.date_of_birth || !employeeData?.hire_date) {
      setError("Date de naissance et date d'embauche requises");
      return;
    }

    setLoading(true);
    setError("");
    setPrediction(null);

    try {
      const token = localStorage.getItem("access_token");
      
      const requestData = {
        date_naissance: employeeData.date_of_birth,
        date_embauche: employeeData.hire_date,
        sexe: formData.sexe,
        type_contrat: employeeData.contract_type || "CDI",
        total_jours_absence: parseInt(formData.total_jours_absence) || 0,
        nb_absences: parseInt(formData.nb_absences) || 0,
      };

      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/hr-analytics/predict-turnover",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(requestData),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPrediction(data);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Erreur lors de la prédiction");
      }
    } catch (err) {
      console.error("Error predicting turnover:", err);
      setError("Erreur de connexion au serveur");
    } finally {
      setLoading(false);
    }
  };

  const getRiskBadgeColor = (level: string) => {
    switch (level.toLowerCase()) {
      case "faible":
        return "bg-green-100 text-green-800 border-green-300";
      case "moyen":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      case "élevé":
        return "bg-red-100 text-red-800 border-red-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-purple-100 rounded-lg">
          <Brain className="w-6 h-6 text-purple-600" />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-800">
            Prédiction de Turnover
          </h2>
          <p className="text-sm text-gray-600">
            Modèle Gradient Boosting
          </p>
        </div>
      </div>

      {/* Formulaire */}
      <div className="space-y-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Sexe */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sexe
            </label>
            <select
              value={formData.sexe}
              onChange={(e) =>
                setFormData({ ...formData, sexe: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="Masculin">Masculin</option>
              <option value="Féminin">Féminin</option>
            </select>
          </div>

          {/* Total jours d'absence */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Total jours d'absence
            </label>
            <input
              type="number"
              min="0"
              value={formData.total_jours_absence}
              onChange={(e) =>
                setFormData({ ...formData, total_jours_absence: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="0"
            />
          </div>

          {/* Nombre d'absences */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nombre d'absences
            </label>
            <input
              type="number"
              min="0"
              value={formData.nb_absences}
              onChange={(e) =>
                setFormData({ ...formData, nb_absences: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="0"
            />
          </div>
        </div>

        {/* Informations auto-calculées */}
        {employeeData && (
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <p className="text-sm text-gray-600 mb-2">
              <strong>Calculé automatiquement:</strong>
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
              {employeeData.date_of_birth && (
                <div>
                  <span className="text-gray-500">Âge:</span>{" "}
                  <span className="font-medium">
                    {Math.floor(
                      (new Date().getTime() -
                        new Date(employeeData.date_of_birth).getTime()) /
                        (365.25 * 24 * 60 * 60 * 1000)
                    )}{" "}
                    ans
                  </span>
                </div>
              )}
              {employeeData.hire_date && (
                <div>
                  <span className="text-gray-500">Ancienneté:</span>{" "}
                  <span className="font-medium">
                    {(
                      (new Date().getTime() -
                        new Date(employeeData.hire_date).getTime()) /
                      (365.25 * 24 * 60 * 60 * 1000)
                    ).toFixed(1)}{" "}
                    ans
                  </span>
                </div>
              )}
              {employeeData.contract_type && (
                <div>
                  <span className="text-gray-500">Contrat:</span>{" "}
                  <span className="font-medium">{employeeData.contract_type}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Bouton de prédiction */}
        <button
          onClick={handlePredict}
          disabled={loading || !employeeData?.date_of_birth || !employeeData?.hire_date}
          className="w-full bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium transition-colors"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Prédiction en cours...
            </>
          ) : (
            <>
              <TrendingUp className="w-5 h-5" />
              Prédire le Turnover
            </>
          )}
        </button>
      </div>

      {/* Erreur */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-800">Erreur</p>
            <p className="text-sm text-red-700">{error}</p>
          </div>
        </div>
      )}

      {/* Résultat */}
      {prediction && (
        <div className="space-y-4">
          {/* Badge de risque principal */}
          <div
            className={`p-6 rounded-lg border-2 ${getRiskBadgeColor(
              prediction.risk_level
            )}`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className="text-4xl">{prediction.risk_emoji}</span>
                <div>
                  <p className="text-sm font-medium uppercase tracking-wide">
                    Risque de Turnover
                  </p>
                  <p className="text-3xl font-bold">{prediction.risk_level}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600">Probabilité</p>
                <p className="text-4xl font-bold">
                  {prediction.turnover_probability_percent.toFixed(1)}%
                </p>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t border-current/20">
              <p className="text-xs">
                Prédiction:{" "}
                {prediction.prediction === 1 ? (
                  <span className="font-bold">Risque de départ</span>
                ) : (
                  <span className="font-bold">Devrait rester</span>
                )}
              </p>
            </div>
          </div>

          {/* Détails des features */}
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
            <p className="text-sm font-semibold text-gray-700 mb-3">
              Features utilisées:
            </p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
              <div>
                <span className="text-gray-500">Âge:</span>{" "}
                <span className="font-medium">
                  {prediction.features_used.age} ans
                </span>
              </div>
              <div>
                <span className="text-gray-500">Ancienneté:</span>{" "}
                <span className="font-medium">
                  {prediction.features_used.anciennete_annees.toFixed(1)} ans
                </span>
              </div>
              <div>
                <span className="text-gray-500">Jours absence:</span>{" "}
                <span className="font-medium">
                  {prediction.features_used.total_jours_absence}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Nb absences:</span>{" "}
                <span className="font-medium">
                  {prediction.features_used.nb_absences}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Présence:</span>{" "}
                <span className="font-medium">
                  {prediction.features_used.duree_presence_jours} jours
                </span>
              </div>
            </div>
          </div>

          {/* Métadonnées */}
          <div className="text-xs text-gray-500">
            <p>
              Modèle: {prediction.model_path.split("\\").pop()}
            </p>
            <p>
              Calculé le:{" "}
              {new Date(prediction.computed_at).toLocaleString("fr-FR")}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
