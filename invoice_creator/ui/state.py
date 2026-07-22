from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any
from pathlib import Path

import streamlit as st

from invoice_creator.services.app_paths import default_output_directory
from invoice_creator.services.settings_service import load_settings


WORKFLOW_STEPS = [
    "Upload",
    "Review",
    "Generate",
]


DEFAULT_STATE: dict[str, Any] = {
    "workflow_step": "Upload",
    "requested_workflow_step": None,
    "pending_toast": None,
    "welcome_complete": False,
    "advanced_panel": "Field Mapping",

    "excel_file": None,
    "excel_bytes": None,
    "excel_filename": None,
    "sheet_names": [],
    "selected_sheet": None,
    "current_job": None,
    "workbook_dataframe": None,

    "template_file": None,
    "template_bytes": None,
    "template_filename": None,

    "invoice_date_mode": "One date for all invoices",
    "invoice_date": date.today(),
    "excel_date_column": None,
    "vat_rate": 20.0,
    "default_units": 1.0,
    "include_zero_lines": True,

    "invoices": [],
    "validation": [],
    "invoice_selection": {},
    "selected_invoice": None,

    "mapping": None,
    "mapping_rules": None,
    "layout_offsets": {
        "x": 0.0,
        "y": 0.0,
    },

    "generation_result": None,
    "generated_zip": None,
    "output_mode": "Save to folder",
    "output_folder": str(default_output_directory()),
    "create_timestamped_folder": True,
    "overwrite_existing_pdfs": False,
    "open_folder_when_finished": True,
    "last_output_directory": None,
}


def initialise_state() -> None:
    persisted_settings = load_settings()

    for key, default_value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(
                persisted_settings.get(key, default_value)
            )


def request_workflow_step(step: str) -> None:
    if step not in WORKFLOW_STEPS:
        raise ValueError(f"Unknown workflow step: {step}")

    st.session_state.requested_workflow_step = step


def apply_requested_workflow_step() -> None:
    requested_step = st.session_state.requested_workflow_step

    if requested_step is None:
        return

    st.session_state.workflow_step = requested_step
    st.session_state.requested_workflow_step = None


def queue_toast(message: str, icon: str = "✅") -> None:
    st.session_state.pending_toast = {
        "message": message,
        "icon": icon,
    }


def display_pending_toast() -> None:
    toast_data = st.session_state.pending_toast

    if not toast_data:
        return

    st.toast(
        toast_data["message"],
        icon=toast_data["icon"],
    )

    st.session_state.pending_toast = None


def clear_generation_results() -> None:
    st.session_state.generation_result = None
    st.session_state.generated_zip = None
    st.session_state.last_output_directory = None


def clear_invoice_results() -> None:
    st.session_state.workbook_dataframe = None
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
    st.session_state.template_filename = None
    clear_generation_results()


def reset_state() -> None:
    for key in list(DEFAULT_STATE):
        if key in st.session_state:
            del st.session_state[key]

    initialise_state()
