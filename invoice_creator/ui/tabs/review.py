from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pandas as pd
import streamlit as st

from invoice_creator.services.validation_service import (
    validate_invoices,
)
from invoice_creator.ui.state import (
    clear_generation_results,
)


def _validation_by_row() -> dict:
    return {
        result.row_id: result
        for result in st.session_state.validation
    }


def _invoice_by_row() -> dict:
    return {
        invoice.row_id: invoice
        for invoice in st.session_state.invoices
    }


def _build_review_dataframe() -> pd.DataFrame:
    validation_lookup = _validation_by_row()

    rows: list[dict] = []

    for invoice in st.session_state.invoices:
        result = validation_lookup[
            invoice.row_id
        ]

        rows.append(
            {
                "Generate": (
                    st.session_state.invoice_selection.get(
                        invoice.row_id,
                        True,
                    )
                ),
                "Row ID": invoice.row_id,
                "Status": result.status,
                "Invoice No": invoice.invoice_no,
                "Invoice Date": invoice.invoice_date,
                "Service User": invoice.service_user,
                "Assessor": invoice.assessor,
                "Net": float(invoice.net_amount),
                "VAT": float(invoice.vat),
                "Total": float(invoice.invoice_total),
                "Warnings": result.summary,
            }
        )

    return pd.DataFrame(rows)


def _apply_table_edits(
    edited_dataframe: pd.DataFrame,
) -> None:
    invoice_lookup = _invoice_by_row()

    for _, row in edited_dataframe.iterrows():
        row_id = int(row["Row ID"])

        invoice = invoice_lookup[row_id]

        invoice.invoice_no = str(
            row["Invoice No"]
        ).strip()

        invoice.service_user = str(
            row["Service User"]
        ).strip()

        invoice.assessor = str(
            row["Assessor"]
        ).strip()

        edited_date = row["Invoice Date"]

        if isinstance(
            edited_date,
            pd.Timestamp,
        ):
            invoice.invoice_date = (
                edited_date.date()
            )
        elif isinstance(
            edited_date,
            datetime,
        ):
            invoice.invoice_date = (
                edited_date.date()
            )
        elif hasattr(
            edited_date,
            "year",
        ):
            invoice.invoice_date = (
                edited_date
            )

        st.session_state.invoice_selection[
            row_id
        ] = bool(row["Generate"])

    st.session_state.validation = (
        validate_invoices(
            st.session_state.invoices
        )
    )

    clear_generation_results()


def render_review_tab() -> None:
    if not st.session_state.invoices:
        st.info(
            "Upload a workbook and build invoices "
            "from the Upload & Setup page first."
        )
        return

    validation_lookup = _validation_by_row()

    filter_left, filter_right = st.columns(
        [2, 1]
    )

    with filter_left:
        search_text = st.text_input(
            "Search invoices",
            placeholder=(
                "Invoice number, service user or assessor"
            ),
        )

    with filter_right:
        status_filter = st.selectbox(
            "Status",
            options=[
                "All",
                "Ready",
                "Warning",
                "Blocked",
            ],
        )

    dataframe = _build_review_dataframe()

    if search_text:
        search_lower = search_text.lower()

        mask = (
            dataframe["Invoice No"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False,
            )
            |
            dataframe["Service User"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False,
            )
            |
            dataframe["Assessor"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_lower,
                na=False,
            )
        )

        dataframe = dataframe[mask]

    if status_filter != "All":
        dataframe = dataframe[
            dataframe["Status"]
            == status_filter
        ]

    edited_dataframe = st.data_editor(
        dataframe,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=[
            "Row ID",
            "Status",
            "Net",
            "VAT",
            "Total",
            "Warnings",
        ],
        column_config={
            "Generate": st.column_config.CheckboxColumn(
                "Generate",
                help=(
                    "Choose whether this invoice should "
                    "be included in the PDF batch."
                ),
            ),
            "Row ID": None,
            "Invoice Date": (
                st.column_config.DateColumn(
                    "Invoice Date",
                    format="DD/MM/YYYY",
                )
            ),
            "Net": st.column_config.NumberColumn(
                "Net",
                format="£ %.2f",
            ),
            "VAT": st.column_config.NumberColumn(
                "VAT",
                format="£ %.2f",
            ),
            "Total": st.column_config.NumberColumn(
                "Total",
                format="£ %.2f",
            ),
        },
        key="invoice_review_editor",
    )

    if st.button(
        "Apply review changes",
        type="primary",
    ):
        _apply_table_edits(
            edited_dataframe
        )

        st.success(
            "Invoice changes and selections were applied."
        )

        st.rerun()

    st.divider()

    selected_count = sum(
        st.session_state.invoice_selection.get(
            invoice.row_id,
            False,
        )
        for invoice in st.session_state.invoices
    )

    ready_count = sum(
        result.status == "Ready"
        for result in st.session_state.validation
    )

    warning_count = sum(
        result.status == "Warning"
        for result in st.session_state.validation
    )

    blocked_count = sum(
        result.status == "Blocked"
        for result in st.session_state.validation
    )

    col_one, col_two, col_three, col_four = (
        st.columns(4)
    )

    col_one.metric(
        "Selected",
        selected_count,
    )

    col_two.metric(
        "Ready",
        ready_count,
    )

    col_three.metric(
        "Warnings",
        warning_count,
    )

    col_four.metric(
        "Blocked",
        blocked_count,
    )

    with st.expander(
        "Validation details",
        expanded=blocked_count > 0,
    ):
        issues_found = False

        for invoice in st.session_state.invoices:
            result = validation_lookup[
                invoice.row_id
            ]

            if not result.issues:
                continue

            issues_found = True

            title = (
                invoice.invoice_no
                or f"Excel row {invoice.row_id}"
            )

            st.markdown(
                f"**{title} — {result.status}**"
            )

            for issue in result.issues:
                icon = (
                    "❌"
                    if issue.severity == "error"
                    else "⚠️"
                )

                st.write(
                    f"{icon} {issue.message}"
                )

            st.divider()

        if not issues_found:
            st.success(
                "No validation issues were found."
            )