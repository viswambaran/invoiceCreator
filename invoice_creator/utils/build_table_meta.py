# import json
# from pathlib import Path


# INPUT_FILE = Path(
#     "templates/template_metadata.json"
# )

# OUTPUT_FILE = Path(
#     "templates/table_metadata.json"
# )



# COLUMN_HEADERS = {

#     "description": [
#         "Description",
#         "Charge Desc",
#         "Charge Desc.",
#         "Charge Description"
#     ],

#     "units": [
#         "Units"
#     ],

#     "rate": [
#         "Rate"
#     ],

#     "net": [
#         "Net"
#     ]

# }



# COLUMN_ALIGNMENT = {

#     "description": "left",

#     "units": "right",

#     "rate": "right",

#     "net": "right"

# }



# def load_json(path):

#     with open(
#         path,
#         "r",
#         encoding="utf-8"
#     ) as f:

#         return json.load(f)



# def save_json(data, path):

#     with open(
#         path,
#         "w",
#         encoding="utf-8"
#     ) as f:

#         json.dump(
#             data,
#             f,
#             indent=4
#         )



# def clean_text(text):

#     return (
#         text
#         .replace("\n", "")
#         .strip()
#     )



# def find_header(metadata, aliases):

#     for item in metadata["fields"]:

#         text = clean_text(
#             item["text"]
#         )

#         for alias in aliases:

#             if text.lower() == alias.lower():

#                 return item

#     return None

# def calculate_column_width(
#         headers,
#         index
# ):

#     """
#     Calculate width between
#     neighbouring table columns
#     """

#     current_x = (
#         headers[index]
#         ["data"]
#         ["rect"]
#         ["x0"]
#     )


#     if index + 1 < len(headers):

#         next_x = (
#             headers[index + 1]
#             ["data"]
#             ["rect"]
#             ["x0"]
#         )

#         return round(
#             next_x - current_x,
#             2
#         )


#     return 60

# def calculate_clear_area(
#         headers,
#         index,
#         first_row_y,
#         row_height,
#         max_rows
# ):


#     current = headers[index]["data"]


#     x0 = current["rect"]["x0"]


#     if index + 1 < len(headers):

#         x1 = (
#             headers[index + 1]
#             ["data"]
#             ["rect"]
#             ["x0"]
#         )

#     else:

#         x1 = x0 + 60



#     return {

#         "x0": round(x0,2),

#         "y0": round(first_row_y - 5,2),

#         "x1": round(x1,2),

#         "y1": round(
#             first_row_y +
#             (row_height * max_rows),
#             2
#         )

#     }


# def build_table(metadata):


#     table = {

#         "invoice_lines": {

#             "page": 1,

#             "columns": {},

#             "first_row_y": None,

#             "row_height": 20,

#             "max_rows": 5

#         }

#     }



#     detected_headers = []



#     #
#     # Find table headers
#     #

#     for column, aliases in COLUMN_HEADERS.items():

#         header = find_header(
#             metadata,
#             aliases
#         )


#         if header:

#             detected_headers.append(
#                 {
#                     "name": column,
#                     "data": header
#                 }
#             )


#             print(
#                 f"✓ {column}"
#             )



#     #
#     # Sort columns left to right
#     #

#     detected_headers.sort(
#         key=lambda x:
#         x["data"]["rect"]["x0"]
#     )



#     #
#     # Calculate header baseline
#     #

#     header_y = 0


#     for item in detected_headers:

#         header_y = max(
#             header_y,
#             item["data"]["rect"]["y1"]
#         )



#     first_row_y = round(
#         header_y + 27,
#         2
#     )


#     table["invoice_lines"]["first_row_y"] = first_row_y



#     #
#     # Build columns
#     #

#     for index, item in enumerate(detected_headers):


#         column_name = item["name"]

#         rect = item["data"]["rect"]


#         width = calculate_column_width(
#             detected_headers,
#             index
#         )


#         table["invoice_lines"]["columns"][column_name] = {


#             "header_position": {

#                 "x": rect["x0"],

#                 "y": rect["y1"]

#             },


#             "column_width": width,


#             "write_position": {

#                 "x": rect["x0"],

#                 "y": first_row_y,

#                 "align":
#                     COLUMN_ALIGNMENT[column_name]

#             },
#             "clear_area":

#                 calculate_clear_area(

#                     detected_headers,

#                     index,

#                     first_row_y,

#                     table["invoice_lines"]["row_height"],

#                     table["invoice_lines"]["max_rows"]

#                 )

#         }



#     return table



