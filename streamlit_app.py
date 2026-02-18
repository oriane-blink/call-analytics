import streamlit as st
import pandas as pd
import altair as alt
from snowflake.connector import connect

st.title("Call Analytics")

# --- Snowflake connection ---
# conn = st.connection("snowflake")

# --- Streamlit sidebar configuration ---
st.sidebar.header("Parameters")

start_date = st.sidebar.date_input("Start date", pd.to_datetime("2026-01-01"))
end_date = st.sidebar.date_input("End date", "today")
packet_loss_rate = st.sidebar.slider("Packet loss rate", 0.0, 1.0, 0.10, 0.01)

df = pd.read_csv('call_data.csv')

org = st.sidebar.multiselect("Organisation", df["ORG_NAME"].unique())
if org:
    df = df[df["ORG_NAME"].isin(org)]

# --- Chart config ---
time_grain = st.sidebar.selectbox(
    "Time aggregation",
    ["Day", "Week", "Month"],
    index=0
)
time_map = {
    "Day": "yearmonthdate(CREATED_AT)",
    "Week": "yearweek(CREATED_AT)",
    "Month": "yearmonth(CREATED_AT)"
}
time_encoding = time_map[time_grain]

quality_colors = {
    "Unconnected": "#b5b5b5",
    "Dropped": "#363636",
    "Bad audio": "#ff5959",
    "Bad video": "#ff5959",
    "Missed": "#fcf7a9",
    "Rejected": "#ffd382",
    "Successful": "#a4e3a1"
}
color_scale = alt.Scale(
    domain=list(quality_colors.keys()),
    range=list(quality_colors.values())
)

# --- Chart ---
chart = (
    alt.Chart(df)
    .mark_bar()
    .encode(
        x=alt.X(f"{time_encoding}:T", title="Created At"),
        y=alt.Y(
            "count():Q",
            stack="normalize",
            axis=alt.Axis(format="%"),
            title="Percentage of Calls"
        ),
        color=alt.Color("QUALITY:N", scale=color_scale, title="Quality"),
        tooltip=[
            alt.Tooltip("QUALITY:N"),
            alt.Tooltip("count():Q", title="Calls")
        ]
    )
    .properties(width=900, height=500)
)

st.altair_chart(chart, use_container_width=True)
