from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from invoice_creator.models.app_invoice import AppInvoice


Severity = Literal["warning", "error"]


@dataclass
class ValidationIssue:
    row_id: int
    invoice_no: str
    severity: Severity
    field: str
    message: str


@dataclass
class InvoiceValidation:
    row_id: int
    invoice_no: str
    status: str
    issues: list[ValidationIssue]

    @property
    def warning_count(self) -> int:
        return sum(
            issue.severity == "warning"
            for issue in self.issues
        )

    @property
    def error_count(self) -> int:
        return sum(
            issue.severity == "error"
            for issue in self.issues
        )

    @property
    def summary(self) -> str:
        if not self.issues:
            return ""

        return " | ".join(
            issue.message
            for issue in self.issues
        )


def validate_invoices(
    invoices: list[AppInvoice],
) -> list[InvoiceValidation]:
    invoice_numbers = [
        invoice.invoice_no
        for invoice in invoices
        if invoice.invoice_no
    ]

    duplicate_counts = Counter(invoice_numbers)

    results: list[InvoiceValidation] = []

    for invoice in invoices:
        issues: list[ValidationIssue] = []

        def add_issue(
            severity: Severity,
            field: str,
            message: str,
        ) -> None:
            issues.append(
                ValidationIssue(
                    row_id=invoice.row_id,
                    invoice_no=invoice.invoice_no,
                    severity=severity,
                    field=field,
                    message=message,
                )
            )

        if not invoice.invoice_no:
            add_issue(
                "error",
                "Invoice No",
                "Invoice number is missing.",
            )

        if not invoice.service_user:
            add_issue(
                "error",
                "Service User",
                "Service user is missing.",
            )

        if not invoice.assessor:
            add_issue(
                "warning",
                "Assessor",
                "Assessor is blank.",
            )

        if invoice.invoice_no and (
            duplicate_counts[invoice.invoice_no] > 1
        ):
            add_issue(
                "error",
                "Invoice No",
                "Duplicate invoice number.",
            )

        if len(invoice.invoice_no) > 24:
            add_issue(
                "warning",
                "Invoice No",
                "Invoice number is unusually long.",
            )

        if len(invoice.service_user) > 55:
            add_issue(
                "warning",
                "Service User",
                "Service user text may require font shrinking.",
            )

        if len(invoice.assessor) > 45:
            add_issue(
                "warning",
                "Assessor",
                "Assessor text may require font shrinking.",
            )

        if not invoice.lines:
            add_issue(
                "error",
                "Lines",
                "Invoice has no charge lines.",
            )

        if len(invoice.lines) > 2:
            add_issue(
                "warning",
                "Lines",
                "Invoice contains more lines than expected.",
            )

        for line in invoice.lines:
            if line.rate < Decimal("0"):
                add_issue(
                    "error",
                    line.description,
                    f"{line.description} has a negative rate.",
                )

            if line.rate > Decimal("10000"):
                add_issue(
                    "warning",
                    line.description,
                    f"{line.description} rate is unusually large.",
                )

        expected_total = (
            invoice.net_amount + invoice.vat
        ).quantize(Decimal("0.01"))

        if expected_total != invoice.invoice_total:
            add_issue(
                "error",
                "Invoice Total",
                "Invoice total does not match net plus VAT.",
            )

        if any(
            issue.severity == "error"
            for issue in issues
        ):
            status = "Blocked"
        elif issues:
            status = "Warning"
        else:
            status = "Ready"

        results.append(
            InvoiceValidation(
                row_id=invoice.row_id,
                invoice_no=invoice.invoice_no,
                status=status,
                issues=issues,
            )
        )

    return results