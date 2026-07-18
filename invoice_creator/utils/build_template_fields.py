import json
from pathlib import Path
from typing import Any


INPUT_FILE = Path(
    "templates/template_metadata.json"
)

TABLE_FILE = Path(
    "templates/table_metadata.json"
)

OUTPUT_FILE = Path(
    "templates/template_fields.json"
)


FIELD_RULES = {
    "Invoice No": [
        "Invoice No",
    ],

    "Service User": [
        "Service User",
    ],

    "Assessor": [
        "BIA/DR",
        "Assessor",
    ],

    "Net Amount": [
        "Net Amount",
    ],

    "VAT": [
        "Total Vat",
        "VAT",
        "Vat",
    ],

    "Invoice Total": [
        "Invoice Total",
    ],
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


def build_fields(
    metadata: dict[str, Any],
    table_metadata: dict[str, Any]
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

    output: dict[str, Any] = {
        "template_name":
            metadata["template_name"],

        "pages":
            metadata["pages"],

        "fields":
            {},
    }

    invoice_label = detected[
        "Invoice No"
    ]

    invoice_rect = invoice_label[
        "rect"
    ]

    output["fields"]["Invoice No"] = {
        "pdf_label":
            invoice_label["text"],

        "page":
            invoice_label["page"],

        "cell": {
            "x0": round(
                invoice_rect["x1"] + 8,
                2
            ),

            "x1": round(
                invoice_rect["x1"] + 85,
                2
            ),
        },

        "write_position": {
            "x": round(
                invoice_rect["x1"] + 12,
                2
            ),

            "y": round(
                invoice_rect["y1"],
                2
            ),
        },

        "align":
            "left",

        "font":
            invoice_label["font"],
    }

    header_cells = table_metadata[
        "header_value_cells"
    ]

    first_row_y = table_metadata[
        "invoice_lines"
    ][
        "first_row_y"
    ]

    for field_name in [
        "Service User",
        "Assessor",
    ]:

        label = detected[
            field_name
        ]

        cell_metadata = header_cells[
            field_name
        ]

        cell = cell_metadata[
            "cell"
        ]

        output["fields"][field_name] = {
            "pdf_label":
                label["text"],

            "page":
                label["page"],

            "cell": {
                "x0":
                    cell["x0"],

                "x1":
                    cell["x1"],
            },

            "write_position": {
                "x": round(
                    cell["x0"] + 7,
                    2
                ),

                "y":
                    first_row_y,
            },

            "align":
                "left",

            "font":
                label["font"],
        }

    total_value_cell = (
        table_metadata
        ["totals"]
        ["value_cell"]
    )

    for field_name in [
        "Net Amount",
        "VAT",
        "Invoice Total",
    ]:

        label = detected[
            field_name
        ]

        output["fields"][field_name] = {
            "pdf_label":
                label["text"],

            "page":
                label["page"],

            "cell": {
                "x0":
                    total_value_cell["x0"],

                "x1":
                    total_value_cell["x1"],
            },

            "write_position": {
                "x":
                    total_value_cell["x0"],

                "y": round(
                    label["rect"]["y1"],
                    2
                ),
            },

            "align":
                "right",

            "font":
                label["font"],
        }

    return output


if __name__ == "__main__":

    metadata = load_json(
        INPUT_FILE
    )

    table_metadata = load_json(
        TABLE_FILE
    )

    fields = build_fields(
        metadata,
        table_metadata
    )

    save_json(
        fields,
        OUTPUT_FILE
    )

    print()
    print(
        "Template fields rebuilt"
    )