"""
Mon premier test FastAPI - Exercice du soir
"""
from fastapi import FastAPI

app = FastAPI()

# TODO: Ajoutez vos tests ici après le tutoriel

@app.get("/")
def read_root():
    return {"message": "Hello World - Mon premier API!"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}


# EXERCICE 1: Créez un endpoint GET /employees/{employee_id}
# qui retourne: {"employee_id": ..., "name": "Ahmed", "department": "IT"}

# EXERCICE 2: Créez un endpoint GET /employees 
# avec query parameter ?department=IT
# qui retourne une liste d'employés

# EXERCICE 3: Créez un endpoint POST /employees
# qui accepte: {"name": "...", "department": "...", "salary": ...}
# et retourne l'employé créé avec un ID

# Tapez vos solutions ci-dessous:
