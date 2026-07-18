import json
from pathlib import Path
from typing import Any


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

    "Net Amount": [
        "Net Amount"
    ],

    "VAT": [
        "Total Vat",
        "VAT",
        "Vat"
    ],

    "Invoice Total": [
        "Invoice Total"
    ]
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


def find_field(
    metadata: dict[str, Any],
    aliases: list[str]
) -> dict[str, Any] | None:

    for item in metadata["fields"]:

        item_text = clean_text(
            item["text"]
        ).lower()

        for alias in aliases:

            if alias.lower() in item_text:

                return item

    return None


def build_fields(
    metadata: dict[str, Any]
) -> dict[str, Any]:

    detected: dict[
        str,
        dict[str, Any]
    ] = {}

    for field_name, aliases in (
        FIELD_RULES.items()
    ):

        field = find_field(
            metadata,
            aliases
        )

        if field is None:

            raise ValueError(
                f"Missing required template field: "
                f"{field_name}"
            )

        detected[field_name] = field

        print(
            f"✓ {field_name}"
        )


    invoice_label = detected[
        "Invoice No"
    ]

    service_label = detected[
        "Service User"
    ]

    assessor_label = detected[
        "Assessor"
    ]


    output: dict[str, Any] = {
        "template_name":
            metadata["template_name"],

        "pages":
            metadata["pages"],

        "fields": {}
    }


    #
    # Invoice No
    #

    invoice_rect = invoice_label[
        "rect"
    ]

    output["fields"]["Invoice No"] = {
        "pdf_label":
            invoice_label["text"],

        "page":
            invoice_label["page"],

        "write_position": {
            "x": round(
                invoice_rect["x1"] + 12,
                2
            ),

            "y": round(
                invoice_rect["y1"],
                2
            )
        },

        "box": {
            "x0": round(
                invoice_rect["x1"] + 10,
                2
            ),

            "x1": round(
                invoice_rect["x1"] + 80,
                2
            )
        },

        "align":
            "left",

        "font":
            invoice_label["font"]
    }


    #
    # Service User
    #

    service_rect = service_label[
        "rect"
    ]

    output["fields"]["Service User"] = {
        "pdf_label":
            service_label["text"],

        "page":
            service_label["page"],

        "write_position": {
            "x": round(
                service_rect["x0"] + 4,
                2
            ),

            "y": round(
                service_rect["y1"] + 18,
                2
            )
        },

        "box": {
            "x0": round(
                service_rect["x0"] + 4,
                2
            ),

            "x1": round(
                assessor_label["rect"]["x0"] - 4,
                2
            )
        },

        "align":
            "left",

        "font":
            service_label["font"]
    }


    #
    # BIA/DR / Assessor
    #

    assessor_rect = assessor_label[
        "rect"
    ]

    description_header = find_field(
        metadata,
        [
            "Charge Desc",
            "Charge Desc.",
            "Charge Description",
            "Description"
        ]
    )

    if description_header is None:

        assessor_right = round(
            assessor_rect["x0"] + 170,
            2
        )

    else:

        assessor_right = round(
            description_header["rect"]["x0"] - 4,
            2
        )


    output["fields"]["Assessor"] = {
        "pdf_label":
            assessor_label["text"],

        "page":
            assessor_label["page"],

        "write_position": {
            "x": round(
                assessor_rect["x0"] + 4,
                2
            ),

            "y": round(
                assessor_rect["y1"] + 18,
                2
            )
        },

        "box": {
            "x0": round(
                assessor_rect["x0"] + 4,
                2
            ),

            "x1":
                assessor_right
        },

        "align":
            "left",

        "font":
            assessor_label["font"]
    }


    #
    # Totals
    #
    # Their horizontal cell is supplied by table_metadata.json
    # in writer.py. This metadata provides the exact baseline/font.
    #

    for field_name in [
        "Net Amount",
        "VAT",
        "Invoice Total"
    ]:

        label = detected[
            field_name
        ]

        label_rect = label[
            "rect"
        ]

        output["fields"][field_name] = {
            "pdf_label":
                label["text"],

            "page":
                label["page"],

            "write_position": {
                "x": round(
                    label_rect["x1"] + 5,
                    2
                ),

                "y": round(
                    label_rect["y1"],
                    2
                )
            },

            "align":
                "right",

            "font":
                label["font"]
        }


    return output


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
