from sqlalchemy import create_engine
import pandas as pd
import streamlit as st

# --- Database Connection ---
engine = create_engine("mysql+pymysql://root:Arvind%402003@localhost/food_wastage_management")

@st.cache_data
def run_query(query):
    return pd.read_sql_query(query, con=engine)

# --- Local CSV Loading ---
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

# --- Datasets Dictionary ---
DATASETS = {
    "Providers": "providers_data.csv",
    "Receivers": "receivers_data.csv",
    "Food Listings": "food_listings_data.csv",
    "Claims": "claims_data.csv"
}

DATASET_DESCRIPTIONS = {
    "Providers": "Contains information about food providers such as restaurants or individuals.",
    "Receivers": "Includes details of NGOs or individuals who can receive food.",
    "Food Listings": "Details of available food, quantity, and location.",
    "Claims": "Tracks who claimed food, when, and from which provider."
}

# --- Streamlit Interface ---
st.set_page_config(page_title="Local Food Waste Management", layout="wide")

with st.container(border=True):
    st.title('Local Food Waste Management')
    st.write(
    """Food wastage is a significant issue, with many households and restaurants discarding surplus food while numerous people struggle with food insecurity. 
    This project aims to develop a Local Food Wastage Management System, where:
    - Restaurants and individuals can list surplus food.
    - NGOs or individuals in need can claim the food.
    - SQL stores available food details and locations.
    - A Streamlit app enables interaction, filtering, CRUD operation and visualization.""")
    
 
    col1, col2 = st.columns([2, 2], gap = 'large')
    with col1:
        with st.container(border=True):
            st.write("## Tools Used")
            st.write("- Python\n- SQLite / MySQL\n- Streamlit\n- Pandas\n- Plotly / Matplotlib")
    with col2:
        with st.container(border=True):
            st.write("## Dataset Sources")
            st.write("- Providers Dataset: providers_data.csv\n- Receivers Dataset: receivers_data.csv\n- Food Listings Dataset: food_listings_data.csv\n- Claims Dataset: claims_data.csv")
            
with st.container(border=True):
    # - Dataset Description Section ---
    st.title("📄 Dataset Description")


    # --- Tabs for each dataset ---
    tab1, tab2, tab3, tab4 = st.tabs(["📜 Claims", "🍱 Food Listings", "🏪 Providers", "🏠 Receivers"])

    # --- Helper function to display data ---
    def display_table(table_name, description_key):
        try:
            df = run_query(f"SELECT * FROM {table_name};")
            with st.container(border=True):
                st.markdown(f"### 🧾 Description of `{table_name}`")
                st.markdown(DATASET_DESCRIPTIONS.get(description_key, "No description available."))

            if not df.empty:
                st.markdown("### 📊 Data Preview")
                st.dataframe(df)
                st.success(f"Loaded {len(df)} records from `{table_name}` table.")
            else:
                st.warning(f"The `{table_name}` table is empty.")
        except Exception as e:
            st.error(f"❌ Error loading `{table_name}`: {e}")

    # --- Each Tab ---
    with tab1:
        display_table("claims", "Claims")

    with tab2:
        display_table("food_listings", "Food Listings")

    with tab3:
        display_table("providers", "Providers")

    with tab4:
        display_table("receivers", "Receivers")
