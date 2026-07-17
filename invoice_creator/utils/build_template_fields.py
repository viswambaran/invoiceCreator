# # import json
# # from pathlib import Path


# # INPUT_FILE = Path(
# #     "templates/template_metadata.json"
# # )

# # OUTPUT_FILE = Path(
# #     "templates/template_fields.json"
# # )


# # FIELD_RULES = {

# #     "Invoice No": [
# #         "Invoice No"
# #     ],

# #     "Service User": [
# #         "Service User"
# #     ],

# #     "Assessor": [
# #         "BIA/DR",
# #         "Assessor"
# #     ],

# #     "Net Amount": [
# #         "Net Amount"
# #     ],

# #     "VAT": [
# #         "VAT",
# #         "Vat"
# #     ],

# #     "Invoice Total": [
# #         "Invoice Total"
# #     ]

# # }



# # def load_json(path):

# #     with open(
# #         path,
# #         "r",
# #         encoding="utf-8"
# #     ) as f:
# #         return json.load(f)



# # def save_json(data, path):

# #     with open(
# #         path,
# #         "w",
# #         encoding="utf-8"
# #     ) as f:

# #         json.dump(
# #             data,
# #             f,
# #             indent=4
# #         )



# # def clean_text(text):

# #     return (
# #         text
# #         .replace("\n","")
# #         .strip()
# #     )



# # def find_field(metadata, aliases):

# #     for item in metadata["fields"]:

# #         text = clean_text(
# #             item["text"]
# #         )

# #         for alias in aliases:

# #             if alias.lower() in text.lower():

# #                 return item

# #     return None



# # def calculate_write_position(
# #         field_name,
# #         rect
# # ):

# #     x0 = rect["x0"]
# #     x1 = rect["x1"]
# #     y1 = rect["y1"]


# #     # Inline value
# #     # Invoice No : VALUE

# #     if field_name == "Invoice No":

# #         return {

# #             "x": round(x1 + 21,2),
# #             "y": round(y1,2)

# #         }


# #     # Header/value fields
# #     # Header
# #     #
# #     # Value below

# #     if field_name in [
# #         "Service User",
# #         "Assessor"
# #     ]:

# #         return {

# #             "x": round(x0,2),
# #             "y": round(y1 + 21,2)

# #         }


# #     # Table headers
# #     #
# #     # Actual writing handled separately
# #     if field_name in [
# #         "Rate",
# #         "Net"
# #     ]:

# #         return {

# #             "x": round(x0,2),
# #             "y": round(y1 + 25,2)

# #         }



# #     # Totals
# #     #
# #     # Label          VALUE

# #     if field_name in [
# #         "Net Amount",
# #         "VAT",
# #         "Invoice Total"
# #     ]:

# #         return {

# #             "x": round(x1 + 5,2),
# #             "y": round(y1,2)

# #         }



# #     return {

# #         "x": round(x0,2),
# #         "y": round(y1,2)

# #     }



# # def build_fields(metadata):


# #     output = {

# #         "template_name":
# #             metadata["template_name"],

# #         "pages":
# #             metadata["pages"],

# #         "fields": {}

# #     }


# #     for field_name, aliases in FIELD_RULES.items():


# #         field = find_field(
# #             metadata,
# #             aliases
# #         )


# #         if field:


# #             output["fields"][field_name] = {


# #                 "pdf_label":
# #                     field["text"],


# #                 "page":
# #                     field["page"],


# #                 "label_rect":
# #                     field["rect"],


# #                 "write_position":
# #                     calculate_write_position(
# #                         field_name,
# #                         field["rect"]
# #                     ),
                
# #                 "clear_area":
# #                     calculate_clear_area(
# #                         field_name,
# #                         field["rect"]
# #                     ),


# #                 "font":
# #                     field["font"]

# #             }


# #             print(
# #                 f"✓ {field_name}"
# #             )


# #         else:

# #             print(
# #                 f"⚠ Missing {field_name}"
# #             )


# #     return output

# # def calculate_clear_area(
# #         field_name,
# #         rect
# # ):


# #     if field_name == "Invoice No":

# #         return {

# #             "x0": round(rect["x1"] + 3, 2),

# #             "y0": round(rect["y0"] - 1, 2),

# #             "x1": round(rect["x1"] + 55, 2),

# #             "y1": round(rect["y1"] + 1, 2)

# #         }


# #     if field_name in [
# #         "Service User",
# #         "Assessor"
# #     ]:

# #         return {

# #             "x0": round(rect["x0"], 2),

# #             "y0": round(rect["y0"] + 2, 2),

# #             "x1": round(rect["x1"] + 150, 2),

# #             "y1": round(rect["y1"] + 21, 2)

# #         }


