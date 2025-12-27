"""Export API endpoints."""

import io
import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from src.models.export import ExportFormat, ExportRequest
from src.services.export.csv_exporter import CSVExporter
from src.services.export.json_exporter import JSONExporter
from src.services.export.excel_exporter import ExcelExporter
from src.utils.exceptions import raise_validation_error
from src.utils.filename import generate_filename

logger = logging.getLogger(__name__)
router = APIRouter(tags=["exports"])


@router.post("/databases/{db_name}/export")
async def export_query_results(db_name: str, request: ExportRequest) -> StreamingResponse:
    """
    Export query results in the specified format.

    Args:
        db_name: Database name (used for filename generation)
        request: Export request with format and query results

    Returns:
        StreamingResponse with exported file

    Raises:
        HTTPException: If format is invalid or export fails
    """
    # Validate row count (max 100,000 rows)
    row_count = request.query_results.get("rowCount", 0)
    max_rows = 100_000
    
    if row_count > max_rows:
        raise_validation_error(
            f"Export limited to {max_rows:,} rows. "
            f"Your query returned {row_count:,} rows. "
            f"Please add a LIMIT clause to your query."
        )

    # Extract columns and rows from query results
    columns = request.query_results.get("columns", [])
    rows = request.query_results.get("rows", [])
    
    # Generate filename based on format
    filename = generate_filename(db_name, request.format)
    
    # Export based on format
    try:
        if request.format == ExportFormat.CSV:
            exporter = CSVExporter()
            file_bytes = exporter.export(columns, rows)
            media_type = "text/csv; charset=utf-8"
            
            logger.info(
                f"CSV export successful: db='{db_name}', "
                f"rows={row_count}, filename='{filename}'"
            )
            
            # Stream the file to client
            return StreamingResponse(
                io.BytesIO(file_bytes),
                media_type=media_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        elif request.format == ExportFormat.JSON:
            exporter = JSONExporter()
            file_bytes = exporter.export(columns, rows)
            media_type = "application/json; charset=utf-8"
            
            logger.info(
                f"JSON export successful: db='{db_name}', "
                f"rows={row_count}, filename='{filename}'"
            )
            
            return StreamingResponse(
                io.BytesIO(file_bytes),
                media_type=media_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        elif request.format == ExportFormat.EXCEL:
            exporter = ExcelExporter()
            file_bytes = exporter.export(columns, rows)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            logger.info(
                f"Excel export successful: db='{db_name}', "
                f"rows={row_count}, filename='{filename}'"
            )
            
            return StreamingResponse(
                io.BytesIO(file_bytes),
                media_type=media_type,
                headers={
                    "Content-Disposition": f'attachment; filename="{filename}"'
                }
            )
        else:
            # Invalid format (should not happen due to Pydantic validation)
            logger.warning(f"Invalid export format: {request.format}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid export format: {request.format}"
            )
    except HTTPException:
        # Re-raise HTTP exceptions (like 501 Not Implemented)
        raise
    except Exception as e:
        logger.error(f"Export failed: db='{db_name}', format={request.format}, error={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export generation failed: {str(e)}"
        )
