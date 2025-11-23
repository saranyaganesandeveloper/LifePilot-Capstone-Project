import streamlit as st
from orchestrator import Orchestrator

st.set_page_config(page_title="LifePilot", layout="wide")

orc = Orchestrator()

st.title("🧭 LifePilot – AI Multi-Agent Assistant")

# --- INPUT AREA ---
query = st.text_input("Ask LifePilot...")

if st.button("Run"):
    with st.spinner("Processing..."):
        result = orc.handle(query)
    st.session_state["result"] = result
    st.session_state["query"] = query.lower().strip()

# --- CREATE TABS ---
meal_tab, shopping_tab, travel_tab, raw_tab = st.tabs(
    ["🍽 Meal Output", "🛒 Shopping Output", "✈ Travel Output", "🐞 Raw Debug"]
)

# --- TAB 1: MEAL ---
with meal_tab:
    st.header("🍽 Meal Planning Result")
    if "meal" in st.session_state.get("query", "") and "shop" not in st.session_state.get("query", ""):
        st.write(st.session_state.get("result", ""))
    else:
        st.info("No meal plan requested.")

# --- TAB 2: SHOPPING ---
with shopping_tab:
    st.header("🛒 Shopping List Result")
    q = st.session_state.get("query", "")
    if "shop" in q or "shopping" in q or "grocery" in q:
        st.write(st.session_state.get("result", ""))
    else:
        st.info("No shopping list requested.")

# --- TAB 3: TRAVEL ---
with travel_tab:
    st.header("✈ Travel Itinerary")
    if "travel" in st.session_state.get("query", "") or "trip" in st.session_state.get("query", ""):
        st.write(st.session_state.get("result", ""))
    else:
        st.info("No travel plan requested.")

# --- TAB 4: RAW DEBUG ---
with raw_tab:
    st.header("🐞 Raw Output Debug")
    st.code(st.session_state.get("result", ""))
