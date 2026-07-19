import streamlit as st

from invoice_creator.ui.state import initialise_state
from invoice_creator.ui.styles import load_styles

from invoice_creator.ui.tabs.upload import render_upload_tab
from invoice_creator.ui.tabs.review import render_review_tab
from invoice_creator.ui.tabs.mapping import render_mapping_tab
from invoice_creator.ui.tabs.layout import render_layout_tab
from invoice_creator.ui.tabs.generate import render_generate_tab


st.set_page_config(
    page_title="Invoice Creator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

load_styles()

initialise_state()

st.title("📄 Invoice Creator")

st.caption(
    "Generate professional invoice PDFs from Excel."
)

tab_upload,\
tab_review,\
tab_mapping,\
tab_layout,\
tab_generate = st.tabs(
    [
        "Upload & Setup",
        "Review",
        "Mapping",
        "Layout",
        "Generate"
    ]
)

with tab_upload:
    render_upload_tab()

with tab_review:
    render_review_tab()

with tab_mapping:
    render_mapping_tab()

with tab_layout:
    render_layout_tab()

with tab_generate:
    render_generate_tab()