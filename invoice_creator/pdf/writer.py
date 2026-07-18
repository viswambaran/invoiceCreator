import json
from pathlib import Path

import fitz

from invoice_creator.pdf.table_writer import (
    write_lines
)

from invoice_creator.pdf.text_writer import (
    write_value
)


class InvoicePDFWriter:

    REQUIRED_FIELDS = {
        "Invoice No",
        "Service User",
        "Assessor",
        "Net Amount",
        "VAT",
        "Invoice Total"
    }

    REQUIRED_COLUMNS = {
        "description",
        "units",
        "rate",
        "net"
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
                f"Metadata file does not exist: "
                f"{path}"
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

        available_fields = set(
            self.fields
            .get(
                "fields",
                {}
            )
            .keys()
        )

        missing_fields = (
            self.REQUIRED_FIELDS
            - available_fields
        )

        if missing_fields:

            raise ValueError(
                "Missing template field metadata: "
                + ", ".join(
                    sorted(
                        missing_fields
                    )
                )
            )


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
            self.REQUIRED_COLUMNS
            - available_columns
        )

        if missing_columns:

            raise ValueError(
                "Missing table metadata: "
                + ", ".join(
                    sorted(
                        missing_columns
                    )
                )
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
                f"Blank PDF template does not exist: "
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

        write_value(
            page=page,
            value=invoice.invoice_no,
            metadata=fields["Invoice No"],
            align="left"
        )

        write_value(
            page=page,
            value=invoice.service_user,
            metadata=fields["Service User"],
            align="left"
        )

        write_value(
            page=page,
            value=invoice.assessor,
            metadata=fields["Assessor"],
            align="left"
        )

        #
        # Totals share the right edge of the main table,
        # but need greater right padding than the table values.
        #

        net_box = (
            self.table
            ["invoice_lines"]
            ["columns"]
            ["net"]
            ["box"]
        )

        totals = {
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

        for field_name, value in totals.items():

            metadata = dict(
                fields[field_name]
            )

            #
            # Use a separate box object so the loaded
            # metadata is not modified in memory.
            #

            metadata["box"] = {
                "x0":
                    net_box["x0"],

                "x1":
                    net_box["x1"]
            }

            metadata["align"] = "right"

            write_value(
                page=page,
                value=value,
                metadata=metadata,
                align="right",

                #
                # Move totals safely inside the box.
                #
                padding=7
            )

    @staticmethod
    def _format_money(
        value
    ) -> str:

        return f"{float(value):.2f}"