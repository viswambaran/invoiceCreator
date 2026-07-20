from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import BinaryIO

import pandas as pd

from invoice_creator.importers.excel import (
    ExcelImporter,
)
from invoice_creator.mapping.engine import (
    MappingEngine,
    MappingError,
)
from invoice_creator.models.invoice import (
    Invoice,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

DEFAULT_MAPPING_PATH = (
    PROJECT_ROOT
    / "templates"
    / "mapping.json"
)

DEFAULT_RULES_PATH = (
    PROJECT_ROOT
    / "templates"
    / "mapping_rules.json"
)


class InvoiceBuildError(Exception):
    pass


def _load_json(
    path: Path,
) -> dict:
    if not path.exists():
        raise InvoiceBuildError(
            f"Required configuration file "
            f"was not found: {path}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise InvoiceBuildError(
            f"Configuration file contains "
            f"invalid JSON: {path}"
        ) from exc


def load_mapping() -> dict:
    return _load_json(
        DEFAULT_MAPPING_PATH
    )


def load_mapping_rules() -> dict:
    return _load_json(
        DEFAULT_RULES_PATH
    )


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
            "The Excel workbook could not "
            f"be read: {exc}"
        ) from exc


def get_sheet_names(
    uploaded_file: BinaryIO | bytes,
) -> list[str]:
    try:
        importer = ExcelImporter(
            source=uploaded_file
        )

        return importer.get_sheet_names()

    except Exception as exc:
        raise InvoiceBuildError(
            "The Excel workbook could not "
            f"be opened: {exc}"
        ) from exc


def required_columns() -> list[str]:
    mapping = load_mapping()
    rules = load_mapping_rules()

    columns: list[str] = []

    invoice_mapping = mapping.get(
        "invoice",
        {},
    )

    for field_mapping in (
        invoice_mapping.values()
    ):
        if (
            field_mapping.get("type")
            == "column"
        ):
            value = field_mapping.get(
                "value"
            )

            if value:
                columns.append(
                    str(value).strip()
                )

    charge_rules = (
        rules
        .get("invoice_lines", {})
        .get("charge_types", [])
    )

    for rule in charge_rules:
        source_column = rule.get(
            "source_column"
        )

        if source_column:
            columns.append(
                str(source_column).strip()
            )

    return list(
        dict.fromkeys(columns)
    )


def missing_columns(
    dataframe: pd.DataFrame,
) -> list[str]:
    available_columns = {
        str(column).strip()
        for column in dataframe.columns
    }

    return [
        column
        for column in required_columns()
        if column not in available_columns
    ]


def build_invoices(
    dataframe: pd.DataFrame,
    invoice_date: date,
    vat_rate: Decimal = Decimal("20"),
    default_units: Decimal = Decimal("1"),
    include_zero_lines: bool = True,
) -> list[Invoice]:
    missing = missing_columns(
        dataframe
    )

    if missing:
        raise InvoiceBuildError(
            "The workbook is missing these "
            "required columns: "
            + ", ".join(missing)
        )

    rows = dataframe.to_dict(
        orient="records"
    )

    try:
        engine = MappingEngine(
            mapping=load_mapping(),
            rules=load_mapping_rules(),
            invoice_date=invoice_date,
            vat_rate=vat_rate,
            default_units=default_units,
            include_zero_lines=(
                include_zero_lines
            ),
        )

        return engine.build_invoices(
            rows
        )

    except MappingError as exc:
        raise InvoiceBuildError(
            str(exc)
        ) from exc