"""Models for the refunds domain."""

from pydantic import AliasPath, BaseModel, ConfigDict, Field, model_validator


class RefundFile(BaseModel):
    """An attached file in a refund request."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    document_id: str = Field(alias="documentId")
    file_type: str
    filename: str
    sharepoint_url: str | None = None
    uploader_type: str = ""
    size: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _default_document_id_from_id(cls, values):
        """Fall back to `id` when the response omits `documentId`."""
        if isinstance(values, dict) and not values.get("documentId"):
            values["documentId"] = values.get("id", "")
        return values


class RefundFolio(BaseModel):
    """A settlement folio attached to a refund request."""

    folio: str
    status: str
    payment_status: str | None = None


class RefundEvent(BaseModel):
    """A status change event in a refund request."""

    payload: str
    created_at: str


class RefundRequest(BaseModel):
    """Item from the refund list."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    folio: int
    status: str
    beneficiary_name: str = ""
    beneficiary_rut: str = ""
    refund_type: str = Field(default="", validation_alias=AliasPath("refund", "refund_type"))
    sent_at: str = ""
    created_at: str = ""
    files: list[RefundFile] = Field(default_factory=list, alias="requestFiles")
    folios: list[RefundFolio] = Field(default_factory=list)
    events: list[RefundEvent] = Field(default_factory=list)

    @property
    def settlement_folio(self) -> str | None:
        return self.folios[0].folio if self.folios else None

    @property
    def is_resolved(self) -> bool:
        return bool(self.folios)


class ReimbursementDetail(BaseModel):
    """Full detail of a resolved reimbursement (a single benefit line)."""

    case_folio: int
    settlement_folio: int
    reimbursement_status: str
    request_date: str
    estimated_payment_date: str | None = None
    rejection_reason: str | None = None

    beneficiary_name: str
    beneficiary_rut: str

    provider_name: str
    provider_rut: str

    main_physician_name: str | None = None
    main_physician_rut: str | None = None

    tax_document_type: str | None = None
    tax_document_number: int | None = None

    benefit_date: str
    benefit_description: str
    benefit_code: str | None = None
    benefit_quantity: int = 1

    per_benefit_cost: int
    base_bonus_amount: int
    additional_bonus_amount: int = 0
    copayment: int

    plan_code: str | None = None
    plan_type: str | None = None
    coverage_type: str | None = None
    benefit_type: str | None = None

    bank_name: str | None = None
    bank_account_type: str | None = None
    bank_account_number: str | None = None

    comptroller_name: str | None = None
    entry_channel: str | None = None
    notes: str | None = None
