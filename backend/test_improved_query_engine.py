"""
Test du moteur de requêtes amélioré avec:
- Correction orthographique automatique
- Synonymes RH
- Normalisation du texte
- Nouveaux intents (absence_today, conge, recrutement, anciennete)
- Suggestions automatiques
"""

# Questions de test avec fautes d'orthographe et synonymes
test_questions = [
    # Test synonymes employé
    "Combien de collaborateurs actifs ?",
    "Liste des agents inactifs",
    "Trouve moi les salariés absents",
    
    # Test fautes d'orthographe
    "Combienn d'employés actiff ?",
    "Liste des absennces en 2024",
    "Quelle est la moyene d'age ?",
    
    # Test nouveaux intents
    "Qui est absent aujourd'hui ?",
    "Combien de jours de congé pour chaque employé ?",
    "Quelles sont les nouvelles embauches en 2024 ?",
    "Quels sont les employés avec le plus d'ancienneté ?",
    
    # Test patterns enrichis
    "Montre moi la liste des employés",
    "Donne moi le total des absences",
    "Comment évolue le nombre d'employés par mois ?",
    "Quel département a le plus d'employés ?",
    "Trouve moi les employés de sexe masculin",
    
    # Test accents et normalisation
    "Liste des employés par département",
    "Répartition des congés par société",
    "Moyenne d'âge des salariés actifs",
    
    # Test confiance faible (devrait retourner suggestions)
    "abcdef xyz 123",
    "????",
]

print("=" * 80)
print("TEST DU MOTEUR DE REQUÊTES RH AMÉLIORÉ")
print("=" * 80)
print("\nCes questions testent:")
print("✅ Correction orthographique automatique")
print("✅ Synonymes RH (collaborateur, agent, salarié → employé)")
print("✅ Normalisation (accents, ponctuation)")
print("✅ Nouveaux intents (absence_today, conge, recrutement, anciennete)")
print("✅ Patterns enrichis (montre moi, donne moi, trouve moi, etc.)")
print("✅ Suggestions automatiques (confiance < 0.4)")
print("\n" + "=" * 80)

for i, question in enumerate(test_questions, 1):
    print(f"\n{i}. {question}")

print("\n" + "=" * 80)
print("\n📝 Pour tester, utilisez l'API:")
print("   POST http://127.0.0.1:8000/api/query-engine/execute")
print("   Body: {\"question\": \"Combien de collaborateurs actifs ?\"}")
print("\n" + "=" * 80)