# #     if field_name in [
# #         "Net Amount",
# #         "VAT",
# #         "Invoice Total"
# #     ]:

# #         return {

# #             "x0": round(rect["x1"] + 5, 2),

# #             "y0": round(rect["y0"] - 1, 2),

# #             "x1": round(rect["x1"] + 85, 2),

# #             "y1": round(rect["y1"] + 1, 2)

# #         }


# #     #
# #     # fallback
# #     #

# #     return None

# # if __name__ == "__main__":


# #     metadata = load_json(
# #         INPUT_FILE
# #     )


# #     fields = build_fields(
# #         metadata
# #     )


# #     save_json(
# #         fields,
# #         OUTPUT_FILE
# #     )


# #     print()
# #     print(
# #         "Template fields rebuilt"
# #     )


# ##NEW VERSION

# import json
# from pathlib import Path
# from typing import Any


# INPUT_FILE = Path(
#     "templates/template_metadata.json"
# )

# OUTPUT_FILE = Path(
#     "templates/template_fields.json"
# )


# FIELD_RULES = {
#     "Invoice No": [
#         "Invoice No"
#     ],

#     "Service User": [
#         "Service User"
#     ],

#     "Assessor": [
#         "BIA/DR",
#         "Assessor"
#     ],

#     "Net Amount": [
#         "Net Amount"
#     ],

#     "VAT": [
#         "Total Vat",
#         "VAT",
#         "Vat"
#     ],

#     "Invoice Total": [
#         "Invoice Total"
#     ]
# }


# def load_json(path: Path) -> dict[str, Any]:
#     with open(
#         path,
#         "r",
#         encoding="utf-8"
#     ) as file:
#         return json.load(file)


# def save_json(
#     data: dict[str, Any],
#     path: Path
# ) -> None:
#     with open(
#         path,
#         "w",
#         encoding="utf-8"
#     ) as file:
#         json.dump(
#             data,
#             file,
#             indent=4
#         )


# def clean_text(text: str) -> str:
#     return " ".join(
#         text.replace(
#             "\n",
#             " "
#         ).split()
#     )


# def find_field(
#     metadata: dict[str, Any],
#     aliases: list[str]
# ) -> dict[str, Any] | None:
#     for item in metadata["fields"]:
#         text = clean_text(
#             item["text"]
#         ).lower()

#         for alias in aliases:
#             if alias.lower() in text:
#                 return item

#     return None


# def same_line(
#     first_rect: dict[str, float],
#     second_rect: dict[str, float],
#     tolerance: float = 3
# ) -> bool:
#     return abs(
#         first_rect["y1"]
#         - second_rect["y1"]
#     ) <= tolerance


# def expand_rect(
#     rect: dict[str, float],
#     horizontal: float = 2,
#     vertical: float = 1
# ) -> dict[str, float]:
#     return {
#         "x0": round(
#             rect["x0"] - horizontal,
#             2
#         ),

#         "y0": round(
#             rect["y0"] - vertical,
#             2
#         ),

#         "x1": round(
#             rect["x1"] + horizontal,
#             2
#         ),

#         "y1": round(
#             rect["y1"] + vertical,
#             2
#         )
#     }


# def find_inline_value(
#     metadata: dict[str, Any],
#     label: dict[str, Any]
# ) -> dict[str, Any] | None:
#     label_rect = label["rect"]

#     candidates = []

#     for item in metadata["fields"]:
#         if item is label:
#             continue

#         if item["page"] != label["page"]:
#             continue

#         rect = item["rect"]

#         if (
#             rect["x0"] >= label_rect["x1"]
#             and same_line(
#                 label_rect,
#                 rect
#             )
#         ):
#             candidates.append(item)

#     if not candidates:
#         return None

#     return min(
#         candidates,
#         key=lambda item:
#         item["rect"]["x0"]
#     )


# def find_value_below(
#     metadata: dict[str, Any],
#     label: dict[str, Any],
#     x1_limit: float
# ) -> dict[str, Any] | None:
#     label_rect = label["rect"]

#     candidates = []

#     for item in metadata["fields"]:
#         if item is label:
#             continue

#         if item["page"] != label["page"]:
#             continue

#         rect = item["rect"]

#         if not (
#             label_rect["x0"] - 2
#             <= rect["x0"]
#             < x1_limit
#         ):
#             continue

#         if not (
#             label_rect["y1"] + 2
#             <= rect["y0"]
#             <= label_rect["y1"] + 30
#         ):
#             continue

#         candidates.append(item)

#     if not candidates:
#         return None

#     return min(
#         candidates,
#         key=lambda item: (
#             item["rect"]["y0"],
#             item["rect"]["x0"]
#         )
#     )


