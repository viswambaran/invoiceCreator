from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from tempfile import TemporaryDirectory

import fitz
import pandas as pd
import streamlit as st

from invoice_creator.services.generation_service import (
    generate_invoices,
)
from invoice_creator.services.validation_service import (
    validate_invoices,
)
from invoice_creator.ui.state import (
    clear_generation_results,
    request_workflow_step,
)


def _validation_lookup() -> dict[int, object]:
    return {
        result.row_id: result
        for result in st.session_state.validation
    }


def _invoice_lookup() -> dict[int, object]:
    return {
        invoice.row_id: invoice
        for invoice in st.session_state.invoices
    }


def _to_date(value) -> date:
    if isinstance(value, pd.Timestamp):
        return value.date()

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return st.session_state.invoice_date


def _money(value) -> Decimal:
    return Decimal(str(value)).quantize(
        Decimal("0.01")
    )


def _build_dataframe() -> pd.DataFrame:
    validation_by_row = _validation_lookup()
    rows: list[dict] = []

    for invoice in st.session_state.invoices:
        validation = validation_by_row[invoice.row_id]

        bia_line = next(
            (
                line
                for line in invoice.lines
                if line.description == "BIA Assessment"
            ),
            None,
        )

        authorisation_line = next(
            (
                line
                for line in invoice.lines
                if line.description == "Authorisation"
            ),
            None,
        )

        rows.append(
            {
                "Generate": st.session_state.invoice_selection.get(
                    invoice.row_id,
                    validation.status != "Blocked",
                ),
                "Row ID": invoice.row_id,
                "Status": validation.status,
                "Invoice No": invoice.invoice_no,
                "Invoice Date": invoice.invoice_date,
                "Service User": invoice.service_user,
                "Assessor": invoice.assessor,
                "BIA Assessment": (
                    float(bia_line.rate)
                    if bia_line
                    else 0.0
                ),
                "Authorisation": (
                    float(authorisation_line.rate)
                    if authorisation_line
                    else 0.0
                ),
                "Net": float(invoice.net_amount),
                "VAT": float(invoice.vat),
                "Total": float(invoice.invoice_total),
                "Issues": validation.summary,
            }
        )

    return pd.DataFrame(rows)


def _update_line(
    invoice,
    description: str,
    rate: Decimal,
) -> None:
    line = next(
        (
            item
            for item in invoice.lines
            if item.description == description
        ),
        None,
    )

    if line is None:
        return

    line.rate = rate
    line.net = (
        line.units * line.rate
    ).quantize(Decimal("0.01"))


def _recalculate_invoice(invoice) -> None:
    invoice.net_amount = sum(
        (line.net for line in invoice.lines),
        Decimal("0.00"),
    ).quantize(Decimal("0.01"))

    vat_rate = Decimal(
        str(st.session_state.vat_rate)
    )

    invoice.vat = (
        invoice.net_amount
        * (vat_rate / Decimal("100"))
    ).quantize(Decimal("0.01"))

    invoice.invoice_total = (
        invoice.net_amount + invoice.vat
    ).quantize(Decimal("0.01"))


def _apply_edits(
    edited_dataframe: pd.DataFrame,
) -> None:
    invoices_by_row = _invoice_lookup()

    for _, row in edited_dataframe.iterrows():
        row_id = int(row["Row ID"])
        invoice = invoices_by_row[row_id]

        invoice.invoice_no = str(
            row["Invoice No"]
        ).strip()
        invoice.invoice_date = _to_date(
            row["Invoice Date"]
        )
        invoice.service_user = str(
            row["Service User"]
        ).strip()
        invoice.assessor = str(
            row["Assessor"]
        ).strip()

        _update_line(
            invoice,
            "BIA Assessment",
            _money(row["BIA Assessment"]),
        )
        _update_line(
            invoice,
            "Authorisation",
            _money(row["Authorisation"]),
        )
        _recalculate_invoice(invoice)

        st.session_state.invoice_selection[row_id] = bool(
            row["Generate"]
        )

    st.session_state.validation = validate_invoices(
        st.session_state.invoices
    )

    for result in st.session_state.validation:
        if result.status == "Blocked":
            st.session_state.invoice_selection[
                result.row_id
            ] = False

    clear_generation_results()


