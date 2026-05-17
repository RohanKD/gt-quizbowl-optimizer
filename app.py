import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from itertools import combinations

st.set_page_config(page_title="GT Quizbowl Team Optimizer", layout="wide")

# ============================================================
# DATA: All 16 players with category PPG across tournaments
# Categories: Literature, History, Science, Arts, Beliefs (Relig+Myth), Thought (Phil), Other (SS+Geo)
# ============================================================

# Difficulty weights for team optimization
DIFFICULTY_WEIGHTS = {
    "4-dot (Nationals)": 4.0,
    "3-dot (Regionals)": 3.0,
    "2.5-dot (Penn Bowl)": 2.5,
    "2-dot (Winter/ARCADIA)": 2.0,
    "1.5-dot (HISTONE/Planetfall)": 1.5,
    "1-dot (Fall)": 1.0,
}

# Tournament metadata
TOURNAMENTS = {
    "2025 ACF Nationals": {"difficulty": 4.0, "season": "24-25"},
    "2024 ACF Nationals": {"difficulty": 4.0, "season": "23-24"},
    "2023 ACF Nationals": {"difficulty": 4.0, "season": "22-23"},
    "2026 ACF Regionals": {"difficulty": 3.0, "season": "25-26"},
    "2025 ACF Regionals": {"difficulty": 3.0, "season": "24-25"},
    "2025 Penn Bowl": {"difficulty": 2.5, "season": "25-26"},
    "2025 ACF Winter": {"difficulty": 2.0, "season": "25-26"},
    "2024 ACF Winter": {"difficulty": 2.0, "season": "24-25"},
    "2024 ARCADIA": {"difficulty": 2.0, "season": "24-25"},
    "HISTONE": {"difficulty": 1.5, "season": "25-26"},
    "Planetfall III": {"difficulty": 1.5, "season": "25-26"},
    "2025 ACF Fall": {"difficulty": 1.0, "season": "25-26"},
    "2024 ACF Fall": {"difficulty": 1.0, "season": "24-25"},
    "DART IV": {"difficulty": 1.5, "season": "24-25"},
}

