# Run this script using Streamlit
# pip install -r requirements.txt
# pip install -r /Users/rijpat/Downloads/requirements.txt 
# streamlit run app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np # For correlation matrix

# Call set_page_config as the first Streamlit command
st.set_page_config(layout="wide")

# Define the color palette
genre_colors = {
    "Action": "#4E79A7",  # Blue
    "Adventure": "#A0CBE8",  # Light Blue
    "Fighting": "#F28E2B",  # Orange
    "Misc": "#FFBE7D",  # Light Orange
    "Platform": "#59A14F",  # Green
    "Puzzle": "#8CD17D",  # Light Green
    "Racing": "#B6992D",  # Gold/Dark Yellow
    "Role-Playing": "#86BCB6", # Light Teal/Greenish
    "Shooter": "#499894",  # Teal/Blue-Green
    "Simulation": "#E15759", # Red
    "Sports": "#D37295",  # Pinkish Red / Magenta
    "Strategy": "#FABFD2"  # Light Pink
}

# Load the dataset
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_vgsales.csv")
    df["Year"] = pd.to_numeric(df["Year"], errors='coerce')
    df.dropna(subset=["Year"], inplace=True)
    df["Year"] = df["Year"].astype(int)
    # Fill NaN in Publisher with 'Unknown' for smoother processing in charts
    df["Publisher"].fillna("Unknown Publisher", inplace=True)
    return df

df = load_data()

st.title("Video Game Sales Dashboard")

# Display basic information about the dataset in an expander
with st.expander("Dataset Overview"):
    st.dataframe(df.head())
    st.write(f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns after preprocessing.")
    st.subheader("Missing Values Check (after handling Year and Publisher)")
    missing_values = df.isnull().sum()
    missing_values = missing_values[missing_values > 0]
    if not missing_values.empty:
        st.write(missing_values)
    else:
        st.write("No critical missing values found in the dataset that require further attention for these charts.")
    st.subheader("Data Types")
    st.write(df.dtypes.astype(str))

# --- Tabs for different chart groups ---
st.sidebar.title("Navigation")
tab_selection = st.sidebar.radio("Select Dashboard Section", ["Global Sales Insights", "Regional Performance Analysis", "Platform and Genre Deep Dive"])

if tab_selection == "Global Sales Insights":
    st.header("Global Sales Insights")

    # 1. Global Sales by Genre (Bar Chart)
    st.subheader("1. Global Sales by Genre")
    genre_sales_global = df.groupby("Genre")["Global_Sales"].sum().reset_index().sort_values(by="Global_Sales", ascending=False)
    fig_genre_sales = px.bar(genre_sales_global, x="Genre", y="Global_Sales", title="Global Sales by Genre",
                             color="Genre", color_discrete_map=genre_colors,
                             labels={"Global_Sales": "Total Global Sales (Millions)"})
    fig_genre_sales.update_layout(xaxis_title="Genre", yaxis_title="Total Global Sales (Millions)")
    st.plotly_chart(fig_genre_sales, use_container_width=True)

    # 2. Sales Trend Over Time (Line Chart)
    st.subheader("2. Sales Trend Over Time (Global)")
    yearly_sales = df.groupby("Year")["Global_Sales"].sum().reset_index()
    fig_yearly_sales = px.line(yearly_sales, x="Year", y="Global_Sales", title="Total Global Video Game Sales Over Time",
                               markers=True, labels={"Global_Sales": "Total Global Sales (Millions)"})
    fig_yearly_sales.update_layout(xaxis_title="Year", yaxis_title="Total Global Sales (Millions)")
    st.plotly_chart(fig_yearly_sales, use_container_width=True)

    # 3. Top 10 Best-Selling Games (Horizontal Bar Chart)
    st.subheader("3. Top 10 Best-Selling Games Globally")
    top_10_games = df.nlargest(10, "Global_Sales")
    fig_top_games = px.bar(top_10_games, y="Name", x="Global_Sales", orientation='h',
                           title="Top 10 Best-Selling Games Globally",
                           color="Genre", color_discrete_map=genre_colors,
                           labels={"Global_Sales": "Total Global Sales (Millions)", "Name": "Game Title"})
    fig_top_games.update_layout(yaxis_title="Game Title", xaxis_title="Total Global Sales (Millions)", yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top_games, use_container_width=True)

    # 4. Sales Distribution by Publisher (Bar Chart or Treemap)
    st.subheader("4. Sales Distribution by Publisher (Top 20)")
    publisher_sales = df.groupby("Publisher")["Global_Sales"].sum().reset_index().sort_values(by="Global_Sales", ascending=False)
    top_publishers = publisher_sales.head(20) # Limiting to top 20 for better visualization

    chart_type_publisher = st.selectbox("Select Chart Type for Publisher Sales:", ["Bar Chart", "Treemap"], key="publisher_chart_type")

    if chart_type_publisher == "Bar Chart":
        fig_publisher_sales = px.bar(top_publishers, x="Publisher", y="Global_Sales", title="Top 20 Publishers by Global Sales",
                                     color="Publisher",
                                     labels={"Global_Sales": "Total Global Sales (Millions)"})
        fig_publisher_sales.update_layout(xaxis_title="Publisher", yaxis_title="Total Global Sales (Millions)", xaxis_tickangle=-45)
        st.plotly_chart(fig_publisher_sales, use_container_width=True)
    elif chart_type_publisher == "Treemap":
        fig_publisher_treemap = px.treemap(top_publishers, path=[px.Constant("All Publishers"), "Publisher"], values="Global_Sales",
                                           title="Top 20 Publishers by Global Sales (Treemap)",
                                           color="Publisher",
                                           hover_data={"Global_Sales":':.2f'})
        fig_publisher_treemap.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig_publisher_treemap, use_container_width=True)

