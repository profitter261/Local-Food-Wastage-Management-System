# streamlit_foodshare_app.py
import streamlit as st
import pandas as pd
import os
import sqlite3
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Food Sharing App", layout="wide")

# ---------------------
# Configuration
# ---------------------
# Map friendly dataset names to CSV file paths used throughout the app
DATASETS = {
    "Providers": "providers_data.csv",
    "Receivers": "receivers_data.csv",
    "Foodlisting": "food_listings_data.csv",
    "Claims": "claims_data.csv",
    "ClaimsWithDateTime": "claims_with_date_time (1).csv"
}

DATASET_DESCRIPTIONS = {
    "Providers": """
The `providers.csv` file contains details of food providers.

- **Provider_ID**: Unique ID  
- **Name**: Provider name  
- **Type**: Restaurant/Grocery/etc  
- **Address**: Full address  
- **City**: City name  
- **Contact**: Phone/email  
""",
    "Receivers": """
The `receivers.csv` file contains details of receivers.

- **Receiver_ID**: Unique ID  
- **Name**: Receiver name  
- **Type**: NGO/Individual/etc  
- **City**: City name  
- **Contact**: Phone/email  
""",
    "Foodlisting": """
The `food_listings.csv` contains available food details.

- **Food_ID**: Unique ID  
- **Food_Name**: Item name  
- **Quantity**: Amount available  
- **Expiry_Date**: Expiration date  
- **Provider_ID**: Linked provider  
- **Provider_Type**: Provider category  
- **Location**: City  
- **Food_Type**: Veg/Non-Veg/Vegan  
- **Meal_Type**: Breakfast/Lunch/etc  
""",
    "Claims": """
The `claims.csv` file contains claim records.

- **Claim_ID**: Unique ID  
- **Food_ID**: Food item reference  
- **Receiver_ID**: Receiver reference  
- **Status**: Pending/Completed  
- **Timestamp**: Date and time  
"""
}

# ---------------------
# Helpers
# ---------------------
def load_data(file_path):
    """Load CSV if exists, return DataFrame (empty DF if missing)."""
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            st.error(f"Error reading {file_path}: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

def save_data(file_path, df):
    """Save DataFrame to CSV (create directories if needed)."""
    try:
        df.to_csv(file_path, index=False)
    except Exception as e:
        st.error(f"Error saving to {file_path}: {e}")

def input_form(columns, prefix="new"):
    """Return dictionary of text inputs for each column name."""
    new_data = {}
    for col in columns:
        new_data[col] = st.text_input(f"Enter {col}", key=f"{prefix}_{col}")
    return new_data

# ---------------------
# Sidebar Navigation
# ---------------------
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", [
    "Project Introduction",
    "Dataset Description",
    "CRUD operations",
    "SQL Queries",
    "Learner SQL queries",
    "User Introduction"
])

# Optional: Example MySQL connection (commented) - uncomment and configure if you need DB connection
# import mysql.connector
# try:
#     mysql_conn = mysql.connector.connect(
#         host="127.0.0.1",
#         user="root",
#         password="your_password",
#         database="your_database_name"
#     )
# except Exception as e:
#     st.warning(f"MySQL connection failed or not configured: {e}")

# ---------------------
# Pages
# ---------------------
if choice == "Project Introduction":
    st.title('Local Food Waste Management')
    st.write(
"""Food wastage is a significant issue, with many households and restaurants discarding surplus food while numerous people struggle with food insecurity. This project aims to develop a Local Food Wastage Management System, where:
- Restaurants and individuals can list surplus food.
- NGOs or individuals in need can claim the food.
- SQL stores available food details and locations.
- A Streamlit app enables interaction, filtering, CRUD operation and visualization.""")
    
    st.write("## Tools Used")
    st.write("- Python\n- SQLite (in-memory for queries)\n- Streamlit\n- Pandas\n- Plotly / Matplotlib")
    st.write("## Dataset")
    st.write("- Providers Dataset : providers_data.csv\n- Receivers Dataset: receivers_data.csv\n- Food Listings Dataset: food_listings_data.csv\n- Claims Dataset: claims_data.csv")

# ---------------------
# Dataset Description Page
# ---------------------
elif choice == "Dataset Description":
    st.title("📄 Dataset Description")
    selected_dataset = st.selectbox("Choose a dataset to view:", list(DATASETS.keys()), key="desc_dataset_selector")
    df = load_data(DATASETS[selected_dataset])

    st.markdown(f"### 🧾 Description of `{selected_dataset}`")
    st.markdown(DATASET_DESCRIPTIONS.get(selected_dataset, "No description available."))

    if not df.empty:
        st.markdown("### 📊 Data Preview")
        st.dataframe(df)
    else:
        st.warning("Dataset is empty or not found. Make sure the CSV is in the app folder and has the correct filename.")