# Per-player per-tournament category PPG data
# Format: {player: [{tournament, difficulty, cats: {lit, hist, sci, arts, beliefs, thought, other}, ppg}]}
PLAYER_DATA = {
    "Kevin Wang": [
        {"tournament": "2026 ACF Nationals", "difficulty": 4.0, "ppg": 35.0, "avg_rank": 4.5, "accuracy": 0.78,
         "cats": {"lit": 28.0, "hist": 3.0, "sci": 0.0, "arts": 0.0, "beliefs": 1.0, "thought": 1.0, "other": 2.0}},
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 41.50,
         "cats": {"lit": 29.0, "hist": 4.5, "sci": 0.0, "arts": 1.0, "beliefs": 1.5, "thought": 2.0, "other": 4.0}},
        {"tournament": "2025 ACF Nationals", "difficulty": 4.0, "ppg": 27.77,
         "cats": {"lit": 21.94, "hist": 2.22, "sci": 0.83, "arts": 0.56, "beliefs": 2.22, "thought": 0.0, "other": 0.0}},
        {"tournament": "2025 ACF Regionals", "difficulty": 3.0, "ppg": 30.0,
         "cats": {"lit": 28.64, "hist": 0.0, "sci": 0.0, "arts": 0.0, "beliefs": 0.91, "thought": 0.45, "other": 0.0}},
        {"tournament": "2024 ARCADIA", "difficulty": 2.0, "ppg": 41.0,
         "cats": {"lit": 31.0, "hist": 0.5, "sci": 0.5, "arts": 1.0, "beliefs": 1.0, "thought": 1.0, "other": 5.0}},
        {"tournament": "2024 ACF Winter", "difficulty": 2.0, "ppg": 25.42,
         "cats": {"lit": 20.42, "hist": 1.67, "sci": 0.83, "arts": 0.83, "beliefs": 0.83, "thought": 0.0, "other": 0.83}},
        {"tournament": "2025 Penn Bowl", "difficulty": 2.5, "ppg": 38.13,
         "cats": {"lit": 30.0, "hist": 3.0, "sci": 0.0, "arts": 1.0, "beliefs": 1.5, "thought": 1.5, "other": 1.0}},
        {"tournament": "HISTONE", "difficulty": 1.5, "ppg": 0.0,  # didn't play HISTONE
         "cats": {"lit": 0, "hist": 0, "sci": 0, "arts": 0, "beliefs": 0, "thought": 0, "other": 0}},
    ],
    "Arunn Sankar": [
        {"tournament": "2026 ACF Nationals", "difficulty": 4.0, "ppg": 5.3, "avg_rank": 10.1, "accuracy": 0.53,
         "cats": {"lit": 0.5, "hist": 2.0, "sci": 1.0, "arts": 0.3, "beliefs": 0.5, "thought": 0.3, "other": 1.5}},
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 20.0,
         "cats": {"lit": 0.0, "hist": 8.5, "sci": 9.0, "arts": 1.0, "beliefs": 0.0, "thought": 0.0, "other": 0.0}},
        {"tournament": "2025 ACF Regionals", "difficulty": 3.0, "ppg": 44.0,
         "cats": {"lit": 5.0, "hist": 11.0, "sci": 13.5, "arts": 7.0, "beliefs": 4.5, "thought": 1.0, "other": 2.0}},
        {"tournament": "2024 ACF Winter", "difficulty": 2.0, "ppg": 58.18,
         "cats": {"lit": 15.91, "hist": 15.0, "sci": 13.18, "arts": 8.64, "beliefs": 1.82, "thought": 2.73, "other": 0.91}},
        {"tournament": "2024 ARCADIA", "difficulty": 2.0, "ppg": 33.5,
         "cats": {"lit": 5.0, "hist": 8.0, "sci": 5.5, "arts": 2.5, "beliefs": 3.5, "thought": 0.0, "other": 3.0}},
        {"tournament": "2024 ACF Nationals", "difficulty": 4.0, "ppg": 15.29,
         "cats": {"lit": 0.59, "hist": 4.41, "sci": 7.35, "arts": 0.59, "beliefs": 0.0, "thought": 0.0, "other": 2.35}},
    ],
    "Rohan Dalal": [
        {"tournament": "2026 ACF Nationals", "difficulty": 4.0, "ppg": 22.0, "avg_rank": 5.5, "accuracy": 0.70,
         "cats": {"lit": 0.0, "hist": 1.5, "sci": 17.0, "arts": 0.3, "beliefs": 0.0, "thought": 1.5, "other": 1.5}},
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 12.50,
         "cats": {"lit": 0.0, "hist": -1.0, "sci": 9.5, "arts": 0.5, "beliefs": 1.0, "thought": -0.5, "other": 2.0}},
        {"tournament": "2025 ACF Nationals", "difficulty": 4.0, "ppg": 14.83,
         "cats": {"lit": 0.0, "hist": 1.39, "sci": 11.39, "arts": 0.0, "beliefs": 0.83, "thought": 1.11, "other": 0.56}},
        {"tournament": "2025 ACF Regionals", "difficulty": 3.0, "ppg": 29.73,
         "cats": {"lit": 0.91, "hist": 1.82, "sci": 20.91, "arts": 1.82, "beliefs": 0.45, "thought": 3.64, "other": 0.0}},
        {"tournament": "2024 ACF Winter", "difficulty": 2.0, "ppg": 26.67,
         "cats": {"lit": 1.67, "hist": 1.67, "sci": 18.75, "arts": 0.83, "beliefs": 3.33, "thought": 0.42, "other": 0.0}},
        {"tournament": "2024 ARCADIA", "difficulty": 2.0, "ppg": 21.5,
         "cats": {"lit": 0.0, "hist": 0.0, "sci": 15.0, "arts": 0.0, "beliefs": 1.5, "thought": 2.5, "other": 0.0}},
        {"tournament": "DART IV", "difficulty": 1.5, "ppg": 65.0,
         "cats": {"lit": 5.0, "hist": 5.0, "sci": 40.0, "arts": 5.0, "beliefs": 5.0, "thought": 3.0, "other": 2.0}},
    ],
    "Jeffrey Xu": [
        {"tournament": "2026 ACF Nationals", "difficulty": 4.0, "ppg": 10.0, "avg_rank": 7.0, "accuracy": 0.52,
         "cats": {"lit": 0.0, "hist": 0.0, "sci": 0.8, "arts": 8.5, "beliefs": -0.5, "thought": 0.3, "other": 0.3}},
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 16.50,
         "cats": {"lit": 0.0, "hist": 2.0, "sci": 0.0, "arts": 10.0, "beliefs": 4.5, "thought": -0.5, "other": 0.0}},
        {"tournament": "2025 ACF Nationals", "difficulty": 4.0, "ppg": 5.28,
         "cats": {"lit": 0.56, "hist": 0.56, "sci": 1.11, "arts": 2.22, "beliefs": 0.56, "thought": 0.28, "other": 0.0}},
        {"tournament": "2025 ACF Regionals", "difficulty": 3.0, "ppg": 22.27,
         "cats": {"lit": 0.0, "hist": 3.18, "sci": 0.45, "arts": 12.73, "beliefs": 4.09, "thought": 1.82, "other": 0.0}},
        {"tournament": "2024 ARCADIA", "difficulty": 2.0, "ppg": 51.5,
         "cats": {"lit": 2.5, "hist": 8.0, "sci": 4.0, "arts": 5.0, "beliefs": 4.5, "thought": 4.0, "other": 0.0}},
        {"tournament": "2024 ACF Winter", "difficulty": 2.0, "ppg": 3.33,
         "cats": {"lit": 0.83, "hist": 0.0, "sci": 0.83, "arts": 0.83, "beliefs": 0.0, "thought": 0.83, "other": 0.0}},
        {"tournament": "DART IV", "difficulty": 1.5, "ppg": 66.1,
         "cats": {"lit": 5.0, "hist": 10.0, "sci": 5.0, "arts": 25.0, "beliefs": 10.0, "thought": 8.0, "other": 3.0}},
    ],
    "Tianyu Xu": [
        {"tournament": "2026 ACF Nationals", "difficulty": 4.0, "ppg": 28.0, "avg_rank": 5.0, "accuracy": 0.72,
         "cats": {"lit": 2.5, "hist": 3.0, "sci": 9.0, "arts": 8.5, "beliefs": 0.3, "thought": 1.0, "other": 1.0}},
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 37.0,
         "cats": {"lit": 1.33, "hist": 5.0, "sci": 11.67, "arts": 5.67, "beliefs": 0.33, "thought": 0.67, "other": 1.67}},
        {"tournament": "2025 ACF Regionals", "difficulty": 3.0, "ppg": 23.5,
         "cats": {"lit": 5.0, "hist": 3.0, "sci": 12.5, "arts": 2.0, "beliefs": 1.0, "thought": 0.0, "other": 0.0}},
        {"tournament": "2025 ACF Winter", "difficulty": 2.0, "ppg": 51.36,
         "cats": {"lit": 6.36, "hist": 10.0, "sci": 13.64, "arts": 10.91, "beliefs": 5.45, "thought": 0.91, "other": 1.82}},
        {"tournament": "2024 ACF Winter", "difficulty": 2.0, "ppg": 45.91,
         "cats": {"lit": 10.0, "hist": 5.45, "sci": 16.36, "arts": 5.45, "beliefs": 6.36, "thought": -0.45, "other": 2.73}},
        {"tournament": "2024 ACF Fall", "difficulty": 1.0, "ppg": 47.27,
         "cats": {"lit": 9.55, "hist": 10.0, "sci": 14.55, "arts": 7.27, "beliefs": 5.45, "thought": 0.0, "other": 0.45}},
        {"tournament": "HISTONE", "difficulty": 1.5, "ppg": 50.83,
         "cats": {"lit": 5.0, "hist": 8.0, "sci": 18.0, "arts": 8.0, "beliefs": 5.0, "thought": 3.0, "other": 4.0}},
        {"tournament": "Planetfall III", "difficulty": 1.5, "ppg": 67.5,
         "cats": {"lit": 8.0, "hist": 10.0, "sci": 25.0, "arts": 10.0, "beliefs": 7.0, "thought": 3.0, "other": 4.5}},
        {"tournament": "2025 Penn Bowl", "difficulty": 2.5, "ppg": 33.75,
         "cats": {"lit": 3.0, "hist": 5.0, "sci": 13.0, "arts": 5.0, "beliefs": 3.0, "thought": 1.0, "other": 2.0}},
    ],
    "Alex Thomas": [
        {"tournament": "2026 ACF Nationals", "difficulty": 4.0, "ppg": 25.0, "avg_rank": 5.5, "accuracy": 0.68,
         "cats": {"lit": 3.0, "hist": 2.5, "sci": 5.0, "arts": 8.0, "beliefs": 0.5, "thought": 0.5, "other": 3.0}},
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 30.0,
         "cats": {"lit": 6.0, "hist": 1.33, "sci": 4.67, "arts": 4.33, "beliefs": 0.67, "thought": 0.67, "other": 1.33}},
        {"tournament": "2025 ACF Winter", "difficulty": 2.0, "ppg": 59.55,
         "cats": {"lit": 16.36, "hist": 3.64, "sci": 7.27, "arts": 20.45, "beliefs": 4.55, "thought": 1.82, "other": 3.64}},
        {"tournament": "2024 ACF Winter", "difficulty": 2.0, "ppg": 29.55,
         "cats": {"lit": 13.18, "hist": 0.91, "sci": 7.27, "arts": 3.64, "beliefs": 4.55, "thought": 0.0, "other": 0.0}},
        {"tournament": "2024 ARCADIA", "difficulty": 2.0, "ppg": 51.5,
         "cats": {"lit": 9.5, "hist": 7.0, "sci": 12.0, "arts": 1.5, "beliefs": 6.0, "thought": 3.0, "other": 0.0}},
        {"tournament": "HISTONE", "difficulty": 1.5, "ppg": 54.17,
         "cats": {"lit": 14.0, "hist": 5.0, "sci": 10.0, "arts": 12.0, "beliefs": 5.0, "thought": 3.0, "other": 5.0}},
        {"tournament": "2025 Penn Bowl", "difficulty": 2.5, "ppg": 22.5,
         "cats": {"lit": 8.0, "hist": 2.0, "sci": 4.0, "arts": 5.0, "beliefs": 1.5, "thought": 1.0, "other": 1.0}},
    ],
    "Pranav Jothi": [
        {"tournament": "2026 ACF Nationals", "difficulty": 4.0, "ppg": 6.0, "avg_rank": 8.0, "accuracy": 0.68,
         "cats": {"lit": 5.5, "hist": 0.3, "sci": 0.3, "arts": 0.3, "beliefs": 0.3, "thought": 0.0, "other": 0.3}},
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 20.0,
         "cats": {"lit": 13.67, "hist": 0.0, "sci": 0.0, "arts": 0.67, "beliefs": 0.0, "thought": 0.0, "other": 0.0}},
        {"tournament": "2025 ACF Winter", "difficulty": 2.0, "ppg": 23.18,
         "cats": {"lit": 16.82, "hist": 5.45, "sci": 0.45, "arts": -0.45, "beliefs": 0.91, "thought": 0.0, "other": 0.0}},
        {"tournament": "2025 ACF Fall", "difficulty": 1.0, "ppg": 31.82,
         "cats": {"lit": 17.27, "hist": 4.55, "sci": 0.91, "arts": 7.27, "beliefs": 0.0, "thought": 0.0, "other": 0.0}},
        {"tournament": "2024 ARCADIA", "difficulty": 2.0, "ppg": 23.5,
         "cats": {"lit": 8.5, "hist": 0.0, "sci": 5.0, "arts": 0.0, "beliefs": 2.0, "thought": 5.0, "other": 0.0}},
        {"tournament": "HISTONE", "difficulty": 1.5, "ppg": 37.92,
         "cats": {"lit": 25.0, "hist": 3.0, "sci": 2.0, "arts": 4.0, "beliefs": 2.0, "thought": 1.0, "other": 1.0}},
        {"tournament": "Planetfall III", "difficulty": 1.5, "ppg": 47.27,
         "cats": {"lit": 28.0, "hist": 5.0, "sci": 3.0, "arts": 5.0, "beliefs": 3.0, "thought": 2.0, "other": 1.0}},
        {"tournament": "2025 Penn Bowl", "difficulty": 2.5, "ppg": 31.67,
         "cats": {"lit": 22.0, "hist": 3.0, "sci": 1.0, "arts": 2.0, "beliefs": 2.0, "thought": 1.0, "other": 0.5}},
    ],
    "Arhith Dharanendra": [
        {"tournament": "2026 ACF Nationals", "difficulty": 4.0, "ppg": 10.5, "avg_rank": 7.5, "accuracy": 0.75,
         "cats": {"lit": 0.5, "hist": 2.5, "sci": 0.5, "arts": 0.0, "beliefs": 2.0, "thought": 2.5, "other": 2.5}},
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 27.0,
         "cats": {"lit": 0.67, "hist": 3.67, "sci": 0.0, "arts": 0.33, "beliefs": 8.33, "thought": 0.67, "other": 1.33}},
        {"tournament": "2025 ACF Winter", "difficulty": 2.0, "ppg": 33.64,
         "cats": {"lit": -0.91, "hist": 13.64, "sci": 0.91, "arts": 1.82, "beliefs": 10.45, "thought": 3.64, "other": 0.0}},
        {"tournament": "2025 ACF Regionals", "difficulty": 3.0, "ppg": 11.5,
         "cats": {"lit": 0.0, "hist": 5.0, "sci": 1.0, "arts": 1.0, "beliefs": 3.0, "thought": 0.5, "other": 1.0}},
        {"tournament": "2024 ACF Winter", "difficulty": 2.0, "ppg": 20.91,
         "cats": {"lit": 1.82, "hist": 6.36, "sci": 1.82, "arts": 2.73, "beliefs": 6.82, "thought": 1.36, "other": 0.0}},
        {"tournament": "2024 ARCADIA", "difficulty": 2.0, "ppg": 26.5,
         "cats": {"lit": 2.0, "hist": 9.5, "sci": 0.5, "arts": 2.0, "beliefs": 2.0, "thought": 5.0, "other": 0.5}},
        {"tournament": "2024 ACF Fall", "difficulty": 1.0, "ppg": 30.45,
         "cats": {"lit": 5.45, "hist": 9.09, "sci": 3.64, "arts": -0.45, "beliefs": 6.82, "thought": 4.55, "other": 1.36}},
        {"tournament": "HISTONE", "difficulty": 1.5, "ppg": 16.67,
         "cats": {"lit": 1.0, "hist": 4.0, "sci": 0.0, "arts": 0.5, "beliefs": 7.0, "thought": 2.5, "other": 1.5}},
        {"tournament": "Planetfall III", "difficulty": 1.5, "ppg": 35.0,
         "cats": {"lit": 3.0, "hist": 8.0, "sci": 2.0, "arts": 3.0, "beliefs": 10.0, "thought": 5.0, "other": 4.0}},
        {"tournament": "DART IV", "difficulty": 1.5, "ppg": 41.1,
         "cats": {"lit": 3.0, "hist": 12.0, "sci": 2.0, "arts": 3.0, "beliefs": 12.0, "thought": 5.0, "other": 4.0}},
        {"tournament": "2025 Penn Bowl", "difficulty": 2.5, "ppg": 10.0,
         "cats": {"lit": 0.0, "hist": 3.0, "sci": 0.0, "arts": 0.5, "beliefs": 4.0, "thought": 1.5, "other": 1.0}},
    ],
    "Emerson Patmore": [
        {"tournament": "2026 ACF Nationals", "difficulty": 4.0, "ppg": 24.0, "avg_rank": 6.0, "accuracy": 0.73,
         "cats": {"lit": 2.5, "hist": 9.0, "sci": 1.0, "arts": 2.0, "beliefs": 2.5, "thought": 0.5, "other": 4.0}},
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 37.5,
         "cats": {"lit": 1.88, "hist": 9.38, "sci": 1.25, "arts": 1.25, "beliefs": 3.44, "thought": 1.88, "other": 2.5}},
        {"tournament": "2025 ACF Winter", "difficulty": 2.0, "ppg": 29.09,
         "cats": {"lit": 1.36, "hist": 16.82, "sci": 1.82, "arts": 2.27, "beliefs": 2.73, "thought": 0.45, "other": 0.91}},
        {"tournament": "2025 ACF Fall", "difficulty": 1.0, "ppg": 45.45,
         "cats": {"lit": 9.09, "hist": 11.82, "sci": 7.27, "arts": 4.55, "beliefs": 9.55, "thought": 0.0, "other": 2.27}},
        {"tournament": "HISTONE", "difficulty": 1.5, "ppg": 35.42,
         "cats": {"lit": 3.0, "hist": 12.0, "sci": 3.0, "arts": 3.0, "beliefs": 7.0, "thought": 3.0, "other": 4.0}},
        {"tournament": "Planetfall III", "difficulty": 1.5, "ppg": 47.73,
         "cats": {"lit": 5.0, "hist": 15.0, "sci": 5.0, "arts": 5.0, "beliefs": 8.0, "thought": 4.0, "other": 6.0}},
        {"tournament": "2025 Penn Bowl", "difficulty": 2.5, "ppg": 31.43,
         "cats": {"lit": 2.0, "hist": 12.0, "sci": 2.0, "arts": 2.5, "beliefs": 5.0, "thought": 3.0, "other": 5.0}},
    ],
    "Graham Cope": [
        {"tournament": "2026 ACF Nationals", "difficulty": 4.0, "ppg": 24.0, "avg_rank": 6.5, "accuracy": 0.70,
         "cats": {"lit": 1.5, "hist": 4.5, "sci": 8.0, "arts": 1.0, "beliefs": 1.0, "thought": 0.3, "other": 3.5}},
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 27.19,
         "cats": {"lit": 0.63, "hist": 5.63, "sci": 4.06, "arts": 1.25, "beliefs": 1.88, "thought": 2.5, "other": 0.0}},
        {"tournament": "2024 ACF Nationals", "difficulty": 4.0, "ppg": 25.88,
         "cats": {"lit": 2.35, "hist": 7.94, "sci": 9.12, "arts": 0.29, "beliefs": 1.76, "thought": 2.06, "other": 2.35}},
        {"tournament": "2024 ACF Winter", "difficulty": 2.0, "ppg": 25.45,
         "cats": {"lit": 4.55, "hist": 4.55, "sci": 11.36, "arts": 0.91, "beliefs": 2.73, "thought": 1.82, "other": -0.45}},
        {"tournament": "HISTONE", "difficulty": 1.5, "ppg": 59.58,
         "cats": {"lit": 6.0, "hist": 15.0, "sci": 18.0, "arts": 5.0, "beliefs": 5.0, "thought": 5.0, "other": 6.0}},
        {"tournament": "Planetfall III", "difficulty": 1.5, "ppg": 41.0,
         "cats": {"lit": 4.0, "hist": 10.0, "sci": 12.0, "arts": 4.0, "beliefs": 4.0, "thought": 3.0, "other": 4.0}},
    ],
    "Matthew Sumanen": [
        {"tournament": "2026 ACF Nationals", "difficulty": 4.0, "ppg": 15.0, "avg_rank": 7.5, "accuracy": 0.62,
         "cats": {"lit": 0.5, "hist": 0.5, "sci": 7.5, "arts": -0.3, "beliefs": 0.8, "thought": 3.5, "other": 1.0}},
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 23.44,
         "cats": {"lit": 3.13, "hist": 1.25, "sci": 9.06, "arts": 0.0, "beliefs": 1.25, "thought": 0.94, "other": 0.0}},
        {"tournament": "2025 ACF Winter", "difficulty": 2.0, "ppg": 28.64,
         "cats": {"lit": 3.64, "hist": 0.91, "sci": 10.0, "arts": 3.18, "beliefs": 2.27, "thought": 3.18, "other": -0.45}},
        {"tournament": "2024 ACF Winter", "difficulty": 2.0, "ppg": 14.09,
         "cats": {"lit": 3.64, "hist": 3.18, "sci": 5.45, "arts": 1.36, "beliefs": 0.91, "thought": 0.0, "other": -0.45}},
        {"tournament": "2024 ARCADIA", "difficulty": 2.0, "ppg": 19.5,
         "cats": {"lit": 3.0, "hist": 0.5, "sci": 11.0, "arts": 0.0, "beliefs": -0.5, "thought": 2.5, "other": 0.5}},
        {"tournament": "HISTONE", "difficulty": 1.5, "ppg": 32.5,
         "cats": {"lit": 3.0, "hist": 2.0, "sci": 16.0, "arts": 2.0, "beliefs": 3.0, "thought": 3.0, "other": 3.5}},
        {"tournament": "Planetfall III", "difficulty": 1.5, "ppg": 95.0,
         "cats": {"lit": 10.0, "hist": 12.0, "sci": 40.0, "arts": 10.0, "beliefs": 8.0, "thought": 7.0, "other": 8.0}},
        {"tournament": "2025 Penn Bowl", "difficulty": 2.5, "ppg": 25.83,
         "cats": {"lit": 3.0, "hist": 2.0, "sci": 12.0, "arts": 2.0, "beliefs": 2.5, "thought": 2.0, "other": 2.0}},
    ],
    "Zach Tseng": [
        {"tournament": "2026 ACF Nationals", "difficulty": 4.0, "ppg": 14.5, "avg_rank": 5.5, "accuracy": 0.875,
         "cats": {"lit": 2.0, "hist": 0.0, "sci": 0.3, "arts": 10.0, "beliefs": 0.8, "thought": 0.0, "other": 0.0}},
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 16.88,
         "cats": {"lit": 1.25, "hist": 0.0, "sci": 1.25, "arts": 9.38, "beliefs": -0.31, "thought": 0.0, "other": 0.0}},
        {"tournament": "2025 ACF Winter", "difficulty": 2.0, "ppg": 30.0,
         "cats": {"lit": 4.09, "hist": 5.91, "sci": 2.27, "arts": 12.73, "beliefs": 3.64, "thought": 0.45, "other": 0.91}},
        {"tournament": "2024 ACF Winter", "difficulty": 2.0, "ppg": 20.91,
         "cats": {"lit": 4.55, "hist": 4.09, "sci": 2.27, "arts": 8.64, "beliefs": -0.45, "thought": 1.82, "other": 0.0}},
        {"tournament": "2024 ARCADIA", "difficulty": 2.0, "ppg": 51.0,
         "cats": {"lit": 10.5, "hist": 6.0, "sci": 7.5, "arts": 3.0, "beliefs": 4.0, "thought": 2.0, "other": 2.0}},
        {"tournament": "2025 Penn Bowl", "difficulty": 2.5, "ppg": 15.71,
         "cats": {"lit": 2.0, "hist": 1.0, "sci": 1.0, "arts": 8.0, "beliefs": 1.5, "thought": 1.0, "other": 1.0}},
    ],
    "Aaryan Tomar": [
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 16.67,
         "cats": {"lit": 1.67, "hist": 7.0, "sci": 0.33, "arts": 0.33, "beliefs": 1.33, "thought": 0.67, "other": 2.0}},
        {"tournament": "2025 ACF Winter", "difficulty": 2.0, "ppg": 17.73,
         "cats": {"lit": 1.36, "hist": 10.0, "sci": 0.91, "arts": -0.45, "beliefs": 1.82, "thought": 1.82, "other": 0.0}},
        {"tournament": "2024 ACF Fall", "difficulty": 1.0, "ppg": 37.73,
         "cats": {"lit": 8.64, "hist": 13.18, "sci": 10.91, "arts": 1.82, "beliefs": 1.36, "thought": 1.36, "other": 0.45}},
        {"tournament": "2024 ARCADIA", "difficulty": 2.0, "ppg": 8.0,
         "cats": {"lit": 0.0, "hist": 6.5, "sci": 0.0, "arts": 0.0, "beliefs": 0.0, "thought": 1.5, "other": 0.0}},
    ],
    "Monish Jampala": [
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 18.33,
         "cats": {"lit": 0.33, "hist": 1.0, "sci": 5.67, "arts": 1.0, "beliefs": 2.67, "thought": 1.33, "other": 1.33}},
        {"tournament": "2025 ACF Winter", "difficulty": 2.0, "ppg": 18.18,
         "cats": {"lit": 0.91, "hist": 1.82, "sci": 9.55, "arts": 0.91, "beliefs": 1.82, "thought": 0.91, "other": 0.45}},
        {"tournament": "2024 ACF Fall", "difficulty": 1.0, "ppg": 50.45,
         "cats": {"lit": 9.55, "hist": 4.55, "sci": 17.73, "arts": 5.0, "beliefs": 7.73, "thought": 1.82, "other": 4.09}},
        {"tournament": "2024 ACF Winter", "difficulty": 2.0, "ppg": 16.36,
         "cats": {"lit": 2.73, "hist": -0.45, "sci": 7.27, "arts": 2.73, "beliefs": 2.27, "thought": 0.91, "other": 0.0}},
    ],
    "S.A. Shenoy": [
        {"tournament": "2026 ACF Regionals", "difficulty": 3.0, "ppg": 42.67,
         "cats": {"lit": 4.0, "hist": 0.33, "sci": 8.67, "arts": 7.33, "beliefs": 3.67, "thought": 1.67, "other": 4.0}},
        {"tournament": "2025 ACF Winter", "difficulty": 2.0, "ppg": 44.55,
         "cats": {"lit": 12.73, "hist": 2.73, "sci": 14.55, "arts": 3.64, "beliefs": 7.27, "thought": 1.36, "other": 1.36}},
        {"tournament": "2023 ACF Nationals", "difficulty": 4.0, "ppg": 20.88,
         "cats": {"lit": 2.06, "hist": 1.18, "sci": 8.53, "arts": 5.0, "beliefs": 0.29, "thought": 2.65, "other": 1.18}},
    ],
    "Manu Sankaran": [
        # No ACF category data available - only NAQT Sectional participation (GT C)
    ],
    "Samir Sarma": [
        {"tournament": "2025 ACF Regionals", "difficulty": 3.0, "ppg": 46.0,
         "cats": {"lit": 4.0, "hist": 13.5, "sci": 12.5, "arts": 7.5, "beliefs": 8.0, "thought": -0.5, "other": 1.0}},
        {"tournament": "2025 ACF Winter", "difficulty": 2.0, "ppg": 38.64,
         "cats": {"lit": 6.36, "hist": 3.64, "sci": 18.64, "arts": 4.55, "beliefs": 0.0, "thought": 3.18, "other": 1.36}},
        {"tournament": "2023 DII ICT", "difficulty": 2.0, "ppg": 25.0,
         "cats": {"lit": 0, "hist": 0, "sci": 0, "arts": 0, "beliefs": 0, "thought": 0, "other": 0}},
        {"tournament": "2023 ACF Regionals", "difficulty": 3.0, "ppg": 25.91,
         "cats": {"lit": 0, "hist": 0, "sci": 0, "arts": 0, "beliefs": 0, "thought": 0, "other": 0}},
    ],
}

