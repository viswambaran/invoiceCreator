from __future__ import annotations

import logging

import streamlit as st

from invoice_creator.app_info import APP_DESCRIPTION, APP_NAME, APP_VERSION
from invoice_creator.services.app_paths import logs_directory, settings_path
from invoice_creator.services.logging_service import configure_logging
from invoice_creator.ui.system_actions import open_directory

from invoice_creator.ui.state import (
    WORKFLOW_STEPS,
    apply_requested_workflow_step,
    display_pending_toast,
    initialise_state,
    reset_state,
)
from invoice_creator.ui.styles import load_styles
from invoice_creator.ui.tabs.generate import render_generate_tab
from invoice_creator.ui.tabs.layout import render_layout_tab
from invoice_creator.ui.tabs.mapping import render_mapping_tab
from invoice_creator.ui.tabs.review import render_review_tab
from invoice_creator.ui.tabs.upload import render_upload_tab


configure_logging()
LOGGER = logging.getLogger(__name__)


st.set_page_config(
    page_title="Invoice Creator",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _selected_count() -> int:
    return sum(
        bool(
            st.session_state.invoice_selection.get(
                invoice.row_id,
                False,
            )
        )
        for invoice in st.session_state.invoices
    )


def _render_welcome() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <h1>🧾 Invoice Creator</h1>
            <p>Generate accurate invoice PDFs from Excel in three guided steps.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    columns = st.columns(3)

    cards = [
        ("1️⃣", "Upload", "Choose a workbook, worksheet and invoice settings."),
        ("2️⃣", "Review", "Check every invoice and make manual edits where needed."),
        ("3️⃣", "Generate", "Preview, generate and download the finished PDFs."),
    ]

    for column, (icon, title, body) in zip(columns, cards):
        with column:
            st.markdown(
                f"""
                <div class="workflow-card active">
                    <h3>{icon} {title}</h3>
                    <p>{body}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    if st.button(
        "Start creating invoices 🚀",
        type="primary",
        width="stretch",
    ):
        st.session_state.welcome_complete = True
        st.rerun()


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🧾 Invoice Creator")
        st.caption("Current workflow")

        current = st.session_state.workflow_step
        current_index = WORKFLOW_STEPS.index(current)

        for index, step in enumerate(WORKFLOW_STEPS):
            if index < current_index:
                icon = "✅"
            elif index == current_index:
                icon = "➡️"
            else:
                icon = "○"

            if st.button(
                f"{icon} {index + 1}. {step}",
                key=f"sidebar_{step}",
                type="primary" if step == current else "secondary",
                width="stretch",
            ):
                st.session_state.workflow_step = step
                st.rerun()

        st.divider()
        st.markdown("### 📌 Current batch")

        if st.session_state.excel_filename:
            st.markdown(
                f"**Workbook**  \n{st.session_state.excel_filename}"
            )
            st.markdown(
                f"**Worksheet**  \n{st.session_state.selected_sheet or 'Not selected'}"
            )
        else:
            st.caption("No workbook loaded.")

        st.markdown(
            f"**Invoice date**  \n"
            f"{st.session_state.invoice_date.strftime('%d.%m.%Y')}"
        )
        st.markdown(
            f"**Invoices**  \n{len(st.session_state.invoices)}"
        )
        st.markdown(
            f"**Selected**  \n{_selected_count()}"
        )

        st.divider()

        with st.expander("⚙️ Advanced settings"):
            st.caption(
                "These tools are available when a workbook format or layout needs adjustment."
            )

            advanced = st.radio(
                "Advanced tool",
                options=[
                    "Field Mapping",
                    "Layout",
                ],
                key="advanced_panel",
                label_visibility="collapsed",
            )

            if advanced == "Field Mapping":
                render_mapping_tab()
            else:
                render_layout_tab()

        _render_about()

        with st.expander("🗑️ Reset batch"):
            confirmed = st.checkbox(
                "Clear the current workbook and invoices",
                key="confirm_reset",
            )

            if st.button(
                "Reset everything",
                disabled=not confirmed,
                width="stretch",
            ):
                reset_state()
                st.rerun()



def _render_about() -> None:
    with st.sidebar.expander("ℹ️ About and support"):
        st.markdown(f"**{APP_NAME}**")
        st.caption(APP_DESCRIPTION)
        st.markdown(f"**Version**  \n{APP_VERSION}")
        st.markdown("**Support files**")
        st.caption(f"Logs: {logs_directory()}")
        st.caption(f"Settings: {settings_path()}")

        if st.button("Open support logs", key="open_support_logs", width="stretch"):
            try:
                open_directory(logs_directory())
            except Exception:
                LOGGER.exception("Unable to open support log directory")
                st.error("The support log folder could not be opened.")


def _render_header() -> None:
    st.markdown(
        """
        <div class="hero-card">
            <h1>🧾 Invoice Creator</h1>
            <p>Upload, review and generate invoice PDFs with confidence.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_step_cards() -> None:
    current = st.session_state.workflow_step
    current_index = WORKFLOW_STEPS.index(current)
    columns = st.columns(3)

    descriptions = {
        "Upload": "Add the workbook and choose invoice settings.",
        "Review": "Check selections, edit fields and preview invoices.",
        "Generate": "Create the final PDFs and download the batch.",
    }

    for index, (column, step) in enumerate(
        zip(columns, WORKFLOW_STEPS)
    ):
        if index < current_index:
            status = "complete"
            icon = "✅"
        elif index == current_index:
            status = "active"
            icon = "➡️"
        else:
            status = "pending"
            icon = "○"

        with column:
            st.markdown(
                f"""
                <div class="workflow-card {status}">
                    <strong>{icon} Step {index + 1}</strong>
                    <h3>{step}</h3>
                    <p>{descriptions[step]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_current_page() -> None:
    renderers = {
        "Upload": render_upload_tab,
        "Review": render_review_tab,
        "Generate": render_generate_tab,
    }
    renderers[st.session_state.workflow_step]()


def main() -> None:
    initialise_state()
    apply_requested_workflow_step()
    load_styles()
    display_pending_toast()

    if not st.session_state.welcome_complete:
        _render_welcome()
        return

    _render_sidebar()
    _render_header()
    _render_step_cards()
    st.divider()
    try:
        _render_current_page()
    except Exception as exc:
        LOGGER.exception("Unhandled application error")
        st.error(
            "Invoice Creator could not complete this action. "
            "Your current batch has not been deleted."
        )
        st.info(
            "Open **About and support** in the sidebar, then send the support log "
            "to the application administrator."
        )
        with st.expander("Technical details"):
            st.code(f"{type(exc).__name__}: {exc}", language=None)


if __name__ == "__main__":
    main()
