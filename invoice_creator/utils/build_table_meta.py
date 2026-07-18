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

        item_text = clean_text(
            item["text"]
        ).lower()

        for alias in aliases:

            if item_text == alias.lower():

                return item

    return None


def calculate_column_width(
    detected_headers: list[dict[str, Any]],
    index: int
) -> float:

    current_x = float(
        detected_headers[index]
        ["data"]
        ["rect"]
        ["x0"]
    )

    if index + 1 < len(
        detected_headers
    ):

        next_x = float(
            detected_headers[index + 1]
            ["data"]
            ["rect"]
            ["x0"]
        )

        return round(
            next_x - current_x,
            2
        )

    return 60.0


def build_table(
    metadata: dict[str, Any]
) -> dict[str, Any]:

    detected_headers = []

    for column_name, aliases in (
        COLUMN_HEADERS.items()
    ):

        header = find_header(
            metadata,
            aliases
        )

        if header is None:

            raise ValueError(
                f"Missing table header: "
                f"{column_name}"
            )

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


    table: dict[str, Any] = {
        "invoice_lines": {
            "page":
                1,

            "first_row_y":
                first_row_y,

            "row_height":
                20,

            "max_rows":
                5,

            "columns":
                {}
        }
    }


    for index, item in enumerate(
        detected_headers
    ):

        column_name = item[
            "name"
        ]

        header = item[
            "data"
        ]

        header_rect = header[
            "rect"
        ]

        width = calculate_column_width(
            detected_headers,
            index
        )

        left_x = float(
            header_rect["x0"]
        )

        right_x = round(
            left_x + width,
            2
        )

        alignment = COLUMN_ALIGNMENT[
            column_name
        ]

        table["invoice_lines"][
            "columns"
        ][column_name] = {
            "header_position": {
                "x":
                    header_rect["x0"],

                "y":
                    header_rect["y1"]
            },

            "box": {
                "x0": round(
                    left_x + 4,
                    2
                ),

                "x1": round(
                    right_x - 4,
                    2
                )
            },

            "write_position": {
                "x": round(
                    left_x + 4,
                    2
                ),

                "y":
                    first_row_y
            },

            "align":
                alignment,

            "font":
                header["font"]
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