# ---------------------
# CRUD Page
# ---------------------
elif choice == "CRUD operations":
    dataset_name = st.selectbox("Select Dataset", list(DATASETS.keys()), key="crud_dataset_selector")
    st.title("🛠️ CSV CRUD Operations")

    csv_file = DATASETS[dataset_name]
    df = load_data(csv_file)

    # Show data
    st.markdown("### 🔎 Current Data")
    st.dataframe(df)

    # Create
    st.markdown("### ➕ Add New Entry")
    if not df.empty:
        new_data = input_form(df.columns, prefix="add")
        if st.button("Add Entry"):
            # require non-empty values
            if all(str(value).strip() != "" for value in new_data.values()):
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                save_data(csv_file, df)
                st.success("✅ Entry added successfully!")
                st.experimental_rerun()
            else:
                st.warning("Please fill all fields before adding.")
    else:
        st.info("Dataset is empty or missing. To create entries you should place a CSV with header columns or create a CSV manually.")

    # Update
    if not df.empty:
        st.markdown("### ✏ Update Entry")
        selected_index = st.number_input("Row index to update", min_value=0, max_value=len(df)-1, step=1)
        updated_data = {}
        for col in df.columns:
            updated_data[col] = st.text_input(f"{col} (current: {df.loc[selected_index, col]})", key=f"upd_{col}")
        if st.button("Update Entry"):
            for col in df.columns:
                # only update if input not empty (allow blank to overwrite if desired)
                df.at[selected_index, col] = updated_data[col]
            save_data(csv_file, df)
            st.success("✅ Entry updated successfully!")
            st.experimental_rerun()

    # Delete
    if not df.empty:
        st.markdown("### ❌ Delete Entry")
        delete_index = st.number_input("Row index to delete", min_value=0, max_value=len(df)-1, step=1, key="del_idx")
        if st.button("Delete Entry"):
            df = df.drop(delete_index).reset_index(drop=True)
            save_data(csv_file, df)
            st.success("✅ Entry deleted successfully!")
            st.experimental_rerun()