def _render_metrics() -> None:
    selected = sum(
        st.session_state.invoice_selection.get(
            invoice.row_id,
            False,
        )
        for invoice in st.session_state.invoices
    )
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

    columns = st.columns(4)
    columns[0].metric("Selected", selected)
    columns[1].metric("Ready", ready)
    columns[2].metric("Warnings", warning)
    columns[3].metric("Blocked", blocked)


def _render_preview(invoice) -> None:
    try:
        with TemporaryDirectory(
            prefix="invoice_preview_"
        ) as directory:
            result = generate_invoices(
                invoices=[invoice],
                template_bytes=st.session_state.template_bytes,
                output_directory=directory,
            )

            if result.failures:
                st.error(
                    result.failures[0].message
                )
                return

            pdf_path = result.generated[0].path

            with fitz.open(pdf_path) as document:
                page = document[0]
                pixmap = page.get_pixmap(
                    matrix=fitz.Matrix(1.35, 1.35),
                    alpha=False,
                )
                image_bytes = pixmap.tobytes("png")

            st.image(
                image_bytes,
                caption=f"Live preview — {invoice.invoice_no}",
                width="stretch",
            )

            st.download_button(
                "Download this preview PDF",
                data=pdf_path.read_bytes(),
                file_name=f"{invoice.invoice_no or 'invoice'}_preview.pdf",
                mime="application/pdf",
                width="stretch",
            )

    except Exception as exc:
        st.error(
            "The preview could not be generated."
        )
        st.exception(exc)


def _render_validation_details() -> None:
    validation_by_row = _validation_lookup()
    blocked_count = sum(
        result.status == "Blocked"
        for result in st.session_state.validation
    )

    with st.expander(
        "⚠️ Validation details",
        expanded=blocked_count > 0,
    ):
        found = False

        for invoice in st.session_state.invoices:
            result = validation_by_row[invoice.row_id]

            if not result.issues:
                continue

            found = True
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
                st.write(f"{icon} {issue.message}")

            st.divider()

        if not found:
            st.success(
                "No validation issues were found."
            )


