import streamlit as st
import pandas as pd
import plotly.express as px

# Clean rebate dataset
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

def sanitize_rebate_data(data):
    cleaned = {}
    for pk_type, entries in data.items():
        safe_entries = []
        for entry in entries:
            if isinstance(entry, dict) and all(k in entry for k in ["Diamonds", "Win Beans", "Rebate %", "PK points"]):
                safe_entries.append(entry)
        cleaned[pk_type] = safe_entries
    return cleaned

rebate_data = sanitize_rebate_data(rebate_data)

# 🎯 Start of App
st.set_page_config(page_title="PK Rebate Explorer", layout="wide")
st.title("💎→🫘 PK Rebate Explorer")

tab1, tab2 = st.tabs(["💎 Diamond-Based Search", "🫘 Goal-Based Search"])

with tab1:
    st.header("🔍 Search by Available Diamonds")
    diamond_input = st.number_input("Enter Diamond Amount", min_value=0, value=1000, step=100)
    sort_by = st.selectbox("Sort By", ["Win Beans", "Rebate %"], key="sort1")
    
    results = []
    for pk_type, entries in rebate_data.items():
        for entry in entries:
            if entry["Diamonds"] <= diamond_input:
                new_entry = entry.copy()
                new_entry["PK Type"] = pk_type
                results.append(new_entry)
    
    if results:
        df = pd.DataFrame(results)
        if sort_by == "Win Beans":
            df = df.sort_values(by="Win Beans", ascending=False)
        else:
            df = df.sort_values(by="Rebate %", ascending=False)
        
        best = df.iloc[0]
        st.subheader("🏆 Best Match")
        st.metric("PK Type", best["PK Type"])
        st.metric("Diamonds", best["Diamonds"])
        st.metric("Win Beans", best["Win Beans"])
        st.metric("Rebate %", f'{best["Rebate %"] * 100:.2f}%')

        st.subheader("📊 All Matching Options")
        st.dataframe(df.reset_index(drop=True))

        st.subheader("📉 Efficiency Graph")
        df["Beans per Diamond"] = df["Win Beans"] / df["Diamonds"]
        fig = px.bar(df, x="PK Type", y="Beans per Diamond", color="PK Type", title="Efficiency")
        st.plotly_chart(fig)

        st.download_button("📥 Download Results", df.to_excel(index=False), file_name=f"diamond_search_{diamond_input}.xlsx")

    else:
        st.warning("No matching options found for that diamond amount.")

with tab2:
    st.header("🎯 Search by Goal Win Beans")
    bean_goal = st.number_input("Enter Desired Win Beans", min_value=0, value=1000, step=50)
    sort_by2 = st.selectbox("Sort By", ["Diamonds", "Rebate %"], key="sort2")

    recommendations = []
    for pk_type, entries in rebate_data.items():
        for entry in entries:
            if entry["Win Beans"] >= bean_goal:
                e = entry.copy()
                e["PK Type"] = pk_type
                recommendations.append(e)

    if recommendations:
        df2 = pd.DataFrame(recommendations)
        if sort_by2 == "Diamonds":
            df2 = df2.sort_values(by="Diamonds")
        else:
            df2 = df2.sort_values(by="Rebate %", ascending=False)

        top = df2.iloc[0]
        st.subheader("🏅 Recommended Tier")
        st.metric("PK Type", top["PK Type"])
        st.metric("Diamonds", top["Diamonds"])
        st.metric("Win Beans", top["Win Beans"])
        st.metric("Rebate %", f'{top["Rebate %"] * 100:.2f}%')

        st.subheader("📊 All Recommendations")
        st.dataframe(df2.reset_index(drop=True))

        st.subheader("📉 Efficiency Graph")
        df2["Beans per Diamond"] = df2["Win Beans"] / df2["Diamonds"]
        fig2 = px.bar(df2, x="PK Type", y="Beans per Diamond", color="PK Type", title="Efficiency")
        st.plotly_chart(fig2)

        st.download_button("📥 Download Recommendations", df2.to_excel(index=False), file_name=f"goal_search_{bean_goal}.xlsx")
    else:
        st.warning("No rebate tiers meet or exceed that win bean goal.")

# 🧪 Debug Panel
with st.expander("🧪 Debug Info"):
    st.write("💎 Rebate Data Sample:")
    st.json({k: v[:1] for k, v in rebate_data.items()})