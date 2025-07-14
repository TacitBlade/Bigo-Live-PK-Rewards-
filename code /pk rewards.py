import streamlit as st
import openpyxl
from openpyxl.styles import Font
from openpyxl import Workbook
import tempfile
import os
import pandas as pd
import matplotlib.pyplot as plt

# Read PK rules and rewards from sheet
def read_rules_rewards(sheet):
    pk_data = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        pk_type, pk_points, win_reward = row[0], row[1], row[2]

        if not isinstance(pk_points, (int, float)) or pk_points is None:
            continue

        diamonds_needed = int(pk_points / 10)  # Remove one zero by dividing
        pk_data.append({
            "pk_type": pk_type,
            "pk_points": pk_points,
            "win_reward": win_reward,
            "diamonds_needed": diamonds_needed
        })
    return pk_data

# Choose the most efficient PK option
def calculate_efficiency(pk_data, diamonds_available):
    options = [pk for pk in pk_data if pk["diamonds_needed"] <= diamonds_available]
    if not options:
        return None
    return max(options, key
