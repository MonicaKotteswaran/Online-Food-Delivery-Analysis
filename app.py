import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Online Food Delivery Analysis Dashboard", layout="wide")


# -------------------- DB CONNECTION --------------------
# Example: MySQL
engine = create_engine("mysql+pymysql://root:root@127.0.0.1/OnlineFoodDeliveryData")

@st.cache_data
def load_data():
    query = "SELECT * FROM food_delivery_orders"
    return pd.read_sql(query, engine)

df = load_data()

# ---------------- KPI CALCULATIONS ----------------
total_orders = df["Order_ID"].nunique()
total_revenue = df["Final_Amount"].sum()
avg_orderValue=df["Final_Amount"].mean()
avg_delivery_time = df["Delivery_Time_Min"].mean()
total_customers = df["Customer_ID"].nunique()
avg_deliveryRatings=df["Delivery_Rating"].mean()

def rating_color(value):
    if pd.isna(value):
        return "#90CAF9"   # Light Blue
    elif value <= 1:
        return "#E53935"   # Red
    elif value <= 2:
        return "#FB8C00"   # Orange
    elif value <= 3:
        return "#FDD835"   # Yellow
    elif value <= 4:
        return "#43A047"   # Green
    else:
        return "#1B5E20"   # Dark Green

df["Rating_Color"] = df["Delivery_Rating"].apply(rating_color)

city_cuisine = (
    df.groupby(["City", "Cuisine_Type"])["Final_Amount"]
    .sum()
    .reset_index()
)

rating_df = (
    df.groupby("Restaurant_Name")["Restaurant_Rating"]
    .mean()
    .reset_index()
    .sort_values("Restaurant_Rating")
)
cancelled_orders = df[df["Order_Status"] == "Cancelled"].shape[0]

cancellation_rate = (cancelled_orders / total_orders) * 100
# ---------------- KPI CARDS ----------------
st.markdown("## 🍔Online Food Delivery Analysis Dashboard")

k1, k2, k3, k4 ,k5,k6,k7 = st.columns(7)

k1.metric("Total Orders", f"{total_orders}")
k2.metric(
    "Total Revenue",
    f"${total_revenue/1_000_000:.2f}M"
)
k3.metric("Avg Delivery Time (min)", f"{avg_delivery_time:.2f}")
k4.metric("Total Customers", f"{total_customers}")
k5.metric("Average Order Value",f"{avg_orderValue:,.2f}")
k6.metric("Average Delivery Ratings",f"{avg_deliveryRatings:,.2f}")
k7.metric("Cancellation Rate",f"{cancellation_rate:.2f}%")
st.divider()

# ---------------- ROW 1 ----------------
c1, c2, c3 = st.columns(3)

# 1️⃣ Cuisine Revenue Pie
with c1:
    cuisine_rev = df.groupby("Cuisine_Type")["Final_Amount"].sum().reset_index()
    fig = px.pie(
        cuisine_rev,
        names="Cuisine_Type",
        values="Final_Amount",
        title="Cuisine-wise Revenue"
    )
    st.plotly_chart(fig, use_container_width=True)

# 2️⃣ Delivery Rating Donut

with c2:
    rating_count = (
    df.groupby("Delivery_Rating")
    .size()
    .reset_index(name="Count")
    )

    rating_count["Color"] = rating_count["Delivery_Rating"].apply(rating_color)

    fig = px.pie(
        rating_count,
        names="Delivery_Rating",
        values="Count",
        hole=0.5,
        title="Delivery Rating Distribution"
        )

    fig.update_traces(
            marker=dict(colors=rating_count["Color"]),
            textinfo="percent+label"
        )

    st.plotly_chart(fig, use_container_width=True)
# 3️⃣ Restaurant Rating (Stars)
with c3:

    fig = px.bar(
    rating_df,
    x="Restaurant_Rating",
    y="Restaurant_Name",
    orientation="h",
    color="Restaurant_Rating",
    color_continuous_scale=[
        "#E53935", "#FB8C00", "#FDD835", "#43A047", "#1B5E20"
    ],
    title="Restaurant Ratings"
    )

    fig.update_layout(
    xaxis_range=[0, 5],
    plot_bgcolor="white",
    height=500
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------- ROW 2 ----------------
c4, c5,c6 = st.columns(3)

# 4️⃣ Payment Mode Reference
with c4:
    pay_mode = df.groupby("Payment_Mode").size().reset_index(name="Orders")
    fig = px.bar(
        pay_mode,
        x="Orders",
        y="Payment_Mode",
        orientation="h",
        title="Orders by Payment Mode",
        color="Payment_Mode"
    )
    st.plotly_chart(fig, use_container_width=True)

# 5️⃣ Revenue / Order / Profit Line Chart
with c5:
    daily = df.groupby("Order_Month").agg(
        Revenue=("Final_Amount", "sum"),
        Order_Value=("Order_Value", "sum")
    ).reset_index()

    fig = px.line(
        daily,
        x="Order_Month",
        y=["Revenue", "Order_Value"],
        title="Revenue vs Order Value"
    )
    st.plotly_chart(fig, use_container_width=True)

with c6:

    fig = px.bar(
    city_cuisine,
    x="City",
    y="Final_Amount",
    color="Cuisine_Type",
    title="City vs Cuisine (Revenue)",
    text=city_cuisine["Final_Amount"].apply(lambda x: f"{x/1000:.2f}K"),
    )

    fig.update_traces(
        textposition="inside",
        textfont_color="white"
    )

    fig.update_layout(
    plot_bgcolor="white",
    xaxis_title="City",
    yaxis_title="Revenue",
    height=500,
    bargap=0.25,
    legend_title="Cuisine"
    )

    st.plotly_chart(fig, use_container_width=True)


