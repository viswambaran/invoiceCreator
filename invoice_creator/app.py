import streamlit as st

from invoice_creator.ui.state import initialise_state
from invoice_creator.ui.styles import load_styles

from invoice_creator.ui.tabs.upload import render_upload_tab
from invoice_creator.ui.tabs.review import render_review_tab
from invoice_creator.ui.tabs.mapping import render_mapping_tab
from invoice_creator.ui.tabs.layout import render_layout_tab
from invoice_creator.ui.tabs.generate import render_generate_tab


PAGES = {
    "Upload & Setup": render_upload_tab,
    "Review Invoices": render_review_tab,
    "Mapping": render_mapping_tab,
    "Layout & Preview": render_layout_tab,
    "Generate & Download": render_generate_tab,
}


def main() -> None:
    st.set_page_config(
        page_title="Invoice Creator",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    load_styles()
    initialise_state()

    with st.sidebar:
        st.title("📄 Invoice Creator")

        st.caption(
            "Generate invoice PDFs from Excel."
        )

        st.divider()

        selected_page = st.radio(
            "Navigation",
            options=list(PAGES.keys()),
            label_visibility="collapsed",
        )

        st.divider()

        excel_status = (
            "Loaded"
            if st.session_state.excel_file is not None
            else "Not loaded"
        )

        template_status = (
            "Uploaded"
            if st.session_state.template_file is not None
            else "Default template"
        )

        st.caption("Current session")

        st.write(f"**Excel:** {excel_status}")
        st.write(f"**Template:** {template_status}")
        st.write(
            f"**Invoices:** {len(st.session_state.invoices)}"
        )

    st.title(selected_page)

    st.caption(
        "Create, review and generate invoice PDFs."
    )

    page_renderer = PAGES[selected_page]
    page_renderer()


if __name__ == "__main__":
    main()