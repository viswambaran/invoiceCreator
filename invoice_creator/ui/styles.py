import streamlit as st


def load_styles() -> None:
    st.markdown(
        """
        <style>
            .block-container {
                max-width: 1450px;
                padding-top: 1.25rem;
                padding-bottom: 3rem;
            }

            .hero-card {
                padding: 1.35rem 1.5rem;
                border: 1px solid rgba(128,128,128,.20);
                border-radius: 1rem;
                background: var(--secondary-background-color);
                margin-bottom: 1rem;
            }

            .hero-card h1 {
                margin: 0 0 .35rem 0;
            }

            .hero-card p {
                margin: 0;
                opacity: .75;
                font-size: 1.02rem;
            }

            .workflow-card {
                padding: 1rem 1.1rem;
                border: 1px solid rgba(128,128,128,.20);
                border-radius: .85rem;
                background: var(--secondary-background-color);
                min-height: 118px;
            }

            .workflow-card.complete {
                border-left: 5px solid #2e7d32;
            }

            .workflow-card.active {
                border-left: 5px solid #1976d2;
            }

            .workflow-card.pending {
                opacity: .72;
            }

            .next-step-card {
                padding: 1.25rem 1.4rem;
                border: 1px solid rgba(128,128,128,.20);
                border-radius: 1rem;
                background: var(--secondary-background-color);
                margin-top: 1rem;
            }

            div[data-testid="stMetric"] {
                padding: .85rem 1rem;
                border: 1px solid rgba(128,128,128,.18);
                border-radius: .8rem;
                background: var(--secondary-background-color);
            }

            section[data-testid="stSidebar"] {
                border-right: 1px solid rgba(128,128,128,.20);
            }

            div.stButton > button,
            div.stDownloadButton > button {
                border-radius: .6rem;
                min-height: 2.55rem;
            }

            [data-testid="stDataFrame"] {
                border: 1px solid rgba(128,128,128,.18);
                border-radius: .8rem;
                overflow: hidden;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
