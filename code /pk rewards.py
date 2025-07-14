import streamlit as st
import pandas as pd
from itertools import combinations
from io import BytesIO

# --- Dataset ---
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

# --- Combo Generator ---
def get_all_entries(data):
    all_items = []
    for pk_type, entries in data.items():
        for e in entries:
            item = {**e, "PK Type": pk_type}
            all_items.append(item)
    return all_items

def generate_combinations(all_entries, diamond_limit, max_combo_size=4):
    valid_combos = []
    for r in range(1, max_combo_size + 1):
        for combo in combinations(all_entries, r):
            total_diamonds = sum(e["Diamonds"] for e in combo)
            if total_diamonds <= diamond_limit:
                valid_combos.append(combo)
    return valid_combos

def summarize_combo(combo):
    summary = {
        "Total Diamonds": sum(e["Diamonds"] for e in combo),
        "Total Win Beans": sum(e["Win Beans"] for e in combo),
        "Average Rebate %": round(sum(e["Rebate %"] for e in combo) / len(combo), 3),
    }
    for i, e in enumerate(combo):
        summary[f"Tier {i+1}"] = (
            f'{e["PK Type"]}: {e["PK points"]} pts | '
            f'{e["Diamonds"]}💎 | {e["Win Beans"]}🫘 | {e["Rebate %"]:.2f}'
        )
    return summary

# --- Excel Export ---
def generate_excel_download(df, filename):
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    st.download_button("📥 Download Results", data=buffer, file_name=filename,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# --- Streamlit App ---
st.set_page_config(page_title="PK Combo Finder", layout="centered")
st.title("💎 PK Tier Combo Finder")

diamond_input = st.number_input("Enter your available Diamonds", min_value=0, value=9000, step=100)

entries = get_all_entries(rebate_data)
combos = generate_combinations(entries, diamond_input, max_combo_size=4)

if combos:
    results = pd.DataFrame([summarize_combo(c) for c in combos])
    results = results.sort_values(by="Total Win Beans", ascending=False)
    st.subheader(f"🔍 Found {len(results)} Valid Combos (Up to 4 PKs)")
    st.dataframe(results.reset_index(drop=True))
    generate_excel_download(results, f"combo_results_{diamond_input}.xlsx")
else:
    st.warning("No valid PK combinations found within your diamond amount.")

with st.expander("🛠 Debug Panel", expanded=False):
    st.json({k: v[:1] for k, v in rebate_data.items()})