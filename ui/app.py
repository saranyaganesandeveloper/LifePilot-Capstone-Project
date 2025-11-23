# ui/app.py

import io
import streamlit as st
import pandas as pd

from orchestrator import Orchestrator

# PDF generator
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="LifePilot",
    page_icon="✨",
    layout="wide"
)

st.title("✨ LifePilot — Weekly Planner")
st.write("Plan meals, shopping, and travel using intelligent multi-agent AI.")


# ---------------------------------------------------------
# INITIALIZE ORCHESTRATOR IN SESSION
# ---------------------------------------------------------
if "orc" not in st.session_state:
    st.session_state["orc"] = Orchestrator()

orc: Orchestrator = st.session_state["orc"]


# ---------------------------------------------------------
# PDF GENERATORS
# ---------------------------------------------------------
def build_pdf(text: str) -> bytes:
    """Create a PDF from plain text using ReportLab."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    story = [Paragraph(text.replace("\n", "<br/>"), styles["Normal"])]
    doc.build(story)

    buffer.seek(0)
    return buffer.read()


def build_shopping_pdf(df: pd.DataFrame) -> bytes:
    """Create a PDF from a shopping list DataFrame."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    lines = []
    for _, row in df.iterrows():
        line = f"{row['category']}: {row['item']} — {row['quantity']} {row['notes']}".strip()
        lines.append(line)

    text = "<br/>".join(lines) if lines else "No items."
    story = [Paragraph(text, styles["Normal"])]
    doc.build(story)

    buffer.seek(0)
    return buffer.read()


# ---------------------------------------------------------
# AGENT SELECTION
# ---------------------------------------------------------
st.markdown("### ⚙️ Choose what you want LifePilot to generate:")

agent_opts = st.multiselect(
    "Select agents:",
    ["Meal Plan", "Shopping List", "Travel Itinerary"],
    default=["Meal Plan", "Shopping List", "Travel Itinerary"]
)

run_meal = "Meal Plan" in agent_opts
run_shopping = "Shopping List" in agent_opts
run_travel = "Travel Itinerary" in agent_opts


# ---------------------------------------------------------
# VIEW CURRENT PREFERENCES (MEMORY)
# ---------------------------------------------------------
with st.expander("🔍 View Current Preferences (Memory Debug)"):
    try:
        prefs = orc.build_preferences()
        st.json(prefs)
    except Exception as e:
        st.error(f"Failed to load preferences: {e}")


# ---------------------------------------------------------
# USER INPUT
# ---------------------------------------------------------
query = st.text_area(
    "💬 Ask LifePilot:",
    placeholder="e.g., Plan my week with vegetarian meals, shopping list, and a Dallas trip."
)


# ---------------------------------------------------------
# RUN BUTTON
# ---------------------------------------------------------
if st.button("Run LifePilot 🚀"):

    if not query.strip():
        st.warning("Please enter a request.")
        st.stop()

    # CALL ORCHESTRATOR
    results, logs = orc.handle(
        query,
        run_meal=run_meal,
        run_shopping=run_shopping,
        run_travel=run_travel,
        return_logs=True
    )

    # STORE RESULTS IN SESSION (PREVENT REFRESH CLEAR)
    st.session_state["meal"] = results.get("meal")
    st.session_state["shopping"] = results.get("shopping")
    st.session_state["travel"] = results.get("travel")
    st.session_state["logs"] = logs

    # PRE-BUILD PDFS (SO DOWNLOAD DOES NOT TRIGGER RERUN)
    st.session_state["meal_pdf"] = (
        build_pdf(st.session_state["meal"]) if st.session_state["meal"] else None
    )

    if st.session_state.get("shopping"):
        try:
            df = pd.DataFrame(st.session_state["shopping"])
            st.session_state["shopping_pdf"] = build_shopping_pdf(df)
        except:
            st.session_state["shopping_pdf"] = None
    else:
        st.session_state["shopping_pdf"] = None

    st.session_state["travel_pdf"] = (
        build_pdf(st.session_state["travel"]) if st.session_state["travel"] else None
    )

    st.session_state["ready"] = True


# ---------------------------------------------------------
# SHOW RESULTS IF READY
# ---------------------------------------------------------
if st.session_state.get("ready"):

    tabs = st.tabs(["🍽 Meal Plan", "🛒 Shopping List", "✈ Travel Itinerary", "📜 Logs"])

    # ---------------------- MEAL TAB ----------------------
    with tabs[0]:
        st.subheader("🍽 Weekly Meal Plan")

        meal = st.session_state.get("meal")
        if meal:
            st.markdown(f"```text\n{meal}\n```")

            if st.session_state.get("meal_pdf"):
                st.download_button(
                    "⬇️ Download Meal Plan as PDF",
                    st.session_state["meal_pdf"],
                    "meal_plan.pdf",
                    "application/pdf"
                )
        else:
            st.info("No meal plan generated.")

    # ---------------------- SHOPPING TAB ----------------------
    with tabs[1]:
        st.subheader("🛒 Shopping List (max 30 items)")

        shopping = st.session_state.get("shopping")
        if shopping:
            try:
                df = pd.DataFrame(shopping)
                st.dataframe(df, width="stretch")
            except:
                st.write(shopping)

            if st.session_state.get("shopping_pdf"):
                st.download_button(
                    "⬇️ Download Shopping List as PDF",
                    st.session_state["shopping_pdf"],
                    "shopping_list.pdf",
                    "application/pdf"
                )
        else:
            st.info("No shopping list generated.")

    # ---------------------- TRAVEL TAB ----------------------
    with tabs[2]:
        st.subheader("✈ Travel Itinerary (Plain Text with Emojis)")

        travel = st.session_state.get("travel")
        if travel:
            st.markdown(f"```text\n{travel}\n```")

            if st.session_state.get("travel_pdf"):
                st.download_button(
                    "⬇️ Download Travel Itinerary PDF",
                    st.session_state["travel_pdf"],
                    "travel_itinerary.pdf",
                    "application/pdf"
                )
        else:
            st.info("No travel itinerary generated.")

    # ---------------------- LOGS TAB ----------------------
    with tabs[3]:
        st.subheader("📜 Raw JSON Logs")
        st.json(st.session_state.get("logs"))
