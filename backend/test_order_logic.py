"""
Test simple: vérifier la logique ORDER BY
"""
# Simulation de la logique corrigée

def test_order_by_logic():
    scenarios = [
        {
            "intent": "count",
            "group_by_clause": "",  # Pas de GROUP BY
            "has_plus": False,
            "has_moins": True,
            "expected": "Pas de ORDER BY (COUNT simple)",
        },
        {
            "intent": "count",
            "group_by_clause": "\nGROUP BY e.libelle_sexe",  # Avec GROUP BY
            "has_plus": False,
            "has_moins": True,
            "expected": "ORDER BY total ASC",
        },
        {
            "intent": "list",
            "group_by_clause": "",  # Pas de GROUP BY
            "has_plus": False,
            "has_moins": True,
            "expected": "ORDER BY e.age ASC",
        },
        {
            "intent": "average",
            "group_by_clause": "",  # Pas de GROUP BY
            "has_plus": True,
            "has_moins": False,
            "expected": "Pas de ORDER BY (AVERAGE simple)",
        },
    ]
    
    print("\n" + "="*70)
    print("TEST: Logique ORDER BY avec la correction")
    print("="*70)
    
    for i, scenario in enumerate(scenarios, 1):
        intent = scenario["intent"]
        group_by_clause = scenario["group_by_clause"]
        has_plus = scenario["has_plus"]
        has_moins = scenario["has_moins"]
        expected = scenario["expected"]
        
        # Appliquer la logique corrigée
        order_by_clause = ""
        
        if has_plus and not order_by_clause:
            if group_by_clause:
                order_by_clause = "\nORDER BY total DESC"
            elif intent not in ["count", "average"]:
                order_by_clause = "\nORDER BY e.age DESC"
        elif has_moins and not order_by_clause:
            if group_by_clause:
                order_by_clause = "\nORDER BY total ASC"
            elif intent not in ["count", "average"]:
                order_by_clause = "\nORDER BY e.age ASC"
        
        result = order_by_clause if order_by_clause else "Pas de ORDER BY"
        status = "✅" if result == expected or (not order_by_clause and "Pas de" in expected) else "❌"
        
        print(f"\nScénario {i}:")
        print(f"  Intent: {intent}")
        print(f"  GROUP BY: {'Oui' if group_by_clause else 'Non'}")
        print(f"  has_moins: {has_moins}, has_plus: {has_plus}")
        print(f"  {status} Résultat: {result}")
        print(f"  Attendu: {expected}")

if __name__ == "__main__":
    test_order_by_logic()
