from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional  # <-- Naye fields ke liye zaroori hain
from patients import patients_db

app = FastAPI(title="Hospital Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# 📋 Frontend ke mutabiq bilkul naya structure (Schema)
class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    contact: Optional[str] = None
    email: Optional[str] = None
    blood_group: Optional[str] = None
    medical_conditions: List[str]  # <-- Lovable 'illness' ki jagah ye bhej raha hai
    admission_date: Optional[str] = None
    notes: Optional[str] = None


# 1️⃣ READ (GET) - Saare Patients ka data dekhne ke liye
@app.get("/patients")
def get_all_patients():
    return patients_db


# 2️⃣ READ (GET) - Kisi AIK makhsoos patient ko ID se dhoondne ke liye
@app.get("/patients/{patient_id}")
def get_patient_by_id(patient_id: str):
    for patient in patients_db:
        if str(patient["patient_id"]) == str(patient_id):
            return patient

    raise HTTPException(status_code=404, detail="Mareez (Patient) nahi mila!")


# 3️⃣ READ (GET) - Illness/Medical Condition ke mutabiq search/filter karne ke liye
@app.get("/search-patients/")
def search_patients_by_illness(illness: str):
    results = []
    for patient in patients_db:
        # Purane data ke liye 'illness' check karega aur naye data ke liye 'medical_conditions' list
        has_illness = "illness" in patient and illness.lower() in patient["illness"].lower()
        has_condition = False
        
        if "medical_conditions" in patient and patient["medical_conditions"]:
            for condition in patient["medical_conditions"]:
                if illness.lower() in condition.lower():
                    has_condition = True
                    break
        
        if has_illness or has_condition:
            results.append(patient)

    if not results:
        raise HTTPException(status_code=404, detail="Is bemari ka koi mareez nahi mila")

    return results


# 4️⃣ CREATE (POST) - Naya Patient database aur asli file mein save karne ke liye
import json  # <-- Sab se upar ya function ke andar import kar lein

# 4️⃣ CREATE (POST) - Naya Patient database aur asli file mein khoobsurat format mein save karne ke liye
@app.post("/patients")
def create_patient(patient: PatientCreate):
    new_id = max([p["patient_id"] for p in patients_db]) + 1 if patients_db else 1
    illness_value = patient.medical_conditions if patient.medical_conditions else "None"
    
    new_patient = {
        "patient_id": new_id,
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "illness": illness_value,
        "contact": patient.contact,
        "email": patient.email,
        "blood_group": patient.blood_group,
        "medical_conditions": patient.medical_conditions,
        "admission_date": patient.admission_date,
        "notes": patient.notes
    }
    
    patients_db.append(new_patient)
    
    # 💾 Asli file mein data ko khoobsurat tareeqe se spaces ke saath save karne ke liye
    try:
        # json.dumps data ko 'indent=4' ke zariye table/readable form mein badal deta hai
        formatted_data = json.dumps(patients_db, indent=4, ensure_ascii=False)
        
        with open("patients.py", "w", encoding="utf-8") as file:
            file.write(f"patients_db = {formatted_data}")
    except Exception as e:
        print(f"File save karne mein masla aaya: {e}")
        
    return new_patient

# Terminal mein chalane ke liye: uvicorn main:app --reload
