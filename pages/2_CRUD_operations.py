import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# --- Page config: full-width, single call ---
st.set_page_config(
    page_title="📂 SQL Data Management & Contact Information",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📂 SQL Data Management & Contact Information")

# --- Database Connection (lazy load inside functions) ---
def get_engine():
    try:
        return create_engine("mysql+pymysql://root:Arvind%402003@localhost/food_wastage_management")
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def run_query(query):
    engine = get_engine()
    if engine:
        return pd.read_sql_query(query, con=engine)
    else:
        return pd.DataFrame()  # Return empty DF if DB connection fails

def execute_query(query):
    engine = get_engine()
    if engine:
        with engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()

def input_form(columns, prefix=""):
    """Generate a form with text inputs for each column."""
    new_data = {}
    for col in columns:
        new_data[col] = st.text_input(f"Enter {col}", key=f"{prefix}_{col}")
    return new_data

# --- Table List ---
DATASETS = ["providers", "receivers", "food_listings", "claims"]

# --- Initialize refresh state ---
if "refresh_counter" not in st.session_state:
    st.session_state.refresh_counter = 0

# --- Tabs ---
tab1, tab2 = st.tabs(["🛠️ CRUD Operations", "📞 Contact Information"])

# =====================================================
# TAB 1: CRUD OPERATIONS
# =====================================================
with tab1:
    st.header("🛠️ SQL CRUD Operations")
    dataset_name = st.selectbox("Select Dataset", DATASETS, key="crud_dataset_selector")

    df = run_query(f"SELECT * FROM {dataset_name};")

    st.markdown("### 🔎 Current Data")
    st.dataframe(df)

    # ---------------- CREATE ----------------
    st.markdown("### ➕ Add New Entry")
    if not df.empty:
        new_data = input_form(df.columns, prefix="add")
        if st.button("Add Entry"):
            if all(str(v).strip() != "" for v in new_data.values()):
                cols = ", ".join(new_data.keys())
                vals = ", ".join([f"'{v}'" for v in new_data.values()])
                query = f"INSERT INTO {dataset_name} ({cols}) VALUES ({vals});"
                try:
                    execute_query(query)
                    st.success("✅ Entry added successfully!")
                    st.session_state.refresh_counter += 1
                except Exception as e:
                    st.error(f"Error inserting data: {e}")
            else:
                st.warning("⚠ Please fill all fields before adding.")

    # ---------------- UPDATE ----------------
    if not df.empty:
        st.markdown("### ✏ Update Entry")
        selected_index = st.number_input("Row index to update", min_value=0, max_value=len(df)-1, step=1)
        updated_data = {}
        for col in df.columns:
            updated_data[col] = st.text_input(f"{col} (current: {df.loc[selected_index, col]})", key=f"upd_{col}")
        if st.button("Update Entry"):
            set_clause = ", ".join([f"{col}='{updated_data[col]}'" for col in df.columns])
            primary_key_col = df.columns[0]
            primary_key_val = df.loc[selected_index, primary_key_col]
            query = f"UPDATE {dataset_name} SET {set_clause} WHERE {primary_key_col}='{primary_key_val}';"
            try:
                execute_query(query)
                st.success("✅ Entry updated successfully!")
                st.session_state.refresh_counter += 1
            except Exception as e:
                st.error(f"Error updating data: {e}")

    # ---------------- DELETE ----------------
    if not df.empty:
        st.markdown("### ❌ Delete Entry")
        delete_index = st.number_input("Row index to delete", min_value=0, max_value=len(df)-1, step=1, key="del_idx")
        if st.button("Delete Entry"):
            primary_key_col = df.columns[0]
            primary_key_val = df.loc[delete_index, primary_key_col]
            query = f"DELETE FROM {dataset_name} WHERE {primary_key_col}='{primary_key_val}';"
            try:
                execute_query(query)
                st.success("✅ Entry deleted successfully!")
                st.session_state.refresh_counter += 1
            except Exception as e:
                st.error(f"Error deleting data: {e}")

# =====================================================
# TAB 2: CONTACT INFORMATION
# =====================================================
with tab2:
    st.header("📞 Provider & Receiver Contact Info")
    contact_tabs = st.tabs(["🏪 Providers", "🏠 Receivers"])

    def get_name_column(df):
        for col in df.columns:
            if "name" in col.lower():
                return col
        return None

    # --- Providers ---
    with contact_tabs[0]:
        try:
            providers_df = run_query("SELECT * FROM providers;")
            if not providers_df.empty:
                contact_cols = [c for c in providers_df.columns if any(x in c.lower() for x in ["name","email","phone","contact"])]
                name_col = get_name_column(providers_df)
                if name_col:
                    search_name = st.text_input("Search Providers by Name", key="search_provider_name")
                    filtered_df = providers_df
                    if search_name:
                        filtered_df = providers_df[providers_df[name_col].str.contains(search_name, case=False, na=False)]
                    st.dataframe(filtered_df[contact_cols])
                else:
                    st.warning("⚠ No name column found in providers table.")
                    st.dataframe(providers_df[contact_cols])
            else:
                st.warning("Providers table is empty.")
        except Exception as e:
            st.error(f"Error loading providers: {e}")

    # --- Receivers ---
    with contact_tabs[1]:
        try:
            receivers_df = run_query("SELECT * FROM receivers;")
            if not receivers_df.empty:
                contact_cols = [c for c in receivers_df.columns if any(x in c.lower() for x in ["name","email","phone","contact"])]
                name_col = get_name_column(receivers_df)
                if name_col:
                    search_name = st.text_input("Search Receivers by Name", key="search_receiver_name")
                    filtered_df = receivers_df
                    if search_name:
                        filtered_df = receivers_df[receivers_df[name_col].str.contains(search_name, case=False, na=False)]
                    st.dataframe(filtered_df[contact_cols])
                else:
                    st.warning("⚠ No name column found in receivers table.")
                    st.dataframe(receivers_df[contact_cols])
            else:
                st.warning("Receivers table is empty.")
        except Exception as e:
            st.error(f"Error loading receivers: {e}")
