from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass
class InvoiceLine:
    description: str
    units: Decimal
    rate: Decimal
    net: Decimal


@dataclass
class Invoice:
    invoice_no: str
    service_user: str
    assessor: str
    lines: list[InvoiceLine]
    net_amount: Decimal
    vat: Decimal
    invoice_total: Decimal

    row_id: int = 0
    invoice_date: date = field(
        default_factory=date.today
    )

    @property
    def total_vat(self) -> Decimal:
        return self.vat

    @property
    def total(self) -> Decimal:
        return self.invoice_total

    def as_dict(self) -> dict[str, Any]:
        return {
            "row_id": self.row_id,
            "invoice_no": self.invoice_no,
            "invoice_date": self.invoice_date,
            "service_user": self.service_user,
            "assessor": self.assessor,
            "lines": self.lines,
            "net_amount": self.net_amount,
            "vat": self.vat,
            "invoice_total": self.invoice_total,
        }