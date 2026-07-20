from __future__ import annotations

import streamlit as st

from invoice_creator.ui.state import (
    WORKFLOW_STEPS,
    apply_requested_workflow_step,
    display_pending_toast,
    initialise_state,
)
from invoice_creator.ui.tabs.generate import (
    render_generate_tab,
)
from invoice_creator.ui.tabs.layout import (
    render_layout_tab,
)
from invoice_creator.ui.tabs.mapping import (
    render_mapping_tab,
)
from invoice_creator.ui.tabs.review import (
    render_review_tab,
)
from invoice_creator.ui.tabs.upload import (
    render_upload_tab,
)


st.set_page_config(
    page_title="Invoice Creator",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _render_header() -> None:
    st.title("Invoice Creator")

    st.caption(
        "Upload, review and generate invoice PDFs."
    )


def _render_workflow_navigation() -> str:
    selected_step = st.segmented_control(
        "Workflow",
        options=WORKFLOW_STEPS,
        key="workflow_step",
        selection_mode="single",
        label_visibility="collapsed",
        width="stretch",
    )

    return selected_step or "Upload"


def _render_workflow_summary() -> None:
    invoice_count = len(
        st.session_state.invoices
    )

    selected_count = sum(
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

    generated_count = 0

    generation_result = (
        st.session_state.generation_result
    )

    if generation_result is not None:
        generated_count = len(
            generation_result.generated
        )

    column_one, column_two, column_three = (
        st.columns(3)
    )

    column_one.metric(
        "Invoices built",
        invoice_count,
    )

    column_two.metric(
        "Selected",
        selected_count,
    )

    column_three.metric(
        "PDFs generated",
        generated_count,
    )


def _render_current_step(
    selected_step: str,
) -> None:
    if selected_step == "Upload":
        render_upload_tab()

    elif selected_step == "Review":
        render_review_tab()

    elif selected_step == "Mapping":
        render_mapping_tab()

    elif selected_step == "Layout":
        render_layout_tab()

    elif selected_step == "Generate":
        render_generate_tab()


def main() -> None:
    initialise_state()

    apply_requested_workflow_step()

    display_pending_toast()

    _render_header()

    selected_step = (
        _render_workflow_navigation()
    )

    _render_workflow_summary()

    st.divider()

    _render_current_step(
        selected_step
    )


if __name__ == "__main__":
    main()