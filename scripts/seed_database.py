"""
Seed the ATS database with parsed resumes and synthetic job descriptions.

Usage:
    python -m scripts.seed_database
"""
import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import settings
from src.database.models import Base, Candidate, JobRole
from src.database.session import engine, SessionLocal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Synthetic job descriptions for 8 roles matching our resume categories
SYNTHETIC_JOBS = [
    {
        "title": "Senior Software Engineer",
        "department": "Engineering",
        "description": (
            "We are looking for a Senior Software Engineer to design and build scalable "
            "backend services. You will work with Python, Java, or Go to develop microservices, "
            "REST APIs, and data pipelines. Experience with cloud platforms (AWS/GCP/Azure), "
            "Docker, Kubernetes, and CI/CD is essential. You'll mentor junior engineers and "
            "participate in architecture decisions."
        ),
        "requirements": [
            "5+ years software engineering experience",
            "Proficiency in Python, Java, or Go",
            "Experience with cloud platforms (AWS, GCP, or Azure)",
            "Strong understanding of distributed systems",
            "Experience with Docker and Kubernetes",
            "Bachelor's degree in Computer Science or equivalent",
        ],
        "min_experience_years": 5.0,
        "location": "Remote",
        "salary_range": "$140,000 - $190,000",
    },
    {
        "title": "Data Scientist",
        "department": "Data & Analytics",
        "description": (
            "Join our data science team to build predictive models and derive insights from "
            "large datasets. You will apply machine learning, statistical analysis, and deep "
            "learning techniques to solve business problems. Proficiency in Python, SQL, and "
            "tools like TensorFlow, PyTorch, or scikit-learn is required. Experience with NLP "
            "and computer vision is a plus."
        ),
        "requirements": [
            "3+ years in data science or machine learning",
            "Strong Python and SQL skills",
            "Experience with ML frameworks (TensorFlow, PyTorch, scikit-learn)",
            "Statistics and probability knowledge",
            "Experience with data visualization tools",
            "Master's degree in a quantitative field preferred",
        ],
        "min_experience_years": 3.0,
        "location": "New York, NY",
        "salary_range": "$120,000 - $170,000",
    },
    {
        "title": "Registered Nurse (RN)",
        "department": "Healthcare",
        "description": (
            "Seeking a compassionate Registered Nurse to provide patient care in our medical "
            "facility. Responsibilities include patient assessment, administering medications, "
            "coordinating with physicians, and maintaining medical records. Must have an active "
            "RN license and experience in a clinical setting."
        ),
        "requirements": [
            "Active RN license",
            "2+ years clinical nursing experience",
            "BLS/ACLS certification",
            "Strong communication and patient care skills",
            "Experience with electronic health records (EHR)",
            "BSN preferred",
        ],
        "min_experience_years": 2.0,
        "location": "Chicago, IL",
        "salary_range": "$65,000 - $90,000",
    },
    {
        "title": "Financial Analyst",
        "department": "Finance",
        "description": (
            "We need a Financial Analyst to support budgeting, forecasting, and financial "
            "reporting. You will analyze financial data, build models, and present insights "
            "to stakeholders. Proficiency in Excel, financial modeling, and ERP systems "
            "is required. CPA or CFA certification is a plus."
        ),
        "requirements": [
            "3+ years in financial analysis or accounting",
            "Advanced Excel and financial modeling skills",
            "Experience with ERP systems (SAP, Oracle)",
            "Strong analytical and communication skills",
            "Bachelor's degree in Finance or Accounting",
            "CPA or CFA preferred",
        ],
        "min_experience_years": 3.0,
        "location": "Dallas, TX",
        "salary_range": "$75,000 - $110,000",
    },
    {
        "title": "Sales Manager",
        "department": "Sales",
        "description": (
            "Looking for a results-driven Sales Manager to lead our sales team and drive "
            "revenue growth. You will develop sales strategies, manage key accounts, and "
            "coach sales representatives. Experience with CRM tools like Salesforce, "
            "strong negotiation skills, and a track record of meeting quotas is essential."
        ),
        "requirements": [
            "5+ years in B2B sales with management experience",
            "Proven track record of exceeding sales targets",
            "Experience with Salesforce or similar CRM",
            "Strong leadership and communication skills",
            "Bachelor's degree in Business or related field",
        ],
        "min_experience_years": 5.0,
        "location": "San Francisco, CA",
        "salary_range": "$100,000 - $150,000 + commission",
    },
    {
        "title": "HR Business Partner",
        "department": "Human Resources",
        "description": (
            "Seeking an HR Business Partner to align HR strategy with business objectives. "
            "You will handle employee relations, talent development, performance management, "
            "and organizational design. Experience with HRIS systems, labor law, and change "
            "management is required."
        ),
        "requirements": [
            "4+ years HR experience in a business partner role",
            "Knowledge of employment law and regulations",
            "Experience with HRIS systems (Workday, SAP SuccessFactors)",
            "Strong interpersonal and conflict resolution skills",
            "Bachelor's degree in HR, Business, or related field",
            "SHRM-CP or PHR certification preferred",
        ],
        "min_experience_years": 4.0,
        "location": "Austin, TX",
        "salary_range": "$85,000 - $120,000",
    },
    {
        "title": "Digital Marketing Specialist",
        "department": "Marketing",
        "description": (
            "Join our marketing team to plan and execute digital campaigns across SEO, SEM, "
            "social media, and email marketing. You will analyze campaign performance, manage "
            "ad budgets, and create content strategies. Experience with Google Analytics, "
            "Google Ads, and marketing automation tools is required."
        ),
        "requirements": [
            "2+ years in digital marketing",
            "Experience with Google Analytics and Google Ads",
            "SEO/SEM knowledge",
            "Experience with marketing automation (HubSpot, Marketo)",
            "Strong copywriting and analytical skills",
            "Bachelor's degree in Marketing or Communications",
        ],
        "min_experience_years": 2.0,
        "location": "Remote",
        "salary_range": "$60,000 - $90,000",
    },
    {
        "title": "Civil Engineer",
        "department": "Engineering",
        "description": (
            "We are hiring a Civil Engineer to design and oversee construction projects "
            "including roads, bridges, and buildings. You will prepare engineering plans, "
            "conduct site inspections, and ensure compliance with safety codes. Proficiency "
            "in AutoCAD, project management, and structural analysis is required."
        ),
        "requirements": [
            "3+ years in civil engineering",
            "PE license preferred",
            "Proficiency in AutoCAD and engineering design software",
            "Knowledge of building codes and safety regulations",
            "Strong project management skills",
            "Bachelor's degree in Civil Engineering",
        ],
        "min_experience_years": 3.0,
        "location": "Denver, CO",
        "salary_range": "$80,000 - $120,000",
    },
]


