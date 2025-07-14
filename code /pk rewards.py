import streamlit as st
import pandas as pd

# Rebate dataset from Excel reference
rebate_data = {
    "Daily PK": [...],      # Same structure as before
    "Talent PK": [...],
    "Star Tasks": [...]
}

st.title("💎→🫘 PK Rebate Explorer")

# Choose mode
mode = st.radio("Select Mode", ["Diamond-Based", "Goal-Based"])

# Sort preference
sort_by = st.selectbox("Sort By", ["Win Beans", "Rebate %"])

result_df = pd.DataFrame()
best_option = None

if mode == "Diamond-Based":
    diamond_input = st.number_input("Enter Diamond Amount", min_value=0, value=1000, step=100)
    
    all_results = []
    for pk_type, entries in rebate_data.items():
        for entry in entries:
            if entry["Diamonds"] <= diamond_input:
                entry_copy = entry.copy()
                entry_copy["PK Type"] = pk_type
                all_results.append(entry_copy)

    if all_results:
        result_df = pd.DataFrame(all_results)
        
elif mode == "Goal-Based":
    bean_goal = st.number_input("Enter Goal Win Beans", min_value=0, value=1000, step=50)

    candidates = []
    for pk_type, entries in rebate_data.items():
        for entry in entries:
            if entry["Win Beans"] >= bean_goal:
                entry_copy = entry.copy()
                entry_copy["PK Type"] = pk_type
                candidates.append(entry_copy)

    if candidates:
        result_df = pd.DataFrame(candidates)

# Display results
if not result_df.empty:
    if sort_by == "Win Beans":
        result_df = result_df.sort_values(by="Win Beans", ascending=False)
    else:
        result_df = result_df.sort_values(by="Rebate %", ascending=False)

    best_option = result_df.iloc[0]

    st.subheader("🏆 Best Match")
    st.metric("PK Type", best_option["PK Type"])
    st.metric("Diamonds", best_option["Diamonds"])
    st.metric("Win Beans", best_option["Win Beans"])
    st.metric("Rebate %", f'{best_option["Rebate %"] * 100:.2f}%')

    st.subheader("📊 All Matching Tiers")
    st.dataframe(result_df.reset_index(drop=True))

    # Optional Excel export
    st.subheader("📥 Export Data")
    filename = f"rebate_results_{mode.lower()}.xlsx"
    result_df.to_excel(filename, index=False)
    with open(filename, "rb") as f:
        st.download_button("Download Excel", f, file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.warning("No matching results found for your input.")