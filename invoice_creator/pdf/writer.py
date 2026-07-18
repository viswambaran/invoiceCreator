import json
from pathlib import Path

import fitz

from invoice_creator.pdf.table_writer import write_lines
from invoice_creator.pdf.text_writer import write_in_area


class InvoicePDFWriter:

    def __init__(
        self,
        template_path,
        fields_path,
        table_path
    ):
        self.template_path = template_path

        with open(
            fields_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.fields = json.load(file)

        with open(
            table_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.table = json.load(file)


    def generate(
        self,
        invoice,
        output_path
    ) -> None:

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
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
                f"{float(invoice.invoice_total):.2f}"
        }

        totals = {
            "Net Amount",
            "VAT",
            "Invoice Total"
        }

        for field_name, value in values.items():

            if field_name not in fields:
                raise KeyError(
                    f"Missing PDF field metadata: "
                    f"{field_name}"
                )

            metadata = fields[field_name]

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
                    3
                    if is_total
                    else 0
                )
            )