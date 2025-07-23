import streamlit as st
import pandas as pd
import os
from pandasql import sqldf
import plotly.express as px
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.markdown("""
    <style>
    /* Outer container hover and border gradient */
    .main {
        border: 6px solid;
        border-image: linear-gradient(to right, red, green, blue) 1;
        border-radius: 15px;
        padding: 15px;
        transition: all 0.3s ease-in-out;
    }

    .main:hover {
        box-shadow: 0 0 25px rgba(255, 0, 255, 0.5);
        transform: scale(1.01);
    }

    /* Optional: Background and smoother font */
    body {
        background: linear-gradient(to right, #f7f7f7, #ffffff);
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Food Sharing App", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ["Project Introduction", "Dataset Description", "CRUD operations", "SQL Queries", "Learner SQL queries", "User Introduction"])

# Datasets and Description
DATASETS = {
    "Providers": "providers_data.csv",
    "Receivers": "receivers_data.csv",
    "Foodlisting": "food_listings_data.csv",
    "Claims": "claims_data.csv"
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

# Load CSV into DataFrame
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

# Save DataFrame back to CSV
def save_data(file_path, df):
    df.to_csv(file_path, index=False)

# Dynamic input form
def input_form(columns):
    new_data = {}
    for col in columns:
        new_data[col] = st.text_input(f"Enter {col}")
    return new_data

if choice == "Project Introduction":
    st.title('Local Food Waste Management')
    st.write(
"""Food wastage is a significant issue, with many households and restaurants discarding surplus food while numerous people struggle with food insecurity. This project aims to develop a Local Food Wastage Management System, where:
- Restaurants and individuals can list surplus food.
- NGOs or individuals in need can claim the food.
- SQL stores available food details and locations.
- A Streamlit app enables interaction, filtering, CRUD operation and visualization.""")
    st.write(
""" ## Business Use Cases
- Connecting surplus food providers to those in need through a structured platform.
- Reducing food waste by redistributing excess food efficiently.
- Enhancing accessibility via geolocation features to locate food easily.
- Data analysis on food wastage trends for better decision-making.""")
    st.write(
""" ## Tools Used
- Python.
- Sql Lite 3.
- Streamlit.""")
    st.write(
""" ## Dataset
- Providers Dataset : providers_data.csv
- Receivers Dataset: receivers_data.csv
- Food Listings Dataset: food_listings_data.csv
- Claims Dataset: claims_data.csv""")
    
    
# Dataset Description Page
elif choice == "Dataset Description":
    st.title("📄 Dataset Description")
    selected_dataset = st.selectbox("Choose a dataset to view:", list(DATASETS.keys()), key="desc_dataset_selector")
    df = load_data(DATASETS[selected_dataset])

    st.markdown(f"### 🧾 Description of `{selected_dataset}`")
    st.markdown(DATASET_DESCRIPTIONS[selected_dataset])

    if not df.empty:
        st.markdown(f"### 📊 Data Preview")
        st.dataframe(df)
    else:
        st.warning("Dataset is empty or not found.")

# CRUD Page
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
        new_data = input_form(df.columns)
        if st.button("Add Entry"):
            if all(value.strip() != "" for value in new_data.values()):
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                save_data(csv_file, df)
                st.success("✅ Entry added successfully!")
                st.rerun()
            else:
                st.warning("Please fill all fields before adding.")

    # Update
    st.markdown("### ✏ Update Entry")
    if not df.empty:
        selected_index = st.number_input("Row index to update", min_value=0, max_value=len(df)-1, step=1)
        updated_data = {}
        for col in df.columns:
            updated_data[col] = st.text_input(f"{col} (current: {df.loc[selected_index, col]})", key=f"upd_{col}")
        if st.button("Update Entry"):
            for col in df.columns:
                df.at[selected_index, col] = updated_data[col]
            save_data(csv_file, df)
            st.success("✅ Entry updated successfully!")
            st.rerun()

    # Delete
    st.markdown("### ❌ Delete Entry")
    if not df.empty:
        delete_index = st.number_input("Row index to delete", min_value=0, max_value=len(df)-1, step=1)
        if st.button("Delete Entry"):
            df = df.drop(delete_index).reset_index(drop=True)
            save_data(csv_file, df)
            st.success("✅ Entry deleted successfully!")
            st.rerun()

# Explore Page
elif choice == "SQL Queries":
    
    food_listings = pd.read_csv("food_listings_data.csv")
    claims = pd.read_csv("claims_data.csv")
    claims2 = pd.read_csv("claims_with_date_time (1).csv")
    receivers = pd.read_csv("receivers_data.csv")
    providers = pd.read_csv("providers_data.csv")
    
    # Setup SQLite in-memory DB
    conn = sqlite3.connect(":memory:")

# Push CSVs to SQLite tables
    food_listings.to_sql("food_listings", conn, index=False, if_exists='replace')
    claims.to_sql("claims", conn, index=False, if_exists='replace')
    claims2.to_sql("claims2", conn, index = False, if_exists = 'replace')
    receivers.to_sql("receivers", conn, index=False, if_exists='replace')
    providers.to_sql("providers", conn, index=False, if_exists='replace')

# Title
    st.title("Food Distribution Dashboard")

# Sidebar option menu
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

# Option 1: Food providers by city
    if option == "Food providers and recievers by city":
        st.subheader("City-wise Count of Providers and Receivers")

    # SQL queries
        query_providers = "SELECT count(Type) number_of_providers FROM providers group by City"
        query_receivers = "SELECT count(Type) number_of_receivers FROM receivers group by City"

    # Fetch data
        df_providers = pd.read_sql_query(query_providers, conn)
        df_receivers = pd.read_sql_query(query_receivers, conn)
        col1, spacer, col2 = st.columns([1, 0.2, 1])
        
        st.markdown("""
    <style>
        /* Metric cards */
        .metric-card {
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
        }
    </style>
""", unsafe_allow_html=True)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("City-wise Count of Providers", int(len(df_providers)))
            st.markdown('</div>', unsafe_allow_html=True)
        with spacer:
            st.write("")  # Acts as a spacer
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("City-wise Count of Receivers", int(len(df_receivers)))
            st.markdown('</div>', unsafe_allow_html=True)
        
    if option == "Maximum Contributor/Provider":
        # Fetch distinct provider types for filter
        provider_names = pd.read_sql_query("SELECT DISTINCT Type FROM providers", conn)
        selected_provider = st.selectbox("Filter by Provider Type", ["All"] + provider_names['Type'].dropna().tolist())

    # SQL query with optional filter
        if selected_provider != "All":
            query_max = f"""
        SELECT Type, COUNT(Type) AS provider_type
        FROM providers
        WHERE Type = '{selected_provider}'
        GROUP BY Type
        ORDER BY provider_type DESC
        """
        else:
            query_max = """
        SELECT Type, COUNT(Type) AS provider_type
        FROM providers
        GROUP BY Type
        ORDER BY provider_type DESC
        """

    # Fetch data
        df_max = pd.read_sql_query(query_max, conn)

    # Custom CSS
        st.markdown("""
        <style>
            .metric-card {
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                margin-bottom: 20px;
            }
            .metric-title {
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Metric Title
        if not df_max.empty:
            st.metric("Top Provider Type", df_max['Type'].iloc[0])
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No data available for the selected provider.")

    # Layout: DataFrame and Bar Chart Side-by-Side
        col1, col2 = st.columns([1, 1])

        with col1:
            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-title">Provider Type Counts</div>', unsafe_allow_html=True)
                st.dataframe(df_max, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            with st.container():
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown('<div class="metric-title">Provider Type Bar Chart</div>', unsafe_allow_html=True)
                if not df_max.empty:
                    st.bar_chart(df_max, x="Type", y="provider_type")
                else:
                    st.info("No data to show in chart.")
                st.markdown('</div>', unsafe_allow_html=True)
        
    if option == "Provider's contact information":
        st.subheader("Provider's contact information")
        
        # SQL queries
        query_contact = "SELECT City, Contact from providers group by City"
        
        # Fetch data
        df_contact = pd.read_sql_query(query_contact, conn)
        cities = st.multiselect("Select Cities", df_contact['City'].unique())
        filtered_df = df_contact[df_contact['City'].isin(cities)]
        st.dataframe(filtered_df)
    
    if option == "Recievers with most Food Claims":
        st.markdown("### 🔍 Filter Receivers by Type")
        type_options = pd.read_sql_query("SELECT DISTINCT Type FROM receivers", conn)['Type'].tolist()
        selected_types = st.multiselect("Select Receiver Types", type_options, default=type_options)

# --- SQL query with WHERE clause if filter applied ---
        if selected_types:
            placeholders = ','.join(['?'] * len(selected_types))
            query_reciever_max = f"SELECT Type, count(*) AS reciever_count FROM receivers WHERE Type IN ({placeholders}) GROUP BY Type"
            df_r_max = pd.read_sql_query(query_reciever_max, conn, params=selected_types)
        else:
            query_reciever_max = "SELECT Type, count(*) AS reciever_count FROM receivers GROUP BY Type"
            df_r_max = pd.read_sql_query(query_reciever_max, conn)

# --- Metric Section ---
        total_receivers = df_r_max['reciever_count'].sum()
        

# --- Layout with Chart and Table ---
        col1, spacer, col2 = st.columns([1, 0.2, 1])

        with col1:
            st.markdown("#### 📊 Receiver Type Counts")
            st.dataframe(df_r_max)

        with spacer:
            st.write("")  # Acts as spacer

        with col2:
            st.markdown("#### 📈 Bar Chart")
            st.bar_chart(df_r_max, x="Type", y="reciever_count")

    
    if option == "total food available from providers":
        st.markdown("### 🔍 Filter by Provider Type")
        provider_options = pd.read_sql_query("SELECT DISTINCT Provider_Type FROM food_listings", conn)['Provider_Type'].tolist()
        selected_providers = st.multiselect("Select Provider Types", provider_options, default=provider_options)

# --- SQL query with WHERE clause if filters are selected ---
        if selected_providers:
            placeholders = ','.join(['?'] * len(selected_providers))
            query_provider_max = f"""
        SELECT Provider_Type AS provider, SUM(Quantity) AS Quantity
        FROM food_listings
        WHERE Provider_Type IN ({placeholders})
        GROUP BY Provider_Type
    """
            df_r_max = pd.read_sql_query(query_provider_max, conn, params=selected_providers)
        else:
            query_provider_max = """
        SELECT Provider_Type AS provider, SUM(Quantity) AS Quantity
        FROM food_listings
        GROUP BY Provider_Type
    """
            df_r_max = pd.read_sql_query(query_provider_max, conn)

# --- Metric Display ---
        st.metric("Total Providers Quantity:", int(df_r_max['Quantity'].sum()))

# --- Layout: Table + Chart ---
        col1, spacer, col2 = st.columns([1, 0.2, 1])

        with col1:
            st.markdown("#### 🧾 Provider-wise Quantity")
            st.dataframe(df_r_max)

        with spacer:
            st.write("")

        with col2:
            st.markdown("#### 📊 Bar Chart")
            st.bar_chart(data=df_r_max, x="provider", y="Quantity")
        
        
    if option == "Highest Food Listings":
        st.subheader("Highest Food Listings")
          
        # SQL queries
        query_reciever_max = "SELECT Location, count(Food_Name) food_list FROM food_listings group by Location order by food_list desc"
        # Fetch data
        df_r_max = pd.read_sql_query(query_reciever_max, conn)
        st.metric("Total Providers Quantity:", df_r_max['Location'][0])
        st.dataframe(df_r_max)
        
    if option == "commonly available Food":
        
        st.markdown("### 🔍 Filter by Food Types")

# Get distinct food types
        food_type_options = pd.read_sql_query("SELECT DISTINCT Food_Type FROM food_listings", conn)['Food_Type'].dropna().tolist()

# Multiselect widget
        selected_food_types = st.multiselect("Select Food Types", food_type_options, default=food_type_options)

# SQL query with optional filtering
        if selected_food_types:
            placeholders = ','.join(['?'] * len(selected_food_types))
            query_food_types = f"""
        SELECT Food_Type, COUNT(Food_Type) AS avail_food_type
        FROM food_listings
        WHERE Food_Type IN ({placeholders})
        GROUP BY Food_Type
        ORDER BY avail_food_type DESC
    """
            df_food_types = pd.read_sql_query(query_food_types, conn, params=selected_food_types)
        else:
            query_food_types = """
        SELECT Food_Type, COUNT(Food_Type) AS avail_food_type
        FROM food_listings
        GROUP BY Food_Type
        ORDER BY avail_food_type DESC
    """
            df_food_types = pd.read_sql_query(query_food_types, conn)

# Display metrics
        if not df_food_types.empty:
            st.metric("Most Available Food Type", df_food_types["Food_Type"].iloc[0])
        else:
            st.warning("No food data available.")

# Display data
        st.dataframe(df_food_types)
        chart_type = st.radio("Choose Chart Type", ["Pie Chart", "Bar Chart"])
        if not df_food_types.empty:
            st.markdown("#### 📊 Food Type Distribution")

            if chart_type == "Pie Chart":
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.pie(df_food_types["avail_food_type"],
                labels=df_food_types["Food_Type"],
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 10})
                ax.axis("equal")
                st.pyplot(fig)

            elif chart_type == "Bar Chart":
            
                bar_fig = px.bar(df_food_types,
                         x="Food_Type",
                         y="avail_food_type",
                         color="Food_Type",
                         title="Available Food Types",
                         labels={"avail_food_type": "Count"})
                st.plotly_chart(bar_fig, use_container_width=True)
            else:
                st.warning("No data available for selected filters.")

        
    if option == "Total food claims per food item":
        st.subheader("🍽️ Total Food Claims Per Food Item")

# --- SQL Query ---
        query = """
SELECT t3.Food_Name, COUNT(t2.Claim_ID) AS no_food_claims
FROM food_listings t3
JOIN claims t2 ON t2.Food_ID = t3.Food_ID
GROUP BY t3.Food_Name
ORDER BY no_food_claims DESC
"""
        df_r_max = pd.read_sql_query(query, conn)

# --- Filters ---
        food_names = df_r_max['Food_Name'].unique().tolist()
        selected_foods = st.multiselect("🔍 Filter by Food Item", food_names, default=food_names)
        chart_type = st.radio("📊 Select Chart Type", ["Line Chart", "Bar Chart"], horizontal=True)

# --- Filtered Data ---
        filtered_df = df_r_max[df_r_max["Food_Name"].isin(selected_foods)]

# --- Show Table ---
        st.dataframe(filtered_df)
        
        if not filtered_df.empty:
            if chart_type == "Line Chart":
                fig = px.line(filtered_df, x='Food_Name', y='no_food_claims', markers=True,
                title="Total Claims Per Food Item")
            else:
                fig = px.bar(filtered_df, x='Food_Name', y='no_food_claims',
                title="Total Claims Per Food Item")

            fig.update_layout(xaxis_title="Food Name", yaxis_title="Number of Claims", xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data to display. Please select at least one food item.")


        
    if option == "provider with high number of succesful claims":
        st.subheader("Provider With High Number Of Successful Claims")

# SQL query
        query_reciever_max = """
    SELECT Provider_Type AS Provider, SUM(Quantity) AS total_food_provided 
    FROM food_listings 
    GROUP BY Provider_Type
"""
# Fetch data
        df_r_max = pd.read_sql_query(query_reciever_max, conn)
        st.dataframe(df_r_max)

# Filter: Provider Type
        provider_options = df_r_max['Provider'].unique().tolist()
        selected_providers = st.multiselect("📌 Filter by Provider Type", provider_options, default=provider_options)

# Filter the DataFrame
        filtered_df = df_r_max[df_r_max['Provider'].isin(selected_providers)]

# Plotly Bar Chart
        if not filtered_df.empty:
            fig = px.bar(
        filtered_df,
        x='Provider',
        y='total_food_provided',
        text='total_food_provided',
        title='Total Food Quantity Provided by Each Provider Type',
        labels={'total_food_provided': 'Total Food Quantity'},
        color='Provider'
    )
            fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data to display. Please select at least one provider type.")

        
    if option == "percentage of food claim status":
        st.subheader("Percentage Of Food Claim Status")

# SQL query
        query_reciever_max = """
    SELECT Status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS percentage 
    FROM claims 
    GROUP BY Status
"""
# Fetch data
        df_r_max = pd.read_sql_query(query_reciever_max, conn)
        st.dataframe(df_r_max)

# Optional: Status filter
        status_options = df_r_max['Status'].unique().tolist()
        selected_statuses = st.multiselect("🎯 Filter by Claim Status", status_options, default=status_options)

# Filter DataFrame
        filtered_df = df_r_max[df_r_max['Status'].isin(selected_statuses)]

# Plotly Pie Chart
        if not filtered_df.empty:
            fig = px.pie(
        filtered_df,
        values='percentage',
        names='Status',
        title='Food Claim Status Distribution (%)',
        hole=0.4
    )
            fig.update_traces(textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data to display. Please select at least one claim status.")
        
    if option == "average quantity of food claims per reciever":
        st.subheader("Average Quantity Of Food Claims Per Receiver")

# SQL query
        query_reciever_max = """
    SELECT t3.Food_Name, COUNT(t2.Claim_ID) AS no_food_claims 
    FROM food_listings t3 
    JOIN claims t2 ON t2.Food_ID = t3.Food_ID 
    GROUP BY t3.Food_Name 
    ORDER BY no_food_claims DESC
"""

# Fetch data
        df_r_max = pd.read_sql_query(query_reciever_max, conn)
        st.dataframe(df_r_max)

# Filter: Food selection
        food_options = df_r_max['Food_Name'].unique().tolist()
        selected_foods = st.multiselect("🍽️ Filter by Food Name", food_options, default=food_options)

# Filter the data based on selection
        filtered_df = df_r_max[df_r_max['Food_Name'].isin(selected_foods)]

# Plot with Plotly
        if not filtered_df.empty:
            fig = px.bar(
        filtered_df,
        x="Food_Name",
        y="no_food_claims",
        title="Average Quantity of Food Claims per Receiver",
        labels={"no_food_claims": "Number of Claims", "Food_Name": "Food"},
        color="no_food_claims",
        color_continuous_scale="viridis"
    )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data to display. Please select at least one food item.")
        
    if option == "most claimed meal type":
        st.subheader("Most Claimed Meal Type")

# SQL query
        query_meal_claims = """
    SELECT t3.Meal_Type, COUNT(t2.Status) AS no_of_claims 
    FROM food_listings t3 
    JOIN claims t2 ON t2.Food_ID = t3.Food_ID 
    WHERE t2.Status = 'Completed' 
    GROUP BY t3.Meal_Type 
    ORDER BY no_of_claims DESC
"""

# Fetch data
        df_meal_claims = pd.read_sql_query(query_meal_claims, conn)
        st.dataframe(df_meal_claims)

# Filter: Meal Type multiselect
        meal_type_options = df_meal_claims['Meal_Type'].unique().tolist()
        selected_meal_types = st.multiselect("🍴 Filter by Meal Type", meal_type_options, default=meal_type_options)

# Apply filter
        filtered_meal_df = df_meal_claims[df_meal_claims['Meal_Type'].isin(selected_meal_types)]

# Plot with Plotly
        if not filtered_meal_df.empty:
            fig = px.bar(
        filtered_meal_df,
        x="Meal_Type",
        y="no_of_claims",
        title="Most Claimed Meal Type (Completed Only)",
        labels={"no_of_claims": "Number of Claims", "Meal_Type": "Meal Type"},
        color="no_of_claims",
        color_continuous_scale="plasma"
    )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data to display. Please select at least one meal type.")
        
    if option == "food donated by each provider":
        st.subheader("🍲 Food Donated by Each Provider")

# SQL query
        query_provider_food = """
    SELECT Provider_Type AS Provider, SUM(Quantity) AS total_food_provided 
    FROM food_listings 
    GROUP BY Provider_Type
"""
# Fetch data
        df_provider = pd.read_sql_query(query_provider_food, conn)
        st.dataframe(df_provider)

# Filter: Provider multiselect
        provider_options = df_provider['Provider'].unique().tolist()
        selected_providers = st.multiselect("🏢 Filter by Provider Type", provider_options, default=provider_options)

# Apply filter
        filtered_df = df_provider[df_provider['Provider'].isin(selected_providers)]

# Plot with Plotly
        if not filtered_df.empty:
            fig = px.bar(
        filtered_df,
        x="Provider",
        y="total_food_provided",
        title="Total Food Donated by Provider Type",
        labels={"total_food_provided": "Total Food Donated", "Provider": "Provider Type"},
        color="total_food_provided",
        color_continuous_scale="viridis"
    )
            fig.update_layout(xaxis_tickangle=-25)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data to display. Please select at least one provider type.")
        
    if option == "fast expiring products":
        st.subheader("⏳ Fast Expiring Products")

# SQL query to get food and expiry dates
        query_expiring = """
    SELECT Food_Name, Expiry_Date 
    FROM food_listings 
    ORDER BY Expiry_Date ASC
"""
# Fetch data
        df_expiring = pd.read_sql_query(query_expiring, conn)

# Convert Expiry_Date to datetime if not already
        df_expiring["Expiry_Date"] = pd.to_datetime(df_expiring["Expiry_Date"])

# Sidebar or main filter UI
        food_options = df_expiring['Food_Name'].unique().tolist()
        selected_foods = st.multiselect("🍽️ Filter by Food Name", food_options, default=food_options)

# Date range filter
        min_date = df_expiring["Expiry_Date"].min()
        max_date = df_expiring["Expiry_Date"].max()
        selected_date_range = st.date_input("📅 Select Expiry Date Range", [min_date, max_date])

# Filter data
        filtered_df = df_expiring[
    (df_expiring['Food_Name'].isin(selected_foods)) &
    (df_expiring['Expiry_Date'] >= pd.to_datetime(selected_date_range[0])) &
    (df_expiring['Expiry_Date'] <= pd.to_datetime(selected_date_range[1]))
]

# Show filtered table
        st.dataframe(filtered_df)

# Plotly line plot
        if not filtered_df.empty:
            fig = px.line(
        filtered_df.sort_values("Expiry_Date"),
        x="Expiry_Date",
        y=filtered_df.groupby("Expiry_Date").cumcount()+1,
        color="Food_Name",
        title="Fast Expiring Products Timeline",
        labels={"y": "Product Count", "Expiry_Date": "Expiry Date"},
        markers=True
    )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No products found for the selected filters.")

        
    if option == "faster claim rate":
        import streamlit as st
        import pandas as pd
        import sqlite3
        import plotly.express as px

        st.subheader("📦 Faster Claim Rates (Top 5 Cities)")

# Load datasets
        foodlisting = pd.read_csv('food_listings_data.csv')
        claims = pd.read_csv('claims_data.csv')

# Convert date columns
        foodlisting['Expiry_Date'] = pd.to_datetime(foodlisting['Expiry_Date'], errors='coerce')
        claims['Timestamp'] = pd.to_datetime(claims['Timestamp'], errors='coerce')

# Drop invalid dates
        foodlisting.dropna(subset=['Expiry_Date'], inplace=True)
        claims.dropna(subset=['Timestamp'], inplace=True)

# Optional filters for interactivity
        status_filter = st.selectbox("Select Claim Status", options=claims['Status'].unique())
        city_filter = st.multiselect("Filter by City (Optional)", options=foodlisting['Location'].unique())

# Create in-memory SQLite DB
        conn = sqlite3.connect(":memory:")
        claims.to_sql('claims', conn, index=False, if_exists='replace')
        foodlisting.to_sql('foodlisting', conn, index=False, if_exists='replace')

# Build SQL with filters
        query = f"""
SELECT
    f.Location AS city,
    ROUND(MAX(AVG(julianday(c.Timestamp) - julianday(f.Expiry_Date)) * 100.0 / 30, 0), 2) AS avg_claim_time_percent
FROM
    foodlisting f
JOIN
    claims c ON f.Food_ID = c.Food_ID
WHERE
    c.Status = '{status_filter}'
    {"AND f.Location IN (" + ",".join([f"'{city}'" for city in city_filter]) + ")" if city_filter else ""}
GROUP BY
    city
ORDER BY
    avg_claim_time_percent DESC
LIMIT 5
"""

# Execute query
        df_fast_claims = pd.read_sql_query(query, conn)

# Display data
        st.dataframe(df_fast_claims)

# Plotly Chart
        if not df_fast_claims.empty:
            fig = px.bar(
        df_fast_claims,
        x="city",
        y="avg_claim_time_percent",
        labels={"city": "City", "avg_claim_time_percent": "Avg Claim Time (%)"},
        title="Top 5 Cities with Fastest Claim Completion",
        color="avg_claim_time_percent",
        color_continuous_scale="Blues"
    )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data found for the selected filters.")

        
elif choice == "Learner SQL queries":
    
    food_listings = pd.read_csv("food_listings_data.csv")
    claims = pd.read_csv("claims_data.csv")
    claims2 = pd.read_csv("claims_with_date_time (1).csv")
    receivers = pd.read_csv("receivers_data.csv")
    providers = pd.read_csv("providers_data.csv")
    
    # Setup SQLite in-memory DB
    conn = sqlite3.connect(":memory:")

# Push CSVs to SQLite tables
    food_listings.to_sql("food_listings", conn, index=False, if_exists='replace')
    claims.to_sql("claims", conn, index=False, if_exists='replace')
    claims2.to_sql("claims2", conn, index = False, if_exists = 'replace')
    receivers.to_sql("receivers", conn, index=False, if_exists='replace')
    providers.to_sql("providers", conn, index=False, if_exists='replace')

    # Title
    st.title("Food Distribution Dashboard")
    
    # Sidebar option menu
    option = st.sidebar.selectbox("Select a query to run:", (
    "Reciever share distribution of food",
    "share percent of food provided by each provider",
    "Succesful meal types",
    "most providing food provider",
    "vegan vs non veg vs veg for each meal type"
    ))
    
    if option == "Reciever share distribution of food":
        st.subheader("Receiver Share Distribution of Food")

# SQL query
        query_receiver_max = """
SELECT 
    Type AS receiver_type,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM receivers) AS percentage_share 
FROM receivers 
GROUP BY Type
"""

# Fetch data
        df_r_max = pd.read_sql_query(query_receiver_max, conn)
        st.dataframe(df_r_max)

# Chart type toggle
        chart_type = st.radio("Choose Chart Type", ["Pie Chart", "Bar Chart"], key="receiver_chart")

# Plot based on selection
        if chart_type == "Pie Chart":
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(df_r_max['percentage_share'],
            labels=df_r_max['receiver_type'],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10})
            ax.axis('equal')
            st.pyplot(fig)

        elif chart_type == "Bar Chart":
            import plotly.express as px
            fig_bar = px.bar(df_r_max,
                     x="receiver_type",
                     y="percentage_share",
                     color="receiver_type",
                     title="Receiver Type Share (%)",
                     labels={"receiver_type": "Receiver Type", "percentage_share": "Share (%)"})
            st.plotly_chart(fig_bar, use_container_width=True)

        
    elif option == "share percent of food provided by each provider":
        st.subheader("Share Percent of Food Provided by Each Provider")

# SQL query
        query_provider_max = """
SELECT 
    Type AS provider_type,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM providers) AS percentage_share 
FROM providers 
GROUP BY Type
"""

# Fetch data
        df_p_max = pd.read_sql_query(query_provider_max, conn)
        st.dataframe(df_p_max)

# Chart type toggle
        chart_type = st.radio("Choose Chart Type", ["Pie Chart", "Bar Chart"], key="provider_chart")

# Plot based on selection
        if chart_type == "Pie Chart":
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(df_p_max['percentage_share'],
            labels=df_p_max['provider_type'],
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10})
            ax.axis('equal')
            st.pyplot(fig)

        elif chart_type == "Bar Chart":
            import plotly.express as px
            fig_bar = px.bar(df_p_max,
                     x="provider_type",
                     y="percentage_share",
                     color="provider_type",
                     title="Provider Type Share (%)",
                     labels={"provider_type": "Provider Type", "percentage_share": "Share (%)"})
            st.plotly_chart(fig_bar, use_container_width=True)

    
    elif option == "Succesful meal types":
        st.subheader("Successful Meal Types")

# SQL Query
        query_meal_success = """
SELECT 
    f.Meal_Type, 
    CAST(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) AS REAL) * 100 / 
    (SELECT COUNT(*) FROM claims WHERE Status = 'Completed') AS success_percentage 
FROM claims c 
JOIN food_listings f ON c.Food_ID = f.Food_ID 
GROUP BY f.Meal_Type 
ORDER BY success_percentage DESC;
"""

# Fetch Data
        df_meal_success = pd.read_sql_query(query_meal_success, conn)
        st.dataframe(df_meal_success)

# Chart type toggle
        chart_type = st.radio("Choose Chart Type", ["Bar Chart", "Pie Chart"], key="meal_chart")

# Plotting
        if chart_type == "Bar Chart":
            import plotly.express as px
            fig_bar = px.bar(df_meal_success,
                     x="Meal_Type",
                     y="success_percentage",
                     text="success_percentage",
                     color="Meal_Type",
                     title="Success Rate of Meal Types (%)",
                     labels={"Meal_Type": "Meal Type", "success_percentage": "Success %"})
            fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_bar.update_layout(yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig_bar, use_container_width=True)

        elif chart_type == "Pie Chart":
            fig_pie, ax = plt.subplots(figsize=(8, 6))
            ax.pie(df_meal_success['success_percentage'],
           labels=df_meal_success['Meal_Type'],
           autopct='%1.1f%%',
           startangle=90,
           textprops={'fontsize': 10})
            ax.axis('equal')
            st.pyplot(fig_pie)

        
    elif option == "most providing food provider":
        st.subheader("Successful Provider Types")

# SQL Query
        query_provider_success = """
SELECT 
    f.Provider_Type, 
    ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate 
FROM food_listings f 
JOIN claims c ON f.Food_ID = c.Food_ID 
GROUP BY f.Provider_Type 
ORDER BY success_rate DESC;
"""

# Fetch Data
        df_provider_success = pd.read_sql_query(query_provider_success, conn)
        st.dataframe(df_provider_success)

# Chart type toggle
        chart_type = st.radio("Choose Chart Type", ["Pie Chart", "Bar Chart"], key="provider_chart")

# Plotting based on selection
        if chart_type == "Pie Chart":
            fig_pie, ax = plt.subplots(figsize=(8, 6))
            ax.pie(df_provider_success['success_rate'],
           labels=df_provider_success['Provider_Type'],
           autopct='%1.1f%%',
           startangle=90,
           textprops={'fontsize': 10})
            ax.axis('equal')
            st.pyplot(fig_pie)

        else:  # Bar Chart
            import plotly.express as px
            fig_bar = px.bar(df_provider_success,
                     x="Provider_Type",
                     y="success_rate",
                     text="success_rate",
                     color="Provider_Type",
                     title="Success Rate by Provider Type (%)",
                     labels={"Provider_Type": "Provider Type", "success_rate": "Success %"})
            fig_bar.update_traces(texttemplate='%{text}%', textposition='outside')
            fig_bar.update_layout(yaxis=dict(range=[0, 100]))
            st.plotly_chart(fig_bar, use_container_width=True)

        
    elif option == "vegan vs non veg vs veg for each meal type":
        st.subheader("Vegan vs Non Veg vs Veg For Each Meal Type")

# Queries
        query = "SELECT Meal_Type, COUNT(Food_Type) as count_vegan FROM food_listings WHERE Food_type = 'Vegan' GROUP BY Meal_Type"
        query1 = "SELECT Meal_Type, COUNT(Food_Type) as count_vegetarian FROM food_listings WHERE Food_type = 'Vegetarian' GROUP BY Meal_Type"
        query2 = "SELECT Meal_Type, COUNT(Food_Type) as count_non_veg FROM food_listings WHERE Food_type = 'Non-Vegetarian' GROUP BY Meal_Type"

# Fetch data
        df_vegan = pd.read_sql_query(query, conn)
        df_vegetarian = pd.read_sql_query(query1, conn)
        df_non_veg = pd.read_sql_query(query2, conn)

# Merge all into one DataFrame
        df = pd.merge(pd.merge(df_vegan, df_vegetarian, on='Meal_Type', how='outer'), df_non_veg, on='Meal_Type', how='outer').fillna(0)

# Show DataFrame
        st.dataframe(df)

# Select chart type
        chart_type = st.radio("Select Chart Type", ["Stacked Bar", "Pie (per Meal Type)"])

        if chart_type == "Stacked Bar":
            fig, ax = plt.subplots(figsize=(10, 6))
            plt.bar(df['Meal_Type'], df['count_vegan'], label='Vegan')
            plt.bar(df['Meal_Type'], df['count_vegetarian'], bottom=df['count_vegan'], label='Vegetarian')
            plt.bar(df['Meal_Type'], df['count_non_veg'], bottom=df['count_vegan'] + df['count_vegetarian'], label='Non-Vegetarian')

            plt.xlabel('Meal Type')
            plt.ylabel('Count')
            plt.title('Meal Preferences by Type (Stacked)')
            plt.legend()
            plt.tight_layout()
            st.pyplot(fig)

        else:
    # Pie chart for each meal type
            for index, row in df.iterrows():
                meal = row['Meal_Type']
                values = [row['count_vegan'], row['count_vegetarian'], row['count_non_veg']]
                labels = ['Vegan', 'Vegetarian', 'Non-Vegetarian']
        
                fig, ax = plt.subplots()
                ax.pie(values, labels=labels, autopct='%1.1f%%')
                ax.set_title(f"{meal} Meal Type Distribution")
                st.pyplot(fig)
# Contact Page
elif choice == "User Introduction":
    st.title("About the Creator")
    st.write('Arvind S')
    st.write('phone: 9685696856')
    st.write("Email us at: support@foodshare.org")
st.markdown("</div>", unsafe_allow_html=True)