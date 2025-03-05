from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid
import logging

# Create the FastAPI app with metadata.
app = FastAPI(title="ApexSuite Soil API", version="0.2.0")

# Setup CORS middleware.
origins = [
    "http://localhost",
    "http://localhost:3000",
    # Add additional origins as needed.
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory database simulation.
companies_db = {}

# Data models.
class OnboardingData(BaseModel):
    company_name: str
    data_sample: str

class Company(BaseModel):
    id: str
    company_name: str
    data_sample: str
    inferred_data_type: str
    confidence: float
    onboarded_at: datetime

@app.get("/")
async def read_root():
    return {"message": "Welcome to the ApexSuite Soil API!"}

@app.post("/onboard", response_model=Company)
async def onboard(data: OnboardingData, background_tasks: BackgroundTasks):
    """
    Onboards a new company by accepting a data sample.
    A background task simulates external API calls to deduce data type.
    """
    company_id = str(uuid.uuid4())

    # Create a new company record with pending status.
    new_company = Company(
        id=company_id,
        company_name=data.company_name,
        data_sample=data.data_sample,
        inferred_data_type="Pending",
        confidence=0.0,
        onboarded_at=datetime.utcnow()
    )
    companies_db[company_id] = new_company.dict()

    # Background task to process onboarding.
    def process_onboarding(company_id: str, data: OnboardingData):
        # Simulate processing delay and external API calls (e.g., Grok, ChatGPT).
        import time
        time.sleep(2)
        deduced_data = {
            "inferred_data_type": "Accounting Data",
            "confidence": 0.95
        }
        companies_db[company_id].update(deduced_data)
        logger.info(f"Completed onboarding for company {company_id}")

    background_tasks.add_task(process_onboarding, company_id, data)
    return new_company

@app.get("/companies", response_model=List[Company])
async def list_companies():
    """
    Lists all onboarded companies.
    """
    return list(companies_db.values())

@app.get("/companies/{company_id}", response_model=Company)
async def get_company(company_id: str):
    """
    Returns details for a specific company.
    """
    if company_id not in companies_db:
        raise HTTPException(status_code=404, detail="Company not found")
    return companies_db[company_id]

@app.delete("/companies/{company_id}", response_model=dict)
async def delete_company(company_id: str):
    """
    Deletes a company from the system.
    """
    if company_id in companies_db:
        del companies_db[company_id]
        return {"message": "Company deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Company not found")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)