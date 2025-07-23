import streamlit as st
import pandas as pd
import numpy as np

st.markdown("""
    <style>
    /* Add a linear RGB border around the whole app */
    .main {
        border: 6px solid;
        border-image: linear-gradient(to right, red, green, blue) 1;
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        transition: all 0.3s ease-in-out;
    }

    /* Add a subtle hover effect for the whole app body */
    .main:hover {
        box-shadow: 0 0 25px rgba(255, 0, 255, 0.6);
        transform: scale(1.01);
    }

    /* Optional: Make background slightly interactive */
    body {
        background: linear-gradient(135deg, #f0f2f5, #ffffff);
    }

    /* Enhance elements on hover (e.g., dataframe/table cells) */
    .css-1d391kg:hover, .css-1d391kg:focus {
        background-color: rgba(220, 220, 250, 0.3) !important;
        transition: all 0.3s ease-in-out;
    }
    </style>
""", unsafe_allow_html=True)

# Generate your DataFrame
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

# 🔧 Convert to native Pandas DataFrame (if wrapped by narwhals or others)
if hasattr(chart_data, "to_native"):
    chart_data = chart_data.to_native()

# Plot
st.title("Fixed Bar Chart")
st.bar_chart(chart_data)
st.markdown("</div>", unsafe_allow_html=True)