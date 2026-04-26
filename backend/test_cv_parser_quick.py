"""
Test rapide du CV Parser
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Test imports
print("Testing imports...")
try:
    import PyPDF2
    print("✅ PyPDF2 imported successfully")
except Exception as e:
    print(f"❌ PyPDF2 import failed: {e}")

try:
    import docx
    print("✅ python-docx imported successfully")
except Exception as e:
    print(f"❌ python-docx import failed: {e}")

try:
    from app.services.cv_parser import CVParser
    print("✅ CVParser imported successfully")
except Exception as e:
    print(f"❌ CVParser import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test avec un fichier texte simple
print("\n" + "="*50)
print("Testing with simple text file...")
print("="*50)

test_cv_content = """
Jean Dupont
Email: jean.dupont@example.com
Tel: +33 6 12 34 56 78

COMPÉTENCES
- Python, JavaScript, React
- Docker, Kubernetes
- SQL, PostgreSQL
- AWS, CI/CD

EXPÉRIENCE PROFESSIONNELLE
Développeur Full Stack - TechCorp (2020-2024)
• Développement d'applications web avec React et FastAPI
• Déploiement sur AWS avec Docker
• 4 ans d'expérience

FORMATION
Master en Informatique - Université Paris (2018-2020)
Licence en Informatique - Université Paris (2015-2018)
""".encode('utf-8')

try:
    parser = CVParser()
    result = parser.parse_cv("test_cv.txt", test_cv_content)
    
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Skills found: {result['data']['skills']}")
        print(f"Skills count: {result['data']['extracted_skills_count']}")
        print(f"Years of experience: {result['data']['years_of_experience']}")
        print(f"Email: {result['data']['email']}")
        print(f"Phone: {result['data']['phone']}")
        print("✅ TEXT PARSING WORKS!")
    else:
        print(f"Error: {result.get('error')}")
        print("❌ TEXT PARSING FAILED")
except Exception as e:
    print(f"❌ Exception during parsing: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Test completed!")
print("="*50)
