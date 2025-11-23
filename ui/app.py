import streamlit as st
import re
import html
import json
import pandas as pd
from orchestrator import Orchestrator

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="LifePilot",
    page_icon="✨",
    layout="wide"
)

st.title("✨ LifePilot — Unified Weekly Planner")


# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
st.sidebar.header("⚙️ Options")

run_meal = st.sidebar.checkbox("🍽 Run Meal Plan", value=True)
run_shopping = st.sidebar.checkbox("🛒 Run Shopping List", value=True)
run_travel = st.sidebar.checkbox("✈ Run Travel Itinerary", value=True)

st.sidebar.markdown("---")
show_raw = st.sidebar.checkbox("🧪 Show Raw JSON Logs", value=False)


# ---------------------------------------------------------
# COLOR + ICON HELPERS
# ---------------------------------------------------------
def color(label):
    if label.lower() == "morning": return "#fff6cc"
    if label.lower() == "afternoon": return "#dfeaff"
    if label.lower() == "evening": return "#ffd9d9"
    return "#f2f2f2"

def icon(label):
    if label.lower() == "morning": return "🌅"
    if label.lower() == "afternoon": return "🌞"
    if label.lower() == "evening": return "🌙"
    return "•"


# ---------------------------------------------------------
# TIMELINE RENDERER — JSON BASED
# ---------------------------------------------------------
def render_timeline_json(data):
    for day_key in ["day1", "day2"]:
        if day_key not in data:
            continue

        day = data[day_key]
        day_name = "Day 1" if day_key == "day1" else "Day 2"

        # Day header
        st.markdown(
            f"""
            <div style='padding:0.8rem 1rem; background:#eef2ff;
            border-radius:0.6rem; margin-top:1rem;'>
                <h3 style='margin:0;'>🗓️ {day_name}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Segments
        for seg in ["morning", "afternoon", "evening"]:
            text_val = day.get(seg, "")
            col = color(seg)
            ic = icon(seg)

            st.markdown(
                f"""
                <div style='display:flex; margin:1rem 0;'>

                    <div style='padding-top:6px; margin-right:1rem;'>
                        <div style='width:16px; height:16px; background:#4b6fff;
                        border-radius:50%;'></div>
                        <div style='width:3px; height:60px; background:#4b6fff;
                        margin-left:6px;'></div>
                    </div>

                    <div style='background:{col}; padding:0.8rem 1rem;
                    border-radius:0.6rem; flex:1;'>
                        <strong>{ic} {seg.capitalize()}</strong><br>
                        {text_val}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


# ---------------------------------------------------------
# MAIN INPUT
# ---------------------------------------------------------
query = st.text_area(
    "💬 What do you want LifePilot to do?",
    placeholder="Example: Plan my next week with vegetarian meals, shopping list, and a 2-day trip to Dallas."
)

orc = Orchestrator()


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------
if st.button("Run LifePilot 🚀"):

    if not query.strip():
        st.warning("Please enter a request.")
        st.stop()

    # Call orchestrator
    results, raw_logs = orc.handle(query, run_meal, run_shopping, run_travel, return_logs=True)

    meal = results.get("meal", "")
    shopping = results.get("shopping", [])
    travel = results.get("travel", {})

    # -----------------------------------------------------
    # TABS
    # -----------------------------------------------------
    tabs = st.tabs(["🍽 Meal Plan", "🛒 Shopping List", "✈ Travel Itinerary"])

    # MEAL TAB ------------------------------------------------
    with tabs[0]:
        st.subheader("🍽 Weekly Meal Plan")
        if run_meal:
            st.markdown(f"```\n{meal}\n```")
        else:
            st.info("Meal Plan not requested.")

    # SHOPPING TAB -------------------------------------------
    with tabs[1]:
        st.subheader("🛒 Shopping List")
        if run_shopping:
            if isinstance(shopping, list):
                df = pd.DataFrame(shopping)
                st.dataframe(df, use_container_width=True)
            else:
                st.write(shopping)
        else:
            st.info("Shopping List not requested.")

    # TRAVEL TAB ---------------------------------------------
    with tabs[2]:
        st.subheader("✈ Travel Itinerary")
        st.markdown(f"```\n{travel}\n```")


    # RAW JSON LOGS ------------------------------------------
    if show_raw:
        st.sidebar.markdown("### 🔍 Raw Logs")
        st.sidebar.json(raw_logs)