# ACF Nationals category distribution (tossups per round)
NATS_DISTRIBUTION = {
    "lit": 4,
    "hist": 4,
    "sci": 4,
    "arts": 3,
    "beliefs": 2,  # Religion + Mythology
    "thought": 1,  # Philosophy
    "other": 2,    # Social Science + Geography
}

CATEGORY_LABELS = {
    "lit": "Literature",
    "hist": "History",
    "sci": "Science",
    "arts": "Fine Arts",
    "beliefs": "Religion/Mythology",
    "thought": "Philosophy",
    "other": "Social Sci/Geo",
}


def get_player_avg_rank(player_name, min_difficulty=0.0):
    """Compute difficulty-weighted average buzz rank for a player.
    Lower rank = faster buzzer. Returns None if no rank data available."""
    data = PLAYER_DATA.get(player_name, [])
    if not data:
        return None

    total_rank = 0.0
    total_weight = 0.0
    for entry in data:
        if entry["difficulty"] < min_difficulty:
            continue
        if entry.get("avg_rank") is None:
            continue
        if entry["ppg"] == 0 and all(v == 0 for v in entry["cats"].values()):
            continue
        weight = entry["difficulty"] ** 2
        if entry.get("tournament", "").startswith("2025") or entry.get("tournament", "").startswith("2026"):
            weight *= 1.3
        total_rank += entry["avg_rank"] * weight
        total_weight += weight

    if total_weight == 0:
        return None
    return total_rank / total_weight


