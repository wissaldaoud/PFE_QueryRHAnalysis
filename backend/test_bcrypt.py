import sys
sys.path.insert(0, "C:\\Users\\wdaoud\\Desktop\\test\\backend")

from app.core.security import get_password_hash

try:
    # Test with short password
    hash1 = get_password_hash("short")
    print(f"✓ Short password hashed successfully")
    
    # Test with normal password
    hash2 = get_password_hash("normal_password_123")
    print(f"✓ Normal password hashed successfully")
    
    # Test with very long password  
    long_pass = "a" * 100  # 100 characters
    hash3 = get_password_hash(long_pass)
    print(f"✓ Long password hashed successfully")
    
except Exception as e:
    print(f"✗ Error type: {type(e).__name__}")
    print(f"✗ Error message: {str(e)}")
    import traceback
    traceback.print_exc()
