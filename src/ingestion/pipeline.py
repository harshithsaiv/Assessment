import csv
import logging
import os
import pg8000.native
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MedisyncPipeline")


DB_CONFIG = {
    "user": "medisync_admin",
    "password": "secure_dev_password",
    "host": "localhost",
    "port": 5432,
    "database": "medisync"
}

class ClinicalIngestor:
    def __init__(self, db_config):
        self.db_config = db_config

    def ingest_patients(self, file_path):
        """
        Reads a CSV and UPSERTS patients.
        """
        logger.info(f"Starting patient ingestion from {file_path}")
        
        sql = """
            INSERT INTO patients (mrn, first_name, last_name, dob)
            VALUES (:mrn, :first_name, :last_name, :dob)
            ON CONFLICT (mrn) DO UPDATE 
            SET updated_at = CURRENT_TIMESTAMP
            RETURNING id;
        """

        try:
            conn = pg8000.native.Connection(**self.db_config)
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:

                    if not row.get('mrn'):
                        logger.warning(f"Skipping row missing MRN: {row}")
                        continue
                        
                    conn.run(sql,
                        mrn=row['mrn'],
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        dob=row['dob']
                    )
                    count += 1
            conn.close()
            logger.info(f"Successfully ingested {count} patients.")
        except Exception as e:
            logger.error(f"Failed to ingest patients: {e}")
            raise

    def process_notes(self, mock_notes):
        """
        Simulates reading unstructured notes and parsing them.
        """
        logger.info("Starting clinical note processing...")
        
        conn = pg8000.native.Connection(**self.db_config)
        for note in mock_notes:

            res = conn.run("SELECT id FROM patients WHERE mrn = :mrn", mrn=note['mrn'])
            if not res:
                logger.warning(f"Patient {note['mrn']} not found. Skipping note.")
                continue
            patient_id = res[0][0]

            note_result = conn.run("""
                INSERT INTO clinical_notes (patient_id, note_type, content)
                VALUES (:patient_id, :note_type, :content) 
                RETURNING id
            """, patient_id=patient_id, note_type=note['type'], content=note['content'])
            note_id = note_result[0][0]

            content_lower = note['content'].lower()
            tags = []
            
            if "diabetes" in content_lower: tags.append("Metabolic")
            if "bp" in content_lower or "hypertension" in content_lower: tags.append("Cardiac")
            if "urgent" in content_lower: tags.append("High Risk")

            for tag_name in tags:
                conn.run("INSERT INTO tags (name) VALUES (:name) ON CONFLICT (name) DO NOTHING", name=tag_name)
                tag_result = conn.run("SELECT id FROM tags WHERE name = :name", name=tag_name)
                tag_id = tag_result[0][0]
                conn.run("""
                    INSERT INTO note_tags (note_id, tag_id) 
                    VALUES (:note_id, :tag_id) ON CONFLICT DO NOTHING
                """, note_id=note_id, tag_id=tag_id)
        
        conn.close()
        logger.info("Notes processed and tagged.")


def generate_mock_artifacts():
    """Generates the CSVs required for the assignment"""
    if not os.path.exists("patients.csv"):
        with open("patients.csv", "w") as f:
            f.write("mrn,first_name,last_name,dob\n")
            f.write("MRN-001,Alice,Smith,1985-04-12\n")
            f.write("MRN-002,Bob,Jones,1990-06-23\n")
            f.write("MRN-003,Charlie,Day,1978-11-02\n")
        print("Generated patients.csv")

if __name__ == "__main__":
    generate_mock_artifacts()
    
    pipeline = ClinicalIngestor(DB_CONFIG)
    
    pipeline.ingest_patients("patients.csv")
    
    mock_notes_data = [
        {"mrn": "MRN-001", "type": "Intake", "content": "Patient reports history of Diabetes and frequent thirst."},
        {"mrn": "MRN-002", "type": "Lab Report", "content": "URGENT: Blood pressure critical. Hypertension detected."},
        {"mrn": "MRN-003", "type": "General", "content": "Routine checkup. No issues."}
    ]
    pipeline.process_notes(mock_notes_data)