from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pandas as pd
import streamlit as st

from invoice_creator.services.validation_service import (
    validate_invoices,
)
from invoice_creator.ui.state import (
    clear_generation_results,
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
    return Decimal(
        str(value)
    ).quantize(
        Decimal("0.01")
    )


def _build_dataframe() -> pd.DataFrame:
    validation_by_row = (
        _validation_lookup()
    )

    rows: list[dict] = []

    for invoice in st.session_state.invoices:
        validation = validation_by_row[
            invoice.row_id
        ]

        bia_line = next(
            (
                line
                for line in invoice.lines
                if line.description
                == "BIA Assessment"
            ),
            None,
        )

        authorisation_line = next(
            (
                line
                for line in invoice.lines
                if line.description
                == "Authorisation"
            ),
            None,
        )

        rows.append(
            {
                "Generate": (
                    st.session_state
                    .invoice_selection
                    .get(
                        invoice.row_id,
                        validation.status
                        != "Blocked",
                    )
                ),
                "Row ID": invoice.row_id,
                "Status": validation.status,
                "Invoice No": (
                    invoice.invoice_no
                ),
                "Invoice Date": (
                    invoice.invoice_date
                ),
                "Service User": (
                    invoice.service_user
                ),
                "Assessor": (
                    invoice.assessor
                ),
                "BIA Assessment": (
                    float(bia_line.rate)
                    if bia_line
                    else 0.0
                ),
                "Authorisation": (
                    float(
                        authorisation_line.rate
                    )
                    if authorisation_line
                    else 0.0
                ),
                "Net": float(
                    invoice.net_amount
                ),
                "VAT": float(
                    invoice.vat
                ),
                "Total": float(
                    invoice.invoice_total
                ),
                "Issues": validation.summary,
            }
        )

    return pd.DataFrame(
        rows
    )


def _update_line(
    invoice,
    description: str,
    rate: Decimal,
) -> None:
    line = next(
        (
            item
            for item in invoice.lines
            if item.description
            == description
        ),
        None,
    )

    if line is None:
        return

    line.rate = rate

    line.net = (
        line.units
        * line.rate
    ).quantize(
        Decimal("0.01")
    )


def _recalculate_invoice(
    invoice,
) -> None:
    invoice.net_amount = sum(
        (
            line.net
            for line in invoice.lines
        ),
        Decimal("0.00"),
    ).quantize(
        Decimal("0.01")
    )

    vat_rate = Decimal(
        str(
            st.session_state.vat_rate
        )
    )

    invoice.vat = (
        invoice.net_amount
        * (
            vat_rate
            / Decimal("100")
        )
    ).quantize(
        Decimal("0.01")
    )

    invoice.invoice_total = (
        invoice.net_amount
        + invoice.vat
    ).quantize(
        Decimal("0.01")
    )


def _apply_edits(
    edited_dataframe: pd.DataFrame,
) -> None:
    invoices_by_row = (
        _invoice_lookup()
    )

    for _, row in (
        edited_dataframe.iterrows()
    ):
        row_id = int(
            row["Row ID"]
        )

        invoice = invoices_by_row[
            row_id
        ]

        invoice.invoice_no = str(
            row["Invoice No"]
        ).strip()

        invoice.invoice_date = (
            _to_date(
                row["Invoice Date"]
            )
        )

        invoice.service_user = str(
            row["Service User"]
        ).strip()

        invoice.assessor = str(
            row["Assessor"]
        ).strip()

        _update_line(
            invoice=invoice,
            description=(
                "BIA Assessment"
            ),
            rate=_money(
                row["BIA Assessment"]
            ),
        )

        _update_line(
            invoice=invoice,
            description=(
                "Authorisation"
            ),
            rate=_money(
                row["Authorisation"]
            ),
        )

        _recalculate_invoice(
            invoice
        )

        st.session_state.invoice_selection[
            row_id
        ] = bool(
            row["Generate"]
        )

    st.session_state.validation = (
        validate_invoices(
            st.session_state.invoices
        )
    )

    for result in (
        st.session_state.validation
    ):
        if result.status == "Blocked":
            st.session_state.invoice_selection[
                result.row_id
            ] = False

    clear_generation_results()


def _filter_dataframe(
    dataframe: pd.DataFrame,
    search_text: str,
    status_filter: str,
) -> pd.DataFrame:
    filtered = dataframe.copy()

    if search_text:
        search_value = (
            search_text
            .strip()
            .lower()
        )

        mask = (
            filtered["Invoice No"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_value,
                na=False,
            )
            |
            filtered["Service User"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_value,
                na=False,
            )
            |
            filtered["Assessor"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_value,
                na=False,
            )
        )

        filtered = filtered[
            mask
        ]

    if status_filter != "All":
        filtered = filtered[
            filtered["Status"]
            == status_filter
        ]

    return filtered


def _render_metrics() -> None:
    selected = sum(
        bool(
            st.session_state
            .invoice_selection
            .get(
                invoice.row_id,
                False,
            )
        )
        for invoice in (
            st.session_state.invoices
        )
    )

    ready = sum(
        result.status == "Ready"
        for result in (
            st.session_state.validation
        )
    )

    warning = sum(
        result.status == "Warning"
        for result in (
            st.session_state.validation
        )
    )

    blocked = sum(
        result.status == "Blocked"
        for result in (
            st.session_state.validation
        )
    )

    column_one, column_two, column_three, column_four = (
        st.columns(4)
    )

    column_one.metric(
        "Selected",
        selected,
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


def _render_validation_details() -> None:
    validation_by_row = (
        _validation_lookup()
    )

    blocked_count = sum(
        result.status == "Blocked"
        for result in (
            st.session_state.validation
        )
    )

    with st.expander(
        "Validation details",
        expanded=blocked_count > 0,
    ):
        issues_found = False

        for invoice in (
            st.session_state.invoices
        ):
            result = validation_by_row[
                invoice.row_id
            ]

            if not result.issues:
                continue

            issues_found = True

            title = (
                invoice.invoice_no
                or (
                    f"Excel row "
                    f"{invoice.row_id}"
                )
            )

            st.markdown(
                f"**{title} — "
                f"{result.status}**"
            )

            for issue in result.issues:
                icon = (
                    "❌"
                    if issue.severity
                    == "error"
                    else "⚠️"
                )

                st.write(
                    f"{icon} "
                    f"{issue.message}"
                )

            st.divider()

        if not issues_found:
            st.success(
                "No validation issues "
                "were found."
            )


def render_review_tab() -> None:
    if not st.session_state.invoices:
        st.info(
            "Build invoices from the "
            "Upload & Setup page first."
        )
        return

    search_column, status_column = (
        st.columns(
            [2, 1]
        )
    )

    with search_column:
        search_text = st.text_input(
            "Search invoices",
            placeholder=(
                "Invoice number, "
                "service user or assessor"
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

    dataframe = (
        _build_dataframe()
    )

    filtered_dataframe = (
        _filter_dataframe(
            dataframe=dataframe,
            search_text=search_text,
            status_filter=status_filter,
        )
    )

    edited_dataframe = (
        st.data_editor(
            filtered_dataframe,
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
                "Generate": (
                    st.column_config
                    .CheckboxColumn(
                        "Generate",
                        help=(
                            "Include this invoice "
                            "in the PDF batch."
                        ),
                    )
                ),
                "Row ID": None,
                "Invoice Date": (
                    st.column_config
                    .DateColumn(
                        "Invoice Date",
                        format=(
                            "DD/MM/YYYY"
                        ),
                    )
                ),
                "BIA Assessment": (
                    st.column_config
                    .NumberColumn(
                        "BIA Assessment",
                        min_value=0.0,
                        step=1.0,
                        format="£ %.2f",
                    )
                ),
                "Authorisation": (
                    st.column_config
                    .NumberColumn(
                        "Authorisation",
                        min_value=0.0,
                        step=1.0,
                        format="£ %.2f",
                    )
                ),
                "Net": (
                    st.column_config
                    .NumberColumn(
                        "Net",
                        format="£ %.2f",
                    )
                ),
                "VAT": (
                    st.column_config
                    .NumberColumn(
                        "VAT",
                        format="£ %.2f",
                    )
                ),
                "Total": (
                    st.column_config
                    .NumberColumn(
                        "Total",
                        format="£ %.2f",
                    )
                ),
            },
            key="invoice_review_editor",
        )
    )

    apply_column, reset_column = (
        st.columns(2)
    )

    with apply_column:
        if st.button(
            "Apply review changes",
            type="primary",
            width="stretch",
        ):
            _apply_edits(
                edited_dataframe
            )

            st.success(
                "Invoice changes were "
                "applied."
            )

            st.rerun()

    with reset_column:
        if st.button(
            "Select all eligible invoices",
            width="stretch",
        ):
            for result in (
                st.session_state.validation
            ):
                st.session_state.invoice_selection[
                    result.row_id
                ] = (
                    result.status
                    != "Blocked"
                )

            clear_generation_results()

            st.rerun()

    st.divider()

    _render_metrics()

    _render_validation_details()