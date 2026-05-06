from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from models import models as db_models
from schemas import schemas as api_schemas
from typing import List

router = APIRouter()

@router.post("/companies", response_model=api_schemas.Company)
def create_company(company_in: api_schemas.CompanyCreate, db: Session = Depends(get_db)):
    # Check if slug exists
    db_company = db.query(db_models.Company).filter(db_models.Company.slug == company_in.slug).first()
    if db_company:
        raise HTTPException(status_code=400, detail="Company slug already exists")
    
    new_company = db_models.Company(
        name=company_in.name,
        slug=company_in.slug,
        is_active=company_in.is_active,
        hubtel_client_id=company_in.hubtel_client_id,
        hubtel_client_secret=company_in.hubtel_client_secret,
        brevo_api_key=company_in.brevo_api_key,
        brevo_sender_email=company_in.brevo_sender_email,
        brevo_sender_name=company_in.brevo_sender_name
    )
    db.add(new_company)
    db.commit()
    db.refresh(new_company)
    return new_company

@router.get("/companies", response_model=List[api_schemas.Company])
def get_companies(db: Session = Depends(get_db)):
    return db.query(db_models.Company).all()

@router.get("/companies/{company_id}", response_model=api_schemas.Company)
def get_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(db_models.Company).filter(db_models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@router.put("/companies/{company_id}", response_model=api_schemas.Company)
def update_company(company_id: int, company_in: api_schemas.CompanyUpdate, db: Session = Depends(get_db)):
    company = db.query(db_models.Company).filter(db_models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    update_data = company_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    db.add(company)
    db.commit()
    db.refresh(company)
    return company
 
@router.delete("/companies/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    company = db.query(db_models.Company).filter(db_models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    db.delete(company)
    db.commit()
    return {"detail": "Company and all associated data cleared"}

from core.security import get_pin_hash

@router.get("/stats", response_model=api_schemas.GlobalStats)
def get_global_stats(db: Session = Depends(get_db)):
    total_companies = db.query(db_models.Company).count()
    total_branches = db.query(db_models.Branch).count()
    total_sms = db.query(db_models.SMSLog).count()
    total_emails = db.query(db_models.EmailLog).count()
    total_customers = db.query(db_models.Customer).count()
    
    return {
        "total_companies": total_companies,
        "total_branches": total_branches,
        "total_sms": total_sms,
        "total_emails": total_emails,
        "total_customers": total_customers
    }

@router.get("/logs/sms", response_model=api_schemas.PaginatedAdminSMSLog)
def get_global_sms_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    query = (
        db.query(db_models.SMSLog, db_models.Company.name, db_models.Branch.name)
        .join(db_models.Branch, db_models.SMSLog.branch_id == db_models.Branch.id)
        .join(db_models.Company, db_models.Branch.company_id == db_models.Company.id)
    )
    
    total = query.count()
    results = query.order_by(db_models.SMSLog.created_at.desc()).offset(skip).limit(limit).all()
    
    items = []
    for log, company_name, branch_name in results:
        log_dict = {c.name: getattr(log, c.name) for c in log.__table__.columns}
        log_dict["company_name"] = company_name
        log_dict["branch_name"] = branch_name
        items.append(log_dict)
        
    return {"items": items, "total": total}

@router.get("/logs/email", response_model=api_schemas.PaginatedAdminEmailLog)
def get_global_email_logs(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    query = (
        db.query(db_models.EmailLog, db_models.Company.name, db_models.Branch.name)
        .join(db_models.Branch, db_models.EmailLog.branch_id == db_models.Branch.id)
        .join(db_models.Company, db_models.Branch.company_id == db_models.Company.id)
    )
    
    total = query.count()
    results = query.order_by(db_models.EmailLog.created_at.desc()).offset(skip).limit(limit).all()
    
    items = []
    for log, company_name, branch_name in results:
        log_dict = {c.name: getattr(log, c.name) for c in log.__table__.columns}
        log_dict["company_name"] = company_name
        log_dict["branch_name"] = branch_name
        items.append(log_dict)
        
    return {"items": items, "total": total}

@router.post("/companies/{company_id}/branches", response_model=api_schemas.Branch)
def create_company_branch(company_id: int, branch_in: api_schemas.BranchCreate, db: Session = Depends(get_db)):
    # Check if company exists
    company = db.query(db_models.Company).filter(db_models.Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    # Check if branch code exists
    existing = db.query(db_models.Branch).filter(db_models.Branch.branch_code == branch_in.branch_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Branch code already exists")
        
    new_branch = db_models.Branch(
        name=branch_in.name,
        branch_code=branch_in.branch_code,
        pin=get_pin_hash(branch_in.pin),
        company_id=company_id
    )
    db.add(new_branch)
    db.commit()
    db.refresh(new_branch)
    return new_branch

@router.get("/public/companies/{slug}/branches", response_model=List[api_schemas.Branch])
def get_company_branches(slug: str, db: Session = Depends(get_db)):
    company = db.query(db_models.Company).filter(db_models.Company.slug == slug).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company.branches
