import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from patients import patients_db

app = FastAPI(title="Hospital Management API")

# 🔒 CORS Configurations - Dono URLs (Ghar ka local aur Railway frontend) completely allowed hain
origins = [
    "https://railway.app",
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origins_regex="https://.*\\.railway\\.app", # Railway ke subdomains ke liye safety lock bypass
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# 📋 Schema Structure
class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    contact: Optional[str] = None
    email: Optional[str] = None
    blood_group: Optional[str] = None
    medical_conditions: List[str]
    admission_date: Optional[str] = None
    notes: Optional[str] = None

# 1️⃣ READ (GET) - Humen data ko frontend ke mutabiq map karke bhejna hai taake 'id' aur 'medical_conditions' sahi load hon
@app.get("/patients")
def get_all_patients():
    formatted_list = []
    for p in patients_db:
        # Frontend ke columns ko 'id' aur 'medical_conditions' chahiye hota hai list format mein
        conditions = p.get("medical_conditions", [])
        if not conditions and "illness" in p:
            conditions = [p["illness"]] if isinstance(p["illness"], str) else p["illness"]

        formatted_list.append({
            "id": str(p.get("patient_id")),
            "patient_id": p.get("patient_id"),
            "name": p.get("name"),
            "age": p.get("age"),
            "gender": p.get("gender"),
            "contact": p.get("contact", ""),
            "email": p.get("email", ""),
            "blood_group": p.get("blood_group", p.get("blood_group", "O+")),
            "medical_conditions": conditions,
            "admission_date": p.get("admission_date", "2026-09-05"),
            "notes": p.get("notes", "")
        })
    return formatted_list

# 2️⃣ READ (GET) - Single Patient
@app.get("/patients/{patient_id}")
def get_patient_by_id(patient_id: str):
    for patient in patients_db:
        if str(patient.get("patient_id")) == str(patient_id):
            # Dynamic object transformation
            conditions = patient.get("medical_conditions", [])
            if not conditions and "illness" in patient:
                conditions = [patient["illness"]] if isinstance(patient["illness"], str) else patient["illness"]
            
            return {
                "id": str(patient.get("patient_id")),
                "patient_id": patient.get("patient_id"),
                "name": patient.get("name"),
                "age": patient.get("age"),
                "gender": patient.get("gender"),
                "contact": patient.get("contact", ""),
                "email": patient.get("email", ""),
                "blood_group": patient.get("blood_group", "O+"),
                "medical_conditions": conditions,
                "admission_date": patient.get("admission_date", "2026-09-05"),
                "notes": patient.get("notes", "")
            }
    raise HTTPException(status_code=404, detail="Patient nahi mila!")

# 3️⃣ CREATE (POST) - Naya Patient save karne ke liye
@app.post("/patients")
def create_patient(patient: PatientCreate):
    new_id = max([p.get("patient_id", 0) for p in patients_db]) + 1 if patients_db else 1
    
    new_patient = {
        "patient_id": new_id,
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "illness": patient.medical_conditions[0] if patient.medical_conditions else "None",
        "contact": patient.contact,
        "email": patient.email,
        "blood_group": patient.blood_group,
        "medical_conditions": patient.medical_conditions,
        "admission_date": patient.admission_date,
        "notes": patient.notes
    }
    
    patients_db.append(new_patient)
    
    # Python file ko refresh karne ka tareeqa
    try:
        formatted_data = json.dumps(patients_db, indent=4, ensure_ascii=False)
        with open("patients.py", "w", encoding="utf-8") as file:
            file.write(f"patients_db = {formatted_data}")
    except Exception as e:
        print(f"File save error: {e}")
        
    return new_patient
