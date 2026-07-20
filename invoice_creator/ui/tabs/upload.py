from __future__ import annotations

from decimal import Decimal
from io import BytesIO

import streamlit as st

from invoice_creator.services.invoice_service import (
    InvoiceBuildError,
    build_invoices,
    get_sheet_names,
    load_workbook,
    missing_columns,
)
from invoice_creator.services.validation_service import (
    validate_invoices,
)
from invoice_creator.ui.state import (
    clear_generation_results,
    clear_invoice_results,
)


def _save_excel_upload(
    uploaded_file,
) -> None:
    uploaded_bytes = uploaded_file.getvalue()

    file_changed = (
        st.session_state.excel_filename
        != uploaded_file.name
        or st.session_state.excel_bytes
        != uploaded_bytes
    )

    if not file_changed:
        return

    st.session_state.excel_file = uploaded_file
    st.session_state.excel_bytes = uploaded_bytes
    st.session_state.excel_filename = uploaded_file.name

    clear_invoice_results()

    st.session_state.sheet_names = get_sheet_names(
        uploaded_bytes
    )

    st.session_state.selected_sheet = (
        st.session_state.sheet_names[0]
        if st.session_state.sheet_names
        else None
    )


def _save_template_upload(
    uploaded_file,
) -> None:
    if uploaded_file is None:
        return

    uploaded_bytes = uploaded_file.getvalue()

    st.session_state.template_file = uploaded_file
    st.session_state.template_bytes = uploaded_bytes
    st.session_state.template_filename = (
        uploaded_file.name
    )

    clear_generation_results()


def _build_current_invoices() -> None:
    if not st.session_state.excel_bytes:
        st.error(
            "Upload an Excel workbook first."
        )
        return

    if not st.session_state.selected_sheet:
        st.error(
            "Select a worksheet first."
        )
        return

    try:
        dataframe = load_workbook(
            st.session_state.excel_bytes,
            sheet_name=st.session_state.selected_sheet,
        )

        missing = missing_columns(
            dataframe
        )

        if missing:
            st.error(
                "Required columns are missing: "
                + ", ".join(missing)
            )
            return

        invoices = build_invoices(
            dataframe=dataframe,
            invoice_date=st.session_state.invoice_date,
            vat_rate=Decimal(
                str(st.session_state.vat_rate)
            ),
            default_units=Decimal(
                str(st.session_state.default_units)
            ),
            include_zero_lines=(
                st.session_state.include_zero_lines
            ),
        )

        validation = validate_invoices(
            invoices
        )

        st.session_state.workbook_dataframe = (
            dataframe
        )

        st.session_state.invoices = invoices
        st.session_state.validation = validation

        st.session_state.invoice_selection = {
            invoice.row_id: (
                result.status != "Blocked"
            )
            for invoice, result in zip(
                invoices,
                validation,
            )
        }

        st.session_state.selected_invoice = (
            invoices[0].row_id
            if invoices
            else None
        )

        clear_generation_results()

        st.success(
            f"Built {len(invoices)} invoices."
        )

    except InvoiceBuildError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.exception(exc)


def render_upload_tab() -> None:
    st.subheader("Source files")

    left, right = st.columns(
        [2, 1],
        gap="large",
    )

    with left:
        excel_file = st.file_uploader(
            "Excel workbook",
            type=["xlsx", "xls"],
            help=(
                "Each spreadsheet row is currently treated "
                "as one invoice."
            ),
        )

        if excel_file is not None:
            try:
                _save_excel_upload(
                    excel_file
                )
            except Exception as exc:
                st.error(
                    f"Could not inspect the workbook: {exc}"
                )

        if st.session_state.sheet_names:
            selected_sheet = st.selectbox(
                "Worksheet",
                options=st.session_state.sheet_names,
                index=st.session_state.sheet_names.index(
                    st.session_state.selected_sheet
                ),
            )

            if (
                selected_sheet
                != st.session_state.selected_sheet
            ):
                st.session_state.selected_sheet = (
                    selected_sheet
                )

                clear_invoice_results()

        template_file = st.file_uploader(
            "Replacement PDF template",
            type=["pdf"],
            help=(
                "Leave this empty to use the default "
                "invoice template."
            ),
        )

        if template_file is not None:
            _save_template_upload(
                template_file
            )

    with right:
        st.markdown("#### Current source")

        st.metric(
            "Workbook",
            (
                st.session_state.excel_filename
                or "Not loaded"
            ),
        )

        st.metric(
            "Template",
            (
                st.session_state.template_filename
                or "Default template"
            ),
        )

        st.metric(
            "Invoices built",
            len(st.session_state.invoices),
        )

    st.divider()

    st.subheader("Invoice settings")

    settings_left, settings_right = st.columns(
        2,
        gap="large",
    )

    with settings_left:
        st.session_state.invoice_date_mode = (
            st.radio(
                "Invoice date source",
                options=[
                    "One date for all invoices",
                    "Use an Excel date column",
                    "Assign dates during review",
                ],
                index=[
                    "One date for all invoices",
                    "Use an Excel date column",
                    "Assign dates during review",
                ].index(
                    st.session_state.invoice_date_mode
                ),
            )
        )

        if (
            st.session_state.invoice_date_mode
            == "One date for all invoices"
        ):
            st.session_state.invoice_date = (
                st.date_input(
                    "Invoice date",
                    value=st.session_state.invoice_date,
                    format="DD/MM/YYYY",
                )
            )
        else:
            st.info(
                "The global calendar mode is currently "
                "implemented. Excel-column and individual "
                "date modes will be connected through the "
                "Mapping and Review pages."
            )

    with settings_right:
        st.session_state.vat_rate = (
            st.number_input(
                "VAT rate (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(
                    st.session_state.vat_rate
                ),
                step=0.5,
            )
        )

        st.session_state.default_units = (
            st.number_input(
                "Default units",
                min_value=0.0,
                value=float(
                    st.session_state.default_units
                ),
                step=1.0,
            )
        )

        st.session_state.include_zero_lines = (
            st.checkbox(
                "Include zero-value lines",
                value=(
                    st.session_state.include_zero_lines
                ),
            )
        )

    st.divider()

    if st.button(
        "Build and validate invoices",
        type="primary",
        use_container_width=True,
    ):
        _build_current_invoices()

    if st.session_state.invoices:
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

        metric_one, metric_two, metric_three = (
            st.columns(3)
        )

        metric_one.metric(
            "Ready",
            ready_count,
        )

        metric_two.metric(
            "Warnings",
            warning_count,
        )

        metric_three.metric(
            "Blocked",
            blocked_count,
        )