# def fallback_write_position(
#     field_name: str,
#     rect: dict[str, float]
# ) -> dict[str, float]:
#     if field_name == "Invoice No":
#         return {
#             "x": round(
#                 rect["x1"] + 21,
#                 2
#             ),

#             "y": round(
#                 rect["y1"],
#                 2
#             )
#         }

#     if field_name in {
#         "Service User",
#         "Assessor"
#     }:
#         return {
#             "x": round(
#                 rect["x0"],
#                 2
#             ),

#             "y": round(
#                 rect["y1"] + 21,
#                 2
#             )
#         }

#     if field_name in {
#         "Net Amount",
#         "VAT",
#         "Invoice Total"
#     }:
#         return {
#             "x": round(
#                 rect["x1"] + 5,
#                 2
#             ),

#             "y": round(
#                 rect["y1"],
#                 2
#             )
#         }

#     return {
#         "x": round(
#             rect["x0"],
#             2
#         ),

#         "y": round(
#             rect["y1"],
#             2
#         )
#     }


# def fallback_value_rect(
#     write_position: dict[str, float],
#     font: dict[str, Any],
#     width: float = 80
# ) -> dict[str, float]:
#     font_size = float(
#         font["size"]
#     )

#     return {
#         "x0": round(
#             write_position["x"] - 2,
#             2
#         ),

#         "y0": round(
#             write_position["y"]
#             - font_size
#             - 2,
#             2
#         ),

#         "x1": round(
#             write_position["x"]
#             + width,
#             2
#         ),

#         "y1": round(
#             write_position["y"] + 2,
#             2
#         )
#     }


# def build_fields(
#     metadata: dict[str, Any]
# ) -> dict[str, Any]:
#     detected = {}

#     for field_name, aliases in FIELD_RULES.items():
#         field = find_field(
#             metadata,
#             aliases
#         )

#         if field:
#             detected[field_name] = field
#             print(
#                 f"✓ {field_name}"
#             )
#         else:
#             print(
#                 f"⚠ Missing {field_name}"
#             )

#     output = {
#         "template_name":
#             metadata["template_name"],

#         "pages":
#             metadata["pages"],

#         "fields": {}
#     }

#     assessor_label = detected.get(
#         "Assessor"
#     )

#     description_header = find_field(
#         metadata,
#         [
#             "Charge Desc",
#             "Charge Description",
#             "Description"
#         ]
#     )

#     for field_name, field in detected.items():
#         value_item = None

#         if field_name in {
#             "Invoice No",
#             "Net Amount",
#             "VAT",
#             "Invoice Total"
#         }:
#             value_item = find_inline_value(
#                 metadata,
#                 field
#             )

#         elif field_name == "Service User":
#             if assessor_label:
#                 x1_limit = (
#                     assessor_label
#                     ["rect"]
#                     ["x0"]
#                 )
#             else:
#                 x1_limit = (
#                     field["rect"]["x1"]
#                     + 180
#                 )

#             value_item = find_value_below(
#                 metadata,
#                 field,
#                 x1_limit
#             )

#         elif field_name == "Assessor":
#             if description_header:
#                 x1_limit = (
#                     description_header
#                     ["rect"]
#                     ["x0"]
#                 )
#             else:
#                 x1_limit = (
#                     field["rect"]["x1"]
#                     + 180
#                 )

#             value_item = find_value_below(
#                 metadata,
#                 field,
#                 x1_limit
#             )

#         if value_item:
#             value_rect = expand_rect(
#                 value_item["rect"]
#             )

#             write_position = {
#                 "x": round(
#                     value_item
#                     ["rect"]
#                     ["x0"],
#                     2
#                 ),

#                 "y": round(
#                     value_item
#                     ["rect"]
#                     ["y1"],
#                     2
#                 )
#             }

#             value_font = value_item.get(
#                 "font",
#                 field["font"]
#             )

#         else:
#             write_position = (
#                 fallback_write_position(
#                     field_name,
#                     field["rect"]
#                 )
#             )

#             value_font = field["font"]

#             value_rect = (
#                 fallback_value_rect(
#                     write_position,
#                     value_font
#                 )
#             )

#         output["fields"][field_name] = {
#             "pdf_label":
#                 field["text"],

#             "page":
#                 field["page"],

#             "label_rect":
#                 field["rect"],

#             "write_position":
#                 write_position,

#             "value_rect":
#                 value_rect,

#             "font":
#                 value_font
#         }

#             #
#     # Ensure the BIA/DR value uses the same row geometry
#     # as the Service User value.
#     #
#     # Some PDFs split the Assessor label and its existing value
#     # into separate extraction groups, so automatic value detection
#     # can miss Beth Instone even though the column is present.
#     #