def compute_speed_factor(player_name, min_difficulty=0.0):
    """Compute a speed multiplier based on average buzz rank.
    Rank 1 (fastest) -> ~1.35x, Rank 8 (median) -> 1.0x, Rank 15 (slow) -> ~0.65x
    Players with no rank data get 1.0 (neutral)."""
    avg_rank = get_player_avg_rank(player_name, min_difficulty)
    if avg_rank is None:
        return 1.0
    # Linear scale: each rank away from 8 adjusts by 0.05
    return 1.0 + (8.0 - avg_rank) * 0.05


def compute_weighted_category_ppg(player_name, min_difficulty=0.0):
    """Compute difficulty-weighted average category PPG for a player.
    Uses QUADRATIC weighting: weight = difficulty^2
    This heavily emphasizes high-difficulty tournaments (nationals=16x, regs=9x, winter=4x, fall=1x).
    """
    data = PLAYER_DATA.get(player_name, [])
    if not data:
        return {cat: 0.0 for cat in CATEGORY_LABELS}

    weighted_cats = {cat: 0.0 for cat in CATEGORY_LABELS}
    total_weight = 0.0

    for entry in data:
        if entry["difficulty"] < min_difficulty:
            continue
        if entry["ppg"] == 0 and all(v == 0 for v in entry["cats"].values()):
            continue  # skip empty entries
        # QUADRATIC weighting: difficulty^2
        weight = entry["difficulty"] ** 2
        # Recency boost for 25-26 season
        if entry.get("tournament", "").startswith("2025") or entry.get("tournament", "").startswith("2026"):
            weight *= 1.3
        for cat in CATEGORY_LABELS:
            weighted_cats[cat] += entry["cats"].get(cat, 0) * weight
        total_weight += weight

    if total_weight == 0:
        return {cat: 0.0 for cat in CATEGORY_LABELS}

    return {cat: weighted_cats[cat] / total_weight for cat in CATEGORY_LABELS}


