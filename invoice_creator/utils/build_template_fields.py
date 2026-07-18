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

        text = clean_text(
            item["text"]
        ).lower()

        for alias in aliases:

            if alias.lower() in text:

                return item

    return None


def find_inline_value(
    metadata: dict[str, Any],
    label: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Find the closest extracted value on the same line,
    immediately to the right of the supplied label.

    Used only for the three totals fields.
    """

    label_rect = label["rect"]
    candidates = []

    for item in metadata["fields"]:

        if item is label:
            continue

        if item["page"] != label["page"]:
            continue

        rect = item["rect"]

        same_line = (
            abs(
                rect["y1"]
                - label_rect["y1"]
            )
            <= 3
        )

        is_to_right = (
            rect["x0"]
            >= label_rect["x1"]
        )

        if same_line and is_to_right:

            candidates.append(
                item
            )

    if not candidates:

        return None

    return min(
        candidates,
        key=lambda item:
        item["rect"]["x0"]
    )


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


def build_fields(
    metadata: dict[str, Any]
) -> dict[str, Any]:

    detected: dict[
        str,
        dict[str, Any]
    ] = {}


    #
    # Locate required labels
    #

    for field_name, aliases in (
        FIELD_RULES.items()
    ):

        field = find_field(
            metadata,
            aliases
        )

        if field:

            detected[field_name] = field

            print(
                f"✓ {field_name}"
            )

        else:

            print(
                f"⚠ Missing {field_name}"
            )


    required_fields = {
        "Invoice No",
        "Service User",
        "Assessor",
        "Net Amount",
        "VAT",
        "Invoice Total"
    }

    missing_fields = (
        required_fields
        - detected.keys()
    )

    if missing_fields:

        raise ValueError(
            "Missing required PDF fields: "
            + ", ".join(
                sorted(
                    missing_fields
                )
            )
        )


    output = {
        "template_name":
            metadata["template_name"],

        "pages":
            metadata["pages"],

        "fields": {}
    }


    invoice_label = (
        detected["Invoice No"]
    )

    service_label = (
        detected["Service User"]
    )

    assessor_label = (
        detected["Assessor"]
    )


    #
    # Invoice No
    #
    # Positioned twelve points after the end of
    # the "Invoice No :" label.
    #

    invoice_rect = (
        invoice_label["rect"]
    )

    invoice_font = (
        invoice_label["font"]
    )

    invoice_write_x = round(
        invoice_rect["x1"] + 12,
        2
    )

    invoice_write_y = round(
        invoice_rect["y1"],
        2
    )

    output["fields"]["Invoice No"] = {
        "pdf_label":
            invoice_label["text"],

        "page":
            invoice_label["page"],

        "label_rect":
            invoice_rect,

        "write_position": {
            "x":
                invoice_write_x,

            "y":
                invoice_write_y
        },

        "value_rect": {
            "x0": round(
                invoice_write_x - 2,
                2
            ),

            "y0": round(
                invoice_write_y
                - float(
                    invoice_font["size"]
                )
                - 2,
                2
            ),

            "x1": round(
                invoice_write_x + 70,
                2
            ),

            "y1": round(
                invoice_write_y + 2,
                2
            )
        },

        "font":
            invoice_font
    }


    #
    # Service User
    #

    service_rect = service_label["rect"]
    service_font = service_label["font"]

    service_write_y = round(
        service_rect["y1"] + 18,
        2
    )

    output["fields"]["Service User"] = {
        "pdf_label": service_label["text"],
        "page": service_label["page"],
        "label_rect": service_rect,

        "write_position": {
            "x": round(
                service_rect["x0"] + 4,
                2
            ),
            "y": service_write_y
        },

        "value_rect": {
            "x0": round(
                service_rect["x0"],
                2
            ),
            "y0": round(
                service_write_y
                - float(service_font["size"])
                - 2,
                2
            ),
            "x1": round(
                assessor_label["rect"]["x0"] - 2,
                2
            ),
            "y1": round(
                service_write_y + 2,
                2
            )
        },

        "font": service_font
    }


    #
    # BIA/DR / Assessor
    #

    assessor_rect = assessor_label["rect"]
    assessor_font = assessor_label["font"]

    description_header = find_field(
        metadata,
        [
            "Charge Desc",
            "Charge Desc.",
            "Charge Description",
            "Description"
        ]
    )

    if description_header:
        assessor_right = round(
            description_header["rect"]["x0"] - 2,
            2
        )
    else:
        assessor_right = round(
            assessor_rect["x0"] + 175,
            2
        )

    output["fields"]["Assessor"] = {
        "pdf_label": assessor_label["text"],
        "page": assessor_label["page"],
        "label_rect": assessor_rect,

        "write_position": {
            "x": round(
                assessor_rect["x0"] + 4,
                2
            ),
            "y": service_write_y
        },

        "value_rect": {
            "x0": round(
                assessor_rect["x0"],
                2
            ),
            "y0": round(
                service_write_y
                - float(assessor_font["size"])
                - 2,
                2
            ),
            "x1": assessor_right,
            "y1": round(
                service_write_y + 2,
                2
            )
        },

        "font": assessor_font
    }


    #
    # Totals
    #
    # The existing numeric value beside each label is
    # extracted and used for its exact position.
    #

    for field_name in [
        "Net Amount",
        "VAT",
        "Invoice Total"
    ]:

        label = detected[
            field_name
        ]

        original_value = find_inline_value(
            metadata,
            label
        )

        if original_value:

            value_rect = {
                "x0": round(
                    original_value["rect"]["x0"],
                    2
                ),
                "y0": round(
                    original_value["rect"]["y0"],
                    2
                ),
                "x1": round(
                    original_value["rect"]["x1"],
                    2
                ),
                "y1": round(
                    original_value["rect"]["y1"],
                    2
                )
            }

            write_position = {
                "x": round(
                    original_value
                    ["rect"]
                    ["x0"],
                    2
                ),

                "y": round(
                    original_value
                    ["rect"]
                    ["y1"],
                    2
                )
            }

            value_font = (
                original_value.get(
                    "font",
                    label["font"]
                )
            )

        else:

            label_rect = (
                label["rect"]
            )

            value_font = (
                label["font"]
            )

            write_x = round(
                label_rect["x1"] + 5,
                2
            )

            write_y = round(
                label_rect["y1"],
                2
            )

            write_position = {
                "x":
                    write_x,

                "y":
                    write_y
            }

            value_rect = {
                "x0": round(
                    write_x - 2,
                    2
                ),

                "y0": round(
                    write_y
                    - float(
                        value_font["size"]
                    )
                    - 2,
                    2
                ),

                "x1": round(
                    write_x + 85,
                    2
                ),

                "y1": round(
                    write_y + 2,
                    2
                )
            }


        #
        # Slight vertical adjustment requested for
        # the Invoice Total row.
        #

        # if field_name == "Invoice Total":

        #     write_position["y"] = round(
        #         write_position["y"] - 1,
        #         2
        #     )

        #     value_rect["y0"] = round(
        #         value_rect["y0"] - 1,
        #         2
        #     )

        #     value_rect["y1"] = round(
        #         value_rect["y1"] - 1,
        #         2
        #     )


        output["fields"][field_name] = {
            "pdf_label":
                label["text"],

            "page":
                label["page"],

            "label_rect":
                label["rect"],

            "write_position":
                write_position,

            "value_rect":
                value_rect,

            "font":
                value_font
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