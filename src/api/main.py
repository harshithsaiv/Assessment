from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import logging

# Import our setup
from src.database.models import Base, Patient, Lab, ClinicalNote, Tag, note_tags
from src.api.schemas import PatientCreate, PatientResponse, LabCreate, LabResponse, PillarPatientResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Database Setup (Standard Dependency Pattern) ---
# In a real app, this goes in src/database/session.py
SQLALCHEMY_DATABASE_URL = "postgresql+pg8000://medisync_admin:secure_dev_password@localhost:5432/medisync"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- App Initialization ---
app = FastAPI(
    title="Medisync Clinical Platform",
    description="API for ingesting and retrieving clinical data.",
    version="1.0.0"
)
logger = logging.getLogger("uvicorn")

# --- Endpoints ---

@app.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """
    Creates a new patient. 
    Reasoning: Uses 'mrn' uniqueness check to prevent duplicates.
    """
    existing = db.query(Patient).filter(Patient.mrn == patient.mrn).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient with this MRN already exists")
    
    # Create ORM Object
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@app.post("/labs", response_model=LabResponse, status_code=status.HTTP_201_CREATED)
def create_lab(lab: LabCreate, db: Session = Depends(get_db)):
    """
    Ingests a lab result.
    Reasoning: Automatically calculates 'is_abnormal' flag if not provided (Business Logic).
    """
    # Simple logic: If value > 100, flag as abnormal (Example logic)
    is_abnormal = False
    if lab.result_value and lab.result_value > 100.0:
        is_abnormal = True

    db_lab = Lab(
        **lab.model_dump(),
        is_abnormal=is_abnormal
    )
    db.add(db_lab)
    db.commit()
    db.refresh(db_lab)
    return db_lab

@app.get("/patients/{patient_id}/labs", response_model=List[LabResponse])
def get_patient_labs(patient_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieves all labs for a specific patient.
    """
    labs = db.query(Lab).filter(Lab.patient_id == patient_id).order_by(Lab.collected_at.desc()).all()
    if not labs:
        # Note: Depending on requirements, empty list might be better than 404. 
        # But 404 is standard if the patient doesn't exist.
        return []
    return labs

@app.get("/pillars/{pillar}/patients", response_model=List[PillarPatientResponse])
def get_patients_by_pillar(pillar: str, db: Session = Depends(get_db)):
    """
    COMPLEX QUERY: Finds patients who belong to a specific clinical pillar (Tag).
    Join Path: Tag -> NoteTags -> Notes -> Patient
    """
    # We use a case-insensitive search for the pillar/tag name
    results = (
        db.query(Patient)
        .join(ClinicalNote)
        .join(note_tags)
        .join(Tag)
        .filter(Tag.name.ilike(pillar)) # ILIKE = Case Insensitive
        .distinct() # A patient might have 10 notes with the same tag; show them once.
        .all()
    )
    
    # Map to simplified response model
    response_data = []
    for p in results:
        response_data.append({
            "id": p.id,
            "mrn": p.mrn,
            "name": f"{p.first_name} {p.last_name}"
        })
        
    return response_data