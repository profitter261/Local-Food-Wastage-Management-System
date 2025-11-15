import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine

# ---------- DATABASE CONNECTION ----------
engine = create_engine("mysql+pymysql://root:Arvind%402003@localhost/food_wastage_management")

@st.cache_data
def run_query(query):
    return pd.read_sql_query(query, con=engine)

# ---------- STREAMLIT PAGE CONFIG ----------
st.set_page_config(page_title="Food Wastage Dashboard", layout="wide")
st.title("🥗 Food Wastage Management Dashboard")

# ---------- SIDEBAR NAVIGATION ----------
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=[
            "Providers & Receivers, food listing",
            "Claims",
            "Overall",
        ],
        icons=["building", "box", "bar-chart"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
    )

# ===============================================================
# TAB 1: PROVIDERS, RECEIVERS & FOOD LISTINGS
# ===============================================================
if selected == "Providers & Receivers, food listing":
    
    with st.container(border = True):
        col1, col2, col3, col4, col5 = st.columns(5, gap='large')

        # Queries
        result1 = run_query("SELECT COUNT(Type) AS number_of_providers FROM providers;")
        result2 = run_query("SELECT COUNT(Type) AS number_of_receivers FROM receivers;")
        result3 = run_query("SELECT Provider_Type, SUM(Quantity) AS Total_Quantity FROM food_listings GROUP BY Provider_Type;")
        result4 = run_query("SELECT Type, COUNT(Type) AS number_of_recievers FROM receivers GROUP BY Type;")
        result5 = run_query("SELECT food_name, COUNT(food_name) AS avail_food_count FROM food_listings GROUP BY food_name ORDER BY avail_food_count DESC;")
        result6 = run_query("SELECT Location AS City, COUNT(Food_Name) AS food_list FROM food_listings GROUP BY Location ORDER BY food_list DESC;")

        # Metrics
        col1.metric("Number of Providers", int(result1['number_of_providers'][0]))
        col2.metric("Number of Receivers", int(result2['number_of_receivers'][0]))
        col3.metric("Top Provider Type", result3['Provider_Type'][0])
        col4.metric("Top Receiver Type", result4['Type'][0])
        col5.metric("Most Available Food", result5['food_name'][0])

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Provider Food Distribution",
        "Most Available Items",
        "Receivers by Type",
        "Food Listings per City",
        "Food Availability"
    ])

    with tab1:
        provider_filter = st.multiselect("Filter Provider Types:", result3['Provider_Type'].unique(), default=result3['Provider_Type'].unique())
        filtered = result3[result3['Provider_Type'].isin(provider_filter)]
        fig = px.bar(filtered, x="Provider_Type", y="Total_Quantity", text_auto=True, color="Total_Quantity", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        top_n = st.slider("Select Top N Food Items", 5, 30, 10)
        filtered = result5.head(top_n)
        fig = px.pie(filtered, names="food_name", values="avail_food_count", hole=0.3)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        

        # Debug: show columns if needed
        # st.write("Columns in result4:", result4.columns.tolist())

        # Dynamically detect the count column (anything that isn’t 'Type')
        count_col = [c for c in result4.columns if c.lower() != "type"][0]

        # --- Filter UI ---
        selected_types = st.multiselect(
            "Select Receiver Types",
            options=result4["Type"].unique(),
            default=list(result4["Type"].unique()),
            key="receiver_type_filter"
        )

        sort_order = st.radio(
            "Sort by count order",
            ["Descending", "Ascending"],
            horizontal=True,
            index=0,
            key="receiver_sort_order"
        )

        # --- Filter + Sort the data ---
        filtered = result4[result4["Type"].isin(selected_types)].copy()
        filtered[count_col] = pd.to_numeric(filtered[count_col], errors="coerce").fillna(0)

        ascending = sort_order == "Ascending"
        filtered_sorted = filtered.sort_values(by=count_col, ascending=ascending)

        # --- Plotly Bar Chart ---
        order = filtered_sorted["Type"].tolist()
        fig = px.bar(
            filtered_sorted,
            x="Type",
            y=count_col,
            text=count_col,
            category_orders={"Type": order},
            color=count_col,
            color_continuous_scale="Viridis",
            title="Receivers by Type"
        )

        fig.update_traces(texttemplate="%{text}", textposition="outside")
        fig.update_layout(
            xaxis_tickangle=45,
            plot_bgcolor="white",
            title_x=0.4,
            margin=dict(t=40, b=120)
        )

        st.plotly_chart(fig, use_container_width=True, key="recv_plotly")




    with tab4:
        city_filter = st.multiselect("Select Cities:", result6['City'].unique(), default=result6['City'].unique()[:10])
        filtered = result6[result6['City'].isin(city_filter)]
        fig = px.bar(filtered, x="City", y="food_list", text_auto=True, color="food_list", color_continuous_scale="Viridis")
        st.plotly_chart(fig, use_container_width=True)

    with tab5:
        food_filter = st.multiselect("Filter Foods:", result5['food_name'].unique(), default=result5['food_name'].unique()[:15])
        filtered = result5[result5['food_name'].isin(food_filter)]
        st.bar_chart(data=filtered, x="food_name", y="avail_food_count")


# ===============================================================
# TAB 2: CLAIMS
# ===============================================================
elif selected == "Claims":
    

    # Queries
    result7 = run_query("""
        SELECT f.Food_Name, COUNT(c.Claim_ID) AS no_food_claims
        FROM food_listings f
        JOIN claims c ON c.Food_ID = f.Food_ID
        GROUP BY f.Food_Name
        ORDER BY no_food_claims DESC
    """)
    result8 = run_query("""
        SELECT f.Provider_Type AS Provider, ROUND(AVG(IF(c.Status = 'Completed', 1, 0)), 2) AS average_completed_claims
        FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID
        GROUP BY f.Provider_Type ORDER BY average_completed_claims DESC
    """)
    result9 = run_query("SELECT Status, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS percentage FROM claims GROUP BY Status")
    result10 = run_query("SELECT 100.0 * COUNT((CASE WHEN Status = 'Completed' THEN 1 END)) / COUNT(*) AS avg_food_claimed_per_reciever FROM claims")
    result11 = run_query("""
        SELECT f.Meal_Type, COUNT(c.Status) AS no_of_claims
        FROM food_listings f JOIN claims c ON f.Food_ID = c.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY f.Meal_Type ORDER BY no_of_claims DESC
    """)
    result12 = run_query("SELECT Provider_Type AS Provider, SUM(Quantity) AS total_food_provided FROM food_listings GROUP BY Provider_Type ORDER BY total_food_provided DESC")
    result13 = run_query("""
        SELECT Food_Name, MIN(STR_TO_DATE(Expiry_Date, '%%m/%%d/%%Y')) AS Earliest_Expiry
        FROM food_listings
        WHERE Expiry_Date IS NOT NULL AND Expiry_Date <> ''
        GROUP BY Food_Name ORDER BY Earliest_Expiry ASC
    """)

    with st.container(border = True):
        # KPI Metrics
        col1, col2, col3, col4, col5 = st.columns(5, gap='large')


        with col1:
                st.metric("Top Claimed Food", result7['Food_Name'][0])
        with col2:
                st.metric("Top Provider Type", result8['Provider'][0])
        with col3:
                st.metric("Most Common Status", result9['Status'][2])
        with col4:
                st.metric("Avg Food Claimed per Receiver", round(result10['avg_food_claimed_per_reciever'][0], 2))
        with col5:
                st.metric("Top Meal Type", result11['Meal_Type'][0])

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Claim Status & Quantity Provided",
        "Provider Performance",
        "Top Claimed Foods",
        "Meal Type Claims",
        "Earliest Expiring Items"
    ])

    # ---------------------- TAB 1 ----------------------
    with tab1:
        col1, col2 = st.columns(2, gap="large")

        with col1:
            
            status_filter = st.multiselect(
                "Filter by Claim Status",
                result9["Status"].unique(),
                default=result9["Status"].unique(),
                key="status_filter"
            )
            filtered_status = result9[result9["Status"].isin(status_filter)]

            fig = px.pie(
                filtered_status,
                names="Status",
                values="percentage",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_traces(textinfo="percent+label", textposition="inside")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            
            provider_filter = st.multiselect(
                "Filter Providers:",
                result12['Provider'].unique(),
                default=result12['Provider'].unique(),
                key="provider_pie_filter"
            )
            filtered = result12[result12['Provider'].isin(provider_filter)]
            fig3 = px.pie(
                filtered,
                names="Provider",
                values="total_food_provided",
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Plasma_r
            )
            fig3.update_traces(textinfo="percent+label", textposition="inside")
            st.plotly_chart(fig3, use_container_width=True)

    # ---------------------- TAB 2 ----------------------
    with tab2:
        
        provider_filter = st.multiselect(
            "Filter Provider Types",
            result8["Provider"].unique(),
            default=result8["Provider"].unique(),
            key="provider_perf_filter"
        )
        sort_order = st.radio("Sort Order", ["Descending", "Ascending"], horizontal=True, key="provider_perf_sort")
        ascending = sort_order == "Ascending"
        filtered = result8[result8["Provider"].isin(provider_filter)].sort_values(by="average_completed_claims", ascending=ascending)

        fig = px.bar(
            filtered,
            x="Provider",
            y="average_completed_claims",
            text="average_completed_claims",
            color="average_completed_claims",
            color_continuous_scale="Viridis",
            title="Average Completed Claims by Provider Type"
        )
        fig.update_traces(texttemplate="%{text}", textposition="outside")
        fig.update_layout(plot_bgcolor="white", title_x=0.4)
        st.plotly_chart(fig, use_container_width=True)

    # ---------------------- TAB 3 ----------------------
    with tab3:
        
        top_n = st.slider("Select Top N Foods", 5, 30, 10)
        sort_order = st.radio("Sort Order", ["Descending", "Ascending"], horizontal=True, key="food_sort")
        ascending = sort_order == "Ascending"
        filtered = result7.head(top_n).sort_values(by="no_food_claims", ascending=ascending)

        fig = px.bar(
            filtered,
            x="Food_Name",
            y="no_food_claims",
            text="no_food_claims",
            color="no_food_claims",
            color_continuous_scale="Plasma",
            title=f"Top {top_n} Claimed Foods"
        )
        fig.update_traces(texttemplate="%{text}", textposition="outside")
        fig.update_layout(xaxis_tickangle=45, plot_bgcolor="white", title_x=0.4)
        st.plotly_chart(fig, use_container_width=True)

    # ---------------------- TAB 4 ----------------------
    with tab4:
        
        meal_filter = st.multiselect(
            "Filter Meal Types",
            result11["Meal_Type"].unique(),
            default=result11["Meal_Type"].unique(),
            key="meal_filter"
        )
        filtered = result11[result11["Meal_Type"].isin(meal_filter)]

        fig1 = px.bar(
            filtered,
            x="Meal_Type",
            y="no_of_claims",
            text="no_of_claims",
            color="no_of_claims",
            color_continuous_scale="Greens",
            title="Completed Claims by Meal Type"
        )
        fig1.update_traces(texttemplate="%{text}", textposition="outside")
        fig1.update_layout(xaxis_tickangle=45, plot_bgcolor="white", title_x=0.4)
        st.plotly_chart(fig1, use_container_width=True)

    # ---------------------- TAB 5 ----------------------
    with tab5:
        

        result13["Earliest_Expiry"] = pd.to_datetime(result13["Earliest_Expiry"], errors="coerce")
        result13 = result13.dropna(subset=["Earliest_Expiry"])

        if not result13.empty:
            min_date = result13["Earliest_Expiry"].min().date()
            max_date = result13["Earliest_Expiry"].max().date()

            if min_date == max_date:
                st.info(f"All items have the same expiry date: **{min_date}**")
                filtered = result13.head(15)
            else:
                date_min, date_max = st.slider(
                    "Select Expiry Date Range",
                    min_value=min_date,
                    max_value=max_date,
                    value=(min_date, max_date)
                )

                filtered = result13[
                    (result13["Earliest_Expiry"].dt.date >= date_min)
                    & (result13["Earliest_Expiry"].dt.date <= date_max)
                ].head(15)

            fig2 = px.bar(
                filtered,
                x="Food_Name",
                y="Earliest_Expiry",
                text=filtered["Earliest_Expiry"].dt.strftime("%Y-%m-%d"),
                color="Earliest_Expiry",
                color_continuous_scale="Reds",
                title="Earliest Expiring Food Items"
            )
            fig2.update_traces(textposition="outside")
            fig2.update_layout(xaxis_tickangle=45, plot_bgcolor="white", title_x=0.4)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No valid expiry dates found in the dataset.")



# ===============================================================
# TAB 3: OVERALL INSIGHTS
# ===============================================================
elif selected == "Overall":
    

    # -----------------------------
    # 1️⃣ Receiver Type Percentage
    # -----------------------------
    query = """
    SELECT 
        Type AS receiver_type,
        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM receivers) AS percentage_share 
    FROM receivers 
    GROUP BY Type;
    """
    result17 = pd.read_sql_query(query, con=engine)

    # -----------------------------
    # 2️⃣ Provider Type Percentage
    # -----------------------------
    query = """
    SELECT 
        Type AS provider_type,
        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM providers) AS percentage_share 
    FROM providers 
    GROUP BY Type;
    """
    result18 = pd.read_sql_query(query, con=engine)

    # -----------------------------
    # 3️⃣ Meal Type Success Percentage
    # -----------------------------
    query = """
    SELECT
        f.Meal_Type,
        CAST(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) AS REAL) * 100 / 
        (SELECT COUNT(*) FROM claims c WHERE Status = 'Completed') AS success_percentage
    FROM claims c
    JOIN food_listings f ON c.Food_ID = f.Food_ID
    GROUP BY f.Meal_Type
    ORDER BY success_percentage DESC;
    """
    result19 = pd.read_sql_query(query, con=engine)

    # -----------------------------
    # 4️⃣ Provider Success Rate
    # -----------------------------
    query = """
    SELECT
        f.Provider_Type,
        ROUND(SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS success_rate
    FROM food_listings f
    JOIN claims c ON f.Food_ID = c.Food_ID
    GROUP BY f.Provider_Type
    ORDER BY success_rate DESC;
    """
    result20 = pd.read_sql_query(query, con=engine)

    # -----------------------------
    # 5️⃣ Food Type Distribution by Meal Type
    # -----------------------------
    query = "SELECT Meal_Type, COUNT(Food_Type) AS count_vegan FROM food_listings WHERE Food_Type = 'Vegan' GROUP BY Meal_Type"
    query1 = "SELECT Meal_Type, COUNT(Food_Type) AS count_vegetarian FROM food_listings WHERE Food_Type = 'Vegetarian' GROUP BY Meal_Type"
    query2 = "SELECT Meal_Type, COUNT(Food_Type) AS count_non_veg FROM food_listings WHERE Food_Type = 'Non-Vegetarian' GROUP BY Meal_Type"

    df = pd.merge(
        pd.merge(pd.read_sql_query(query, con=engine), pd.read_sql_query(query1, con=engine), on='Meal_Type', how='outer'),
        pd.read_sql_query(query2, con=engine), on='Meal_Type', how='outer'
    ).fillna(0)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Receiver vs Provider Types",
        "Meal Type Success %",
        "Provider Success Rate",
        "Food Type Distribution"
    ])

    # ---- Tab 1 ----
    with tab1:
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.subheader("🎯 Receiver Type Distribution")
            receiver_filter = st.multiselect(
                "Select Receiver Types:",
                options=result17["receiver_type"].unique(),
                default=result17["receiver_type"].unique(),
                key="receiver_filter_overall"
            )
            filtered_receivers = result17[result17["receiver_type"].isin(receiver_filter)]
            fig1 = px.pie(filtered_receivers, names="receiver_type", values="percentage_share",
                          title="Receivers by Type (%)", hole=0.4,
                          color_discrete_sequence=px.colors.sequential.RdBu)
            fig1.update_traces(textinfo="percent+label", textposition="inside")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("🏢 Provider Type Distribution")
            provider_filter = st.multiselect(
                "Select Provider Types:",
                options=result18["provider_type"].unique(),
                default=result18["provider_type"].unique(),
                key="provider_filter_overall"
            )
            filtered_providers = result18[result18["provider_type"].isin(provider_filter)]
            fig2 = px.pie(filtered_providers, names="provider_type", values="percentage_share",
                          title="Providers by Type (%)", hole=0.4,
                          color_discrete_sequence=px.colors.sequential.Blues_r)
            fig2.update_traces(textinfo="percent+label", textposition="inside")
            st.plotly_chart(fig2, use_container_width=True)

    # ---- Tab 2 ----
    with tab2:
        st.subheader("🍽️ Success Rate by Meal Type")
        meal_filter = st.multiselect(
            "Select Meal Types:",
            options=result19["Meal_Type"].unique(),
            default=result19["Meal_Type"].unique(),
            key="meal_filter_overall"
        )
        filtered_meals = result19[result19["Meal_Type"].isin(meal_filter)]
        fig3 = px.bar(filtered_meals, x="Meal_Type", y="success_percentage",
                      color="success_percentage", text_auto=True,
                      color_continuous_scale="Greens",
                      title="Meal Type Claim Success (%)")
        fig3.update_layout(xaxis_tickangle=45, plot_bgcolor="white", title_x=0.4)
        st.plotly_chart(fig3, use_container_width=True)

    # ---- Tab 3 ----
    with tab3:
        st.subheader("🏢 Provider Claim Success Rate")
        prov_filter = st.multiselect(
            "Select Provider Types:",
            options=result20["Provider_Type"].unique(),
            default=result20["Provider_Type"].unique(),
            key="prov_filter_overall"
        )
        filtered_prov = result20[result20["Provider_Type"].isin(prov_filter)]
        fig4 = px.bar(filtered_prov, x="Provider_Type", y="success_rate",
                      color="success_rate", text_auto=True,
                      color_continuous_scale="Viridis",
                      title="Provider Claim Success Rate (%)")
        fig4.update_layout(xaxis_tickangle=45, plot_bgcolor="white", title_x=0.4)
        st.plotly_chart(fig4, use_container_width=True)

    # ---- Tab 4 ----
    with tab4:
        st.subheader("🥗 Vegan / Vegetarian / Non-Veg Distribution by Meal Type")
        df_melt = df.melt(id_vars="Meal_Type", var_name="Food_Type", value_name="Count")

        meal_filter2 = st.multiselect(
            "Select Meal Types:",
            options=df_melt["Meal_Type"].unique(),
            default=df_melt["Meal_Type"].unique(),
            key="meal_filter2_overall"
        )
        foodtype_filter = st.multiselect(
            "Select Food Types:",
            options=df_melt["Food_Type"].unique(),
            default=df_melt["Food_Type"].unique(),
            key="foodtype_filter_overall"
        )

        filtered_df = df_melt[
            df_melt["Meal_Type"].isin(meal_filter2) & df_melt["Food_Type"].isin(foodtype_filter)
        ]

        fig5 = px.bar(filtered_df, x="Meal_Type", y="Count", color="Food_Type",
                      barmode="group", text_auto=True,
                      title="Food Type Breakdown by Meal Type")
        fig5.update_layout(xaxis_tickangle=45, plot_bgcolor="white", title_x=0.4)
        st.plotly_chart(fig5, use_container_width=True)
