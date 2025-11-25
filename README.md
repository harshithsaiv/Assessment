# Medisync Clinical Platform

A clinical data platform for ingesting and managing patient records, lab results, and clinical notes with intelligent tagging capabilities.

## 🏗️ Architecture

### Database Schema
![Database Schema](database_schema.png)

The system uses a PostgreSQL database with the following core entities:
- **Patients**: Store patient demographics with unique Medical Record Numbers (MRN)
- **Labs**: Lab results with abnormality flagging
- **Clinical Notes**: Unstructured clinical documentation
- **Tags**: Clinical pillars/categories (e.g., Metabolic, Cardiac, High Risk)
- **Note Tags**: Many-to-many relationship between notes and tags

### Tech Stack
- **Backend**: FastAPI (Python 3.13)
- **Database**: PostgreSQL 15 with pg8000 driver
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Dependency Management**: Poetry

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Docker & Docker Compose
- Poetry

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Medisync
   ```

2. **Start the PostgreSQL database**
   ```bash
   docker-compose up -d
   ```

3. **Install dependencies**
   ```bash
   python -m poetry install
   ```

4. **Run database migrations**
   ```bash
   python -m poetry run alembic upgrade head
   ```

5. **Ingest sample data**
   ```bash
   python -m poetry run python src/ingestion/pipeline.py
   ```

6. **Start the API server**
   ```bash
   python -m poetry run uvicorn src.api.main:app --reload --port 8080
   ```

   API will be available at: `http://127.0.0.1:8080`
   
   Interactive docs: `http://127.0.0.1:8080/docs`

## 📡 API Endpoints

### Create Patient
```http
POST /patients
Content-Type: application/json

{
  "mrn": "MRN-001",
  "first_name": "Alice",
  "last_name": "Smith",
  "dob": "1985-04-12"
}
```

### Create Lab Result
```http
POST /labs
Content-Type: application/json

{
  "patient_id": "uuid-here",
  "lab_code": "GLU",
  "lab_name": "Glucose",
  "result_value": 120.5,
  "result_unit": "mg/dL",
  "collected_at": "2025-11-24T10:30:00"
}
```

### Get Patient Labs
```http
GET /patients/{patient_id}/labs
```

### Get Patients by Clinical Pillar
```http
GET /pillars/{pillar}/patients
```
Example: `/pillars/Cardiac/patients` returns all patients with cardiac-related notes

## 🗄️ Database Configuration

**Connection Details:**
- Host: `localhost`
- Port: `5432`
- Database: `medisync`
- User: `medisync_admin`
- Password: `secure_dev_password`

## 📊 Data Ingestion Pipeline

The ingestion pipeline (`src/ingestion/pipeline.py`) demonstrates:
- CSV-based patient data loading
- UPSERT operations on unique MRN
- Automatic tagging based on clinical note content
- Keyword detection (diabetes, hypertension, urgent care scenarios)

**Run the pipeline:**
```bash
python -m poetry run python src/ingestion/pipeline.py
```

## 🔧 Development

### Create a new migration
```bash
python -m poetry run alembic revision --autogenerate -m "Description"
```

### Apply migrations
```bash
python -m poetry run alembic upgrade head
```

### Rollback migration
```bash
python -m poetry run alembic downgrade -1
```

### Database Access
```bash
docker exec -it medisync_db psql -U medisync_admin medisync
```

## 📁 Project Structure

```
Medisync/
├── alembic/                 # Database migrations
│   └── versions/
├── src/
│   ├── api/                 # FastAPI application
│   │   ├── main.py         # API endpoints
│   │   └── schemas.py      # Pydantic models
│   ├── database/
│   │   └── models.py       # SQLAlchemy models
│   └── ingestion/
│       └── pipeline.py     # Data ingestion logic
├── docker-compose.yml       # PostgreSQL container config
├── pyproject.toml          # Poetry dependencies
└── alembic.ini             # Alembic configuration
```

## 🎯 Key Features

- **Unique Patient Identification**: MRN-based uniqueness constraints
- **Automatic Lab Flagging**: Business logic to flag abnormal results
- **Intelligent Tagging**: NLP-style keyword detection in clinical notes
- **Complex Queries**: Join-based queries across patients, notes, and tags
- **RESTful API**: Standard HTTP methods with proper status codes
- **Type Safety**: Pydantic validation for all inputs
- **Database Migrations**: Version-controlled schema changes

## 🔐 Security Notes

⚠️ **Development Mode**: Current credentials are for development only. In production:
- Use environment variables for secrets
- Enable SSL/TLS for database connections
- Implement authentication/authorization
- Add rate limiting and input sanitization
