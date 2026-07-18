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
    Find the nearest extracted item on the same line
    and to the right of the supplied label.
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

        to_the_right = (
            rect["x0"]
            >= label_rect["x1"]
        )

        if same_line and to_the_right:

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


def make_text_band(
    x0: float,
    x1: float,
    baseline_y: float,
    font_size: float,
    left_inset: float = 1.0,
    right_inset: float = 1.0
) -> dict[str, float]:
    """
    Produce a narrow whiteout rectangle around the text glyph band.

    It deliberately avoids the top, bottom and vertical cell borders.
    """

    return {
        "x0": round(
            x0 + left_inset,
            2
        ),

        "y0": round(
            baseline_y
            - font_size
            - 0.5,
            2
        ),

        "x1": round(
            x1 - right_inset,
            2
        ),

        "y1": round(
            baseline_y + 0.75,
            2
        )
    }


def exact_safe_rect(
    rect: dict[str, float]
) -> dict[str, float]:
    """
    Use the extracted text rectangle itself as the safe clear region.

    No expansion is applied because totals sit inside tightly bordered rows.
    """

    return {
        "x0": round(
            rect["x0"],
            2
        ),

        "y0": round(
            rect["y0"],
            2
        ),

        "x1": round(
            rect["x1"],
            2
        ),

        "y1": round(
            rect["y1"],
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


    required_fields = set(
        FIELD_RULES.keys()
    )

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


    output: dict[str, Any] = {
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

    invoice_rect = (
        invoice_label["rect"]
    )

    invoice_font = (
        invoice_label["font"]
    )

    invoice_font_size = float(
        invoice_font["size"]
    )

    invoice_write_x = round(
        invoice_rect["x1"] + 12,
        2
    )

    invoice_write_y = round(
        invoice_rect["y1"],
        2
    )

    invoice_value_rect = {
        "x0": round(
            invoice_write_x - 2,
            2
        ),

        "y0": round(
            invoice_write_y
            - invoice_font_size
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
    }

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

        "value_rect":
            invoice_value_rect,

        "safe_clear_rect":
            make_text_band(
                x0=invoice_value_rect["x0"],
                x1=invoice_value_rect["x1"],
                baseline_y=invoice_write_y,
                font_size=invoice_font_size
            ),

        "font":
            invoice_font
    }


    #
    # Service User
    #

    service_rect = (
        service_label["rect"]
    )

    service_font = (
        service_label["font"]
    )

    service_font_size = float(
        service_font["size"]
    )

    service_write_x = round(
        service_rect["x0"] + 4,
        2
    )

    service_write_y = round(
        service_rect["y1"] + 18,
        2
    )

    service_cell_x0 = float(
        service_rect["x0"]
    )

    service_cell_x1 = round(
        assessor_label["rect"]["x0"],
        2
    )

    service_value_rect = {
        "x0":
            service_cell_x0,

        "y0": round(
            service_write_y
            - service_font_size
            - 2,
            2
        ),

        "x1":
            service_cell_x1,

        "y1": round(
            service_write_y + 2,
            2
        )
    }

    output["fields"]["Service User"] = {
        "pdf_label":
            service_label["text"],

        "page":
            service_label["page"],

        "label_rect":
            service_rect,

        "write_position": {
            "x":
                service_write_x,

            "y":
                service_write_y
        },

        "value_rect":
            service_value_rect,

        "safe_clear_rect":
            make_text_band(
                x0=service_cell_x0,
                x1=service_cell_x1,
                baseline_y=service_write_y,
                font_size=service_font_size,
                left_inset=2,
                right_inset=2
            ),

        "font":
            service_font
    }


    #
    # BIA/DR / Assessor
    #

    assessor_rect = (
        assessor_label["rect"]
    )

    assessor_font = (
        assessor_label["font"]
    )

    assessor_font_size = float(
        assessor_font["size"]
    )

    assessor_write_x = round(
        assessor_rect["x0"] + 4,
        2
    )

    assessor_write_y = round(
        assessor_rect["y1"] + 18,
        2
    )

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

        assessor_cell_x1 = round(
            description_header["rect"]["x0"],
            2
        )

    else:

        assessor_cell_x1 = round(
            assessor_rect["x0"] + 175,
            2
        )

    assessor_cell_x0 = float(
        assessor_rect["x0"]
    )

    assessor_value_rect = {
        "x0":
            assessor_cell_x0,

        "y0": round(
            assessor_write_y
            - assessor_font_size
            - 2,
            2
        ),

        "x1":
            assessor_cell_x1,

        "y1": round(
            assessor_write_y + 2,
            2
        )
    }

    output["fields"]["Assessor"] = {
        "pdf_label":
            assessor_label["text"],

        "page":
            assessor_label["page"],

        "label_rect":
            assessor_rect,

        "write_position": {
            "x":
                assessor_write_x,

            "y":
                assessor_write_y
        },

        "value_rect":
            assessor_value_rect,

        "safe_clear_rect":
            make_text_band(
                x0=assessor_cell_x0,
                x1=assessor_cell_x1,
                baseline_y=assessor_write_y,
                font_size=assessor_font_size,
                left_inset=2,
                right_inset=2
            ),

        "font":
            assessor_font
    }


    #
    # Totals
    #

    for field_name in [
        "Net Amount",
        "VAT",
        "Invoice Total"
    ]:

        label = detected[
            field_name
        ]

        original_value = (
            find_inline_value(
                metadata,
                label
            )
        )

        if original_value:

            original_rect = (
                original_value["rect"]
            )

            write_position = {
                "x": round(
                    original_rect["x0"],
                    2
                ),

                "y": round(
                    original_rect["y1"],
                    2
                )
            }

            value_font = (
                original_value.get(
                    "font",
                    label["font"]
                )
            )

            value_rect = (
                exact_safe_rect(
                    original_rect
                )
            )

            safe_clear_rect = (
                exact_safe_rect(
                    original_rect
                )
            )

        else:

            label_rect = (
                label["rect"]
            )

            value_font = (
                label["font"]
            )

            font_size = float(
                value_font["size"]
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
                    - font_size
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

            safe_clear_rect = (
                make_text_band(
                    x0=value_rect["x0"],
                    x1=value_rect["x1"],
                    baseline_y=write_y,
                    font_size=font_size,
                    left_inset=1,
                    right_inset=1
                )
            )


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

            "safe_clear_rect":
                safe_clear_rect,

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