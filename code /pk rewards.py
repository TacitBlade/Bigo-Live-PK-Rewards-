import streamlit as st
import pandas as pd
from io import BytesIO

# --- PK Rebate Dataset ---
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
def sanitize_data(data):
    all_entries = []
    for pk_type, tiers in data.items():
        for e in tiers:
            entry = {**e, "PK Type": pk_type}
            all_entries.append(entry)
    return pd.DataFrame(all_entries)

def filter_by_diamonds(df, diamond_limit):
    return df[df["Diamonds"] <= diamond_limit].copy()

def generate_excel_download(df, filename):
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    st.download_button("📥 Download Excel", data=buffer, file_name=filename,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Streamlit App ---
st.set_page_config(page_title="PK Rebate Explorer", layout="centered")
st.title("💎 PK Rebate Explorer")

diamond_input = st.number_input("Enter your available Diamonds", min_value=0, value=1000, step=100)
sort_by = st.selectbox("Sort by", ["Win Beans", "Rebate %"])

df_all = sanitize_data(rebate_data)
df_filtered = filter_by_diamonds(df_all, diamond_input)

if not df_filtered.empty:
    df_sorted = df_filtered.sort_values(by=sort_by, ascending=False).reset_index(drop=True)
    st.subheader("📊 Matching PK Tiers")
    st.dataframe(df_sorted)
    generate_excel_download(df_sorted, f"pk_tiers_{diamond_input}.xlsx")
else:
    st.warning("No PK tiers available within that diamond budget.")

with st.expander("🛠 Debug Panel", expanded=False):
    st.json({k: v[:1] for k, v in rebate_data.items()})