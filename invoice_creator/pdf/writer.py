import json
from pathlib import Path

import fitz

from invoice_creator.pdf.table_writer import (
    write_lines,
)

from invoice_creator.pdf.text_writer import (
    write_metadata_value,
)


class InvoicePDFWriter:

    TOTAL_FIELDS = {
        "Net Amount",
        "VAT",
        "Invoice Total",
    }

    REQUIRED_FIELDS = {
        "Invoice No",
        "Service User",
        "Assessor",
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
        path: Path,
    ) -> dict:

        if not path.exists():
            raise FileNotFoundError(
                f"Metadata file does not exist: "
                f"{path}"
            )

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)


    def _validate_metadata(
        self,
    ) -> None:

        available_fields = set(
            self.fields
            .get(
                "fields",
                {},
            )
            .keys()
        )

        missing_fields = (
            self.REQUIRED_FIELDS
            - available_fields
        )

        if missing_fields:
            raise ValueError(
                "Template field metadata is incomplete. "
                "Missing: "
                + ", ".join(
                    sorted(missing_fields)
                )
            )

        available_columns = set(
            self.table
            .get(
                "invoice_lines",
                {},
            )
            .get(
                "columns",
                {},
            )
            .keys()
        )

        missing_columns = (
            self.REQUIRED_COLUMNS
            - available_columns
        )

        if missing_columns:
            raise ValueError(
                "Table metadata is incomplete. "
                "Missing: "
                + ", ".join(
                    sorted(missing_columns)
                )
            )


    def generate(
        self,
        invoice,
        output_path,
    ) -> None:

        output_path = Path(output_path)

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

        values = {
            "Invoice No":
                invoice.invoice_no,

            "Service User":
                invoice.service_user,

            "Assessor":
                invoice.assessor,

            "Net Amount":
                f"{float(invoice.net_amount):.2f}",

            "VAT":
                f"{float(invoice.vat):.2f}",

            "Invoice Total":
                self._format_money(
                    invoice.invoice_total
                ),
        }

        for field_name, value in values.items():
            is_total = (
                field_name in totals
            )

            write_in_area(
                page=page,
                value=value,
                value_rect=metadata["value_rect"],
                write_position=metadata["write_position"],
                font=metadata["font"],
                align=(
                    "right"
                    if is_total
                    else "left"
                ),
                padding=(
                    2
                    if is_total
                    else 0
                ),
                clear_padding_x=(
                    1.5
                    if is_total
                    else 1.25
                ),
                clear_padding_top=0.75,
                clear_padding_bottom=0.5,
            )


    @staticmethod
    def _format_money(
        value
    ) -> str:

        return f"{float(value):.2f}"