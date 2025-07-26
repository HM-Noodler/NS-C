from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_
from app.database import get_session
from app.models.account import Account
from app.models.invoice import Invoice
from app.models.invoice_aging_snapshot import InvoiceAgingSnapshot
from app.models.contact import Contact
from typing import Dict, Any, List
import asyncio
from datetime import datetime, timedelta

router = APIRouter(tags=["Dashboard"])

@router.get("/dashboard/metrics")
async def get_dashboard_metrics(
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get dashboard KPI metrics from real data."""
    
    try:
        # Get basic counts
        total_accounts = await session.scalar(select(func.count(Account.id))) or 0
        total_invoices = await session.scalar(select(func.count(Invoice.id))) or 0
        
        # Simple total outstanding calculation (fallback for when tables are empty)
        total_outstanding = 0
        if total_invoices > 0:
            try:
                # Try to get total from aging snapshots first
                snapshots_total = await session.scalar(
                    select(func.count(InvoiceAgingSnapshot.id))
                )
                if snapshots_total and snapshots_total > 0:
                    # Use string conversion for safety with PostgreSQL
                    outstanding_query = select(
                        func.sum(
                            func.cast(InvoiceAgingSnapshot.days_0_30, "decimal") +
                            func.cast(InvoiceAgingSnapshot.days_31_60, "decimal") +
                            func.cast(InvoiceAgingSnapshot.days_61_90, "decimal") +
                            func.cast(InvoiceAgingSnapshot.days_91_120, "decimal") +
                            func.cast(InvoiceAgingSnapshot.days_over_120, "decimal")
                        )
                    ).select_from(InvoiceAgingSnapshot)
                    total_outstanding = await session.scalar(outstanding_query) or 0
                else:
                    # Fallback to invoice amounts if no snapshots
                    invoice_total = await session.scalar(
                        select(func.sum(func.cast(Invoice.invoice_amount, "decimal")))
                        .select_from(Invoice)
                    )
                    total_outstanding = invoice_total or 0
            except Exception as e:
                print(f"Error calculating outstanding amounts: {e}")
                total_outstanding = 0
        
        return {
            "successful_collections": 0,  # Will be implemented with payment tracking
            "successful_collections_amount": 0,
            "active_email_campaigns": 0,  # Will be based on sent emails
            "active_email_campaigns_amount": 0,
            "email_escalation_queue": int(total_accounts),
            "email_escalation_queue_amount": float(total_outstanding),
            "total_email_communications": 0  # Will be tracked with email sending
        }
        
    except Exception as e:
        print(f"Error in get_dashboard_metrics: {e}")
        # Return zeros if there's any error
        return {
            "successful_collections": 0,
            "successful_collections_amount": 0,
            "active_email_campaigns": 0,
            "active_email_campaigns_amount": 0,
            "email_escalation_queue": 0,
            "email_escalation_queue_amount": 0,
            "total_email_communications": 0
        }

@router.get("/dashboard/recent-activity")
async def get_recent_activity(
    session: AsyncSession = Depends(get_session)
) -> List[Dict[str, Any]]:
    """Get recent email activity from real data."""
    
    # TODO: Implement email activity tracking
    # For now return empty array until email tracking is implemented
    return []

@router.get("/dashboard/escalation-queue") 
async def get_escalation_queue(
    session: AsyncSession = Depends(get_session)
) -> List[Dict[str, Any]]:
    """Get current escalation queue items from real data."""
    
    try:
        # First check if we have any data
        account_count = await session.scalar(select(func.count(Account.id))) or 0
        if account_count == 0:
            return []
        
        # Simple query for accounts with contacts
        query = select(
            Account.id,
            Account.client_id,
            Account.account_name,
            Contact.email_address
        ).select_from(
            Account
        ).outerjoin(
            Contact, Account.id == Contact.account_id
        ).where(
            and_(
                Contact.email_address.isnot(None),
                Contact.is_billing_contact == True
            )
        )
        
        result = await session.execute(query)
        items = []
        
        for row in result:
            # Get invoice count for this account
            invoice_count = await session.scalar(
                select(func.count(Invoice.id))
                .where(Invoice.account_id == row.id)
            ) or 0
            
            # Simple amount calculation 
            total_amount = 0
            if invoice_count > 0:
                try:
                    amount_result = await session.scalar(
                        select(func.sum(func.cast(Invoice.total_outstanding, "decimal")))
                        .where(Invoice.account_id == row.id)
                    )
                    total_amount = float(amount_result or 0)
                except:
                    total_amount = 0
            
            if total_amount > 0:  # Only include if there's an outstanding amount
                items.append({
                    "id": str(row.id),
                    "company_name": row.account_name,
                    "amount": total_amount,
                    "invoice_count": invoice_count,
                    "days_in_queue": 0,  # Will be calculated properly later
                    "last_contact": None,
                    "contact_email": row.email_address,
                    "status": "pending"
                })
        
        return items[:10]  # Limit to first 10 items
        
    except Exception as e:
        print(f"Error in get_escalation_queue: {e}")
        return []

@router.get("/dashboard/receivables")
async def get_receivables_data(
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get receivables summary from real data."""
    
    try:
        # Check if we have any invoice data
        invoice_count = await session.scalar(select(func.count(Invoice.id))) or 0
        if invoice_count == 0:
            return {
                "paid_collections": 0,
                "paid_percentage": 0,
                "outstanding_receivables": 0,
                "outstanding_percentage": 0,
                "total_amount": 0
            }
        
        # Simple calculation using invoice amounts
        total_invoice_amount = 0
        total_outstanding = 0
        
        try:
            # Get total invoice amounts
            invoice_total = await session.scalar(
                select(func.sum(func.cast(Invoice.invoice_amount, "decimal")))
                .select_from(Invoice)
            )
            total_invoice_amount = float(invoice_total or 0)
            
            # Get total outstanding amounts
            outstanding_total = await session.scalar(
                select(func.sum(func.cast(Invoice.total_outstanding, "decimal")))
                .select_from(Invoice)
            )
            total_outstanding = float(outstanding_total or 0)
            
        except Exception as e:
            print(f"Error calculating receivables: {e}")
            total_invoice_amount = 0
            total_outstanding = 0
        
        paid_collections = max(0, total_invoice_amount - total_outstanding)
        total_amount = max(total_outstanding, total_invoice_amount)
        
        paid_percentage = (paid_collections / total_amount * 100) if total_amount > 0 else 0
        outstanding_percentage = (total_outstanding / total_amount * 100) if total_amount > 0 else 0
        
        return {
            "paid_collections": paid_collections,
            "paid_percentage": round(paid_percentage),
            "outstanding_receivables": total_outstanding,
            "outstanding_percentage": round(outstanding_percentage),
            "total_amount": total_amount
        }
        
    except Exception as e:
        print(f"Error in get_receivables_data: {e}")
        return {
            "paid_collections": 0,
            "paid_percentage": 0,
            "outstanding_receivables": 0,
            "outstanding_percentage": 0,
            "total_amount": 0
        }

@router.get("/dashboard/activity-summary")
async def get_activity_summary(
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get activity summary from real data."""
    
    # TODO: Implement email activity tracking
    # For now return zeros until email tracking is implemented
    return {
        "concierge_emails": 0,
        "concierge_emails_percentage": 0,
        "total_activity": 0,
        "recent_emails": 0
    }

@router.get("/dashboard")
async def get_full_dashboard_data(
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
    """Get complete dashboard data in one call."""
    
    # Run all queries concurrently for better performance
    metrics_task = get_dashboard_metrics(session)
    recent_activity_task = get_recent_activity(session)
    escalation_queue_task = get_escalation_queue(session)
    receivables_task = get_receivables_data(session)
    activity_summary_task = get_activity_summary(session)
    
    metrics, recent_activity, escalation_queue, receivables, activity_summary = await asyncio.gather(
        metrics_task,
        recent_activity_task,
        escalation_queue_task,
        receivables_task,
        activity_summary_task
    )
    
    return {
        "metrics": metrics,
        "recent_activity": recent_activity,
        "escalation_queue": escalation_queue,
        "receivables": receivables,
        "activity_summary": activity_summary
    }