import json
from pathlib import Path
from typing import Any


INPUT_FILE = Path(
    "templates/template_metadata.json"
)

OUTPUT_FILE = Path(
    "templates/table_metadata.json"
)


COLUMN_HEADERS = {
    "description": [
        "Description",
        "Charge Desc",
        "Charge Desc.",
        "Charge Description"
    ],

    "units": [
        "Units",
        "Unit"
    ],

    "rate": [
        "Rate"
    ],

    "net": [
        "Net"
    ]
}


COLUMN_ALIGNMENT = {
    "description": "left",
    "units": "right",
    "rate": "right",
    "net": "right"
}


def load_json(
    path: Path
) -> dict[str, Any]:

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(
            file
        )


def save_json(
    data: dict[str, Any],
    path: Path
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )


def clean_text(
    text: str
) -> str:

    return " ".join(
        text
        .replace("\n", " ")
        .split()
    )


def find_header(
    metadata: dict[str, Any],
    aliases: list[str]
) -> dict[str, Any] | None:

    for item in metadata["fields"]:

        text = clean_text(
            item["text"]
        ).lower()

        for alias in aliases:

            if text == alias.lower():

                return item

    return None


def calculate_column_width(
    headers: list[dict[str, Any]],
    index: int
) -> float:

    current_x = float(
        headers[index]
        ["data"]
        ["rect"]
        ["x0"]
    )

    if index + 1 < len(headers):

        next_x = float(
            headers[index + 1]
            ["data"]
            ["rect"]
            ["x0"]
        )

        return round(
            next_x - current_x,
            2
        )

    return 60.0


def make_cell_text_band(
    x0: float,
    x1: float,
    baseline_y: float,
    font_size: float
) -> dict[str, float]:
    """
    Narrow text-only area within a table cell.

    The rectangle remains clear of cell borders.
    """

    return {
        "x0": round(
            x0 + 2,
            2
        ),

        "y0": round(
            baseline_y
            - font_size
            - 0.5,
            2
        ),

        "x1": round(
            x1 - 2,
            2
        ),

        "y1": round(
            baseline_y + 0.75,
            2
        )
    }


def build_table(
    metadata: dict[str, Any]
) -> dict[str, Any]:

    table: dict[str, Any] = {
        "invoice_lines": {
            "page": 1,
            "columns": {},
            "first_row_y": None,
            "row_height": 20,
            "max_rows": 5
        }
    }

    detected_headers = []


    for column_name, aliases in (
        COLUMN_HEADERS.items()
    ):

        header = find_header(
            metadata,
            aliases
        )

        if header:

            detected_headers.append(
                {
                    "name":
                        column_name,

                    "data":
                        header
                }
            )

            print(
                f"✓ {column_name}"
            )

        else:

            print(
                f"⚠ Missing {column_name}"
            )


    if len(detected_headers) != len(
        COLUMN_HEADERS
    ):

        raise ValueError(
            "One or more invoice table headers "
            "could not be detected."
        )


    detected_headers.sort(
        key=lambda item:
        item["data"]["rect"]["x0"]
    )


    header_y = max(
        item["data"]["rect"]["y1"]
        for item in detected_headers
    )

    first_row_y = round(
        header_y + 27,
        2
    )

    table["invoice_lines"][
        "first_row_y"
    ] = first_row_y


    for index, item in enumerate(
        detected_headers
    ):

        column_name = item[
            "name"
        ]

        header = item[
            "data"
        ]

        rect = header[
            "rect"
        ]

        column_width = (
            calculate_column_width(
                detected_headers,
                index
            )
        )

        x0 = float(
            rect["x0"]
        )

        x1 = round(
            x0 + column_width,
            2
        )

        font = header[
            "font"
        ]

        font_size = float(
            font["size"]
        )

        alignment = (
            COLUMN_ALIGNMENT[
                column_name
            ]
        )

        write_x = (
            round(
                x0 + 4,
                2
            )
            if alignment == "left"
            else x0
        )

        cell_rect = {
            "x0":
                x0,

            "y0": round(
                first_row_y
                - table["invoice_lines"]["row_height"],
                2
            ),

            "x1":
                x1,

            "y1": round(
                first_row_y + 3,
                2
            )
        }

        safe_clear_rect = (
            make_cell_text_band(
                x0=x0,
                x1=x1,
                baseline_y=first_row_y,
                font_size=font_size
            )
        )

        table["invoice_lines"][
            "columns"
        ][column_name] = {
            "header_position": {
                "x":
                    rect["x0"],

                "y":
                    rect["y1"]
            },

            "column_width":
                column_width,

            "cell_rect":
                cell_rect,

            "safe_clear_rect":
                safe_clear_rect,

            "write_position": {
                "x":
                    write_x,

                "y":
                    first_row_y,

                "align":
                    alignment
            },

            "font":
                font
        }


    return table


if __name__ == "__main__":

    metadata = load_json(
        INPUT_FILE
    )

    table = build_table(
        metadata
    )

    save_json(
        table,
        OUTPUT_FILE
    )

    print()
    print(
        "Table metadata rebuilt"
    )