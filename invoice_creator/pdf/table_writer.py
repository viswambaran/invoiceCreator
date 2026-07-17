# # from invoice_creator.pdf.text_writer import write_text



# # def write_lines(
# #     page,
# #     invoice,
# #     table_metadata,
# #     font
# # ):


# #     table = (
# #         table_metadata
# #         ["invoice_lines"]
# #     )


# #     y = table["first_row_y"]


# #     for line in invoice.lines:


# #         values = {

# #             "description":
# #                 line.description,

# #             "units":
# #                 line.units,

# #             "rate":
# #                 line.rate,

# #             "net":
# #                 line.net

# #         }


# #         for column, value in values.items():

# #             ##DEBUG LINE ONLY 
# #             print(
# #                 "TABLE REDACTION:",
# #                 column,
# #                 value
# #             )
# #             if column not in table["columns"]:

# #                 continue


# #             position = (
# #                 table["columns"]
# #                 [column]
# #                 ["write_position"]
# #             )

# #             column_metadata = (
# #                 table["columns"][column]
# #                 )


# #             write_text(

# #                 page,

# #                 value,

# #                 {
# #                     "x": position["x"],
# #                     "y": y
# #                 },

# #                 font,

# #                 {

# #                     "x0": position["x"],

# #                     "y0": y - table["row_height"] + 5,

# #                     "x1": position["x"] + column_metadata["column_width"],

# #                     "y1": y + 5
# #                 }
                
# #                 # table["columns"][column].get("clear_area")

# #             )


# #         y += table["row_height"]

# ##NEW VERSION

# from invoice_creator.pdf.text_writer import write_in_area


# def format_table_value(column: str, value) -> str:
#     if column in {"rate", "net"}:
#         return f"{float(value):.2f}"

#     if column == "units":
#         numeric_value = float(value)

#         if numeric_value.is_integer():
#             return str(int(numeric_value))

#         return str(numeric_value)

#     return str(value)


# def write_lines(
#     page,
#     invoice,
#     table_metadata,
#     font,
# ):
#     table = table_metadata["invoice_lines"]
#     columns = table["columns"]

#     if len(invoice.lines) > table["max_rows"]:
#         raise ValueError(
#             f"Invoice {invoice.invoice_no} has {len(invoice.lines)} lines, "
#             f"but the template supports only {table['max_rows']}."
#         )

#     for row_index, line in enumerate(invoice.lines):
#         baseline_y = (
#             table["first_row_y"]
#             + row_index * table["row_height"]
#         )

#         values = {
#             "description": line.description,
#             "units": line.units,
#             "rate": line.rate,
#             "net": line.net,
#         }

#         for column_name, value in values.items():
#             if column_name not in columns:
#                 continue

#             column = columns[column_name]
#             x0 = column["write_position"]["x"]
#             x1 = x0 + column["column_width"]

#             # Clear only the text band within this row.
#             # The one-point inset in write_in_area preserves borders.
#             cell_rect = {
#                 "x0": x0,
#                 "y0": baseline_y - float(font["size"]) - 2,
#                 "x1": x1,
#                 "y1": baseline_y + 3,
#             }

#             write_in_area(
#                 page=page,
#                 value=format_table_value(column_name, value),
#                 clear_rect=cell_rect,
#                 baseline_y=baseline_y,
#                 font=font,
#                 align=column["write_position"].get(
#                     "align",
#                     "left",
#                 ),
#             )

## NEWER VERSION

from invoice_creator.pdf.text_writer import (
    write_in_area
)


def format_table_value(
    column_name: str,
    value
) -> str:
    if column_name in {
        "rate",
        "net"
    }:
        return f"{float(value):.2f}"

    if column_name == "units":
        numeric_value = float(
            value
        )

        if numeric_value.is_integer():
            return str(
                int(numeric_value)
            )

        return str(
            numeric_value
        )

    return str(
        value
    )


def write_lines(
    page,
    invoice,
    table_metadata
) -> None:
    table = (
        table_metadata
        ["invoice_lines"]
    )

    columns = table["columns"]

    if len(invoice.lines) > table["max_rows"]:
        raise ValueError(
            f"Invoice {invoice.invoice_no} has "
            f"{len(invoice.lines)} lines, but the "
            f"template supports only "
            f"{table['max_rows']}."
        )

    for row_index, line in enumerate(
        invoice.lines
    ):
        row_offset_y = (
            row_index
            * table["row_height"]
        )

        values = {
            "description":
                line.description,

            "units":
                line.units,

            "rate":
                line.rate,

            "net":
                line.net
        }

        for column_name, value in (
            values.items()
        ):
            if column_name not in columns:
                continue

            column = columns[
                column_name
            ]

            write_in_area(
                page=page,

                value=format_table_value(
                    column_name,
                    value
                ),

                value_rect=
                    column["value_rect"],

                write_position=
                    column["write_position"],

                font=
                    column["font"],

                align=
                    column
                    ["write_position"]
                    .get(
                        "align",
                        "left"
                    ),

                row_offset_y=
                    row_offset_y
            )