# ---------------------
# SQL Queries / Explore Page
# ---------------------
elif choice == "SQL Queries":
    # Load CSVs
    food_listings = load_data(DATASETS["Foodlisting"])
    claims = load_data(DATASETS["Claims"])
    # load optional claims with detailed datetime if present
    claims2 = load_data(DATASETS.get("ClaimsWithDateTime", "claims_with_date_time (1).csv"))
    receivers = load_data(DATASETS["Receivers"])
    providers = load_data(DATASETS["Providers"])

    # Setup SQLite in-memory DB
    sql_conn = sqlite3.connect(":memory:")

    # Push CSVs to SQLite tables (only those that are non-empty)
    if not food_listings.empty:
        food_listings.to_sql("food_listings", sql_conn, index=False, if_exists='replace')
    else:
        st.warning("food_listings_data.csv is empty or missing — some queries will not work.")

    if not claims.empty:
        claims.to_sql("claims", sql_conn, index=False, if_exists='replace')

    if not claims2.empty:
        claims2.to_sql("claims2", sql_conn, index=False, if_exists='replace')

    if not receivers.empty:
        receivers.to_sql("receivers", sql_conn, index=False, if_exists='replace')

    if not providers.empty:
        providers.to_sql("providers", sql_conn, index=False, if_exists='replace')

    st.title("Food Distribution Dashboard")
    option = st.sidebar.selectbox("Select a query to run:", (
        "Food providers and recievers by city",
        "Maximum Contributor/Provider",
        "Provider's contact information",
        "Recievers with most Food Claims",
        "total food available from providers",
        "Highest Food Listings",
        "commonly available Food",
        "Total food claims per food item",
        "provider with high number of succesful claims",
        "percentage of food claim status",
        "average quantity of food claims per reciever",
        "most claimed meal type",
        "food donated by each provider",
        "fast expiring products",
        "faster claim rate",
    ))

    # Example option: providers & receivers by city
    if option == "Food providers and recievers by city":
        st.subheader("City-wise Count of Providers and Receivers")
        # guard for missing tables
        try:
            df_providers = pd.read_sql_query("SELECT City, COUNT(*) AS number_of_providers FROM providers GROUP BY City", sql_conn)
            df_receivers = pd.read_sql_query("SELECT City, COUNT(*) AS number_of_receivers FROM receivers GROUP BY City", sql_conn)
            col1, spacer, col2 = st.columns([1, 0.2, 1])
            with col1:
                st.markdown("#### Providers by City")
                st.dataframe(df_providers)
            with col2:
                st.markdown("#### Receivers by City")
                st.dataframe(df_receivers)
        except Exception as e:
            st.error(f"Query failed — check the CSVs are present and have expected columns. Error: {e}")

    # Maximum Contributor/Provider
    if option == "Maximum Contributor/Provider":
        try:
            provider_names = pd.read_sql_query("SELECT DISTINCT Type FROM providers", sql_conn) if not providers.empty else pd.DataFrame()
            selected_provider = st.selectbox("Filter by Provider Type", ["All"] + provider_names['Type'].dropna().tolist() if not provider_names.empty else ["All"])
            if selected_provider != "All":
                query_max = f"""
                    SELECT Type, COUNT(Type) AS provider_type
                    FROM providers
                    WHERE Type = ?
                    GROUP BY Type
                    ORDER BY provider_type DESC
                """
                df_max = pd.read_sql_query(query_max, sql_conn, params=(selected_provider,))
            else:
                query_max = """
                    SELECT Type, COUNT(Type) AS provider_type
                    FROM providers
                    GROUP BY Type
                    ORDER BY provider_type DESC
                """
                df_max = pd.read_sql_query(query_max, sql_conn)
            if not df_max.empty:
                st.metric("Top Provider Type", df_max['Type'].iloc[0])
                st.dataframe(df_max)
                st.bar_chart(data=df_max.set_index('Type'))
            else:
                st.warning("No provider data available.")
        except Exception as e:
            st.error(f"Query failed: {e}")

    # Provider's contact information
    if option == "Provider's contact information":
        try:
            df_contact = pd.read_sql_query("SELECT City, Contact FROM providers GROUP BY City", sql_conn)
            cities = st.multiselect("Select Cities", df_contact['City'].unique() if not df_contact.empty else [])
            if cities:
                filtered_df = df_contact[df_contact['City'].isin(cities)]
            else:
                filtered_df = df_contact
            st.dataframe(filtered_df)
        except Exception as e:
            st.error(f"Query failed: {e}")

    # Recievers with most Food Claims (example simplified)
    if option == "Recievers with most Food Claims":
        try:
            if 'receivers' in sql_conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
                # Use receivers table counts by Type
                df_r_max = pd.read_sql_query("SELECT Type, COUNT(*) AS reciever_count FROM receivers GROUP BY Type", sql_conn)
            else:
                df_r_max = pd.DataFrame()
            st.dataframe(df_r_max)
            if not df_r_max.empty:
                st.bar_chart(data=df_r_max.set_index('Type'))
        except Exception as e:
            st.error(f"Query failed: {e}")

    # total food available from providers
    if option == "total food available from providers":
        try:
            df_r_max = pd.read_sql_query("""
                SELECT Provider_Type AS provider, SUM(Quantity) AS Quantity
                FROM food_listings
                GROUP BY Provider_Type
            """, sql_conn)
            st.metric("Total Providers Quantity:", int(df_r_max['Quantity'].sum()) if not df_r_max.empty else 0)
            st.dataframe(df_r_max)
            if not df_r_max.empty:
                st.bar_chart(data=df_r_max.set_index('provider'))
        except Exception as e:
            st.error(f"Query failed: {e}")

    # Highest Food Listings
    if option == "Highest Food Listings":
        try:
            df_r_max = pd.read_sql_query("SELECT Location, COUNT(Food_Name) AS food_list FROM food_listings GROUP BY Location ORDER BY food_list DESC", sql_conn)
            if not df_r_max.empty:
                st.metric("Top Location (by listings)", df_r_max['Location'].iloc[0])
            st.dataframe(df_r_max)
        except Exception as e:
            st.error(f"Query failed: {e}")

    # commonly available Food
    if option == "commonly available Food":
        try:
            df_food_types = pd.read_sql_query("""
                SELECT Food_Type, COUNT(Food_Type) AS avail_food_type
                FROM food_listings
                GROUP BY Food_Type
                ORDER BY avail_food_type DESC
            """, sql_conn)
            if not df_food_types.empty:
                st.metric("Most Available Food Type", df_food_types["Food_Type"].iloc[0])
                st.dataframe(df_food_types)
                chart_type = st.radio("Choose Chart Type", ["Pie Chart", "Bar Chart"])
                if chart_type == "Pie Chart":
                    fig, ax = plt.subplots(figsize=(8, 5))
                    ax.pie(df_food_types["avail_food_type"], labels=df_food_types["Food_Type"], autopct='%1.1f%%', startangle=90)
                    ax.axis("equal")
                    st.pyplot(fig)
                else:
                    fig = px.bar(df_food_types, x="Food_Type", y="avail_food_type", labels={"avail_food_type":"Count"})
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No food data available.")
        except Exception as e:
            st.error(f"Query failed: {e}")

    # total food claims per food item
    if option == "Total food claims per food item":
        try:
            query = """
                SELECT f.Food_Name, COUNT(c.Claim_ID) AS no_food_claims
                FROM food_listings f
                JOIN claims c ON c.Food_ID = f.Food_ID
                GROUP BY f.Food_Name
                ORDER BY no_food_claims DESC
            """
            df_r_max = pd.read_sql_query(query, sql_conn)
            if df_r_max.empty:
                st.warning("No matching claims or food_listings data.")
            else:
                st.dataframe(df_r_max)
                fig = px.bar(df_r_max, x='Food_Name', y='no_food_claims', title="Total Claims Per Food Item")
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Query failed: {e}")

    # provider with high number of succesful claims (example)
    if option == "provider with high number of succesful claims":
        try:
            df_r_max = pd.read_sql_query("""
                SELECT Provider_Type AS Provider, SUM(Quantity) AS total_food_provided
                FROM food_listings
                GROUP BY Provider_Type
            """, sql_conn)
            st.dataframe(df_r_max)
            if not df_r_max.empty:
                fig = px.bar(df_r_max, x='Provider', y='total_food_provided', title='Total Food Quantity Provided by Each Provider Type')
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Query failed: {e}")

    # percentage of food claim status
    if option == "percentage of food claim status":
        try:
            df_r_max = pd.read_sql_query("""
                SELECT Status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS percentage
                FROM claims
                GROUP BY Status
            """, sql_conn)
            st.dataframe(df_r_max)
            if not df_r_max.empty:
                fig = px.pie(df_r_max, values='percentage', names='Status', title='Food Claim Status Distribution (%)', hole=0.4)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Query failed: {e}")

    # fast expiring products
    if option == "fast expiring products":
        try:
            df_expiring = pd.read_sql_query("SELECT Food_Name, Expiry_Date FROM food_listings ORDER BY Expiry_Date ASC", sql_conn)
            if df_expiring.empty:
                st.warning("No expiry data available.")
            else:
                df_expiring["Expiry_Date"] = pd.to_datetime(df_expiring["Expiry_Date"], errors='coerce')
                df_expiring = df_expiring.dropna(subset=["Expiry_Date"])
                st.dataframe(df_expiring.sort_values("Expiry_Date").head(50))
        except Exception as e:
            st.error(f"Query failed: {e}")

    # faster claim rate (simplified safe version)
    if option == "faster claim rate":
        try:
            # Use claims and food_listings if available
            if not claims.empty and not food_listings.empty:
                merged = claims.merge(food_listings[['Food_ID', 'Location', 'Expiry_Date']], on='Food_ID', how='left')
                merged['Timestamp'] = pd.to_datetime(merged['Timestamp'], errors='coerce')
                merged['Expiry_Date'] = pd.to_datetime(merged['Expiry_Date'], errors='coerce')
                merged = merged.dropna(subset=['Timestamp', 'Expiry_Date'])
                merged['days_between'] = (merged['Expiry_Date'] - merged['Timestamp']).dt.days
                # group by Location, take average absolute days difference
                df_fast_claims = merged.groupby('Location', as_index=False)['days_between'].mean().rename(columns={'days_between':'avg_days_to_claim'})
                df_fast_claims = df_fast_claims.sort_values('avg_days_to_claim')
                st.dataframe(df_fast_claims.head(10))
                if not df_fast_claims.empty:
                    fig = px.bar(df_fast_claims.head(10), x='Location', y='avg_days_to_claim', title='Average Days Between Claim Timestamp and Expiry Date (by Location)')
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Need both claims_data.csv and food_listings_data.csv for this calculation.")
        except Exception as e:
            st.error(f"Computation failed: {e}")

