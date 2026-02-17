"""Models for invoice creation (Sales/Purchase vouchers with ISINVOICE=Yes)."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, model_validator

from purchase_models import PurchaseVoucher


class InvoiceVoucher(PurchaseVoucher):
    """A purchase/sales voucher that is always an invoice."""

    @model_validator(mode="after")
    def _force_invoice(self) -> "InvoiceVoucher":
        self.is_invoice = True
        return self


class CreateInvoicePayload(BaseModel):
    company_name: str
    username: Optional[str] = None
    password: Optional[str] = None
    invoice_type: Literal["Sales", "Purchase"] = "Sales"
    vouchers: list[InvoiceVoucher]

    @model_validator(mode="after")
    def _set_voucher_type(self) -> "CreateInvoicePayload":
        for v in self.vouchers:
            v.voucher_type_name = self.invoice_type
        return self
