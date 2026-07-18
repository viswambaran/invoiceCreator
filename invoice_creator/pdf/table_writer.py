from invoice_creator.pdf.text_writer import (
    write_metadata_value,
)


def format_table_value(
    column_name: str,
    value,
) -> str:

    if column_name in {
        "rate",
        "net",
    }:
        return f"{float(value):.2f}"

    if column_name == "units":
        numeric_value = float(value)

        if numeric_value.is_integer():
            return str(
                int(numeric_value)
            )

        return str(numeric_value)

    return str(value)


def write_lines(
    page,
    invoice,
    table_metadata,
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
                line.net,
        }

        for column_name, value in values.items():
            if column_name not in columns:
                continue

            metadata = columns[
                column_name
            ]

            alignment = (
                metadata["write_position"]
                .get(
                    "align",
                    "left",
                )
            )

            write_metadata_value(
                page=page,
                value=format_table_value(
                    column_name,
                    value,
                ),
                metadata=metadata,
                align=alignment,
                row_offset_y=row_offset_y,
                padding=(
                    4
                    if alignment == "right"
                    else 0
                ),
                clear_padding_x=2.0,
                clear_padding_top=1.0,
                clear_padding_bottom=0.75,
            )