# ---------------------
# Learner SQL queries (kept similar structure but guarded)
# ---------------------
elif choice == "Learner SQL queries":
    # Load CSVs and push to sqlite
    food_listings = load_data(DATASETS["Foodlisting"])
    claims = load_data(DATASETS["Claims"])
    claims2 = load_data(DATASETS.get("ClaimsWithDateTime", "claims_with_date_time (1).csv"))
    receivers = load_data(DATASETS["Receivers"])
    providers = load_data(DATASETS["Providers"])

    sql_conn = sqlite3.connect(":memory:")
    if not food_listings.empty: food_listings.to_sql("food_listings", sql_conn, index=False, if_exists='replace')
    if not claims.empty: claims.to_sql("claims", sql_conn, index=False, if_exists='replace')
    if not claims2.empty: claims2.to_sql("claims2", sql_conn, index=False, if_exists='replace')
    if not receivers.empty: receivers.to_sql("receivers", sql_conn, index=False, if_exists='replace')
    if not providers.empty: providers.to_sql("providers", sql_conn, index=False, if_exists='replace')

    st.title("Learner SQL Dashboard")
    option = st.sidebar.selectbox("Select a query to run:", (
        "Reciever share distribution of food",
        "share percent of food provided by each provider",
        "Succesful meal types",
        "most providing food provider",
        "vegan vs non veg vs veg for each meal type"
    ))

    if option == "Reciever share distribution of food":
        try:
            df_r_max = pd.read_sql_query("""
                SELECT Type AS receiver_type,
                       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM receivers) AS percentage_share
                FROM receivers
                GROUP BY Type
            """, sql_conn)
            st.dataframe(df_r_max)
            fig = px.pie(df_r_max, names='receiver_type', values='percentage_share', title='Receiver Type Share (%)')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Query failed: {e}")

    if option == "share percent of food provided by each provider":
        try:
            df_p_max = pd.read_sql_query("""
                SELECT Type AS provider_type,
                       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM providers) AS percentage_share
                FROM providers
                GROUP BY Type
            """, sql_conn)
            st.dataframe(df_p_max)
            fig = px.bar(df_p_max, x='provider_type', y='percentage_share', title='Provider Type Share (%)')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Query failed: {e}")

    if option == "Succesful meal types":
        try:
            df_meal_success = pd.read_sql_query("""
                SELECT f.Meal_Type,
                       SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / (
                           SELECT COUNT(*) FROM claims WHERE Status = 'Completed'
                       ) AS success_percentage
                FROM claims c
                JOIN food_listings f ON c.Food_ID = f.Food_ID
                GROUP BY f.Meal_Type
                ORDER BY success_percentage DESC
            """, sql_conn)
            st.dataframe(df_meal_success)
            fig = px.bar(df_meal_success, x='Meal_Type', y='success_percentage', title='Success Rate of Meal Types (%)')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Query failed: {e}")

    if option == "most providing food provider":
        try:
            df_provider_success = pd.read_sql_query("""
                SELECT f.Provider_Type,
                       ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate
                FROM food_listings f
                JOIN claims c ON f.Food_ID = c.Food_ID
                GROUP BY f.Provider_Type
                ORDER BY success_rate DESC
            """, sql_conn)
            st.dataframe(df_provider_success)
            fig = px.bar(df_provider_success, x='Provider_Type', y='success_rate', title='Success Rate by Provider Type (%)')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Query failed: {e}")

    if option == "vegan vs non veg vs veg for each meal type":
        try:
            df_vegan = pd.read_sql_query("SELECT Meal_Type, COUNT(*) AS count_vegan FROM food_listings WHERE Food_Type = 'Vegan' GROUP BY Meal_Type", sql_conn)
            df_vegetarian = pd.read_sql_query("SELECT Meal_Type, COUNT(*) AS count_vegetarian FROM food_listings WHERE Food_Type = 'Vegetarian' GROUP BY Meal_Type", sql_conn)
            df_non_veg = pd.read_sql_query("SELECT Meal_Type, COUNT(*) AS count_non_veg FROM food_listings WHERE Food_Type = 'Non-Vegetarian' GROUP BY Meal_Type", sql_conn)

            df_merge = pd.merge(pd.merge(df_vegan, df_vegetarian, on='Meal_Type', how='outer'), df_non_veg, on='Meal_Type', how='outer').fillna(0)
            st.dataframe(df_merge)

            chart_type = st.radio("Select Chart Type", ["Stacked Bar", "Pie (per Meal Type)"])
            if chart_type == "Stacked Bar":
                fig = px.bar(df_merge, x='Meal_Type', y=['count_vegan','count_vegetarian','count_non_veg'], title='Meal Preferences by Type (Stacked)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                for _, row in df_merge.iterrows():
                    fig = px.pie(names=['Vegan','Vegetarian','Non-Vegetarian'], values=[row['count_vegan'], row['count_vegetarian'], row['count_non_veg']], title=row['Meal_Type'])
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Query failed: {e}")

# ---------------------
# Contact / About
# ---------------------
elif choice == "User Introduction":
    st.title("About the Creator")
    st.write('Arvind S')
    st.write('phone: 9685696856')
    st.write("Email us at: support@foodshare.org")