# if __name__ == "__main__":


#     metadata = load_json(
#         INPUT_FILE
#     )


#     table = build_table(
#         metadata
#     )


#     save_json(
#         table,
#         OUTPUT_FILE
#     )


#     print()

#     print(
#         "Table metadata rebuilt"
#     )

## NEW VERSION

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


def load_json(path: Path) -> dict[str, Any]:
    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_json(
    data: dict[str, Any],
    path: Path
) -> None:
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


def clean_text(text: str) -> str:
    return " ".join(
        text.replace(
            "\n",
            " "
        ).split()
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


def expand_rect(
    rect: dict[str, float],
    horizontal: float = 2,
    vertical: float = 1
) -> dict[str, float]:
    return {
        "x0": round(
            rect["x0"] - horizontal,
            2
        ),

        "y0": round(
            rect["y0"] - vertical,
            2
        ),

        "x1": round(
            rect["x1"] + horizontal,
            2
        ),

        "y1": round(
            rect["y1"] + vertical,
            2
        )
    }


def find_first_row_values(
    metadata: dict[str, Any],
    first_row_y: float,
    expected_count: int
) -> list[dict[str, Any]]:
    candidates = []

    for item in metadata["fields"]:
        text = clean_text(
            item["text"]
        )

        if not text:
            continue

        rect = item["rect"]

        if abs(
            rect["y1"]
            - first_row_y
        ) <= 8:
            candidates.append(item)

    candidates.sort(
        key=lambda item:
        item["rect"]["x0"]
    )

    if len(candidates) < expected_count:
        return []

    # The invoice-line fields are the rightmost four values.
    return candidates[
        -expected_count:
    ]


def calculate_fallback_width(
    headers: list[dict[str, Any]],
    index: int
) -> float:
    current_x = (
        headers[index]
        ["data"]
        ["rect"]
        ["x0"]
    )

    if index + 1 < len(headers):
        next_x = (
            headers[index + 1]
            ["data"]
            ["rect"]
            ["x0"]
        )

        return round(
            next_x - current_x,
            2
        )

    return 60


def build_table(
    metadata: dict[str, Any]
) -> dict[str, Any]:
    table = {
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
                    "name": column_name,
                    "data": header
                }
            )

            print(
                f"✓ {column_name}"
            )
        else:
            print(
                f"⚠ Missing {column_name}"
            )

    detected_headers.sort(
        key=lambda item:
        item["data"]["rect"]["x0"]
    )

    if not detected_headers:
        raise ValueError(
            "No invoice table headers were detected."
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

    sample_values = find_first_row_values(
        metadata,
        first_row_y,
        len(detected_headers)
    )

    for index, header_item in enumerate(
        detected_headers
    ):
        column_name = header_item["name"]
        header = header_item["data"]
        header_rect = header["rect"]

        sample = (
            sample_values[index]
            if len(sample_values)
            == len(detected_headers)
            else None
        )

        if sample:
            sample_rect = sample["rect"]

            write_position = {
                "x": round(
                    sample_rect["x0"],
                    2
                ),

                "y": round(
                    sample_rect["y1"],
                    2
                ),

                "align":
                    COLUMN_ALIGNMENT[
                        column_name
                    ]
            }

            value_rect = expand_rect(
                sample_rect,
                horizontal=3,
                vertical=1
            )

            value_font = sample.get(
                "font",
                header["font"]
            )

            column_width = round(
                value_rect["x1"]
                - value_rect["x0"],
                2
            )

        else:
            fallback_width = (
                calculate_fallback_width(
                    detected_headers,
                    index
                )
            )

            write_position = {
                "x": round(
                    header_rect["x0"],
                    2
                ),

                "y": first_row_y,

                "align":
                    COLUMN_ALIGNMENT[
                        column_name
                    ]
            }

            value_rect = {
                "x0": round(
                    header_rect["x0"] - 2,
                    2
                ),

                "y0": round(
                    first_row_y
                    - float(
                        header["font"]["size"]
                    )
                    - 2,
                    2
                ),

                "x1": round(
                    header_rect["x0"]
                    + fallback_width,
                    2
                ),

                "y1": round(
                    first_row_y + 2,
                    2
                )
            }

            value_font = header["font"]
            column_width = fallback_width

        table["invoice_lines"][
            "columns"
        ][column_name] = {
            "header_position": {
                "x": header_rect["x0"],
                "y": header_rect["y1"]
            },

            "write_position":
                write_position,

            "value_rect":
                value_rect,

            "column_width":
                column_width,

            "font":
                value_font
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