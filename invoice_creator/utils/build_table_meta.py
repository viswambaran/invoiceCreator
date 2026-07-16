import json
from pathlib import Path


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
        "Charge Desc."
        "Charge Description"
    ],

    "units": [
        "Units"
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



def load_json(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)



def save_json(data, path):

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )



def clean_text(text):

    return (
        text
        .replace("\n", "")
        .strip()
    )



def find_header(metadata, aliases):

    for item in metadata["fields"]:

        text = clean_text(
            item["text"]
        )

        for alias in aliases:

            if text.lower() == alias.lower():

                return item

    return None



def calculate_column_width(
        headers,
        index
):

    """
    Calculate width between
    neighbouring table columns
    """

    current_x = headers[index]["data"]["rect"]["x0"]


    if index + 1 < len(headers):

        next_x = headers[index + 1]["data"]["rect"]["x0"]

        return round(
            next_x - current_x,
            2
        )


    #
    # Last column fallback
    #

    return 60

def calculate_clear_area(
        headers,
        index
):

    """
    Area containing the existing
    template value to remove
    """

    current = headers[index]["data"]["rect"]


    x0 = current["x0"]


    y0 = current["rect"]["y1"] if "rect" in current else current["y1"]


    #
    # Start just below header
    #

    y0 = current["y1"] + 5



    #
    # Width is based on next column
    #

    if index + 1 < len(headers):

        x1 = (
            headers[index + 1]
            ["data"]
            ["rect"]
            ["x0"]
        )

    else:

        x1 = x0 + 60



    return {

        "x0": round(x0,2),

        "y0": round(y0,2),

        "x1": round(x1,2),

        "y1": round(y0 + 20,2)

    }


def build_table(metadata):


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



    #
    # Find table headers
    #

    for column, aliases in COLUMN_HEADERS.items():

        header = find_header(
            metadata,
            aliases
        )


        if header:

            detected_headers.append(
                {
                    "name": column,
                    "data": header
                }
            )


            print(
                f"✓ {column}"
            )



    #
    # Sort columns left to right
    #

    detected_headers.sort(
        key=lambda x:
        x["data"]["rect"]["x0"]
    )



    #
    # Calculate header baseline
    #

    header_y = 0


    for item in detected_headers:

        header_y = max(
            header_y,
            item["data"]["rect"]["y1"]
        )



    first_row_y = round(
        header_y + 27,
        2
    )


    table["invoice_lines"]["first_row_y"] = first_row_y



    #
    # Build columns
    #

    for index, item in enumerate(detected_headers):


        column_name = item["name"]

        rect = item["data"]["rect"]


        width = calculate_column_width(
            detected_headers,
            index
        )


        table["invoice_lines"]["columns"][column_name] = {


            "header_position": {

                "x": rect["x0"],

                "y": rect["y1"]

            },


            "column_width": width,


            "write_position": {

                "x": rect["x0"],

                "y": first_row_y,

                "align":
                    COLUMN_ALIGNMENT[column_name]

            },
            "clear_area":

                calculate_clear_area(
                    detected_headers,
                    index
                )

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