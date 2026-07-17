# # import fitz
# # import json

# # from invoice_creator.pdf.text_writer import write_text #, apply_redactions, add_redaction
# # from invoice_creator.pdf.table_writer import write_lines



# # class InvoicePDFWriter:


# #     def __init__(
# #         self,
# #         template_path,
# #         fields_path,
# #         table_path
# #     ):


# #         self.template_path = template_path


# #         with open(
# #             fields_path,
# #             "r"
# #         ) as f:

# #             self.fields = json.load(f)



# #         with open(
# #             table_path,
# #             "r"
# #         ) as f:

# #             self.table = json.load(f)



# #     def generate(
# #         self,
# #         invoice,
# #         output_path
# #     ):


# #         doc = fitz.open(
# #             self.template_path
# #         )


# #         page = doc[0]
        
# #         # self.collect_redactions(
# #         #     page
# #         # )


# #         # page.apply_redactions()


# #         self.write_header(
# #             page,
# #             invoice
# #         )


# #         write_lines(
# #             page,
# #             invoice,
# #             self.table,
# #             self.fields["fields"]["Invoice No"]["font"]
# #         )


# #         # write_lines(

# #         #     page,

# #         #     invoice,

# #         #     self.table,

# #         #     self.fields["fields"]["Invoice No"]["font"]

# #         # )


# #         doc.save(
# #             output_path
# #         )

# #     # def collect_redactions(
# #     #         self,
# #     #         page
# #     # ):


# #     #     #
# #     #     # Header fields
# #     #     #

# #     #     for field in self.fields["fields"].values():

# #     #         ## Debug line only print 
# #     #         print(
# #     #             "FIELD REDACTION:",
# #     #             field.get("pdf_label"),
# #     #             field.get("clear_area")
# #     #         )

# #     #         area = field.get(
# #     #             "clear_area"
# #     #         )

# #     #         if area:

# #     #             add_redaction(
# #     #                 page,
# #     #                 area
# #     #             )


# #     #     #
# #     #     # Table columns
# #     #     #

# #     #     # Commented below for testing and debug

# #     #     # columns = (
# #     #     #     self.table["invoice_lines"]
# #     #     #     ["columns"]
# #     #     # )


# #     #     # for column in columns.values():

# #     #     #     area = column.get(
# #     #     #         "clear_area"
# #     #     #     )

# #     #     #     if area:

# #     #     #         add_redaction(
# #     #     #             page,
# #     #     #             area
# #     #     #         )

# #     def write_header(
# #         self,
# #         page,
# #         invoice
# #     ):


# #         mappings = {

# #             "Invoice No":
# #                 invoice.invoice_no,

# #             "Service User":
# #                 invoice.service_user,

# #             "Assessor":
# #                 invoice.assessor,
            
# #             "Net Amount": invoice.net_amount,

# #             "VAT": invoice.vat,

# #             "Invoice Total": invoice.invoice_total

# #         }


# #         for field, value in mappings.items():


# #             metadata = (
# #                 self.fields
# #                 ["fields"]
# #                 [field]
# #             )


# #             write_text(

# #                 page,

# #                 value,

# #                 metadata["write_position"],

# #                 metadata["font"],

# #                 metadata.get("clear_area")

# #             )

# ## NEW VERISON

# import json
# from pathlib import Path

# import fitz

# from invoice_creator.pdf.table_writer import write_lines
# from invoice_creator.pdf.text_writer import write_in_area


# class InvoicePDFWriter:

#     def __init__(
#         self,
#         template_path,
#         fields_path,
#         table_path,
#     ):
#         self.template_path = template_path

#         with open(
#             fields_path,
#             "r",
#             encoding="utf-8",
#         ) as file:
#             self.fields = json.load(file)

#         with open(
#             table_path,
#             "r",
#             encoding="utf-8",
#         ) as file:
#             self.table = json.load(file)

#     def generate(
#         self,
#         invoice,
#         output_path,
#     ):
#         output_path = Path(output_path)
#         output_path.parent.mkdir(
#             parents=True,
#             exist_ok=True,
#         )

#         doc = fitz.open(self.template_path)

#         try:
#             page = doc[0]

#             self.write_invoice_fields(
#                 page,
#                 invoice,
#             )

#             write_lines(
#                 page=page,
#                 invoice=invoice,
#                 table_metadata=self.table,
#                 font=self.fields["fields"]["Invoice No"]["font"],
#             )

#             self.write_totals(
#                 page,
#                 invoice,
#             )

#             doc.save(
#                 output_path,
#                 garbage=4,
#                 deflate=True,
#             )

#         finally:
#             doc.close()

