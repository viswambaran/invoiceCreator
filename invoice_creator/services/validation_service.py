from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from invoice_creator.models.invoice import (
    Invoice,
)


Severity = Literal[
    "warning",
    "error",
]


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
        return " | ".join(
            issue.message
            for issue in self.issues
        )


def validate_invoices(
    invoices: list[Invoice],
) -> list[InvoiceValidation]:
    invoice_numbers = [
        invoice.invoice_no.strip()
        for invoice in invoices
        if invoice.invoice_no.strip()
    ]

    duplicate_counts = Counter(
        invoice_numbers
    )

    results: list[
        InvoiceValidation
    ] = []

    for invoice in invoices:
        issues: list[
            ValidationIssue
        ] = []

        invoice_no = (
            invoice.invoice_no.strip()
        )

        def add_issue(
            severity: Severity,
            field: str,
            message: str,
        ) -> None:
            issues.append(
                ValidationIssue(
                    row_id=invoice.row_id,
                    invoice_no=invoice_no,
                    severity=severity,
                    field=field,
                    message=message,
                )
            )

        if not invoice_no:
            add_issue(
                "error",
                "Invoice No",
                "Invoice number is missing.",
            )

        if not invoice.service_user.strip():
            add_issue(
                "error",
                "Service User",
                "Service user is missing.",
            )

        if not invoice.assessor.strip():
            add_issue(
                "warning",
                "Assessor",
                "Assessor is blank.",
            )

        if (
            invoice_no
            and duplicate_counts[
                invoice_no
            ] > 1
        ):
            add_issue(
                "error",
                "Invoice No",
                "Duplicate invoice number.",
            )

        if len(invoice_no) > 24:
            add_issue(
                "warning",
                "Invoice No",
                "Invoice number is unusually long.",
            )

        if len(
            invoice.service_user
        ) > 55:
            add_issue(
                "warning",
                "Service User",
                "Service user text may require "
                "font shrinking.",
            )

        if len(invoice.assessor) > 45:
            add_issue(
                "warning",
                "Assessor",
                "Assessor text may require "
                "font shrinking.",
            )

        if invoice.invoice_date is None:
            add_issue(
                "error",
                "Invoice Date",
                "Invoice date is missing.",
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
                "Invoice contains more than "
                "two charge lines.",
            )

        calculated_net = sum(
            (
                line.net
                for line in invoice.lines
            ),
            Decimal("0"),
        ).quantize(
            Decimal("0.01")
        )

        if (
            calculated_net
            != invoice.net_amount
        ):
            add_issue(
                "error",
                "Net Amount",
                "Net amount does not match "
                "the invoice lines.",
            )

        for line in invoice.lines:
            if line.units < Decimal("0"):
                add_issue(
                    "error",
                    line.description,
                    f"{line.description} has "
                    "negative units.",
                )

            if line.rate < Decimal("0"):
                add_issue(
                    "error",
                    line.description,
                    f"{line.description} has "
                    "a negative rate.",
                )

            if line.rate > Decimal(
                "10000"
            ):
                add_issue(
                    "warning",
                    line.description,
                    f"{line.description} rate "
                    "is unusually large.",
                )

            expected_line_net = (
                line.units * line.rate
            ).quantize(
                Decimal("0.01")
            )

            if expected_line_net != line.net:
                add_issue(
                    "error",
                    line.description,
                    f"{line.description} net "
                    "does not match units "
                    "multiplied by rate.",
                )

        expected_total = (
            invoice.net_amount
            + invoice.vat
        ).quantize(
            Decimal("0.01")
        )

        if (
            expected_total
            != invoice.invoice_total
        ):
            add_issue(
                "error",
                "Invoice Total",
                "Invoice total does not "
                "match net plus VAT.",
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
                invoice_no=invoice_no,
                status=status,
                issues=issues,
            )
        )

    return results