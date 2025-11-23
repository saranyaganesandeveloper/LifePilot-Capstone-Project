import streamlit as st
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

st.title("✨ LifePilot — Weekly Life Planner")
st.write("Plan meals, shopping, and travel in one place with memory-aware AI.")


# ---------------------------------------------------------
# ORCHESTRATOR (PERSIST IN SESSION)
# ---------------------------------------------------------
if "orc" not in st.session_state:
    st.session_state["orc"] = Orchestrator()

orc: Orchestrator = st.session_state["orc"]


# ---------------------------------------------------------
# AGENT SELECTION
# ---------------------------------------------------------
st.markdown("### ⚙️ What do you want LifePilot to generate?")

agent_options = st.multiselect(
    "Select one or more:",
    ["Meal Plan", "Shopping List", "Travel Itinerary"],
    default=["Meal Plan", "Shopping List", "Travel Itinerary"]
)

run_meal = "Meal Plan" in agent_options
run_shopping = "Shopping List" in agent_options
run_travel = "Travel Itinerary" in agent_options


# ---------------------------------------------------------
# USER QUERY
# ---------------------------------------------------------
query = st.text_area(
    "💬 Ask LifePilot:",
    placeholder="Example: Plan my next week with vegetarian meals, a shopping list, and a 2-day trip to Dallas."
)


# ---------------------------------------------------------
# RUN BUTTON
# ---------------------------------------------------------
if st.button("Run LifePilot 🚀"):
    if not query.strip():
        st.warning("Please enter a request.")
        st.stop()

    # Call orchestrator
    results, raw_logs = orc.handle(
        query,
        run_meal=run_meal,
        run_shopping=run_shopping,
        run_travel=run_travel,
        return_logs=True
    )

    meal = results.get("meal", "")
    shopping = results.get("shopping", [])
    travel = results.get("travel", "")

    # -----------------------------------------------------
    # TABS: Meal | Shopping | Travel | Logs
    # -----------------------------------------------------
    tabs = st.tabs(["🍽 Meal Plan", "🛒 Shopping List", "✈ Travel Itinerary", "📜 Logs"])

    # MEAL TAB ------------------------------------------------
    with tabs[0]:
        st.subheader("🍽 Weekly Meal Plan")
        if run_meal:
            if meal:
                st.markdown(f"```text\n{meal}\n```")
            else:
                st.info("No meal plan was generated.")
        else:
            st.info("Meal Plan agent is disabled. Enable it above to generate meals.")

    # SHOPPING TAB -------------------------------------------
    with tabs[1]:
        st.subheader("🛒 Shopping List (max 30 items)")
        if run_shopping:
            if isinstance(shopping, list) and shopping:
                try:
                    df = pd.DataFrame(shopping)
                    st.dataframe(df, use_container_width=True)
                except Exception:
                    st.write(shopping)
            else:
                st.info("No shopping list was generated.")
        else:
            st.info("Shopping List agent is disabled. Enable it above to generate a list.")

    # TRAVEL TAB ---------------------------------------------
    with tabs[2]:
        st.subheader("✈ Travel Itinerary (Plain Text with Emojis)")
        if run_travel:
            if travel:
                st.markdown(f"```text\n{travel}\n```")
            else:
                st.info("No travel itinerary was generated.")
        else:
            st.info("Travel Itinerary agent is disabled. Enable it above to generate a trip plan.")

    # LOGS TAB -----------------------------------------------
    with tabs[3]:
        st.subheader("📜 Raw JSON Logs")
        st.json(raw_logs)
