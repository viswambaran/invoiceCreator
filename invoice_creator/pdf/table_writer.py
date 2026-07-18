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

    columns = table[
        "columns"
    ]

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