def render_review_tab() -> None:
    st.header("🔍 Review invoices")
    st.caption(
        "Edit any generated field, choose which invoices to include and preview the final PDF."
    )

    if not st.session_state.invoices:
        st.info(
            "Build invoices from the Upload step first."
        )
        return

    _render_metrics()

    search_column, status_column = st.columns(
        [2, 1]
    )

    with search_column:
        search_text = st.text_input(
            "Search invoices",
            placeholder=(
                "Invoice number, service user or assessor"
            ),
        )

    with status_column:
        status_filter = st.selectbox(
            "Status",
            options=[
                "All",
                "Ready",
                "Warning",
                "Blocked",
            ],
        )

    dataframe = _build_dataframe()

    if search_text:
        value = search_text.strip().lower()
        mask = (
            dataframe["Invoice No"].astype(str).str.lower().str.contains(value, na=False)
            | dataframe["Service User"].astype(str).str.lower().str.contains(value, na=False)
            | dataframe["Assessor"].astype(str).str.lower().str.contains(value, na=False)
        )
        dataframe = dataframe[mask]

    if status_filter != "All":
        dataframe = dataframe[
            dataframe["Status"] == status_filter
        ]

    edited_dataframe = st.data_editor(
        dataframe,
        hide_index=True,
        width="stretch",
        num_rows="fixed",
        disabled=[
            "Row ID",
            "Status",
            "Net",
            "VAT",
            "Total",
            "Issues",
        ],
        column_config={
            "Generate": st.column_config.CheckboxColumn(
                "Generate",
                help="Include this invoice in the PDF batch.",
            ),
            "Row ID": None,
            "Invoice Date": st.column_config.DateColumn(
                "Invoice Date",
                format="DD/MM/YYYY",
            ),
            "BIA Assessment": st.column_config.NumberColumn(
                "BIA Assessment",
                min_value=0.0,
                step=1.0,
                format="£ %.2f",
            ),
            "Authorisation": st.column_config.NumberColumn(
                "Authorisation",
                min_value=0.0,
                step=1.0,
                format="£ %.2f",
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

    controls = st.columns([1, 1, 1])

    with controls[0]:
        if st.button(
            "💾 Save table changes",
            type="primary",
            width="stretch",
        ):
            _apply_edits(edited_dataframe)
            st.toast(
                "Invoice changes saved.",
                icon="✅",
            )
            st.rerun()

    with controls[1]:
        if st.button(
            "✅ Select all eligible",
            width="stretch",
        ):
            for result in st.session_state.validation:
                st.session_state.invoice_selection[
                    result.row_id
                ] = result.status != "Blocked"

            clear_generation_results()
            st.rerun()

    with controls[2]:
        if st.button(
            "Clear selections",
            width="stretch",
        ):
            for invoice in st.session_state.invoices:
                st.session_state.invoice_selection[
                    invoice.row_id
                ] = False

            clear_generation_results()
            st.rerun()

    st.caption(
        "Manual edits are saved when you click Save table changes. Totals are recalculated automatically."
    )

    st.divider()

    st.subheader("👁️ Live PDF preview")

    preview_options = {
        (
            invoice.invoice_no
            or f"Excel row {invoice.row_id}"
        ): invoice.row_id
        for invoice in st.session_state.invoices
    }

    selected_label = st.selectbox(
        "Choose an invoice to preview",
        options=list(preview_options.keys()),
    )

    selected_row_id = preview_options[selected_label]
    selected_invoice = _invoice_lookup()[selected_row_id]

    st.session_state.selected_invoice = selected_row_id

    preview_col, details_col = st.columns(
        [2, 1],
        gap="large",
    )

    with preview_col:
        _render_preview(selected_invoice)

    with details_col:
        validation = _validation_lookup()[
            selected_row_id
        ]

        st.markdown(
            f"### {selected_invoice.invoice_no or 'No invoice number'}"
        )
        st.write(
            f"**Status:** {validation.status}"
        )
        st.write(
            f"**Date:** {selected_invoice.invoice_date.strftime('%d/%m/%Y')}"
        )
        st.write(
            f"**Service user:** {selected_invoice.service_user}"
        )
        st.write(
            f"**Assessor:** {selected_invoice.assessor}"
        )
        st.write(
            f"**Total:** £{float(selected_invoice.invoice_total):.2f}"
        )

        if validation.issues:
            for issue in validation.issues:
                st.warning(issue.message)
        else:
            st.success(
                "This invoice is ready."
            )

    _render_validation_details()

    selected_count = sum(
        st.session_state.invoice_selection.get(
            invoice.row_id,
            False,
        )
        for invoice in st.session_state.invoices
    )
    blocked_count = sum(
        result.status == "Blocked"
        for result in st.session_state.validation
    )
    warning_count = sum(
        result.status == "Warning"
        and st.session_state.invoice_selection.get(
            result.row_id,
            False,
        )
        for result in st.session_state.validation
    )

    st.markdown(
        """
        <div class="next-step-card">
            <h3>✅ Ready for the next step?</h3>
            <p>Save any table edits, confirm your selection and continue to generation.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if selected_count == 0:
        st.warning(
            "Select at least one eligible invoice before continuing."
        )
    elif blocked_count:
        st.info(
            f"{blocked_count} blocked invoice(s) will be skipped automatically."
        )

    if warning_count:
        st.warning(
            f"{warning_count} selected invoice(s) contain warnings but may still be generated."
        )

    if st.button(
        f"Continue to Generate 🚀 ({selected_count} selected)",
        type="primary",
        width="stretch",
        disabled=selected_count == 0,
    ):
        _apply_edits(edited_dataframe)

        selected_after_save = sum(
            st.session_state.invoice_selection.get(
                invoice.row_id,
                False,
            )
            for invoice in st.session_state.invoices
        )

        if selected_after_save == 0:
            st.error(
                "No eligible invoices remain selected."
            )
            return

        request_workflow_step("Generate")
        st.rerun()