def compute_expected_nats_ppg(player_name, min_difficulty=0.0):
    """Estimate expected nationals PPG based on difficulty-weighted category performance.
    Incorporates speed factor from average buzz rank."""
    cat_ppg = compute_weighted_category_ppg(player_name, min_difficulty)
    sf = compute_speed_factor(player_name, min_difficulty)
    # Sum across categories, adjusted by speed factor
    return sum(cat_ppg.values()) * sf


def compute_team_score(team, min_difficulty=0.0):
    """Compute expected team score considering category coverage and diminishing returns."""
    cat_contributions = {cat: [] for cat in CATEGORY_LABELS}

    # Pre-compute speed factors for each player
    speed_factors = {player: compute_speed_factor(player, min_difficulty) for player in team}

    for player in team:
        cat_ppg = compute_weighted_category_ppg(player, min_difficulty)
        sf = speed_factors[player]
        for cat in CATEGORY_LABELS:
            if cat_ppg[cat] > 0:
                # Apply speed factor: faster buzzers convert more often
                cat_contributions[cat].append((player, cat_ppg[cat] * sf))

    # For each category, model diminishing returns for multiple players
    total_score = 0.0
    category_scores = {}
    for cat, contributions in cat_contributions.items():
        contributions.sort(key=lambda x: x[1], reverse=True)
        cat_score = 0.0
        for i, (player, ppg) in enumerate(contributions):
            # Diminishing returns: 2nd player adds 40% value, 3rd adds 20%
            multiplier = [1.0, 0.4, 0.2, 0.1][min(i, 3)]
            cat_score += ppg * multiplier
        category_scores[cat] = cat_score
        total_score += cat_score

    return total_score, category_scores


