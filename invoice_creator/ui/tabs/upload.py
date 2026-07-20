from __future__ import annotations

from decimal import Decimal

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
    queue_toast,
    request_workflow_step,
)


def _store_excel(
    uploaded_file,
) -> None:
    data = uploaded_file.getvalue()

    same_file = (
        st.session_state.excel_filename
        == uploaded_file.name
        and st.session_state.excel_bytes
        == data
    )

    if same_file:
        return

    st.session_state.excel_file = (
        uploaded_file
    )

    st.session_state.excel_filename = (
        uploaded_file.name
    )

    st.session_state.excel_bytes = data

    clear_invoice_results()

    try:
        sheets = get_sheet_names(
            data
        )

    except Exception as exc:
        st.session_state.sheet_names = []

        st.session_state.selected_sheet = (
            None
        )

        st.error(
            "The workbook could not be read."
        )

        st.exception(exc)
        return

    st.session_state.sheet_names = sheets

    st.session_state.selected_sheet = (
        sheets[0]
        if sheets
        else None
    )

    sheet_message = (
        f"{len(sheets)} worksheet"
        if len(sheets) == 1
        else f"{len(sheets)} worksheets"
    )

    st.toast(
        (
            f"{uploaded_file.name} uploaded. "
            f"Found {sheet_message}."
        ),
        icon="✅",
    )


def _store_template(
    uploaded_file,
) -> None:
    if uploaded_file is None:
        return

    data = uploaded_file.getvalue()

    same_file = (
        st.session_state.template_filename
        == uploaded_file.name
        and st.session_state.template_bytes
        == data
    )

    if same_file:
        return

    st.session_state.template_file = (
        uploaded_file
    )

    st.session_state.template_filename = (
        uploaded_file.name
    )

    st.session_state.template_bytes = data

    clear_generation_results()

    st.toast(
        (
            f"{uploaded_file.name} uploaded "
            "as the PDF template."
        ),
        icon="✅",
    )


def _show_uploaded_file_summary() -> None:
    if st.session_state.excel_filename:
        st.success(
            (
                "Workbook ready: "
                f"**{st.session_state.excel_filename}**"
            ),
            icon="✅",
        )

    if st.session_state.template_filename:
        st.success(
            (
                "Custom template ready: "
                f"**{st.session_state.template_filename}**"
            ),
            icon="✅",
        )
    else:
        st.info(
            "The default project PDF template will be used."
        )


def _build() -> None:
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

    progress = st.progress(
        0,
        text="Preparing workbook...",
    )

    try:
        with st.status(
            "Building invoices...",
            expanded=True,
        ) as status:
            status.write(
                "Reading the selected worksheet."
            )

            progress.progress(
                15,
                text="Reading worksheet...",
            )

            dataframe = load_workbook(
                st.session_state.excel_bytes,
                st.session_state.selected_sheet,
            )

            row_count = len(
                dataframe.index
            )

            status.write(
                (
                    f"Loaded {row_count} spreadsheet "
                    f"{'row' if row_count == 1 else 'rows'}."
                )
            )

            progress.progress(
                35,
                text="Checking required columns...",
            )

            missing = missing_columns(
                dataframe
            )

            if missing:
                status.update(
                    label="Workbook validation failed",
                    state="error",
                    expanded=True,
                )

                progress.empty()

                st.error(
                    "Missing required columns:\n\n"
                    + "\n".join(
                        f"- {column}"
                        for column in missing
                    )
                )
                return

            status.write(
                "Required columns are present."
            )

            progress.progress(
                55,
                text="Creating invoice records...",
            )

            invoices = build_invoices(
                dataframe=dataframe,
                invoice_date=(
                    st.session_state.invoice_date
                ),
                vat_rate=Decimal(
                    str(
                        st.session_state.vat_rate
                    )
                ),
                default_units=Decimal(
                    str(
                        st.session_state
                        .default_units
                    )
                ),
                include_zero_lines=(
                    st.session_state
                    .include_zero_lines
                ),
            )

            status.write(
                (
                    f"Created {len(invoices)} "
                    f"{'invoice' if len(invoices) == 1 else 'invoices'}."
                )
            )

            progress.progress(
                80,
                text="Validating invoices...",
            )

            validation = validate_invoices(
                invoices
            )

            st.session_state.workbook_dataframe = (
                dataframe
            )

            st.session_state.invoices = invoices

            st.session_state.validation = (
                validation
            )

            st.session_state.invoice_selection = {
                invoice.row_id: (
                    result.status != "Blocked"
                )
                for invoice, result in zip(
                    invoices,
                    validation,
                )
            }

            clear_generation_results()

            ready_count = sum(
                result.status == "Ready"
                for result in validation
            )

            warning_count = sum(
                result.status == "Warning"
                for result in validation
            )

            blocked_count = sum(
                result.status == "Blocked"
                for result in validation
            )

            progress.progress(
                100,
                text="Invoice build complete.",
            )

            status.write(
                (
                    f"Ready: {ready_count} · "
                    f"Warnings: {warning_count} · "
                    f"Blocked: {blocked_count}"
                )
            )

            status.update(
                label=(
                    f"Build complete — "
                    f"{len(invoices)} invoices created"
                ),
                state="complete",
                expanded=False,
            )

        queue_toast(
            (
                f"Upload processed successfully. "
                f"{len(invoices)} invoices were created."
            ),
            icon="✅",
        )

        request_workflow_step(
            "Review"
        )

        st.rerun()

    except InvoiceBuildError as exc:
        progress.empty()

        st.error(
            str(exc)
        )

    except Exception as exc:
        progress.empty()

        st.error(
            "An unexpected error occurred while building invoices."
        )

        st.exception(exc)


