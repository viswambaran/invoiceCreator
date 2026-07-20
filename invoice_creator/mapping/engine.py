from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd

from invoice_creator.models.invoice import (
    Invoice,
    InvoiceLine,
)


class MappingError(Exception):
    pass


class MappingEngine:
    def __init__(
        self,
        mapping: dict,
        rules: dict,
        *,
        invoice_date: date | None = None,
        vat_rate: Decimal = Decimal("20"),
        default_units: Decimal | None = None,
        include_zero_lines: bool = True,
    ) -> None:
        self.mapping = mapping
        self.rules = rules
        self.invoice_date = (
            invoice_date or date.today()
        )
        self.vat_rate = self._to_decimal(
            vat_rate
        )
        self.include_zero_lines = (
            include_zero_lines
        )

        if default_units is None:
            self.default_units = (
                self._read_mapped_units()
            )
        else:
            self.default_units = (
                self._to_decimal(
                    default_units
                )
            )

    def build_invoices(
        self,
        rows: list[dict],
    ) -> list[Invoice]:
        invoices: list[Invoice] = []

        for row_id, row in enumerate(
            rows,
            start=1,
        ):
            invoices.append(
                self.build_invoice(
                    row=row,
                    row_id=row_id,
                )
            )

        return invoices

    def build_invoice(
        self,
        row: dict,
        row_id: int,
    ) -> Invoice:
        invoice_lines = (
            self.build_lines_from_row(row)
        )

        net_amount = self._money(
            sum(
                (
                    line.net
                    for line in invoice_lines
                ),
                Decimal("0"),
            )
        )

        vat = self._money(
            net_amount
            * (
                self.vat_rate
                / Decimal("100")
            )
        )

        invoice_total = self._money(
            net_amount + vat
        )

        return Invoice(
            row_id=row_id,
            invoice_no=self.get_invoice_value(
                row,
                "invoice_no",
            ),
            invoice_date=self.invoice_date,
            service_user=self.get_invoice_value(
                row,
                "service_user",
            ),
            assessor=self.get_invoice_value(
                row,
                "assessor",
            ),
            lines=invoice_lines,
            net_amount=net_amount,
            vat=vat,
            invoice_total=invoice_total,
        )

    def build_lines_from_row(
        self,
        row: dict,
    ) -> list[InvoiceLine]:
        lines: list[InvoiceLine] = []

        charge_rules = (
            self.rules
            .get("invoice_lines", {})
            .get("charge_types", [])
        )

        for rule in charge_rules:
            source_column = rule.get(
                "source_column"
            )

            description = str(
                rule.get(
                    "description",
                    source_column or "Charge",
                )
            ).strip()

            if not source_column:
                raise MappingError(
                    "A charge rule is missing "
                    "'source_column'."
                )

            rate = self._to_decimal(
                row.get(source_column)
            )

            if (
                not self.include_zero_lines
                and rate == Decimal("0")
            ):
                continue

            units = self.default_units

            lines.append(
                InvoiceLine(
                    description=description,
                    units=units,
                    rate=self._money(rate),
                    net=self._money(
                        units * rate
                    ),
                )
            )

        return lines

    def get_invoice_value(
        self,
        row: dict,
        field: str,
    ) -> str:
        try:
            field_mapping = (
                self.mapping["invoice"][field]
            )
        except KeyError as exc:
            raise MappingError(
                f"Missing mapping for invoice "
                f"field '{field}'."
            ) from exc

        mapping_type = field_mapping.get(
            "type"
        )

        mapping_value = field_mapping.get(
            "value"
        )

        if mapping_type == "column":
            return self._clean_text(
                row.get(mapping_value)
            )

        if mapping_type == "constant":
            return self._clean_text(
                mapping_value
            )

        raise MappingError(
            f"Unsupported mapping type "
            f"{mapping_type!r} for '{field}'."
        )

    def _read_mapped_units(
        self,
    ) -> Decimal:
        try:
            units_mapping = (
                self.mapping
                ["invoice_lines"]
                ["units"]
            )
        except KeyError:
            return Decimal("1")

        mapping_type = units_mapping.get(
            "type"
        )

        if mapping_type != "constant":
            raise MappingError(
                "Only constant unit mappings "
                "are currently supported."
            )

        return self._to_decimal(
            units_mapping.get("value", 1)
        )

    @staticmethod
    def _clean_text(
        value: Any,
    ) -> str:
        if value is None:
            return ""

        try:
            if pd.isna(value):
                return ""
        except (TypeError, ValueError):
            pass

        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))

        return str(value).strip()

    @staticmethod
    def _to_decimal(
        value: Any,
    ) -> Decimal:
        if value is None:
            return Decimal("0")

        try:
            if pd.isna(value):
                return Decimal("0")
        except (TypeError, ValueError):
            pass

        if isinstance(value, Decimal):
            return value

        if isinstance(value, str):
            cleaned = (
                value.strip()
                .replace("£", "")
                .replace(",", "")
            )

            if not cleaned:
                return Decimal("0")

            value = cleaned

        try:
            return Decimal(str(value))
        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ) as exc:
            raise MappingError(
                f"Could not convert "
                f"{value!r} into a number."
            ) from exc

    @staticmethod
    def _money(
        value: Decimal,
    ) -> Decimal:
        return value.quantize(
            Decimal("0.01")
        )