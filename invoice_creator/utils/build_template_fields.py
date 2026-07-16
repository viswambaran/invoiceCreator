import json
from pathlib import Path


INPUT_FILE = Path(
    "templates/template_metadata.json"
)

OUTPUT_FILE = Path(
    "templates/template_fields.json"
)


FIELD_RULES = {

    "Invoice No": [
        "Invoice No"
    ],

    "Service User": [
        "Service User"
    ],

    "Assessor": [
        "BIA/DR",
        "Assessor"
    ],

    "Rate": [
        "Rate"
    ],

    "Net": [
        "Net"
    ],

    "Net Amount": [
        "Net Amount"
    ],

    "VAT": [
        "VAT",
        "Vat"
    ],

    "Invoice Total": [
        "Invoice Total"
    ]

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
        .replace("\n","")
        .strip()
    )



def find_field(metadata, aliases):

    for item in metadata["fields"]:

        text = clean_text(
            item["text"]
        )

        for alias in aliases:

            if alias.lower() in text.lower():

                return item

    return None



def calculate_write_position(
        field_name,
        rect
):

    x0 = rect["x0"]
    x1 = rect["x1"]
    y1 = rect["y1"]


    # Inline value
    # Invoice No : VALUE

    if field_name == "Invoice No":

        return {

            "x": round(x1 + 5,2),
            "y": round(y1,2)

        }


    # Header/value fields
    # Header
    #
    # Value below

    if field_name in [
        "Service User",
        "Assessor"
    ]:

        return {

            "x": round(x0,2),
            "y": round(y1 + 18,2)

        }


    # Table headers
    #
    # Actual writing handled separately
    if field_name in [
        "Rate",
        "Net"
    ]:

        return {

            "x": round(x0,2),
            "y": round(y1 + 25,2)

        }



    # Totals
    #
    # Label          VALUE

    if field_name in [
        "Net Amount",
        "VAT",
        "Invoice Total"
    ]:

        return {

            "x": round(x1 + 20,2),
            "y": round(y1,2)

        }



    return {

        "x": round(x0,2),
        "y": round(y1,2)

    }



def build_fields(metadata):


    output = {

        "template_name":
            metadata["template_name"],

        "pages":
            metadata["pages"],

        "fields": {}

    }


    for field_name, aliases in FIELD_RULES.items():


        field = find_field(
            metadata,
            aliases
        )


        if field:


            output["fields"][field_name] = {


                "pdf_label":
                    field["text"],


                "page":
                    field["page"],


                "label_rect":
                    field["rect"],


                "write_position":
                    calculate_write_position(
                        field_name,
                        field["rect"]
                    ),
                
                "clear_area":
                    calculate_clear_area(
                        field_name,
                        field["rect"]
                    ),


                "font":
                    field["font"]

            }


            print(
                f"✓ {field_name}"
            )


        else:

            print(
                f"⚠ Missing {field_name}"
            )


    return output

def calculate_clear_area(
        field_name,
        rect
):

    """
    Area to remove before writing replacement value
    """

    x0 = rect["x0"]

    y0 = rect["y0"] - 2

    x1 = rect["x1"] + 80

    y1 = rect["y1"] + 5


    return {

        "x0": round(x0, 2),

        "y0": round(y0, 2),

        "x1": round(x1, 2),

        "y1": round(y1, 2)

    }

if __name__ == "__main__":


    metadata = load_json(
        INPUT_FILE
    )


    fields = build_fields(
        metadata
    )


    save_json(
        fields,
        OUTPUT_FILE
    )


    print()
    print(
        "Template fields rebuilt"
    )