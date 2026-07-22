from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from invoice_creator.models.invoice_profile import InvoiceProfile


@dataclass(slots=True)
class GenerationJob:
    profile: InvoiceProfile | None = None

    workbook_name: str | None = None
    workbook_bytes: bytes | None = None

    worksheet: str | None = None

    invoice_date: date = date.today()

    vat_rate: Decimal = Decimal("20")

    default_units: Decimal = Decimal("1")

    include_zero_lines: bool = True