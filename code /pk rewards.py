import streamlit as st
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font
import pandas as pd
import tempfile
import os

# Read and validate PK data
def read_rules_rewards(sheet):
    pk_data = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        pk_type, pk_points, win_reward = row[0], row[1], row[2]

        if pk_type is None or pk_points is None or win_reward is None:
            continue
        if not isinstance(pk_points, (int, float)) or not isinstance(win_reward, (int, float)):
            continue

        pk_data.append({
            "pk_type": str(pk_type),
            "pk_points": int(pk_points),
            "win_reward": float(win_reward)
        })
    return pk_data

# Maximize total win rewards given score limit
def optimize_rewards(pk_data, max_score):
    pk_data.sort(key=lambda x: x["win_reward"] / x["pk_points"], reverse=True)
    allocation = []
    remaining_score = max_score

    for option in pk_data:
        if option["pk_points"] <= remaining_score:
            uses = remaining_score // option["pk_points"]
            total_points = uses * option["pk_points"]
            total_reward = uses * option["win_reward"]
            allocation.append({
                "PK Type": option["pk_type"],
                "Points Each": option["pk_points"],
                "Win Reward Each": option["win_reward"],
                "Uses": uses,
                "Total Points": total_points,
                "Total Reward": total_reward
            })
            remaining_score -= total_points

    return allocation, max_score - remaining_score

# Generate Excel download
def generate_excel(allocation, diamonds, total_used_score):
    wb = Workbook()
    ws = wb.active
    ws.title = "Optimized Allocation"

    header_font = Font(bold=True)
    ws.append(["Diamonds Used", diamonds])
    ws.append(["Score Target", diamonds * 10])
    ws.append(["Score Utilized", total_used_score])
    ws.append([])

    ws.append(["PK Type", "Points Each", "Win Reward Each", "Uses", "Total Points", "Total Reward"])
    for row in allocation:
        ws.append([
            row["PK Type"],
            row["Points Each"],
            row["Win Reward Each"],
            row["Uses"],
            row["Total Points"],
            row["Total Reward"]
        ])
    for cell in ws["6:6"]:
        cell.font = header_font

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(temp_file.name)
    return temp_file.name

# Streamlit UI
st.set_page_config(page_title="PK Reward Maximizer", layout="centered")
st.title("💎 PK Score-Based Reward Optimizer")

uploaded_file = st.file_uploader("📤 Upload your event Excel file (.xlsx)")
diamonds = st.number_input("Enter number of diamonds", min_value=0, value=0, step=1)

if uploaded_file and diamonds:
    try:
        wb = openpyxl.load_workbook(uploaded_file, data_only=True)
        if "Rules and rewards" not in wb.sheetnames:
            st.error("Sheet 'Rules and rewards' not found.")
        else:
            sheet = wb["Rules and rewards"]
            pk_data = read_rules_rewards(sheet)
            score_limit = diamonds * 10

            allocation, total_used_score = optimize_rewards(pk_data, score_limit)

            if allocation:
                st.success("✅ Optimization complete.")
                st.write(f"💎 Diamonds: {diamonds}")
                st.write(f"🏁 Score Limit: {score_limit}")
                st.write(f"🔥 Score Used: {total_used_score}")

                df = pd.DataFrame(allocation)
                st.dataframe(df, use_container_width=True)

                excel_file = generate_excel(allocation, diamonds, total_used_score)
                with open(excel_file, "rb") as f:
                    st.download_button("📥 Download Excel Breakdown", f, file_name="pk_reward_allocation.xlsx")
                os.remove(excel_file)
            else:
                st.warning("No PK options fit within your score limit.")
    except Exception as e:
        st.error(f"⚠️ Error processing file: {e}")