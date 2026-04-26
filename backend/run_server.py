import os
import sys

if __name__ == '__main__':
    # Changer le répertoire de travail
    backend_dir = r"C:\Users\wdaoud\Desktop\test\backend"
    os.chdir(backend_dir)
    
    # Ajouter au PYTHONPATH
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")

