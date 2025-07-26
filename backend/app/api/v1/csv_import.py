from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlmodel.ext.asyncio.session import AsyncSession
import structlog

from app.database import get_session
from app.services.csv_import_service import CSVImportService
from app.schemas.csv_import import ImportResultSchema

logger = structlog.get_logger()
router = APIRouter()


@router.post("/upload", response_model=ImportResultSchema)
async def upload_csv_file(
    file: UploadFile = File(..., description="CSV file to import"),
    session: AsyncSession = Depends(get_session)
) -> ImportResultSchema:
    """
    Upload and process CSV1 file for invoice aging data import.
    
    The CSV file should contain the following columns (CSV1 format):
    - Client ID: Unique client identifier
    - Client Name: Account name  
    - Email Address: Contact email address (optional)
    - Invoice #: Unique invoice number
    - Invoice Date: Invoice date (YYYY-MM-DD)
    - Invoice Amount: Original invoice amount (formatted as $XX,XXX.XX)
    - Current (0-30): Amount outstanding 0-30 days
    - 31-60 Days: Amount outstanding 31-60 days
    - 61-90 Days: Amount outstanding 61-90 days
    - 91-120 Days: Amount outstanding 91-120 days
    - 120+ Days: Amount outstanding over 120 days
    - Total Outstanding: Current total outstanding amount
    
    Additional fields are computed automatically:
    - snapshot_date: Set to current upload date
    - Contact name: Extracted from email or account name
    - phone: Set to null (not provided in CSV1)
    - is_billing_contact: Set to true
    
    Returns:
        ImportResultSchema with import results and statistics
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    # Check file size (10MB limit)
    max_size = 10 * 1024 * 1024  # 10MB
    file_size = 0
    
    try:
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size allowed is {max_size // (1024*1024)}MB"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        # Decode content
        try:
            csv_content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                csv_content = content.decode('utf-8-sig')  # Handle BOM
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File must be UTF-8 encoded"
                )
        
        # Initialize service
        import_service = CSVImportService(session)
        
        # Validate CSV format first
        is_valid, validation_errors = await import_service.validate_csv_format(csv_content)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid CSV format: {'; '.join(validation_errors)}"
            )
        
        logger.info("Starting CSV import", 
                   filename=file.filename, 
                   file_size=file_size)
        
        # Process the CSV
        result = await import_service.import_csv_data(csv_content)
        
        # Log results
        logger.info("CSV import completed",
                   filename=file.filename,
                   success=result.success,
                   total_rows=result.total_rows,
                   successful_rows=result.successful_rows,
                   failed_rows=result.failed_rows,
                   processing_time=result.processing_time_seconds)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error during CSV import", 
                    filename=file.filename,
                    error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.get("/template")
async def download_csv_template():
    """
    Download a CSV template file with the required column headers.
    
    Returns:
        CSV template file for download
    """
    from fastapi.responses import Response
    
    # CSV1 template with headers and sample data
    csv_template = """Client ID,Client Name,Email Address,Invoice #,Invoice Date,Invoice Amount,Current (0-30),31-60 Days,61-90 Days,91-120 Days,120+ Days,Total Outstanding
C001001,Bright Horizon Manufacturing,accounting@brighthorizonmfg.com,INV-2024-1001,2025-07-13,"$23,264.00","$23,264.00",$0.00,$0.00,$0.00,$0.00,"$23,264.00"
C001002,Legacy Manufacturing Inc,,INV-2024-1002,2024-12-31,"$23,605.00",$0.00,$0.00,$0.00,$0.00,"$23,605.00","$23,605.00"
C001003,Sunrise Retail Co.,billing@sunriseretail.com,INV-2024-1003,2025-07-02,"$3,904.00","$3,904.00",$0.00,$0.00,$0.00,$0.00,"$3,904.00\""""
    
    return Response(
        content=csv_template,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=invoice_aging_template.csv"}
    )