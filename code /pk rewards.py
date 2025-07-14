import streamlit as st
import openpyxl
from openpyxl.styles import Font
from openpyxl import Workbook
import tempfile
import os

def read_rules_rewards(sheet):
    pk_data = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if row[0] is None or row[1] is None or row[2] is None:
            continue
        pk_type, pk_points, win_reward = row[0], row[1], row[2]
        diamonds_needed = int(str(pk_points).replace("0", ""))
        pk_data.append({
            "pk_type": pk_type,
            "pk_points": pk_points,
            "win_reward": win_reward,
            "diamonds_needed": diamonds_needed
        })
    return pk_data

def calculate_efficiency(pk_data, diamonds_available):
    options = [pk for pk in pk_data if pk["diamonds_needed"] <= diamonds_available]
    if not options:
        return None
    return max(options, key=lambda x: x["win_reward"] / x["diamonds_needed"])

def generate_excel(optimal_pk, diamonds_available):
    wb = Workbook()
    ws = wb.active
    ws.title = "PK Efficiency"

    header_font = Font(bold=True)
    ws.append(["Diamonds Available", diamonds_available])
    ws.append(["PK Type", optimal_pk["pk_type"]])
    ws.append(["PK Points", optimal_pk["pk_points"]])
    ws.append(["Diamonds Needed", optimal_pk["diamonds_needed"]])
    ws.append(["Win Reward", optimal_pk["win_reward"]])
    ws.append(["Efficiency (Reward/Diamond)", round(optimal_pk["win_reward"] / optimal_pk["diamonds_needed"], 2)])

    for cell in ws["1:1"]:
        cell.font = header_font

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    wb.save(temp_file.name)
    return temp_file.name

# -------- Streamlit UI --------
st.title("💎 PK Reward Efficiency Calculator")

uploaded_file = st.file_uploader("Upload your event Excel file")
diamonds = st.number_input("Enter the number of diamonds you have", min_value=0, value=0, step=1)

if uploaded_file and diamonds:
    wb = openpyxl.load_workbook(uploaded_file, data_only=True)
    if "Rules and rewards" in wb.sheetnames:
        sheet = wb["Rules and rewards"]
        pk_data = read_rules_rewards(sheet)
        optimal = calculate_efficiency(pk_data, diamonds)

        if optimal:
            st.success("Most efficient PK reward found!")
            st.write(f"🔹 PK Type: {optimal['pk_type']}")
            st.write(f"🔹 Diamonds Needed: {optimal['diamonds_needed']}")
            st.write(f"🔹 Win Reward: {optimal['win_reward']}")
            st.write(f"🔹 Efficiency: {round(optimal['win_reward'] / optimal['diamonds_needed'], 2)} reward/diamond")

            file_path = generate_excel(optimal, diamonds)
            with open(file_path, "rb") as f:
                st.download_button("📥 Download Excel Breakdown", f, file_name="pk_efficiency_breakdown.xlsx")

            os.remove(file_path)
        else:
            st.warning("No eligible PK found for your diamond amount.")
    else:
        st.error("Sheet 'Rules and rewards' not found in uploaded file.")