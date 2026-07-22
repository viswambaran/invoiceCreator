from __future__ import annotations

import json
from pathlib import Path

import fitz

from invoice_creator.pdf.table_writer import write_lines
from invoice_creator.pdf.text_writer import write_value


class InvoicePDFWriter:
    REQUIRED_FIELDS = {
        "Invoice No",
        "Invoice Date",
        "Service User",
        "Assessor",
        "Comments",
        "Net Amount",
        "VAT",
        "Invoice Total",
    }

    REQUIRED_COLUMNS = {
        "description",
        "units",
        "rate",
        "net",
    }

    def __init__(
        self,
        template_path,
        fields_path,
        table_path,
    ):
        self.template_path = Path(template_path)
        self.fields = self._load_json(Path(fields_path))
        self.table = self._load_json(Path(table_path))
        self._validate_metadata()

    @staticmethod
    def _load_json(path: Path) -> dict:
        if not path.exists():
            raise FileNotFoundError(
                f"Metadata file does not exist: {path}"
            )

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _validate_metadata(self) -> None:
        available_fields = set(
            self.fields.get("fields", {}).keys()
        )
        missing_fields = (
            self.REQUIRED_FIELDS - available_fields
        )

        if missing_fields:
            raise ValueError(
                "Missing field metadata: "
                + ", ".join(sorted(missing_fields))
            )

        available_columns = set(
            self.table
            .get("invoice_lines", {})
            .get("columns", {})
            .keys()
        )
        missing_columns = (
            self.REQUIRED_COLUMNS - available_columns
        )

        if missing_columns:
            raise ValueError(
                "Missing table metadata: "
                + ", ".join(sorted(missing_columns))
            )

    def generate(
        self,
        invoice,
        output_path,
    ) -> None:
        output_path = Path(output_path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = fitz.open(self.template_path)

        try:
            page = document[0]

            self.write_invoice_fields(
                page,
                invoice,
            )

            write_lines(
                page=page,
                invoice=invoice,
                table_metadata=self.table,
            )

            document.save(
                output_path,
                garbage=4,
                deflate=True,
            )
        finally:
            document.close()

    def write_invoice_fields(
        self,
        page,
        invoice,
    ) -> None:
        fields = self.fields["fields"]

        write_value(
            page=page,
            value=invoice.invoice_no,
            metadata=fields["Invoice No"],
            padding=4,
        )

        write_value(
            page=page,
            value=self._format_date(
                invoice.invoice_date
            ),
            metadata=fields["Invoice Date"],
            padding=4,
        )

        write_value(
            page=page,
            value=invoice.service_user,
            metadata=fields["Service User"],
            padding=7,
        )

        write_value(
            page=page,
            value=invoice.assessor,
            metadata=fields["Assessor"],
            padding=7,
        )

        write_value(
            page=page,
            value=invoice.comments,
            metadata=fields["Comments"],
            padding=7,
        )

        totals = {
            "Net Amount": self._format_money(
                invoice.net_amount
            ),
            "VAT": self._format_money(
                invoice.vat
            ),
            "Invoice Total": self._format_money(
                invoice.invoice_total
            ),
        }

        for field_name, value in totals.items():
            write_value(
                page=page,
                value=value,
                metadata=fields[field_name],
                align="right",
                padding=8,
            )

    @staticmethod
    def _format_money(value) -> str:
        return f"{float(value):.2f}"

    @staticmethod
    def _format_date(value) -> str:
        if value is None:
            return ""

        if hasattr(value, "strftime"):
            return value.strftime("%d.%m.%Y")

        return str(value)
