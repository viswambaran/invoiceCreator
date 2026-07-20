from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import BinaryIO

import pandas as pd

from invoice_creator.models.app_invoice import (
    AppInvoice,
    AppInvoiceLine,
)


INVOICE_COLUMN = "Invoice No"
SERVICE_USER_COLUMN = "Client Name"
ASSESSOR_COLUMN = "Assessor"
CHARGE_COLUMN = "Charge"
QA_CHARGE_COLUMN = "QA Charge"


class InvoiceBuildError(Exception):
    """Raised when a workbook cannot be converted into invoices."""


def clean_column_name(value: object) -> str:
    return str(value).strip()


def clean_text(value: object) -> str:
    if value is None:
        return ""

    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    return str(value).strip()


def to_decimal(
    value: object,
    *,
    default: Decimal = Decimal("0.00"),
) -> Decimal:
    if value is None:
        return default

    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass

    if isinstance(value, Decimal):
        return value

    if isinstance(value, str):
        value = (
            value.strip()
            .replace("£", "")
            .replace(",", "")
        )

        if not value:
            return default

    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(
            f"Could not convert {value!r} into a number."
        )


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def load_workbook(
    uploaded_file: BinaryIO | bytes,
    sheet_name: str | int = 0,
) -> pd.DataFrame:
    """
    Load an uploaded Excel workbook and clean its column names.
    """

    if isinstance(uploaded_file, bytes):
        source = BytesIO(uploaded_file)
    else:
        source = uploaded_file

    try:
        dataframe = pd.read_excel(
            source,
            sheet_name=sheet_name,
        )
    except Exception as exc:
        raise InvoiceBuildError(
            f"The Excel workbook could not be read: {exc}"
        ) from exc

    dataframe.columns = [
        clean_column_name(column)
        for column in dataframe.columns
    ]

    return dataframe


def get_sheet_names(
    uploaded_file: BinaryIO | bytes,
) -> list[str]:
    if isinstance(uploaded_file, bytes):
        source = BytesIO(uploaded_file)
    else:
        source = uploaded_file

    try:
        workbook = pd.ExcelFile(source)
    except Exception as exc:
        raise InvoiceBuildError(
            f"The Excel workbook could not be opened: {exc}"
        ) from exc

    return list(workbook.sheet_names)


def required_columns() -> list[str]:
    return [
        INVOICE_COLUMN,
        SERVICE_USER_COLUMN,
        ASSESSOR_COLUMN,
        CHARGE_COLUMN,
        QA_CHARGE_COLUMN,
    ]


def missing_columns(
    dataframe: pd.DataFrame,
) -> list[str]:
    return [
        column
        for column in required_columns()
        if column not in dataframe.columns
    ]


def build_invoices(
    dataframe: pd.DataFrame,
    invoice_date: date,
    vat_rate: Decimal = Decimal("20"),
    default_units: Decimal = Decimal("1"),
    include_zero_lines: bool = True,
) -> list[AppInvoice]:
    """
    Build one invoice per Excel row.

    Charge becomes the BIA Assessment line.
    QA Charge becomes the Authorisation line.
    """

    missing = missing_columns(dataframe)

    if missing:
        joined = ", ".join(missing)

        raise InvoiceBuildError(
            "The workbook is missing these required columns: "
            f"{joined}"
        )

    invoices: list[AppInvoice] = []

    vat_multiplier = vat_rate / Decimal("100")

    for row_position, (_, row) in enumerate(
        dataframe.iterrows(),
        start=1,
    ):
        invoice_no = clean_text(
            row.get(INVOICE_COLUMN)
        )

        service_user = clean_text(
            row.get(SERVICE_USER_COLUMN)
        )

        assessor = clean_text(
            row.get(ASSESSOR_COLUMN)
        )

        try:
            charge = money(
                to_decimal(row.get(CHARGE_COLUMN))
            )

            qa_charge = money(
                to_decimal(row.get(QA_CHARGE_COLUMN))
            )
        except ValueError as exc:
            # Keep the invoice available for review and validation.
            # Invalid numeric fields are represented as zero here and
            # separately flagged by validation.
            charge = Decimal("0.00")
            qa_charge = Decimal("0.00")

        lines: list[AppInvoiceLine] = []

        if include_zero_lines or charge != 0:
            lines.append(
                AppInvoiceLine(
                    description="BIA Assessment",
                    units=default_units,
                    rate=charge,
                    net=money(default_units * charge),
                )
            )

        if include_zero_lines or qa_charge != 0:
            lines.append(
                AppInvoiceLine(
                    description="Authorisation",
                    units=default_units,
                    rate=qa_charge,
                    net=money(default_units * qa_charge),
                )
            )

        net_amount = money(
            sum(
                (line.net for line in lines),
                Decimal("0.00"),
            )
        )

        vat = money(
            net_amount * vat_multiplier
        )

        invoice_total = money(
            net_amount + vat
        )

        invoices.append(
            AppInvoice(
                row_id=row_position,
                invoice_no=invoice_no,
                invoice_date=invoice_date,
                service_user=service_user,
                assessor=assessor,
                lines=lines,
                net_amount=net_amount,
                vat=vat,
                invoice_total=invoice_total,
            )
        )

    return invoices