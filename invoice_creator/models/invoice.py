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
    service_user: str = ""
    assessor: str = ""


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
    invoice_date: date = field(default_factory=date.today)
    comments: str = ""
    page_no: int = 1
    generation_mode: str = "single"

    @property
    def total_vat(self) -> Decimal:
        return self.vat

    @property
    def total(self) -> Decimal:
        return self.invoice_total

    @property
    def is_grouped(self) -> bool:
        return self.generation_mode == "grouped"

    def as_dict(self) -> dict[str, Any]:
        return {
            "row_id": self.row_id,
            "invoice_no": self.invoice_no,
            "invoice_date": self.invoice_date,
            "service_user": self.service_user,
            "assessor": self.assessor,
            "comments": self.comments,
            "page_no": self.page_no,
            "generation_mode": self.generation_mode,
            "lines": self.lines,
            "net_amount": self.net_amount,
            "vat": self.vat,
            "invoice_total": self.invoice_total,
        }