def _render_existing_build_summary() -> None:
    if not st.session_state.invoices:
        return

    ready = sum(
        result.status == "Ready"
        for result in st.session_state.validation
    )

    warning = sum(
        result.status == "Warning"
        for result in st.session_state.validation
    )

    blocked = sum(
        result.status == "Blocked"
        for result in st.session_state.validation
    )

    st.subheader("Current invoice batch")

    column_one, column_two, column_three, column_four = (
        st.columns(4)
    )

    column_one.metric(
        "Invoices",
        len(
            st.session_state.invoices
        ),
    )

    column_two.metric(
        "Ready",
        ready,
    )

    column_three.metric(
        "Warnings",
        warning,
    )

    column_four.metric(
        "Blocked",
        blocked,
    )

    if st.button(
        "Continue to Review",
        type="primary",
        width="stretch",
    ):
        request_workflow_step(
            "Review"
        )

        st.rerun()


def render_upload_tab() -> None:
    st.header("Upload and Setup")

    st.write(
        "Upload the Excel workbook and optionally "
        "replace the default PDF template."
    )

    left_column, right_column = (
        st.columns(
            [2, 1],
            gap="large",
        )
    )

    with left_column:
        workbook = st.file_uploader(
            "Excel workbook",
            type=[
                "xlsx",
                "xls",
            ],
            help=(
                "Each spreadsheet row currently "
                "creates one invoice."
            ),
            key="excel_workbook_uploader",
        )

        if workbook is not None:
            _store_excel(
                workbook
            )

        if st.session_state.sheet_names:
            current_sheet = (
                st.session_state.selected_sheet
            )

            if (
                current_sheet
                not in st.session_state.sheet_names
            ):
                current_sheet = (
                    st.session_state
                    .sheet_names[0]
                )

            selected_index = (
                st.session_state
                .sheet_names
                .index(
                    current_sheet
                )
            )

            selected_sheet = st.selectbox(
                "Worksheet",
                options=(
                    st.session_state.sheet_names
                ),
                index=selected_index,
                key="worksheet_selector",
            )

            if (
                selected_sheet
                != st.session_state
                .selected_sheet
            ):
                st.session_state.selected_sheet = (
                    selected_sheet
                )

                clear_invoice_results()

                st.toast(
                    (
                        f"Worksheet changed to "
                        f"{selected_sheet}."
                    ),
                    icon="📄",
                )

        template = st.file_uploader(
            "PDF template",
            type=["pdf"],
            help=(
                "Optional. Leave empty to use "
                "the default project template."
            ),
            key="pdf_template_uploader",
        )

        if template is not None:
            _store_template(
                template
            )

        _show_uploaded_file_summary()

    with right_column:
        st.subheader(
            "Invoice settings"
        )

        st.session_state.invoice_date = (
            st.date_input(
                "Invoice date",
                value=(
                    st.session_state
                    .invoice_date
                ),
                format="DD/MM/YYYY",
            )
        )

        st.session_state.vat_rate = (
            st.number_input(
                "VAT percentage",
                min_value=0.0,
                max_value=100.0,
                value=float(
                    st.session_state.vat_rate
                ),
                step=1.0,
                format="%.2f",
            )
        )

        st.session_state.default_units = (
            st.number_input(
                "Default units",
                min_value=0.0,
                value=float(
                    st.session_state
                    .default_units
                ),
                step=1.0,
                format="%.2f",
            )
        )

        st.session_state.include_zero_lines = (
            st.checkbox(
                "Include zero-value lines",
                value=(
                    st.session_state
                    .include_zero_lines
                ),
            )
        )

        st.info(
            (
                "Current rule: every spreadsheet "
                "row creates one invoice."
            ),
            icon="ℹ️",
        )

    st.divider()

    build_disabled = not bool(
        st.session_state.excel_bytes
        and st.session_state.selected_sheet
    )

    if st.button(
        "Build Invoices",
        type="primary",
        width="stretch",
        disabled=build_disabled,
    ):
        _build()

    if build_disabled:
        st.caption(
            "Upload a workbook and select a worksheet "
            "to enable invoice building."
        )

    _render_existing_build_summary()