import fitz
import json

from invoice_creator.pdf.text_writer import write_text
from invoice_creator.pdf.table_writer import write_lines



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
            "r"
        ) as f:

            self.fields = json.load(f)



        with open(
            table_path,
            "r"
        ) as f:

            self.table = json.load(f)



    def generate(
        self,
        invoice,
        output_path
    ):


        doc = fitz.open(
            self.template_path
        )


        page = doc[0]
        
        self.collect_redactions(
        page,
        invoice
        )


        page.apply_redactions()


        self.write_header(
            page,
            invoice
        )


        write_lines(
            page,
            invoice,
            self.table,
            self.fields["fields"]["Invoice No"]["font"]
        )

        self.write_header(
            page,
            invoice
        )


        write_lines(

            page,

            invoice,

            self.table,

            self.fields["fields"]["Invoice No"]["font"]

        )


        doc.save(
            output_path
        )

    def collect_redactions(
        self,
        page,
        invoice
    ):

        for field in [
            "Invoice No",
            "Service User",
            "Assessor"
        ]:

            area = (
                self.fields
                ["fields"]
                [field]
                .get("clear_area")
            )

            if area:

                add_redaction(
                    page,
                    area
                )


        table = (
            self.table
            ["invoice_lines"]
            ["columns"]
        )


        for column in table.values():

            if column.get("clear_area"):

                add_redaction(
                    page,
                    column["clear_area"]
                )

    def write_header(
        self,
        page,
        invoice
    ):


        mappings = {

            "Invoice No":
                invoice.invoice_no,

            "Service User":
                invoice.service_user,

            "Assessor":
                invoice.assessor

        }


        for field, value in mappings.items():


            metadata = (
                self.fields
                ["fields"]
                [field]
            )


            write_text(

                page,

                value,

                metadata["write_position"],

                metadata["font"]

            )