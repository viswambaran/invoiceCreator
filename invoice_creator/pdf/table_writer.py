from invoice_creator.pdf.text_writer import (
    write_value
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
        numeric_value = float(value)

        if numeric_value.is_integer():
            return str(int(numeric_value))

        return str(numeric_value)

    return str(value)


def write_lines(
    page,
    invoice,
    table_metadata
) -> None:

    table = table_metadata[
        "invoice_lines"
    ]

    columns = table[
        "columns"
    ]

    if len(invoice.lines) > table["max_rows"]:
        raise ValueError(
            f"Invoice {invoice.invoice_no} has "
            f"{len(invoice.lines)} lines, but "
            f"the template supports only "
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

        for column_name, value in values.items():

            if column_name not in columns:
                continue

            column_metadata = columns[
                column_name
            ]

            #
            # Each table column needs its own alignment
            # and padding rather than one generic rule.
            #

            if column_name == "description":
                alignment = "left"
                padding = 3

            elif column_name == "units":
                alignment = "center"
                padding = 0

            elif column_name in {
                "rate",
                "net"
            }:
                alignment = "right"
                padding = 6

            else:
                alignment = "left"
                padding = 0

            write_value(
                page=page,

                value=format_table_value(
                    column_name,
                    value
                ),

                metadata=
                    column_metadata,

                align=
                    alignment,

                row_offset_y=
                    row_offset_y,

                padding=
                    padding
            )