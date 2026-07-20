import streamlit as st


def render_layout_tab():

    st.header("Layout Preview")

    st.caption(
        "Global offsets for writing into the PDF."
    )

    x = st.slider(
        "Horizontal offset",
        -20,
        20,
        int(
            st.session_state.layout_offsets["x"]
        ),
    )

    y = st.slider(
        "Vertical offset",
        -20,
        20,
        int(
            st.session_state.layout_offsets["y"]
        ),
    )

    st.session_state.layout_offsets["x"] = x
    st.session_state.layout_offsets["y"] = y

    st.success(
        f"Current Offset : X {x}px   Y {y}px"
    )

    st.info(
        "The PDF preview/editor will be added here later."
    )