def seed_candidates(session):
    """Load parsed resumes into candidates table."""
    parsed_dir = settings.parsed_dir
    if not parsed_dir.exists():
        logger.error(f"Parsed resumes directory not found: {parsed_dir}")
        return 0

    count = 0
    for json_file in sorted(parsed_dir.rglob("*.json")):
        if json_file.name == "all_resumes.json":
            continue

        data = json.loads(json_file.read_text())

        # Check if already exists
        existing = session.query(Candidate).filter_by(file_name=data["file_name"]).first()
        if existing:
            continue

        candidate = Candidate(
            file_name=data["file_name"],
            category=data["category"],
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            skills=data.get("skills", []),
            experience=data.get("experience", []),
            education=data.get("education", []),
            summary=data.get("summary"),
            total_years_experience=data.get("total_years_experience"),
            raw_text=data.get("raw_text", ""),
        )
        session.add(candidate)
        count += 1

        if count % 100 == 0:
            session.commit()
            logger.info(f"  Inserted {count} candidates...")

    session.commit()
    return count


def seed_job_roles(session):
    """Insert synthetic job descriptions."""
    count = 0
    for job_data in SYNTHETIC_JOBS:
        existing = session.query(JobRole).filter_by(title=job_data["title"]).first()
        if existing:
            continue

        job = JobRole(**job_data)
        session.add(job)
        count += 1

    session.commit()
    return count


def main():
    logger.info("Seeding ATS database...")

    session = SessionLocal()
    try:
        candidate_count = seed_candidates(session)
        logger.info(f"Inserted {candidate_count} new candidates")

        job_count = seed_job_roles(session)
        logger.info(f"Inserted {job_count} new job roles")

        # Print summary
        total_candidates = session.query(Candidate).count()
        total_jobs = session.query(JobRole).count()
        logger.info(f"Database totals — Candidates: {total_candidates}, Job Roles: {total_jobs}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
