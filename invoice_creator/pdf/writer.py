import json
from pathlib import Path

import fitz

from invoice_creator.pdf.table_writer import (
    write_lines
)

from invoice_creator.pdf.text_writer import (
    write_metadata_value
)


class InvoicePDFWriter:

    TOTAL_FIELDS = {
        "Net Amount",
        "VAT",
        "Invoice Total"
    }

    def __init__(
        self,
        template_path,
        fields_path,
        table_path
    ):
        self.template_path = Path(
            template_path
        )

        self.fields_path = Path(
            fields_path
        )

        self.table_path = Path(
            table_path
        )

        self.fields = self._load_json(
            self.fields_path
        )

        self.table = self._load_json(
            self.table_path
        )

        self._validate_metadata()


    @staticmethod
    def _load_json(
        path: Path
    ) -> dict:

        if not path.exists():
            raise FileNotFoundError(
                f"Metadata file does not exist: {path}"
            )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(
                file
            )


    def _validate_metadata(
        self
    ) -> None:

        required_fields = {
            "Invoice No",
            "Service User",
            "Assessor",
            "Net Amount",
            "VAT",
            "Invoice Total"
        }

        available_fields = set(
            self.fields
            .get(
                "fields",
                {}
            )
            .keys()
        )

        missing_fields = (
            required_fields
            - available_fields
        )

        if missing_fields:
            raise ValueError(
                "Template field metadata is incomplete. "
                f"Missing: {', '.join(sorted(missing_fields))}"
            )

        required_columns = {
            "description",
            "units",
            "rate",
            "net"
        }

        available_columns = set(
            self.table
            .get(
                "invoice_lines",
                {}
            )
            .get(
                "columns",
                {}
            )
            .keys()
        )

        missing_columns = (
            required_columns
            - available_columns
        )

        if missing_columns:
            raise ValueError(
                "Table metadata is incomplete. "
                f"Missing: {', '.join(sorted(missing_columns))}"
            )


    def generate(
        self,
        invoice,
        output_path
    ) -> None:

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if not self.template_path.exists():
            raise FileNotFoundError(
                f"PDF template does not exist: "
                f"{self.template_path}"
            )

        document = fitz.open(
            self.template_path
        )

        try:
            page = document[0]

            self.write_invoice_fields(
                page,
                invoice
            )

            write_lines(
                page=page,
                invoice=invoice,
                table_metadata=self.table
            )

            document.save(
                output_path,
                garbage=4,
                deflate=True
            )

        finally:
            document.close()


    def write_invoice_fields(
        self,
        page,
        invoice
    ) -> None:

        fields = self.fields[
            "fields"
        ]

        values = {
            "Invoice No":
                invoice.invoice_no,

            "Service User":
                invoice.service_user,

            "Assessor":
                invoice.assessor,

            "Net Amount":
                self._format_money(
                    invoice.net_amount
                ),

            "VAT":
                self._format_money(
                    invoice.vat
                ),

            "Invoice Total":
                self._format_money(
                    invoice.invoice_total
                )
        }

        for field_name, value in values.items():

            is_total = (
                field_name
                in self.TOTAL_FIELDS
            )

            write_metadata_value(
                page=page,
                value=value,
                metadata=fields[field_name],
                align=(
                    "right"
                    if is_total
                    else "left"
                ),
                padding=(
                    3
                    if is_total
                    else 0
                )
            )


    @staticmethod
    def _format_money(
        value
    ) -> str:

        return f"{float(value):.2f}"