def predict_buzz(question_category, question_subcategory=""):
    """Given a category, return ranked list of who's most likely to get it."""
    results = []
    for player in PLAYER_DATA:
        cat_ppg = compute_weighted_category_ppg(player, min_difficulty=2.0)
        cat_key = None
        for key, label in CATEGORY_LABELS.items():
            if question_category.lower() in label.lower() or question_category.lower() == key:
                cat_key = key
                break
        if cat_key:
            results.append((player, cat_ppg.get(cat_key, 0)))
    results.sort(key=lambda x: x[1], reverse=True)
    return results


# ============================================================
# STREAMLIT APP
# ============================================================

st.title("GT Quizbowl - ACF Nationals Team Optimizer")
st.markdown("*Data: 2022-2026 seasons | Weighting: quadratic (difficulty\u00b2) | Includes 2026 ACF Nationals*")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Player Profiles", "Team Optimizer", "Compare Teams", "Who Gets It?", "Add Stats"])

# --- TAB 1: Player Profiles ---
with tab1:
    st.header("Player Category Profiles")

    min_diff = st.select_slider(
        "Minimum tournament difficulty to include",
        options=[0.0, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0],
        value=2.0,
        format_func=lambda x: f"{x} dot"
    )

    # Build comparison dataframe
    players = [p for p in PLAYER_DATA if PLAYER_DATA[p]]
    cat_data = []
    for player in players:
        cat_ppg = compute_weighted_category_ppg(player, min_difficulty=min_diff)
        sf = compute_speed_factor(player, min_difficulty=min_diff)
        avg_r = get_player_avg_rank(player, min_difficulty=min_diff)
        row = {"Player": player, "Total PPG": round(sum(cat_ppg.values()) * sf, 2),
               "Avg Rank": round(avg_r, 1) if avg_r else "—",
               "Speed": f"{sf:.2f}x"}
        for cat, label in CATEGORY_LABELS.items():
            row[label] = round(cat_ppg[cat], 2)
        cat_data.append(row)

    df = pd.DataFrame(cat_data).sort_values("Total PPG", ascending=False)

    # Heatmap
    fig = go.Figure()
    cat_cols = list(CATEGORY_LABELS.values())
    z_data = df[cat_cols].values
    fig.add_trace(go.Heatmap(
        z=z_data,
        x=cat_cols,
        y=df["Player"].tolist(),
        colorscale="YlOrRd",
        text=np.round(z_data, 1),
        texttemplate="%{text}",
        textfont={"size": 11},
    ))
    fig.update_layout(height=600, title="Category PPG Heatmap (difficulty-weighted)")
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Individual player drill-down
    st.subheader("Individual Player Detail")
    selected_player = st.selectbox("Select player", players)
    player_entries = PLAYER_DATA[selected_player]
    if player_entries:
        detail_data = []
        for entry in player_entries:
            row = {"Tournament": entry["tournament"], "Difficulty": entry["difficulty"], "PPG": entry["ppg"]}
            for cat, label in CATEGORY_LABELS.items():
                row[label] = entry["cats"].get(cat, 0)
            detail_data.append(row)
        detail_df = pd.DataFrame(detail_data)
        st.dataframe(detail_df, use_container_width=True, hide_index=True)

        # Radar chart
        cat_ppg = compute_weighted_category_ppg(selected_player, min_difficulty=min_diff)
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[cat_ppg[cat] for cat in CATEGORY_LABELS],
            theta=list(CATEGORY_LABELS.values()),
            fill='toself',
            name=selected_player
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 30])),
                               title=f"{selected_player} - Category Radar")
        st.plotly_chart(fig_radar, use_container_width=True)


# --- TAB 2: Team Optimizer ---
with tab2:
    st.header("Optimal Team Construction")

    min_diff_opt = st.select_slider(
        "Min difficulty for optimization",
        options=[0.0, 1.0, 1.5, 2.0, 2.5, 3.0],
        value=2.0,
        key="opt_diff",
        format_func=lambda x: f"{x} dot"
    )

    available_players = [p for p in PLAYER_DATA if PLAYER_DATA[p]]
    selected_pool = st.multiselect(
        "Player pool (select 12+ for 3 teams)",
        available_players,
        default=available_players
    )

    if st.button("Generate Optimal Teams"):
        if len(selected_pool) < 4:
            st.error("Need at least 4 players")
        else:
            # Greedy optimization: pick best team A, then B from remainder, then D
            remaining = list(selected_pool)
            teams = {}

            for team_name in ["A", "B", "D"]:
                if len(remaining) < 4:
                    break
                best_score = -1
                best_team = None
                best_cats = None

                # Try all combinations of 4 from remaining
                for combo in combinations(remaining, 4):
                    score, cat_scores = compute_team_score(list(combo), min_diff_opt)
                    # Penalty for uncovered categories
                    penalty = sum(10 for cat, s in cat_scores.items() if s < 1.0 and NATS_DISTRIBUTION.get(cat, 0) > 0)
                    adjusted_score = score - penalty
                    if adjusted_score > best_score:
                        best_score = adjusted_score
                        best_team = list(combo)
                        best_cats = cat_scores

                if best_team:
                    teams[team_name] = {"players": best_team, "score": best_score, "cats": best_cats}
                    for p in best_team:
                        remaining.remove(p)

            # Display results
            for team_name, team_info in teams.items():
                st.subheader(f"Team {team_name} — Score: {team_info['score']:.1f}")
                cols = st.columns(4)
                for i, player in enumerate(team_info["players"]):
                    with cols[i]:
                        cat_ppg = compute_weighted_category_ppg(player, min_diff_opt)
                        top_cat = max(cat_ppg, key=cat_ppg.get)
                        st.metric(player, f"{sum(cat_ppg.values()):.1f} PPG",
                                  delta=f"{CATEGORY_LABELS[top_cat]}: {cat_ppg[top_cat]:.1f}")

                # Category coverage bar
                cat_df = pd.DataFrame([
                    {"Category": CATEGORY_LABELS[cat], "Score": score, "Tossups/Round": NATS_DISTRIBUTION.get(cat, 0)}
                    for cat, score in team_info["cats"].items()
                ])
                fig_bar = px.bar(cat_df, x="Category", y="Score", color="Score",
                                 color_continuous_scale="RdYlGn", title=f"Team {team_name} Category Strength")
                st.plotly_chart(fig_bar, use_container_width=True)

            if remaining:
                st.subheader(f"Remaining (Tentative 4th): {', '.join(remaining)}")


