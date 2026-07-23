from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import BinaryIO, Literal

import pandas as pd

from invoice_creator.importers.excel import ExcelImporter
from invoice_creator.mapping.engine import MappingEngine, MappingError
from invoice_creator.models.invoice import Invoice, InvoiceLine
from invoice_creator.services.app_paths import SHARED_DIRECTORY


GenerationMode = Literal["single", "grouped"]

DEFAULT_MAPPING_PATH = SHARED_DIRECTORY / "mapping.json"
DEFAULT_RULES_PATH = SHARED_DIRECTORY / "mapping_rules.json"

GROUPED_LINE_DESCRIPTION = "Assessment"


class InvoiceBuildError(Exception):
    pass


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise InvoiceBuildError(
            f"Required configuration file was not found: {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise InvoiceBuildError(
            f"Configuration file contains invalid JSON: {path}"
        ) from exc


def load_mapping() -> dict:
    return _load_json(DEFAULT_MAPPING_PATH)


def load_mapping_rules() -> dict:
    return _load_json(DEFAULT_RULES_PATH)


def load_workbook(
    uploaded_file: BinaryIO | bytes,
    sheet_name: str | int = 0,
) -> pd.DataFrame:
    try:
        importer = ExcelImporter(
            source=uploaded_file,
            sheet_name=sheet_name,
        )
        return importer.load_dataframe()
    except Exception as exc:
        raise InvoiceBuildError(
            f"The Excel workbook could not be read: {exc}"
        ) from exc


def get_sheet_names(uploaded_file: BinaryIO | bytes) -> list[str]:
    try:
        importer = ExcelImporter(source=uploaded_file)
        return importer.get_sheet_names()
    except Exception as exc:
        raise InvoiceBuildError(
            f"The Excel workbook could not be opened: {exc}"
        ) from exc


def required_columns() -> list[str]:
    mapping = load_mapping()
    rules = load_mapping_rules()
    columns: list[str] = []

    for field_mapping in mapping.get("invoice", {}).values():
        if field_mapping.get("type") == "column":
            value = field_mapping.get("value")
            if value:
                columns.append(str(value).strip())

    charge_rules = (
        rules.get("invoice_lines", {}).get("charge_types", [])
    )

    for rule in charge_rules:
        source_column = rule.get("source_column")
        if source_column:
            columns.append(str(source_column).strip())

    return list(dict.fromkeys(columns))


def missing_columns(dataframe: pd.DataFrame) -> list[str]:
    available_columns = {
        str(column).strip() for column in dataframe.columns
    }
    return [
        column
        for column in required_columns()
        if column not in available_columns
    ]


def _validate_generation_mode(generation_mode: str) -> GenerationMode:
    mode = str(generation_mode).strip().lower()
    if mode not in {"single", "grouped"}:
        raise InvoiceBuildError(
            f"Unsupported generation mode: {generation_mode!r}."
        )
    return mode  # type: ignore[return-value]


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def _build_grouped_invoice(
    *,
    engine: MappingEngine,
    rows: list[dict],
    vat_rate: Decimal,
    include_zero_lines: bool,
) -> Invoice:
    """
    Build one invoice containing one table line per spreadsheet row.

    Each row becomes:
        Description = Assessment
        Units       = 1
        Rate        = Charge + QA Charge
        Net         = Charge + QA Charge
    """
    if not rows:
        raise InvoiceBuildError(
            "The workbook did not contain any invoice rows."
        )

    first_row = rows[0]
    grouped_lines: list[InvoiceLine] = []

    for row in rows:
        source_lines = engine.build_lines_from_row(row)

        combined_rate = _money(
            sum(
                (line.rate for line in source_lines),
                Decimal("0"),
            )
        )

        if (
            not include_zero_lines
            and combined_rate == Decimal("0.00")
        ):
            continue

        grouped_lines.append(
            InvoiceLine(
                description=GROUPED_LINE_DESCRIPTION,
                units=Decimal("1"),
                rate=combined_rate,
                net=combined_rate,
                service_user=engine.get_invoice_value(
                    row,
                    "service_user",
                ),
                assessor=engine.get_invoice_value(
                    row,
                    "assessor",
                ),
            )
        )

    net_amount = _money(
        sum(
            (line.net for line in grouped_lines),
            Decimal("0"),
        )
    )

    decimal_vat_rate = Decimal(str(vat_rate))
    vat = _money(
        net_amount * (decimal_vat_rate / Decimal("100"))
    )
    invoice_total = _money(net_amount + vat)

    return Invoice(
        row_id=1,
        invoice_no=engine.get_invoice_value(first_row, "invoice_no"),
        invoice_date=engine.invoice_date,
        service_user=engine.get_invoice_value(first_row, "service_user"),
        assessor=engine.get_invoice_value(first_row, "assessor"),
        comments=engine.get_comments(first_row),
        page_no=1,
        lines=grouped_lines,
        net_amount=net_amount,
        vat=vat,
        invoice_total=invoice_total,
        generation_mode="grouped",
    )


def build_invoices(
    dataframe: pd.DataFrame,
    invoice_date: date,
    vat_rate: Decimal = Decimal("20"),
    default_units: Decimal = Decimal("1"),
    include_zero_lines: bool = True,
    generation_mode: GenerationMode = "single",
) -> list[Invoice]:
    missing = missing_columns(dataframe)

    if missing:
        raise InvoiceBuildError(
            "The workbook is missing these required columns: "
            + ", ".join(missing)
        )

    rows = dataframe.to_dict(orient="records")
    mode = _validate_generation_mode(generation_mode)

    try:
        engine = MappingEngine(
            mapping=load_mapping(),
            rules=load_mapping_rules(),
            invoice_date=invoice_date,
            vat_rate=vat_rate,
            default_units=default_units,
            include_zero_lines=include_zero_lines,
        )

        if mode == "single":
            return engine.build_invoices(rows)

        return [
            _build_grouped_invoice(
                engine=engine,
                rows=rows,
                vat_rate=vat_rate,
                include_zero_lines=include_zero_lines,
            )
        ]

    except MappingError as exc:
        raise InvoiceBuildError(str(exc)) from exc
