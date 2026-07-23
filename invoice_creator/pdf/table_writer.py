from __future__ import annotations

from collections.abc import Iterable

from invoice_creator.models.invoice import InvoiceLine
from invoice_creator.pdf.text_writer import write_value


def format_table_value(column_name: str, value) -> str:
    if value is None:
        return ""

    if column_name in {"rate", "net"}:
        return f"{float(value):.2f}"

    if column_name == "units":
        numeric_value = float(value)
        if numeric_value.is_integer():
            return str(int(numeric_value))
        return str(numeric_value)

    return str(value)


def get_max_rows(table_metadata: dict) -> int:
    try:
        max_rows = int(
            table_metadata["invoice_lines"]["max_rows"]
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(
            "Table metadata must contain "
            "a valid invoice_lines.max_rows."
        ) from exc

    if max_rows < 1:
        raise ValueError(
            "Table metadata max_rows must be at least 1."
        )

    return max_rows


def paginate_lines(
    lines: Iterable[InvoiceLine],
    table_metadata: dict,
) -> list[list[InvoiceLine]]:
    line_list = list(lines)
    max_rows = get_max_rows(table_metadata)

    if not line_list:
        return [[]]

    return [
        line_list[start:start + max_rows]
        for start in range(0, len(line_list), max_rows)
    ]


def _get_columns(
    table_metadata: dict,
    include_identity_columns: bool,
) -> dict:
    table = table_metadata["invoice_lines"]
    columns: dict = {}

    if include_identity_columns:
        identity_columns = table_metadata.get(
            "line_identity_columns",
            {},
        )
        columns.update(identity_columns)

    columns.update(table["columns"])
    return columns


def write_lines(
    page,
    lines: Iterable[InvoiceLine],
    table_metadata: dict,
    include_identity_columns: bool = False,
) -> None:
    table = table_metadata["invoice_lines"]
    columns = _get_columns(
        table_metadata,
        include_identity_columns,
    )
    page_lines = list(lines)
    max_rows = get_max_rows(table_metadata)

    if len(page_lines) > max_rows:
        raise ValueError(
            "A PDF page received "
            f"{len(page_lines)} invoice lines, "
            "but the template supports only "
            f"{max_rows}."
        )

    for row_index, line in enumerate(page_lines):
        row_offset_y = row_index * table["row_height"]

        for column_name, column_metadata in columns.items():
            if not hasattr(line, column_name):
                raise ValueError(
                    "InvoiceLine does not contain the field "
                    f"required by table metadata: {column_name!r}."
                )

            value = getattr(line, column_name)

            write_value(
                page=page,
                value=format_table_value(column_name, value),
                metadata=column_metadata,
                align=column_metadata["align"],
                row_offset_y=row_offset_y,
                padding=6,
            )