#     if (
#         "Service User" in output["fields"]
#         and "Assessor" in output["fields"]
#     ):
#         service_metadata = (
#             output["fields"]["Service User"]
#         )

#         assessor_metadata = (
#             output["fields"]["Assessor"]
#         )

#         assessor_label_rect = (
#             assessor_metadata["label_rect"]
#         )

#         description_header = find_field(
#             metadata,
#             [
#                 "Charge Desc",
#                 "Charge Desc.",
#                 "Charge Description",
#                 "Description"
#             ]
#         )

#         if description_header:
#             assessor_column_right = (
#                 description_header
#                 ["rect"]
#                 ["x0"]
#                 - 2
#             )
#         else:
#             assessor_column_right = (
#                 assessor_label_rect["x1"]
#                 + 165
#             )

#         assessor_metadata["write_position"] = {
#             "x": round(
#                 assessor_label_rect["x0"] + 2,
#                 2
#             ),

#             "y": round(
#                 service_metadata
#                 ["write_position"]
#                 ["y"],
#                 2
#             )
#         }

#         assessor_metadata["value_rect"] = {
#             "x0": round(
#                 assessor_label_rect["x0"] + 1,
#                 2
#             ),

#             "y0": round(
#                 service_metadata
#                 ["value_rect"]
#                 ["y0"],
#                 2
#             ),

#             "x1": round(
#                 assessor_column_right,
#                 2
#             ),

#             "y1": round(
#                 service_metadata
#                 ["value_rect"]
#                 ["y1"],
#                 2
#             )
#         }

#     return output


# if __name__ == "__main__":
#     metadata = load_json(
#         INPUT_FILE
#     )

#     fields = build_fields(
#         metadata
#     )

#     save_json(
#         fields,
#         OUTPUT_FILE
#     )

#     print()
#     print(
#         "Template fields rebuilt"
#     )

## new version 1707261400

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

        if (
            same_line
            and is_to_right
        ):

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

    detected = {}

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
    # Use fixed geometry from the known label.
    # Do not try to infer the existing value.
    #

     #
    # Invoice No
    #
    # Known template geometry:
    # the value begins five points after the label.
    #

    invoice_rect = invoice_label["rect"]
    invoice_font = invoice_label["font"]

    invoice_write_x = round(
        invoice_rect["x1"] + 5,
        2
    )

    invoice_write_y = round(
        invoice_rect["y1"],
        2
    )

    output["fields"]["Invoice No"] = {
        "pdf_label": invoice_label["text"],
        "page": invoice_label["page"],
        "label_rect": invoice_rect,

        "write_position": {
            "x": invoice_write_x,
            "y": invoice_write_y
        },

        "value_rect": {
            "x0": round(
                invoice_write_x - 2,
                2
            ),

            "y0": round(
                invoice_write_y
                - float(invoice_font["size"])
                - 2,
                2
            ),

            "x1": round(
                invoice_write_x + 62,
                2
            ),

            "y1": round(
                invoice_write_y + 2,
                2
            )
        },

        "font": invoice_font
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
                service_rect["x0"],
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
                assessor_rect["x0"],
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
    # The Charge Desc column begins at x=829-ish in the PDF
    # extraction coordinate system used by this template, but the
    # actual assessor cell boundary can be derived safely from the
    # known table header where available.
    #

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
            description_header
            ["rect"]
            ["x0"]
            - 2,
            2
        )

    else:

        assessor_right = round(
            assessor_rect["x0"] + 175,
            2
        )


    output["fields"]["Assessor"] = {
        "pdf_label":
            assessor_label["text"],

        "page":
            assessor_label["page"],

        "label_rect":
            assessor_rect,

        "write_position": {
            "x": round(
                assessor_rect["x0"] + 2,
                2
            ),

            "y":
                assessor_write_y
        },

        "value_rect": {
            "x0": round(
                assessor_rect["x0"] + 1,
                2
            ),

            "y0": round(
                assessor_write_y
                - float(assessor_font["size"])
                - 2,
                2
            ),

            "x1":
                assessor_right,

            "y1": round(
                assessor_write_y + 2,
                2
            )
        },

        "font":
            assessor_font
    }


    #
    # Totals
    #
    # Inline values can safely use their extracted original values.
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

            value_rect = expand_rect(
                original_value["rect"],
                horizontal=2,
                vertical=1
            )

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
                "x": write_x,
                "y": write_y
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
        # Move Invoice Total one point upward.
        #

        if field_name == "Invoice Total":

            write_position["y"] = round(
                write_position["y"] - 1,
                2
            )

            value_rect["y0"] = round(
                value_rect["y0"] - 1,
                2
            )

            value_rect["y1"] = round(
                value_rect["y1"] - 1,
                2
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