from __future__ import annotations

import pandas as pd
import streamlit as st

from invoice_creator.services.generation_service import (
    generate_invoices,
)
from invoice_creator.services.zip_service import (
    create_pdf_zip,
)


def _selected_generation_invoices():
    validation_lookup = {
        result.row_id: result
        for result in st.session_state.validation
    }

    return [
        invoice
        for invoice in st.session_state.invoices
        if (
            st.session_state.invoice_selection.get(
                invoice.row_id,
                False,
            )
            and validation_lookup[
                invoice.row_id
            ].status != "Blocked"
        )
    ]


def render_generate_tab() -> None:
    if not st.session_state.invoices:
        st.info(
            "Build invoices from the Upload & Setup "
            "page before generating PDFs."
        )
        return

    validation_lookup = {
        result.row_id: result
        for result in st.session_state.validation
    }

    selected_invoices = (
        _selected_generation_invoices()
    )

    selected_ready = sum(
        validation_lookup[
            invoice.row_id
        ].status == "Ready"
        for invoice in selected_invoices
    )

    selected_warnings = sum(
        validation_lookup[
            invoice.row_id
        ].status == "Warning"
        for invoice in selected_invoices
    )

    total_blocked = sum(
        result.status == "Blocked"
        for result in st.session_state.validation
    )

    metric_one, metric_two, metric_three = (
        st.columns(3)
    )

    metric_one.metric(
        "Selected to generate",
        len(selected_invoices),
    )

    metric_two.metric(
        "Selected with warnings",
        selected_warnings,
    )

    metric_three.metric(
        "Blocked",
        total_blocked,
    )

    st.caption(
        "PDF filenames use the invoice number, "
        "for example 86262-1.pdf."
    )

    include_warning_invoices = st.checkbox(
        "Generate selected invoices that have warnings",
        value=True,
    )

    if not include_warning_invoices:
        selected_invoices = [
            invoice
            for invoice in selected_invoices
            if validation_lookup[
                invoice.row_id
            ].status == "Ready"
        ]

    st.write(
        f"**{len(selected_invoices)} PDFs** will be generated."
    )

    if not selected_invoices:
        st.warning(
            "No eligible invoices are selected."
        )
        return

    if st.button(
        "Generate selected PDFs",
        type="primary",
        use_container_width=True,
    ):
        with st.spinner(
            "Generating invoice PDFs..."
        ):
            try:
                result = generate_invoices(
                    invoices=selected_invoices,
                    template_bytes=(
                        st.session_state.template_bytes
                    ),
                )

                st.session_state.generation_result = (
                    result
                )

                st.session_state.generated_zip = (
                    create_pdf_zip(
                        [
                            item.path
                            for item in result.generated
                        ]
                    )
                    if result.generated
                    else None
                )

            except Exception as exc:
                st.exception(exc)

    result = st.session_state.generation_result

    if result is None:
        return

    st.divider()

    success_col, failure_col = st.columns(2)

    success_col.metric(
        "Generated",
        len(result.generated),
    )

    failure_col.metric(
        "Failed",
        len(result.failures),
    )

    if result.generated:
        st.success(
            f"Successfully generated "
            f"{len(result.generated)} PDFs."
        )

        st.download_button(
            "Download invoice PDFs",
            data=st.session_state.generated_zip,
            file_name="invoices.zip",
            mime_type="application/zip",
            type="primary",
            use_container_width=True,
        )

        generated_dataframe = pd.DataFrame(
            [
                {
                    "Invoice No": item.invoice_no,
                    "Filename": item.filename,
                }
                for item in result.generated
            ]
        )

        with st.expander(
            "Generated files"
        ):
            st.dataframe(
                generated_dataframe,
                hide_index=True,
                use_container_width=True,
            )

    if result.failures:
        st.error(
            f"{len(result.failures)} invoices "
            "could not be generated."
        )

        failure_dataframe = pd.DataFrame(
            [
                {
                    "Invoice No": failure.invoice_no,
                    "Error": failure.message,
                }
                for failure in result.failures
            ]
        )

        st.dataframe(
            failure_dataframe,
            hide_index=True,
            use_container_width=True,
        )

        st.download_button(
            "Download failure report",
            data=failure_dataframe.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="invoice_generation_failures.csv",
            mime_type="text/csv",
            use_container_width=True,
        )