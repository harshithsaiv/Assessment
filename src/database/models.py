import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Numeric, DateTime, ForeignKey, Text, Table, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

# Junction table for Many-to-Many relationship between Notes and Tags
note_tags = Table(
    'note_tags', Base.metadata,
    Column('note_id', UUID(as_uuid=True), ForeignKey('clinical_notes.id', ondelete="CASCADE"), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete="CASCADE"), primary_key=True)
)

class Patient(Base):
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mrn = Column(String(50), unique=True, nullable=False, index=True)  # Indexed for fast lookups
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    dob = Column(DateTime(timezone=False), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    labs = relationship("Lab", back_populates="patient", cascade="all, delete-orphan")
    notes = relationship("ClinicalNote", back_populates="patient", cascade="all, delete-orphan")

class Lab(Base):
    __tablename__ = "labs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    lab_code = Column(String(50), nullable=False) # LOINC code
    lab_name = Column(String(255), nullable=False)
    result_value = Column(Numeric(10, 2), nullable=True)
    result_unit = Column(String(20), nullable=True)
    is_abnormal = Column(Boolean, default=False, index=True) # Indexed for "High Risk" queries
    collected_at = Column(DateTime(timezone=True), nullable=False)
    
    patient = relationship("Patient", back_populates="labs")

class ClinicalNote(Base):
    __tablename__ = "clinical_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    note_type = Column(String(50), nullable=False) # e.g. "Intake", "Discharge"
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("Patient", back_populates="notes")
    tags = relationship("Tag", secondary=note_tags, back_populates="notes")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False) # e.g. "Cardiology", "Urgent"
    
    notes = relationship("ClinicalNote", secondary=note_tags, back_populates="tags")