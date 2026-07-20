from __future__ import annotations

from datetime import date

import streamlit as st


DEFAULTS = {
    "excel_file": None,
    "excel_bytes": None,
    "excel_filename": None,
    "sheet_names": [],
    "selected_sheet": None,
    "workbook_dataframe": None,

    "template_file": None,
    "template_bytes": None,
    "template_filename": None,

    "invoice_date_mode": "One date for all invoices",
    "invoice_date": date.today(),
    "vat_rate": 20.0,
    "default_units": 1.0,
    "include_zero_lines": True,

    "invoices": [],
    "validation": [],
    "invoice_selection": {},

    "mapping": None,
    "layout": None,
    "selected_invoice": None,

    "generation_result": None,
    "generated_zip": None,
}


def initialise_state() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_invoice_results() -> None:
    st.session_state.invoices = []
    st.session_state.validation = []
    st.session_state.invoice_selection = {}
    st.session_state.selected_invoice = None
    st.session_state.generation_result = None
    st.session_state.generated_zip = None


def clear_generation_results() -> None:
    st.session_state.generation_result = None
    st.session_state.generated_zip = None