from typing import List, Tuple, Union
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import SessionLocal
from models.models_loans import LoanPublic, QueuePublic
from operations.operations_loans import list_loans, borrow_work, return_loan, list_queue
from services.security import get_current_user

router = APIRouter()

async def get_session():
    async with SessionLocal() as s:
        yield s

@router.get("/", response_model=List[LoanPublic])
async def all_loans(session: AsyncSession = Depends(get_session)):
    return await list_loans(session)

@router.post("/borrow", response_model=Union[LoanPublic, QueuePublic])
async def borrow(user_id: int, work_id: int, session: AsyncSession = Depends(get_session), user=Depends(get_current_user)):
    if user.id != user_id and user.role != "admin":
        raise HTTPException(403, "Not allowed")
    status, payload = await borrow_work(session, user_id, work_id)
    return payload

@router.post("/return/{loan_id}", response_model=LoanPublic)
async def return_book(loan_id: int, session: AsyncSession = Depends(get_session), user=Depends(get_current_user)):
    loan = await return_loan(session, loan_id)
    if not loan:
        raise HTTPException(404, "Loan not found or not active")
    return loan

@router.get("/queue/{work_id}", response_model=List[QueuePublic])
async def queue(work_id: int, session: AsyncSession = Depends(get_session)):
    return await list_queue(session, work_id)
