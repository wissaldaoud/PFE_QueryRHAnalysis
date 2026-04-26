"""Test rapide du scoring DWH Sopra HR + XGBoost + SHAP"""
from app.services.predictive_scoring_ml import PredictiveScorerML

scorer = PredictiveScorerML()

# Test batch scoring
result = scorer.score_all_employees(limit=10)
print(f"Total employés scorés : {result['stats']['total']}")
print(f"Stats : {result['stats']}")
print()

for p in result.get("predictions", []):
    print(f"  {p['prenom']} {p['nom']}: {p['score']}% {p['niveau']}")
    for f in p["key_factors"][:2]:
        print(f"    -> {f['feature']}: {f['shap_value']}")
    print()

# Test backward compatible score() method
print("--- Test score() avec nudoss ---")
from sqlalchemy import text
with scorer.dwh_engine.connect() as conn:
    row = conn.execute(text("SELECT nudoss FROM dim.dim_employe WHERE flag_employe_actif = 1 LIMIT 1")).fetchone()
    nudoss = str(row[0])

ps = scorer.score({"nudoss": nudoss})
print(f"PredictiveScore: churn={ps.churn_risk_score}, risk={ps.risk_level}, confidence={ps.prediction_confidence}")
print(f"Top factors: {ps.key_factors[:3]}")
print(f"Recommendations: {len(ps.recommendations)}")

print("\nAll tests passed!")
