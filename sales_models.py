from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from purchase_models import PurchaseVoucher

# Sales voucher has the same XML structure as purchase voucher.
# The difference is in the data: VCHTYPE="Sales", party is a debtor, etc.
SalesVoucher = PurchaseVoucher


class CreateSalesPayload(BaseModel):
    company_name: str
    username: Optional[str] = None
    password: Optional[str] = None
    vouchers: list[SalesVoucher]
