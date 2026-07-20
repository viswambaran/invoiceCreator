import json
from pathlib import Path

import streamlit as st


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[3]
)

MAPPING_FILE = (
    PROJECT_ROOT
    / "templates"
    / "mapping.json"
)


def render_mapping_tab():

    st.header("Field Mapping")

    st.caption(
        "Current Excel → Invoice field mappings."
    )

    with open(
        MAPPING_FILE,
        encoding="utf-8",
    ) as f:
        mapping = json.load(f)

    invoice = mapping["invoice"]

    rows = []

    for key, value in invoice.items():

        rows.append(
            {
                "Invoice Field": key,
                "Source": value["value"],
                "Type": value["type"],
            }
        )

    st.dataframe(
        rows,
        hide_index=True,
        width="stretch",
    )

    st.info(
        "Editing mappings will be the next feature."
    )