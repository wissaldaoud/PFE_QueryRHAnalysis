#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script for query engine service"""
import asyncio
from app.services.query_engine_service import QueryEngineService
from app.db.base import SessionLocal

async def test_query():
    db = SessionLocal()
    try:
        print("Initializing service...")
        service = QueryEngineService(db)
        print("✓ Service initialized")
        
        print("\nTesting query...")
        result = await service.process_query("Combien d'employés actifs?", 1)
        
        print(f"\n✓ Query executed")
        print(f"Success: {result.get('success')}")
        print(f"Answer: {result.get('answer')}")
        if not result.get('success'):
            print(f"Error: {result.get('error')}")
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_query())
