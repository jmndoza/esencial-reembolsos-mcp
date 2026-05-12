"""Client for Esencial refunds API endpoints."""

from typing import Any

from esencial.auth.session import load_session
from esencial.client import endpoints
from esencial.client.api import EsencialClient
from esencial.client.refunds.models import (
    RefundRequest,
    ReimbursementDetail,
)


class RefundsClient:

    def __init__(self, client: EsencialClient | None = None):
        self._client = client or EsencialClient()
        session = load_session()
        self._rut = session.local_storage.affiliate_rut if session else None

    @property
    def affiliate_rut(self) -> str:
        if not self._rut:
            raise ValueError("RUT not available. Run the `auth` tool first.")
        return self._rut

    def fetch(
        self,
        status: str = "ACTIVO",
        page: int = 1,
        per_page: int = 20,
    ) -> dict[str, Any]:
        """Fetch refunds. `status` can be 'ACTIVO' or 'RESUELTO'.

        Returns {'items': list[RefundRequest], 'pagination': {...}}.
        """
        r = self._client.get(endpoints.REFUNDS_LIST, params={
            "rut": self.affiliate_rut,
            "status": status,
            "page": page,
            "per_page": per_page,
            "as_affiliate": "true",
        })
        data = r.json()
        return {
            "items": [RefundRequest.model_validate(item) for item in data.get("items", [])],
            "pagination": data.get("pagination", {}),
        }

    def detail(
        self,
        case_folio: int,
        settlement_folio: str | int,
    ) -> list[ReimbursementDetail]:
        """Detail of a resolved refund. May return multiple lines (one per benefit)."""
        r = self._client.get(
            endpoints.REFUNDS_REIMBURSEMENT_DETAIL.format(case_folio=case_folio),
            params={
                "affiliateRut": self.affiliate_rut,
                "settlementFolio": str(settlement_folio),
            },
        )
        return [ReimbursementDetail.model_validate(d) for d in r.json()]
