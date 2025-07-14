import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# --- Clean Rebate Data ---
rebate_data = {
    "Daily PK": [
        {"PK points": 7000, "Diamonds": 700, "Win Beans": 210, "Rebate %": 0.3},
        {"PK points": 10000, "Diamonds": 1000, "Win Beans": 300, "Rebate %": 0.3},
        {"PK points": 20000, "Diamonds": 2000, "Win Beans": 600, "Rebate %": 0.3},
        {"PK points": 30000, "Diamonds": 3000, "Win Beans": 900, "Rebate %": 0.3},
        {"PK points": 50000, "Diamonds": 5000, "Win Beans": 1000, "Rebate %": 0.2},
        {"PK points": 100000, "Diamonds": 10000, "Win Beans": 1800, "Rebate %": 0.18},
        {"PK points": 150000, "Diamonds": 15000, "Win Beans": 2700, "Rebate %": 0.18},
    ],
    "Talent PK": [
        {"PK points": 5000, "Diamonds": 500, "Win Beans": 150, "Rebate %": 0.3},
        {"PK points": 10000, "Diamonds": 1000, "Win Beans": 350, "Rebate %": 0.35},
        {"PK points": 20000, "Diamonds": 2000, "Win Beans": 700, "Rebate %": 0.35},
        {"PK points": 30000, "Diamonds": 3000, "Win Beans": 1000, "Rebate %": 0.333},
        {"PK points": 50000, "Diamonds": 5000, "Win Beans": 1700, "Rebate %": 0.34},
    ],
    "Star Tasks": [
        {"PK points": 2000, "Diamonds": 200, "Win Beans": 60, "Rebate %": 0.3},
        {"PK points": 10000, "Diamonds": 1000, "Win Beans": 320, "Rebate %": 0.32},
        {"PK points": 50000, "Diamonds": 5000, "Win Beans": 1700, "Rebate %": 0.34},
        {"PK points": 80000, "Diamonds": 8000, "Win Beans": 2800, "Rebate %": 0.35},
        {"PK points": 100000, "Diamonds": 10000, "Win Beans": 3500, "Rebate %": 0.35},
        {"PK points": 120000, "Diamonds": 12000, "Win Beans": 4000, "Rebate %": 0.333},
    ]
}

# --- Helpers ---
def sanitize_rebate_data(data):
    return {
        pk_type: [e for e in entries if isinstance(e, dict) and
                  all(k in e for k in ["Diamonds", "Win Beans", "Rebate %", "PK points"])]
        for pk_type, entries in data.items()
    }

def filter_by_diamonds(data, diamond_input):
    results = []
    for pk_type, entries in data.items():
        for e in entries:
            if e["Diamonds"] <= diamond_input:
                e = e.copy()
                e["PK Type"] = pk_type
                results.append(e)
    return pd.DataFrame(results)

def filter_by_goal(data, bean_goal):
    results = []
    for pk_type, entries in data.items():
        for e in entries:
            if e["Win Beans"] >= bean_goal:
                e = e.copy()
                e["PK Type"] = pk_type
                results.append(e)
    return pd.DataFrame(results)

def show_best(df, key_fields=["PK Type", "Diamonds", "Win Beans", "Rebate %"]):
    best = df.iloc[0]
    st.subheader("🏆 Best Match")
    for field in key_fields:
        val = f'{best[field]*100:.2f}%' if "Rebate %" in field else best[field]
        st.metric(label=field, value=val)

def show_chart(df):
    df["Beans per Diamond"] = df["Win Beans"] / df["Diamonds"]
    fig = px.bar(df, x="PK Type", y="Beans per Diamond", color="PK Type", title="Efficiency")
    st.plotly_chart(fig)

def generate_excel_download(dataframe, filename, label="📥 Download Excel"):
    buffer = BytesIO()
    dataframe.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    st.download_button(label=label, data=buffer, file_name=filename,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- App Interface ---
st.set_page_config(page_title="PK Rebate Explorer", layout="wide")
st.title("💎→🫘 PK Rebate Explorer")

rebate_data = sanitize_rebate_data(rebate_data)
tab1, tab2 = st.tabs(["💎 Diamond-Based Search", "🫘 Goal-Based Search"])

with tab1:
    st.header("💠 Filter by Diamond Budget")
    diamonds = st.number_input("Diamond Amount", min_value=0, value=1000, step=100)
    sort1 = st.selectbox("Sort by", ["Win Beans", "Rebate %"], key="sort1")
    
    df1 = filter_by_diamonds(rebate_data, diamonds)
    if not df1.empty:
        df1 = df1.sort_values(by=sort1, ascending=False)
        show_best(df1)
        st.subheader("📊 Matching Options")
        st.dataframe(df1.reset_index(drop=True))
        show_chart(df1)
        generate_excel_download(df1, f"diamond_search_{diamonds}.xlsx")
    else:
        st.warning("No matching results for that diamond amount.")

with tab2:
    st.header("🎯 Filter by Desired Win Beans")
    beans = st.number_input("Win Beans Goal", min_value=0, value=1000, step=50)
    sort2 = st.selectbox("Sort by", ["Diamonds", "Rebate %"], key="sort2")
    
    df2 = filter_by_goal(rebate_data, beans)
    if not df2.empty:
        df2 = df2.sort_values(by=sort2, ascending=(sort2 == "Diamonds"))
        show_best(df2)
        st.subheader("📊 Recommended Tiers")
        st.dataframe(df2.reset_index(drop=True))
        show_chart(df2)
        generate_excel_download(df2, f"goal_search_{beans}.xlsx")
    else:
        st.warning("No rebate tiers meet or exceed that goal.")

# --- Debug Info ---
with st.expander("🛠 Debug Panel"):
    st.json({k: v[:1] for k, v in rebate_data.items()})