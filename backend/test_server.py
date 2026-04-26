"""Test si le serveur peut démarrer"""
import sys
sys.path.insert(0, '.')

try:
    from app.main import app
    print("✅ App importée avec succès")
    
    # Test les routes
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"  Route: {route.path}")
            
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