# --- TAB 3: Compare Teams ---
with tab3:
    st.header("Custom Team Comparison")
    available = [p for p in PLAYER_DATA if PLAYER_DATA[p]]

    col1, col2, col3 = st.columns(3)
    with col1:
        team_a = st.multiselect("Team A", available, key="cmp_a",
                                default=["Kevin Wang", "Tianyu Xu", "Graham Cope", "S.A. Shenoy"][:min(4, len(available))])
    with col2:
        team_b = st.multiselect("Team B", available, key="cmp_b",
                                default=["Alex Thomas", "Emerson Patmore", "Pranav Jothi", "Arunn Sankar"][:min(4, len(available))])
    with col3:
        team_d = st.multiselect("Team D", available, key="cmp_d",
                                default=["Matthew Sumanen", "Arhith Dharanendra", "Rohan Dalal", "Zach Tseng"][:min(4, len(available))])

    if team_a or team_b or team_d:
        comparison_data = []
        for name, team in [("A", team_a), ("B", team_b), ("D", team_d)]:
            if team:
                score, cat_scores = compute_team_score(team, min_difficulty=2.0)
                row = {"Team": name, "Total Score": round(score, 1)}
                for cat, label in CATEGORY_LABELS.items():
                    row[label] = round(cat_scores.get(cat, 0), 2)
                comparison_data.append(row)

        if comparison_data:
            comp_df = pd.DataFrame(comparison_data)
            st.dataframe(comp_df, use_container_width=True, hide_index=True)

            # Radar comparison
            fig_cmp = go.Figure()
            colors = ["red", "blue", "green"]
            for i, row in comp_df.iterrows():
                fig_cmp.add_trace(go.Scatterpolar(
                    r=[row[label] for label in CATEGORY_LABELS.values()],
                    theta=list(CATEGORY_LABELS.values()),
                    fill='toself',
                    name=f"Team {row['Team']}",
                    line_color=colors[i % 3]
                ))
            fig_cmp.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 25])),
                                  title="Team Category Comparison")
            st.plotly_chart(fig_cmp, use_container_width=True)


# --- Keyword-based question classifier ---
SUBCAT_KEYWORDS = {
    "lit": {
        "American Lit": ["american", "fitzgerald", "hemingway", "twain", "faulkner", "poe", "melville", "hawthorne",
                         "steinbeck", "vonnegut", "morrison", "gatsby", "moby dick", "catcher"],
        "British Lit": ["british", "english", "shakespeare", "dickens", "austen", "chaucer", "milton", "byron",
                        "keats", "shelley", "woolf", "orwell", "hardy", "bronte"],
        "European Lit": ["european", "french", "russian", "german", "dostoevsky", "tolstoy", "kafka", "proust",
                         "flaubert", "cervantes", "dante", "goethe", "hugo", "camus", "sartre"],
        "World Lit": ["japanese", "chinese", "latin american", "african", "borges", "marquez", "rushdie",
                      "murakami", "achebe", "garcia marquez"],
        "Poetry": ["poem", "poet", "verse", "stanza", "sonnet", "ode", "elegy", "haiku"],
        "Drama": ["play", "drama", "tragedy", "comedy", "act", "scene", "playwright", "theater"],
    },
    "hist": {
        "American History": ["american", "united states", "colonial", "revolution", "civil war", "president",
                            "congress", "constitution", "reconstruction", "new deal", "cold war"],
        "European History": ["european", "french revolution", "napoleon", "world war", "renaissance", "reformation",
                            "habsburg", "ottoman", "medieval", "crusade", "roman empire"],
        "British History": ["british", "england", "parliament", "monarchy", "tudor", "victorian", "magna carta"],
        "Ancient History": ["ancient", "greek", "roman", "egypt", "mesopotamia", "persian", "byzantine", "classical"],
        "World History": ["chinese", "japanese", "indian", "african", "colonial", "mongol", "islamic"],
    },
    "sci": {
        "Physics": ["physics", "quantum", "relativity", "electromagnetic", "force", "energy", "momentum", "wave",
                    "particle", "electron", "photon", "thermodynamic", "entropy", "magnetic", "electric"],
        "Biology": ["biology", "cell", "dna", "rna", "protein", "gene", "evolution", "species", "organism",
                    "enzyme", "mitosis", "ecology", "photosynthesis", "membrane", "amino acid"],
        "Chemistry": ["chemistry", "element", "compound", "reaction", "bond", "acid", "base", "organic",
                     "molecule", "catalyst", "oxidation", "solution", "periodic", "ion", "isotope"],
        "Math": ["math", "theorem", "equation", "integral", "derivative", "topology", "algebra", "geometry",
                "number theory", "prime", "function", "matrix", "vector", "proof"],
        "Computer Science": ["algorithm", "computer", "programming", "turing", "complexity", "data structure"],
        "Earth Science": ["geology", "earthquake", "volcano", "plate tectonics", "mineral", "fossil", "climate"],
        "Astronomy": ["astronomy", "planet", "star", "galaxy", "nebula", "black hole", "orbit", "solar"],
    },
    "arts": {
        "Painting": ["painting", "painter", "canvas", "oil", "fresco", "portrait", "landscape", "impressionist",
                    "cubist", "surrealist", "renaissance", "baroque", "monet", "picasso", "van gogh", "rembrandt"],
        "Classical Music": ["symphony", "concerto", "sonata", "opera", "composer", "orchestra", "movement",
                           "beethoven", "mozart", "bach", "tchaikovsky", "brahms", "chopin", "vivaldi", "mahler"],
        "Sculpture": ["sculpture", "sculptor", "statue", "bronze", "marble", "relief", "rodin", "bernini"],
        "Architecture": ["architecture", "architect", "building", "cathedral", "dome", "gothic", "baroque"],
        "Film": ["film", "director", "movie", "cinema", "scene", "shot", "screenplay"],
        "Jazz/Pop": ["jazz", "blues", "rock", "album", "song", "band", "musician"],
    },
    "beliefs": {
        "Christianity": ["christian", "bible", "jesus", "church", "gospel", "apostle", "protestant", "catholic",
                        "saint", "pope", "trinity", "baptism", "reformation"],
        "Islam": ["islam", "muslim", "quran", "muhammad", "mosque", "sunni", "shia", "hadith", "allah"],
        "Judaism": ["jewish", "torah", "talmud", "rabbi", "synagogue", "moses", "hebrew"],
        "Hinduism": ["hindu", "vedas", "brahma", "vishnu", "shiva", "karma", "dharma", "upanishad"],
        "Buddhism": ["buddhist", "buddha", "nirvana", "dharma", "zen", "enlightenment", "sutra"],
        "Greek Myth": ["greek myth", "zeus", "athena", "apollo", "heracles", "odysseus", "trojan", "olympus",
                      "titan", "prometheus", "hercules", "poseidon", "hades"],
        "Norse Myth": ["norse", "odin", "thor", "loki", "valhalla", "ragnarok", "yggdrasil"],
        "Other Myth": ["myth", "legend", "folklore", "deity", "god", "goddess", "creation myth"],
    },
    "thought": {
        "Ancient Phil": ["plato", "aristotle", "socrates", "stoic", "epicurean", "republic", "virtue"],
        "Modern Phil": ["kant", "hegel", "nietzsche", "descartes", "hume", "locke", "spinoza", "leibniz"],
        "Contemporary": ["wittgenstein", "heidegger", "sartre", "foucault", "derrida", "rawls", "quine"],
        "Ethics": ["ethics", "moral", "utilitarian", "deontological", "virtue ethics", "categorical imperative"],
        "Epistemology": ["knowledge", "epistemology", "empiricism", "rationalism", "skepticism", "a priori"],
    },
    "other": {
        "Economics": ["economics", "gdp", "inflation", "market", "keynes", "supply", "demand", "trade", "fiscal"],
        "Psychology": ["psychology", "freud", "cognitive", "behavioral", "experiment", "pavlov", "skinner"],
        "Sociology": ["sociology", "society", "weber", "durkheim", "social", "institution", "class"],
        "Geography": ["geography", "river", "mountain", "continent", "ocean", "island", "capital", "border",
                     "country", "city", "lake", "desert", "peninsula"],
        "Political Science": ["political", "government", "democracy", "election", "party", "legislature"],
        "Anthropology": ["anthropology", "culture", "tribe", "ritual", "kinship", "ethnography"],
        "Linguistics": ["language", "linguistic", "phoneme", "syntax", "morpheme", "grammar", "dialect"],
    },
}


