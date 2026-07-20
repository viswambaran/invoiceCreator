from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any

import streamlit as st


WORKFLOW_STEPS = [
    "Upload",
    "Review",
    "Mapping",
    "Layout",
    "Generate",
]


DEFAULT_STATE: dict[str, Any] = {
    # Workflow navigation
    "workflow_step": "Upload",
    "requested_workflow_step": None,
    "pending_toast": None,

    # Excel upload
    "excel_file": None,
    "excel_bytes": None,
    "excel_filename": None,
    "sheet_names": [],
    "selected_sheet": None,
    "workbook_dataframe": None,

    # Optional PDF template upload
    "template_file": None,
    "template_bytes": None,
    "template_filename": None,

    # Invoice settings
    "invoice_date_mode": "One date for all invoices",
    "invoice_date": date.today(),
    "excel_date_column": None,
    "vat_rate": 20.0,
    "default_units": 1.0,
    "include_zero_lines": True,

    # Built invoices and validation
    "invoices": [],
    "validation": [],
    "invoice_selection": {},
    "selected_invoice": None,

    # Mapping and layout
    "mapping": None,
    "mapping_rules": None,
    "layout_offsets": {
        "x": 0.0,
        "y": 0.0,
    },

    # Generation
    "generation_result": None,
    "generated_zip": None,
}


def initialise_state() -> None:
    for key, default_value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(
                default_value
            )


def request_workflow_step(
    step: str,
) -> None:
    if step not in WORKFLOW_STEPS:
        raise ValueError(
            f"Unknown workflow step: {step}"
        )

    st.session_state.requested_workflow_step = (
        step
    )


def apply_requested_workflow_step() -> None:
    requested_step = (
        st.session_state
        .requested_workflow_step
    )

    if requested_step is None:
        return

    st.session_state.workflow_step = (
        requested_step
    )

    st.session_state.requested_workflow_step = (
        None
    )


def queue_toast(
    message: str,
    icon: str = "✅",
) -> None:
    st.session_state.pending_toast = {
        "message": message,
        "icon": icon,
    }


def display_pending_toast() -> None:
    toast_data = (
        st.session_state.pending_toast
    )

    if not toast_data:
        return

    st.toast(
        toast_data["message"],
        icon=toast_data["icon"],
    )

    st.session_state.pending_toast = None


def clear_generation_results() -> None:
    st.session_state.generation_result = (
        None
    )

    st.session_state.generated_zip = None


def clear_invoice_results() -> None:
    st.session_state.workbook_dataframe = (
        None
    )

    st.session_state.invoices = []

    st.session_state.validation = []

    st.session_state.invoice_selection = {}

    st.session_state.selected_invoice = None

    clear_generation_results()


def clear_excel_upload() -> None:
    st.session_state.excel_file = None

    st.session_state.excel_bytes = None

    st.session_state.excel_filename = None

    st.session_state.sheet_names = []

    st.session_state.selected_sheet = None

    clear_invoice_results()


def clear_template_upload() -> None:
    st.session_state.template_file = None

    st.session_state.template_bytes = None

    st.session_state.template_filename = (
        None
    )

    clear_generation_results()