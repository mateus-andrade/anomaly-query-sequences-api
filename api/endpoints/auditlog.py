from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.db import crud
from api.db.database import Base, engine
from api.endpoints.utils import get_db
from api.schemas import schemas

Base.metadata.create_all(bind=engine)


router = APIRouter()


@router.get("/audit-logs/", response_model=List[schemas.AuditLog])
async def read_audit_logs(
    offset: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    audit_logs = crud.get_audit_logs(db, offset=offset, limit=limit)
    return audit_logs


@router.get("/audit-logs/{audit_log_id}", response_model=schemas.AuditLog)
async def read_audit_log(audit_log_id: int, db: Session = Depends(get_db)):
    if (db_audit_log := crud.get_audit_log(db, audit_log_id)) is None:
        raise HTTPException(
            status_code=404, detail=f"Audit log with id:{audit_log_id} not found"
        )
    return db_audit_log


@router.post("/audit-logs/", response_model=schemas.AuditLog)
async def create_audit_log(
    audit_log: schemas.AuditLogCreate, db: Session = Depends(get_db)
):
    if (db_anomaly := crud.get_anomaly(db, audit_log.anomaly_id)) is None:
        raise HTTPException(
            status_code=400,
            detail=f"Does not exist an anomaly with id: {audit_log.anomaly_id}",
        )

    if db_anomaly.session != audit_log.session:
        raise HTTPException(
            status_code=400,
            detail="Audit log does not have same session of referenced anomaly",
        )

    return crud.create_audit_log(db, audit_log)
