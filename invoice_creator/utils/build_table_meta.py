import json
from pathlib import Path
from typing import Any


INPUT_FILE = Path(
    "templates/template_metadata.json"
)

OUTPUT_FILE = Path(
    "templates/table_metadata.json"
)


COLUMN_ORDER = [
    "service_user",
    "assessor",
    "description",
    "units",
    "rate",
    "net",
]


COLUMN_ALIGNMENT = {
    "service_user": "left",
    "assessor": "left",
    "description": "left",
    "units": "center",
    "rate": "center",
    "net": "center",
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


def find_text(
    metadata: dict[str, Any],
    aliases: list[str]
) -> dict[str, Any] | None:

    normalised_aliases = {
        alias.lower()
        for alias in aliases
    }

    for item in metadata["fields"]:

        text = clean_text(
            item["text"]
        ).lower()

        if text in normalised_aliases:
            return item

    return None


def is_vertical_line(
    drawing: dict[str, Any],
    tolerance: float = 0.5
) -> bool:

    if drawing["type"] != "line":
        return False

    return (
        abs(
            drawing["start"]["x"]
            - drawing["end"]["x"]
        )
        <= tolerance
    )


def is_horizontal_line(
    drawing: dict[str, Any],
    tolerance: float = 0.5
) -> bool:

    if drawing["type"] != "line":
        return False

    return (
        abs(
            drawing["start"]["y"]
            - drawing["end"]["y"]
        )
        <= tolerance
    )


def find_main_table_rect(
    metadata: dict[str, Any]
) -> dict[str, float]:

    candidates = []

    for drawing in metadata["drawings"]:

        if drawing["type"] != "rectangle":
            continue

        rect = drawing["rect"]

        width = (
            rect["x1"]
            - rect["x0"]
        )

        height = (
            rect["y1"]
            - rect["y0"]
        )

        if (
            width > 400
            and height > 150
        ):
            candidates.append(
                rect
            )

    if not candidates:

        raise ValueError(
            "Could not detect the main invoice table."
        )

    return max(
        candidates,
        key=lambda rect:
        (
            rect["x1"] - rect["x0"]
        )
        *
        (
            rect["y1"] - rect["y0"]
        )
    )


def find_totals_table_rect(
    metadata: dict[str, Any],
    main_table: dict[str, float]
) -> dict[str, float]:

    candidates = []

    for drawing in metadata["drawings"]:

        if drawing["type"] != "rectangle":
            continue

        rect = drawing["rect"]

        width = (
            rect["x1"]
            - rect["x0"]
        )

        height = (
            rect["y1"]
            - rect["y0"]
        )

        if (
            rect["y0"] > main_table["y1"]
            and 120 < width < 250
            and 20 < height < 60
        ):
            candidates.append(
                rect
            )

    if not candidates:

        raise ValueError(
            "Could not detect the totals table."
        )

    return min(
        candidates,
        key=lambda rect:
        rect["y0"]
    )


def find_vertical_boundaries(
    metadata: dict[str, Any],
    table_rect: dict[str, float]
) -> list[float]:

    boundaries = {
        round(
            table_rect["x0"],
            2
        ),

        round(
            table_rect["x1"],
            2
        ),
    }

    for drawing in metadata["drawings"]:

        if not is_vertical_line(
            drawing
        ):
            continue

        x = round(
            drawing["start"]["x"],
            2
        )

        line_y0 = min(
            drawing["start"]["y"],
            drawing["end"]["y"]
        )

        line_y1 = max(
            drawing["start"]["y"],
            drawing["end"]["y"]
        )

        overlaps_table = (
            x > table_rect["x0"]
            and x < table_rect["x1"]
            and line_y0 <= table_rect["y0"] + 1
            and line_y1 >= table_rect["y1"] - 1
        )

        if overlaps_table:

            boundaries.add(
                x
            )

    return sorted(
        boundaries
    )


def find_header_separator(
    metadata: dict[str, Any],
    table_rect: dict[str, float]
) -> float:

    candidates = []

    for drawing in metadata["drawings"]:

        if not is_horizontal_line(
            drawing
        ):
            continue

        y = round(
            drawing["start"]["y"],
            2
        )

        x0 = min(
            drawing["start"]["x"],
            drawing["end"]["x"]
        )

        x1 = max(
            drawing["start"]["x"],
            drawing["end"]["x"]
        )

        if (
            abs(
                x0
                - table_rect["x0"]
            )
            <= 1
            and abs(
                x1
                - table_rect["x1"]
            )
            <= 1
            and table_rect["y0"] < y < table_rect["y1"]
        ):
            candidates.append(
                y
            )

    if not candidates:

        raise ValueError(
            "Could not detect the table header separator."
        )

    return min(
        candidates
    )


def find_totals_divider(
    metadata: dict[str, Any],
    totals_rect: dict[str, float]
) -> float:

    candidates = []

    for drawing in metadata["drawings"]:

        if not is_vertical_line(
            drawing
        ):
            continue

        x = round(
            drawing["start"]["x"],
            2
        )

        y0 = min(
            drawing["start"]["y"],
            drawing["end"]["y"]
        )

        y1 = max(
            drawing["start"]["y"],
            drawing["end"]["y"]
        )

        if (
            totals_rect["x0"] < x < totals_rect["x1"]
            and y0 <= totals_rect["y0"] + 1
            and y1 >= totals_rect["y1"] - 1
        ):
            candidates.append(
                x
            )

    if not candidates:

        raise ValueError(
            "Could not detect the totals value divider."
        )

    return candidates[0]


def build_table(
    metadata: dict[str, Any]
) -> dict[str, Any]:

    main_table = find_main_table_rect(
        metadata
    )

    totals_table = find_totals_table_rect(
        metadata,
        main_table
    )

    boundaries = find_vertical_boundaries(
        metadata,
        main_table
    )

    if len(boundaries) != 7:

        raise ValueError(
            "Expected 7 main table boundaries, "
            f"but found {len(boundaries)}: "
            f"{boundaries}"
        )

    header_separator_y = find_header_separator(
        metadata,
        main_table
    )

    totals_divider_x = find_totals_divider(
        metadata,
        totals_table
    )

    #
    # Existing template header font.
    #

    description_header = find_text(
        metadata,
        [
            "Charge Desc.",
            "Charge Desc",
            "Description",
        ]
    )

    if description_header is None:

        raise ValueError(
            "Could not detect the Charge Desc header font."
        )

    default_font = description_header[
        "font"
    ]

    first_row_y = round(
        header_separator_y + 14.85,
        2
    )

    row_height = 20.0

    columns: dict[str, Any] = {}

    for index, column_name in enumerate(
        COLUMN_ORDER
    ):

        x0 = boundaries[index]
        x1 = boundaries[index + 1]

        alignment = COLUMN_ALIGNMENT[
            column_name
        ]

        columns[column_name] = {
            "cell": {
                "x0": x0,
                "x1": x1,
            },

            "write_position": {
                "x": round(
                    x0 + 7,
                    2
                ),

                "y":
                    first_row_y,
            },

            "align":
                alignment,

            "font":
                default_font,
        }

    table = {
        "invoice_lines": {
            "page":
                1,

            "table_rect":
                main_table,

            "header_separator_y":
                header_separator_y,

            "first_row_y":
                first_row_y,

            "row_height":
                row_height,

            "max_rows":
                5,

            "columns": {
                "description":
                    columns["description"],

                "units":
                    columns["units"],

                "rate":
                    columns["rate"],

                "net":
                    columns["net"],
            },
        },

        "header_value_cells": {
            "Service User":
                columns["service_user"],

            "Assessor":
                columns["assessor"],
        },

        "totals": {
            "table_rect":
                totals_table,

            "label_cell": {
                "x0":
                    totals_table["x0"],

                "x1":
                    totals_divider_x,
            },

            "value_cell": {
                "x0":
                    totals_divider_x,

                "x1":
                    totals_table["x1"],
            },
        },
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

    print(
        "Main table boundaries:"
    )

    for boundary in (
        find_vertical_boundaries(
            metadata,
            find_main_table_rect(
                metadata
            )
        )
    ):

        print(
            f"  {boundary}"
        )

    print()
    print(
        "Table metadata rebuilt"
    )