#     def write_invoice_fields(
#         self,
#         page,
#         invoice,
#     ):
#         fields = self.fields["fields"]
#         columns = self.table["invoice_lines"]["columns"]

#         invoice_no = fields["Invoice No"]
#         invoice_y = invoice_no["write_position"]["y"]
#         invoice_font = invoice_no["font"]

#         # Inline Invoice No: clear from its write position to the right,
#         # while keeping the label and invoice date row untouched.
#         write_in_area(
#             page=page,
#             value=invoice.invoice_no,
#             clear_rect={
#                 "x0": invoice_no["write_position"]["x"] - 2,
#                 "y0": invoice_y - float(invoice_font["size"]) - 2,
#                 "x1": invoice_no["write_position"]["x"] + 75,
#                 "y1": invoice_y + 3,
#             },
#             baseline_y=invoice_y,
#             font=invoice_font,
#             align="left",
#         )

#         service_user = fields["Service User"]
#         assessor = fields["Assessor"]

#         service_y = service_user["write_position"]["y"]
#         assessor_y = assessor["write_position"]["y"]

#         # Service User value cell ends at the BIA/DR column.
#         write_in_area(
#             page=page,
#             value=invoice.service_user,
#             clear_rect={
#                 "x0": service_user["write_position"]["x"],
#                 "y0": service_y - float(service_user["font"]["size"]) - 2,
#                 "x1": assessor["label_rect"]["x0"],
#                 "y1": service_y + 3,
#             },
#             baseline_y=service_y,
#             font=service_user["font"],
#             align="left",
#         )

#         # BIA/DR value cell ends at Charge Desc.
#         description_x = columns["description"]["write_position"]["x"]

#         write_in_area(
#             page=page,
#             value=invoice.assessor,
#             clear_rect={
#                 "x0": assessor["write_position"]["x"],
#                 "y0": assessor_y - float(assessor["font"]["size"]) - 2,
#                 "x1": description_x,
#                 "y1": assessor_y + 3,
#             },
#             baseline_y=assessor_y,
#             font=assessor["font"],
#             align="left",
#         )

#     def write_totals(
#         self,
#         page,
#         invoice,
#     ):
#         fields = self.fields["fields"]

#         # The totals use the same rightmost value column as the table Net
#         # column. This places them inside the existing right-hand boxes.
#         net_column = self.table["invoice_lines"]["columns"]["net"]
#         total_x0 = net_column["write_position"]["x"]
#         total_x1 = total_x0 + net_column["column_width"]

#         totals = {
#             "Net Amount": invoice.net_amount,
#             "VAT": invoice.vat,
#             "Invoice Total": invoice.invoice_total,
#         }

#         for field_name, value in totals.items():
#             metadata = fields[field_name]
#             baseline_y = metadata["write_position"]["y"]
#             fontsize = float(metadata["font"]["size"])

#             write_in_area(
#                 page=page,
#                 value=f"{float(value):.2f}",
#                 clear_rect={
#                     "x0": total_x0,
#                     "y0": baseline_y - fontsize - 2,
#                     "x1": total_x1,
#                     "y1": baseline_y + 3,
#                 },
#                 baseline_y=baseline_y,
#                 font=metadata["font"],
#                 align="right",
#             )

## NEWER VESRION 170726 1345

import json
from pathlib import Path

import fitz

from invoice_creator.pdf.table_writer import (
    write_lines
)

from invoice_creator.pdf.text_writer import (
    write_in_area
)


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
            self.fields = json.load(
                file
            )

        with open(
            table_path,
            "r",
            encoding="utf-8"
        ) as file:
            self.table = json.load(
                file
            )

    def generate(
        self,
        invoice,
        output_path
    ) -> None:
        
        print("PDF INPUT DEBUG")
        print("Invoice No:", repr(invoice.invoice_no))
        print("Service User:", repr(invoice.service_user))
        print("Assessor:", repr(invoice.assessor))
        print()
        output_path = Path(
            output_path
        )

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
        fields = (
            self.fields
            ["fields"]
        )

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

        for field_name, value in (
            values.items()
        ):
            if field_name not in fields:
                raise KeyError(
                    f"Missing PDF field metadata: "
                    f"{field_name}"
                )

            metadata = fields[
                field_name
            ]

            alignment = (
                "right"
                if field_name in {
                    "Net Amount",
                    "VAT",
                    "Invoice Total"
                }
                else "left"
            )

        write_in_area(
            page=page,

            value=value,

            value_rect=
                metadata["value_rect"],

            write_position=
                metadata["write_position"],

            font=
                metadata["font"],

            align=
                alignment,

            padding=(
                3
                if alignment == "right"
                else 0
            )
        )