elif tab_selection == "Regional Performance Analysis":
    st.header("Regional Performance Analysis")

    # 5. Regional Sales Comparison by Genre (Grouped or Stacked Bar Chart)
    st.subheader("5. Regional Sales Comparison by Genre")
    regional_genre_sales = df.groupby("Genre")[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]].sum().reset_index()
    regional_genre_sales_melted = regional_genre_sales.melt(id_vars="Genre", 
                                                            value_vars=["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"], 
                                                            var_name="Region", value_name="Sales")
    
    regional_chart_type = st.selectbox("Select Chart Type for Regional Genre Sales:", ["Grouped Bar", "Stacked Bar"], key="regional_genre_chart_type")
    barmode = "group" if regional_chart_type == "Grouped Bar" else "stack"

    fig_regional_genre = px.bar(regional_genre_sales_melted, x="Genre", y="Sales", color="Region",
                                title=f"Regional Sales Comparison by Genre ({regional_chart_type})",
                                barmode=barmode,
                                color_discrete_map={"NA_Sales": "#1f77b4", "EU_Sales": "#ff7f0e", "JP_Sales": "#2ca02c", "Other_Sales": "#d62728"},
                                labels={"Sales": "Sales (Millions)"})
    fig_regional_genre.update_layout(xaxis_title="Genre", yaxis_title="Sales (Millions)")
    st.plotly_chart(fig_regional_genre, use_container_width=True)

    # 6. Regional Sales Share by Game (Pie Chart or Donut Chart)
    st.subheader("6. Regional Sales Share by Game")
    game_list = sorted(df["Name"].unique())
    default_game_name = "Wii Sports" if "Wii Sports" in game_list else game_list[0] if game_list else None
    default_game_index = game_list.index(default_game_name) if default_game_name else 0

    selected_game = st.selectbox("Select a Game:", game_list, index=default_game_index, key="regional_game_select")

    if selected_game:
        game_data = df[df["Name"] == selected_game][["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]].sum()
        game_data = game_data[game_data > 0] # Only show regions with sales

        if not game_data.empty:
            fig_game_regional_share = px.pie(values=game_data.values, names=game_data.index, 
                                             title=f"Regional Sales Share for {selected_game}",
                                             hole=0.3, # For Donut chart
                                             color_discrete_map={"NA_Sales": "#1f77b4", "EU_Sales": "#ff7f0e", "JP_Sales": "#2ca02c", "Other_Sales": "#d62728"})
            fig_game_regional_share.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_game_regional_share, use_container_width=True)
        else:
            st.write(f"No regional sales data found for {selected_game} or all sales are zero.")

elif tab_selection == "Platform and Genre Deep Dive":
    st.header("Platform and Genre Deep Dive")

    # 8. Platform Popularity Over Time (Multi-line Chart or Area Chart)
    st.subheader("7. Platform Popularity Over Time (Global Sales)")
    platform_yearly_sales = df.groupby(["Year", "Platform"])["Global_Sales"].sum().reset_index()
    
    # Select top N platforms to avoid clutter, or let user select
    top_platforms_overall = df.groupby("Platform")["Global_Sales"].sum().nlargest(10).index
    platform_yearly_sales_filtered = platform_yearly_sales[platform_yearly_sales["Platform"].isin(top_platforms_overall)]

    platform_chart_type = st.selectbox("Select Chart Type for Platform Popularity:", ["Multi-line Chart", "Area Chart"], key="platform_pop_chart_type")

    if platform_chart_type == "Multi-line Chart":
        fig_platform_popularity = px.line(platform_yearly_sales_filtered, x="Year", y="Global_Sales", color="Platform",
                                          title="Platform Popularity Over Time (Top 10 Platforms by Global Sales)",
                                          markers=True, labels={"Global_Sales": "Global Sales (Millions)"})
    else: # Area Chart
        fig_platform_popularity = px.area(platform_yearly_sales_filtered, x="Year", y="Global_Sales", color="Platform",
                                          title="Platform Popularity Over Time (Top 10 Platforms by Global Sales) - Area Chart",
                                          labels={"Global_Sales": "Global Sales (Millions)"})
    
    fig_platform_popularity.update_layout(xaxis_title="Year", yaxis_title="Global Sales (Millions)")
    st.plotly_chart(fig_platform_popularity, use_container_width=True)

    # 9. Heatmap of Genre vs Platform (Global Sales)
    st.subheader("8. Heatmap of Genre vs. Platform (Global Sales)")
    genre_platform_sales = df.groupby(["Genre", "Platform"])["Global_Sales"].sum().reset_index()
    
    # Pivot table for heatmap
    heatmap_data = genre_platform_sales.pivot_table(index="Genre", columns="Platform", values="Global_Sales", fill_value=0)
    
    # Filter to top N platforms for better readability if too many platforms
    if len(heatmap_data.columns) > 15:
        top_platforms_for_heatmap = df.groupby("Platform")["Global_Sales"].sum().nlargest(15).index
        heatmap_data_filtered = heatmap_data[top_platforms_for_heatmap]
        st.write("(Showing Top 15 Platforms for clarity)")
    else:
        heatmap_data_filtered = heatmap_data

    if not heatmap_data_filtered.empty:
        fig_genre_platform_heatmap = px.imshow(heatmap_data_filtered, 
                                               text_auto=".1f", # Show values with 1 decimal place
                                               aspect="auto",
                                               title="Heatmap of Genre Sales Across Platforms (Global Sales)",
                                               color_continuous_scale="Viridis",
                                               labels=dict(color="Global Sales (Millions)"))
        fig_genre_platform_heatmap.update_layout(xaxis_title="Platform", yaxis_title="Genre")
        st.plotly_chart(fig_genre_platform_heatmap, use_container_width=True)
    else:
        st.write("Not enough data to generate Genre vs. Platform heatmap.")