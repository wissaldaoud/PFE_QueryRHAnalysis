"""
train_nlp_rh.py - Entraînement NLP supervisé TF-IDF + SVM
Compatible Python 3.14
"""
import os, json, pickle, random
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split, cross_val_score
from collections import Counter

os.makedirs("models", exist_ok=True)
random.seed(42)

DATASET = [
    # PAIE
    ("quel est le salaire moyen des employes",           "paie"),
    ("salaire maximum dans l entreprise",                "paie"),
    ("qui gagne le plus dans la societe",                "paie"),
    ("affiche les salaires des employes actifs",         "paie"),
    ("top 10 des salaires les plus eleves",              "paie"),
    ("quel est le salaire minimum",                      "paie"),
    ("liste des remunerations par departement",          "paie"),
    ("max salary",                                       "paie"),
    ("moyenne des salaires par poste",                   "paie"),
    ("combien gagne un employe en CDI",                  "paie"),
    ("grille de salaire du personnel",                   "paie"),
    ("remuneration des salaries",                        "paie"),
    # TURNOVER
    ("quel est le taux de turnover",                     "turnover"),
    ("combien d employes ont quitte l entreprise",       "turnover"),
    ("taux de depart du personnel cette annee",          "turnover"),
    ("rotation des effectifs en 2024",                   "turnover"),
    ("attrition des salaries",                           "turnover"),
    ("employes qui ont quitte la societe",               "turnover"),
    ("roulement du personnel",                           "turnover"),
    ("nombre de demissions cette annee",                 "turnover"),
    ("taux d attrition du personnel",                    "turnover"),
    ("combien de personnes ont quitte en 2023",          "turnover"),
    ("liste des employes partis",                        "turnover"),
    ("employes inactifs cette annee",                    "turnover"),
    # ABSENCE
    ("qui est absent aujourd hui",                       "absence"),
    ("liste des absences en cours",                      "absence"),
    ("taux d absenteisme par departement",               "absence"),
    ("combien d absences cette annee",                   "absence"),
    ("repartition des absences par motif",               "absence"),
    ("employes en arret maladie ce mois",                "absence"),
    ("duree moyenne des absences",                       "absence"),
    ("top 10 des employes les plus absents",             "absence"),
    ("analyse de l absenteisme cette annee",             "absence"),
    ("liste des conges en cours",                        "absence"),
    ("qui n est pas venu travailler aujourd hui",        "absence"),
    ("employes absents maintenant",                      "absence"),
    # COUNT
    ("combien d employes actifs",                        "count"),
    ("quel est l effectif total",                        "count"),
    ("nombre de CDI dans l entreprise",                  "count"),
    ("combien de CDD cette annee",                       "count"),
    ("quel est le nombre total de salaries",             "count"),
    # LIST
    ("liste des employes en CDI",                        "list"),
    ("affiche les salaries actifs",                      "list"),
    ("montre les employes du departement RH",            "list"),
    ("voir tous les collaborateurs",                     "list"),
    ("donne moi la liste des agents",                    "list"),
    # STATS
    ("repartition des employes par sexe",                "stats"),
    ("distribution par departement",                     "stats"),
    ("repartition hommes femmes",                        "stats"),
    ("ventilation par type de contrat",                  "stats"),
    ("statistiques des employes par tranche d age",      "stats"),
    # TREND
    ("evolution des embauches par annee",                "trend"),
    ("tendance des absences dans le temps",              "trend"),
    ("historique des recrutements par mois",             "trend"),
    ("comment a evolue l effectif par annee",            "trend"),
    ("progression des contrats au fil du temps",         "trend"),
]

texts  = [t for t, _ in DATASET]
labels = [l for _, l in DATASET]
intents = sorted(set(labels))

print("="*60)
print("ENTRAINEMENT NLP SUPERVISE — TF-IDF + SVM")
print("="*60)
print(f"Dataset : {len(DATASET)} questions — {len(intents)} intents")
for intent, count in sorted(Counter(labels).items()):
    print(f"   {intent:15s} → {count} questions")

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.20, random_state=42, stratify=labels
)
print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")

pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        sublinear_tf=True,
        strip_accents='unicode',
        lowercase=True,
    )),
    ('svm', LinearSVC(C=1.0, max_iter=2000, random_state=42))
])

print("\nEntrainement en cours...")
pipeline.fit(X_train, y_train)
print("Entrainement termine !")

print("\nValidation croisee 5-fold...")
cv_scores = cross_val_score(pipeline, texts, labels, cv=5, scoring='accuracy')
print(f"Scores  : {[round(s,3) for s in cv_scores]}")
print(f"Moyenne : {cv_scores.mean()*100:.1f}%")
print(f"Std     : +/-{cv_scores.std()*100:.1f}%")

y_pred = pipeline.predict(X_test)
acc    = accuracy_score(y_test, y_pred)
print(f"\nAccuracy test : {acc*100:.1f}%")
print(classification_report(y_test, y_pred, zero_division=0))

with open("models/nlp_intent_model.pkl", "wb") as f:
    pickle.dump(pipeline, f)

report = {
    "accuracy": round(acc, 4),
    "cv_mean": round(float(cv_scores.mean()), 4),
    "cv_std": round(float(cv_scores.std()), 4),
    "cv_scores": [round(float(s), 4) for s in cv_scores],
    "nb_questions": len(DATASET),
    "nb_intents": len(intents),
    "intents": intents,
    "model": "TF-IDF + LinearSVC",
}
with open("models/training_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("\nTests manuels :")
for q in ["max salary","salaire moyen","taux de turnover",
          "qui est absent aujourd hui","combien d employes actifs",
          "liste des CDI","repartition par sexe","taux d absenteisme",
          "qui a quitte l entreprise","top 10 salaires"]:
    pred = pipeline.predict([q])[0]
    print(f"   '{q}' → {pred}")

print(f"\nModele sauvegarde → models/nlp_intent_model.pkl")
print(f"Accuracy : {acc*100:.1f}% | CV : {cv_scores.mean()*100:.1f}%")