def classify_question(text):
    """Classify a question into category and subcategory using keyword matching."""
    text_lower = text.lower()
    scores = {}  # (cat_key, subcat) -> score

    for cat_key, subcats in SUBCAT_KEYWORDS.items():
        for subcat_name, keywords in subcats.items():
            score = 0
            for kw in keywords:
                if kw in text_lower:
                    score += len(kw)  # longer keyword matches = higher confidence
            if score > 0:
                scores[(cat_key, subcat_name)] = score

    if not scores:
        return None, ""

    best = max(scores, key=scores.get)
    return best[0], best[1]


# --- TAB 4: Who Gets It? ---
with tab4:
    st.header("Question Predictor")
    st.markdown("Type or paste a question and it'll classify the category and predict who buzzes.")

    question_text = st.text_area("Paste a question here",
                                  placeholder="This American author's 1925 novel features the character Jay Gatsby...",
                                  height=150)

    col_mode1, col_mode2 = st.columns(2)
    with col_mode1:
        auto_classify = st.checkbox("Auto-classify from text", value=True)
    with col_mode2:
        manual_cat = st.selectbox("Or select category manually",
                                  ["(auto)"] + list(CATEGORY_LABELS.values()))

    team_filter = st.multiselect(
        "Filter to specific players (leave empty for all)",
        [p for p in PLAYER_DATA if PLAYER_DATA[p]],
        key="who_gets_filter"
    )

    if st.button("Analyze Question", type="primary"):
        cat_key = None
        subcategory = ""

        if auto_classify and manual_cat == "(auto)" and question_text.strip():
            cat_key, subcategory = classify_question(question_text)
            if cat_key:
                st.success(f"**Detected:** {CATEGORY_LABELS[cat_key]} → {subcategory}")
            else:
                st.warning("Couldn't classify — try selecting category manually.")
        elif manual_cat != "(auto)":
            for key, label in CATEGORY_LABELS.items():
                if label == manual_cat:
                    cat_key = key
                    break

        if cat_key:
            pool = team_filter if team_filter else [p for p in PLAYER_DATA if PLAYER_DATA[p]]
            results = []
            for player in pool:
                cat_ppg = compute_weighted_category_ppg(player, min_difficulty=2.0)
                ppg_in_cat = cat_ppg.get(cat_key, 0)
                sf = compute_speed_factor(player, min_difficulty=2.0)
                tossups_per_round = NATS_DISTRIBUTION.get(cat_key, 1)
                max_possible = tossups_per_round * 15
                adj_ppg = ppg_in_cat * sf
                prob = min(max(adj_ppg / max_possible, 0), 1.0) if max_possible > 0 else 0
                results.append({
                    "Player": player,
                    "Cat PPG": round(ppg_in_cat, 2),
                    "Speed": f"{sf:.2f}x",
                    "Adj PPG": round(adj_ppg, 2),
                    "Buzz Prob": f"{prob*100:.0f}%",
                })

            results.sort(key=lambda x: x["Adj PPG"], reverse=True)
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True, hide_index=True)

            # Bar chart
            fig_who = px.bar(
                results_df, x="Player", y="Adj PPG",
                title=f"Who buzzes on {CATEGORY_LABELS.get(cat_key, '')}?{' (' + subcategory + ')' if subcategory else ''}",
                color="Adj PPG", color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_who, use_container_width=True)


# --- TAB 5: Add Stats ---
with tab5:
    st.header("Paste New Stats")
    st.markdown("""
    Paste buzzpoints data from a tournament page to add new stats for a player.
    Format the data as category lines like:
    ```
    Literature - American: 5 buzzes, 3 correct, 2 incorrect
    Science - Physics: 10 buzzes, 7 correct, 1 incorrect
    ```
    Or paste raw text from a buzzpoints page and it will be parsed.
    """)

    paste_player = st.selectbox("Player", list(PLAYER_DATA.keys()), key="paste_player")
    paste_tournament = st.text_input("Tournament name", placeholder="e.g., 2026 ACF Nationals")
    paste_difficulty = st.select_slider(
        "Tournament difficulty",
        options=[1.0, 1.5, 2.0, 2.5, 3.0, 4.0],
        value=3.0,
        key="paste_diff",
        format_func=lambda x: f"{x} dot"
    )
    paste_games = st.number_input("Games played", min_value=1, max_value=30, value=18)
    paste_data = st.text_area("Paste buzzpoints data here", height=300,
                              placeholder="Paste from buzzpoints page...")

    if st.button("Parse & Preview"):
        if paste_data.strip():
            # Parse the pasted data
            import re
            lines = paste_data.strip().split('\n')
            parsed_cats = {"lit": 0, "hist": 0, "sci": 0, "arts": 0, "beliefs": 0, "thought": 0, "other": 0}

            cat_mapping = {
                "literature": "lit", "lit": "lit",
                "history": "hist", "hist": "hist",
                "science": "sci", "sci": "sci", "physics": "sci", "chemistry": "sci", "biology": "sci",
                "fine arts": "arts", "arts": "arts", "painting": "arts", "classical music": "arts", "sculpture": "arts",
                "religion": "beliefs", "mythology": "beliefs",
                "philosophy": "thought",
                "social science": "other", "geography": "other", "current events": "other", "other": "other",
            }

            total_points = 0
            for line in lines:
                line_lower = line.lower().strip()
                if not line_lower:
                    continue
                # Try to extract category and buzz count
                for cat_name, cat_key in cat_mapping.items():
                    if cat_name in line_lower:
                        # Extract numbers
                        numbers = re.findall(r'\d+', line)
                        if numbers:
                            buzzes = int(numbers[0])
                            correct = int(numbers[1]) if len(numbers) > 1 else buzzes
                            incorrect = int(numbers[2]) if len(numbers) > 2 else 0
                            points = correct * 10 - incorrect * 5
                            parsed_cats[cat_key] += points / paste_games
                            total_points += points
                        break

            st.subheader("Parsed Category PPG")
            parsed_df = pd.DataFrame([{
                "Category": CATEGORY_LABELS[k],
                "PPG": round(v, 2)
            } for k, v in parsed_cats.items()])
            st.dataframe(parsed_df, use_container_width=True, hide_index=True)
            st.metric("Total PPG", f"{total_points/paste_games:.1f}")

            st.subheader("Entry to add (copy this into PLAYER_DATA)")
            entry_str = f'{{"tournament": "{paste_tournament}", "difficulty": {paste_difficulty}, "ppg": {total_points/paste_games:.1f},\n'
            entry_str += f' "cats": {{"lit": {parsed_cats["lit"]:.2f}, "hist": {parsed_cats["hist"]:.2f}, "sci": {parsed_cats["sci"]:.2f}, "arts": {parsed_cats["arts"]:.2f}, "beliefs": {parsed_cats["beliefs"]:.2f}, "thought": {parsed_cats["thought"]:.2f}, "other": {parsed_cats["other"]:.2f}}}}}'
            st.code(entry_str, language="python")
