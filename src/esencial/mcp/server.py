"""MCP Server for Isapre Esencial reimbursements."""

import io
from typing import Literal

import pdfplumber
from mcp.server.fastmcp import FastMCP

from esencial.auth.login import login
from esencial.auth.session import clear_session
from esencial.client.api import EsencialClient
from esencial.client.refunds import RefundsClient
from esencial.mcp.messages import ABOUT, AUTH_FAILED, AUTH_SUCCESS, LOGOUT_SUCCESS

mcp = FastMCP(name="esencial-reembolsos")


@mcp.tool()
def about() -> str:
    """Return information about this MCP server."""
    return ABOUT


@mcp.tool()
def auth() -> str:
    """Open Chrome for the user to log in to Isapre Esencial."""
    return AUTH_SUCCESS if login() else AUTH_FAILED


@mcp.tool()
def logout() -> str:
    """Delete the locally saved session."""
    clear_session()
    return LOGOUT_SUCCESS


@mcp.tool()
def list_refunds(
    status: Literal["active", "resolved"] = "active",
    page: int = 1,
    per_page: int = 10,
) -> dict:
    """List the affiliate's refund requests.

    Args:
        status: "active" (in progress) or "resolved" (accepted/rejected).
        page: Page number (from 1).
        per_page: Results per page (max 50).

    Returns:
        Pagination info plus the list of refund requests with their files.
    """
    api_status = {"active": "ACTIVO", "resolved": "RESUELTO"}[status]

    with EsencialClient.ensure_session() as client:
        rc = RefundsClient(client)
        result = rc.fetch(status=api_status, page=page, per_page=per_page)

    return {
        "pagination": result["pagination"],
        "items": [item.model_dump() for item in result["items"]],
    }


@mcp.tool()
def refund_detail(folio: int, settlement_folio: str) -> list[dict]:
    """Get the full detail of a resolved refund.

    Args:
        folio: Case folio (from list_refunds).
        settlement_folio: Settlement folio (from list_refunds for RESUELTO requests).

    Returns:
        A list of reimbursement detail entries — one per benefit line in the case.
    """
    with EsencialClient.ensure_session() as client:
        rc = RefundsClient(client)
        details = rc.detail(folio, settlement_folio)

    return [d.model_dump() for d in details]


@mcp.tool()
def list_documents() -> dict:
    """List documents (invoices/receipts) attached to refund requests.

    Returns:
        A dict with `active` and `resolved` lists of document references.
    """
    with EsencialClient.ensure_session() as client:
        rc = RefundsClient(client)
        active_page = rc.fetch(status="ACTIVO", per_page=50)
        resolved_page = rc.fetch(status="RESUELTO", per_page=50)

    return {
        "active": _extract_client_documents(active_page["items"]),
        "resolved": _extract_client_documents(resolved_page["items"]),
    }


@mcp.tool()
def read_active_documents() -> dict:
    """Download and extract text from all PDFs uploaded in ACTIVE refund requests.

    Useful to identify SII folio, provider RUT and amount inside each document,
    e.g. to detect duplicates before uploading a new invoice.

    Returns:
        A dict with `documents` (list of extracted PDF texts) and `errors`.
    """
    with EsencialClient.ensure_session() as client:
        rc = RefundsClient(client)

        first_page = rc.fetch(status="ACTIVO", per_page=50, page=1)
        items = list(first_page["items"])
        total_pages = first_page["pagination"]["totalPages"]
        for p in range(2, total_pages + 1):
            items += rc.fetch(status="ACTIVO", per_page=50, page=p)["items"]

        documents = []
        errors = []
        for item in items:
            for doc in (f for f in item.files if f.uploader_type == "CLIENTE"):
                try:
                    pdf_bytes = client.download_file(doc.document_id)
                    documents.append({
                        "request_folio": item.folio,
                        "filename": doc.filename,
                        "sent_at": item.sent_at,
                        "text": _pdf_to_text(pdf_bytes),
                    })
                except Exception as e:
                    errors.append({
                        "request_folio": item.folio,
                        "filename": doc.filename,
                        "error": str(e),
                    })

    return {"documents": documents, "errors": errors}


@mcp.tool()
def refunds_summary() -> dict:
    """Totals for active and resolved refunds."""
    with EsencialClient.ensure_session() as client:
        rc = RefundsClient(client)
        active = rc.fetch(status="ACTIVO", per_page=1)
        resolved = rc.fetch(status="RESUELTO", per_page=1)

    return {
        "active_total": active["pagination"]["total"],
        "resolved_total": resolved["pagination"]["total"],
    }


def _extract_client_documents(items) -> list[dict]:
    """Flatten refund items into a list of client-uploaded documents."""
    return [
        {
            "request_folio": item.folio,
            "request_status": item.status,
            "sent_at": item.sent_at,
            "filename": doc.filename,
            "file_type": doc.file_type,
        }
        for item in items
        for doc in item.files
        if doc.uploader_type == "CLIENTE"
    ]


def _pdf_to_text(pdf_bytes: bytes) -> str:
    """Extract text from a PDF and return it as a string."""
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages).strip()


def main() -> None:
    mcp.run()
