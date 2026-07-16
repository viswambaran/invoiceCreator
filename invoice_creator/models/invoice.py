from dataclasses import dataclass
from typing import List


@dataclass
class InvoiceLine:

    description: str

    units: float

    rate: float

    net: float



@dataclass
class Invoice:

    invoice_no: str

    service_user: str

    assessor: str

    lines: List[InvoiceLine]

    net_amount: float

    vat: float

    invoice_total: float