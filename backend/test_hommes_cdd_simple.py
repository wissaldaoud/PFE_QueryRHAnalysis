"""Test simple pour "Combien d'employés hommes en CDD" via requête HTTP"""
import requests
import json

API_URL = "http://127.0.0.1:8000/api/query/ask"

def test_query():
    question = "Combien d'employés hommes en CDD"
    
    print("="*80)
    print(f"🔍 TEST: {question}")
    print("="*80)
    
    try:
        response = requests.post(API_URL, json={"question": question}, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        
        print(f"\n📊 Intent: {result.get('intent', 'N/A')}")
        print(f"📊 Confidence: {result.get('confidence', 'N/A'):.2f}")
        print(f"📊 Entities: {result.get('entities', [])}")
        
        # Afficher les filtres s'ils existent
        if 'filters' in result:
            print(f"📊 Filters: {result['filters']}")
        
        # Afficher le SQL
        if 'sql_query' in result:
            print(f"\n🔧 SQL:\n{result['sql_query']}")
        
        # Afficher les données
        if 'data' in result:
            print(f"\n📈 Result: {result['data']}")
            if isinstance(result['data'], list) and len(result['data']) > 0:
                first_row = result['data'][0]
                if 'total' in first_row:
                    print(f"\n✅ Total: {first_row['total']}")
        
        # Afficher les suggestions si disponibles
        if 'suggestions' in result:
            print(f"\n💡 Suggestions: {result['suggestions']}")
        
        print("\n" + "="*80)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend. Is it running on http://127.0.0.1:8000?")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query()
