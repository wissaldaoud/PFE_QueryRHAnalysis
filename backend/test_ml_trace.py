#!/usr/bin/env python3
"""Test MLService avec traceback complet"""

import sys
import os
import traceback

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(__file__))

# Setup env
os.environ.setdefault("ENV_FILE", ".env")

from app.services.ml_service import MLService
from app.database import SessionLocal

def test_predict():
    """Test prédiction avec traceback détaillé"""
    try:
        db = SessionLocal()
        ml_service = MLService(db)
        
        print("=" * 80)
        print("Testing prediction for employee 164771...")
        print("=" * 80)
        
        result = ml_service.predict_from_dwh("164771")
        
        print("\n✅ RESULT:")
        import json
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print("\n❌ ERROR:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")
        print("\n📍 FULL TRACEBACK:")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_predict()
