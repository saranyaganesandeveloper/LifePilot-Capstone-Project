# ui/app.py

import io
import os
import base64
import json
import sys
from typing import Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
from orchestrator import Orchestrator

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="LifePilot",
    page_icon="✨",
    layout="wide",
)


# ---------------------------------------------------------
# SESSION-STATE INITIALIZATION
# ---------------------------------------------------------
if "orc" not in st.session_state:
    st.session_state["orc"] = Orchestrator()

if "ready" not in st.session_state:
    st.session_state["ready"] = False

orc: Orchestrator = st.session_state["orc"]


# ---------------------------------------------------------
# UTIL: LOAD LOGO
# ---------------------------------------------------------
def load_image_base64(path: str) -> str | None:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None


LOGO_PATH = os.path.join(BASE_DIR, "..", "docs", "lifepilot_logo.png")
logo_b64 = load_image_base64(LOGO_PATH)


# ---------------------------------------------------------
# GLOBAL STYLES – PURE WHITE LIGHT THEME
# ---------------------------------------------------------
st.markdown(
    """
<style>

/* ---------- Global layout ---------- */
.stApp {
    background: #f5f5f7 !important;
    color: #111827 !important;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1100px;
}

/* ---------- Header ---------- */
.lp-header {
    width: 100%;
    padding: 22px 26px;
    border-radius: 22px;
    background: linear-gradient(115deg, #4b6fff, #7b9dff, #fb7185);
    display: flex;
    align-items: center;
    gap: 20px;
    color: #ffffff;
    margin-bottom: 1.8rem;
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.35);
}

.lp-header-logo {
    width: 72px;
    height: 72px;
    border-radius: 24px;
    overflow: hidden;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.6);
    flex-shrink: 0;
}

.lp-header-logo img {
    width: 100%;
    height: 100%;
}

.lp-header-title {
    font-size: 30px;
    font-weight: 750;
    letter-spacing: 0.03em;
    margin-bottom: 4px;
}

.lp-header-sub {
    font-size: 13px;
    opacity: 0.98;
}

.lp-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 11px;
    margin-top: 8px;
    border-radius: 999px;
    border: 1px solid rgba(255, 255, 255, 0.35);
    background: rgba(15, 23, 42, 0.15);
    font-size: 11px;
}

/* ---------- Cards ---------- */
.lp-card {
    background: #ffffff;
    border-radius: 18px;
    padding: 18px 20px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
    margin-bottom: 18px;
}

.lp-section-title {
    font-weight: 600;
    font-size: 15px;
    color: #111827;
    display: flex;
    align-items: center;
    gap: 8px;
}

.lp-section-caption {
    font-size: 12px;
    color: #6b7280;
    margin-top: 4px;
}

/* ---------- Buttons ---------- */
div.stButton > button {
    border-radius: 999px !important;
    padding: 0.55rem 1.2rem !important;
    border: 1px solid #d1d5db !important;
    background: #ffffff !important;
    color: #111827 !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    box-shadow: 0 8px 18px rgba(148, 163, 184, 0.4);
}

div.stButton > button:hover {
    border-color: #4b6fff !important;
    background: linear-gradient(135deg, #eef2ff, #e0f2fe) !important;
    color: #1f2937 !important;
}

/* ---------- Text area (Streamlit v1.40+ DOM) ---------- */
div[data-testid="stTextArea"] textarea {
    background-color: #ffffff !important;
    color: #111827 !important;
    border-radius: 12px !important;
    border: 1px solid #d1d5db !important;
    padding: 10px 12px !important;
    opacity: 1 !important;
    font-size: 14px !important;
    min-height: 120px !important;
    box-shadow: inset 0 0 0 1px rgba(243, 244, 246, 0.9);
}

div[data-testid="stTextArea"] textarea::placeholder {
    color: #9ca3af !important;
}

/* ---------- Tabs ---------- */
div[data-baseweb="tab-list"] {
    gap: 6px;
}

button[role="tab"] {
    border-radius: 999px !important;
    padding: 6px 14px !important;
    font-size: 13px !important;
    border: 1px solid #e5e7eb !important;
    background: #f9fafb !important;
    color: #6b7280 !important;
}

button[role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #4b6fff, #7b9dff) !important;
    color: #f9fafb !important;
    border-color: transparent !important;
    box-shadow: 0 8px 20px rgba(129, 140, 248, 0.45);
}

/* ---------- Footer ---------- */
.lp-footer {
    text-align: center;
    padding: 26px 0 12px 0;
    color: #6b7280;
    margin-top: 2.2rem;
    font-size: 12px;
}

.lp-footer img {
    width: 64px;
    margin-bottom: 6px;
    border-radius: 14px;
    box-shadow: 0 10px 25px rgba(148, 163, 184, 0.7);
}

.lp-footer a {
    color: #2563eb;
    text-decoration: none;
    font-weight: 500;
}

.lp-footer a:hover {
    color: #fb7185;
}

.lp-dot {
    margin: 0 6px;
    opacity: 0.6;
}

</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# RESET FUNCTION
# ---------------------------------------------------------
def reset_everything():
    # Clear entire session state
    st.session_state.clear()

    # Reset the text box explicitly so Streamlit doesn't reuse previous widget state
    st.session_state["user_query"] = ""

    # Reload the page
    st.rerun()


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
header_html = f"""
<div class="lp-header">
  <div class="lp-header-logo">
    {"<img src='data:image/png;base64," + logo_b64 + "' />" if logo_b64 else ""}
  </div>
  <div style="flex:1; display:flex; flex-direction:column;">
    <div class="lp-header-title">✨ LifePilot</div>
    <div class="lp-header-sub">
      Your Intelligent Planner · Meals · Shopping · Travel
    </div>
    <div>
      <span class="lp-pill">Multi-Agent · Gemini · Vector Memory</span>
    </div>
  </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)


# ---------------------------------------------------------
# ASK LIFEPILOT (CARD)
# ---------------------------------------------------------
st.markdown(
    """
    <div class="lp-card">
        <div class="lp-section-title">💬 Ask LifePilot</div>
        <div class="lp-section-caption">
            Describe what you need. LifePilot can plan meals, shopping, travel,  
            and adapt to your preferences like vegetarian meals, kids-friendly itineraries,  
            budget requirements, health restrictions, and more.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# TEXT AREA BELOW
st.markdown("""
<style>
.lp-hand {
    position: absolute;
    margin-left: -28px;
    margin-top: 6px;
    font-size: 20px;
}
</style>
""", unsafe_allow_html=True)
st.markdown("<div class='lp-hand'>👉</div>", unsafe_allow_html=True)
query = st.text_area(
    label="Ask LifePilot",
    label_visibility="collapsed",
    height=140,
    key="user_query",  
    placeholder=(
        "Examples:\n"
        "• Plan my meals for 5 days (vegetarian).\n"
        "• Prepare a shopping list for South Indian cooking.\n"
        "• Plan a 1-day Austin trip with kid-friendly places.\n"
        "• Create a 3-day itinerary for New York with preferences.\n"
    ),
)


# BUTTON ROW (Run Left, Reset Right)
btn_left, btn_right = st.columns([1, 1])

with btn_left:
    run_clicked = st.button("🚀 Run LifePilot", use_container_width=True)

with btn_right:
    reset_btn = st.button(
        "🔥 Reset Everything",
        help="This clears preferences, memory, and current outputs.",
        use_container_width=True,
    )
    if reset_btn:
        reset_everything()


# ---------------------------------------------------------
# PDF HELPERS
# ---------------------------------------------------------
def build_pdf(text: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph(text.replace("\n", "<br/>"), styles["Normal"])]
    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def build_shopping_pdf(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    lines: list[str] = []
    for _, row in df.iterrows():
        lines.append(
            f"{row.get('category', '')}: {row.get('item', '')} — "
            f"{row.get('quantity', '')} {row.get('notes', '')}"
        )
    text = "<br/>".join(lines) if lines else "No items."
    story = [Paragraph(text, styles["Normal"])]
    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# ---------------------------------------------------------
# RUN ORCHESTRATOR
# ---------------------------------------------------------
if run_clicked:
    if not query.strip():
        st.warning("Please type a request before running LifePilot.")
    else:
        with st.spinner("✨ Orchestrating agents…"):
            results, logs = orc.handle(query, return_logs=True)

        st.session_state["meal"] = results.get("meal")
        st.session_state["shopping"] = results.get("shopping")
        st.session_state["travel"] = results.get("travel")
        st.session_state["logs"] = logs

        st.session_state["meal_pdf"] = (
            build_pdf(st.session_state["meal"]) if st.session_state.get("meal") else None
        )

        shopping_data: Any = st.session_state.get("shopping")
        if isinstance(shopping_data, list):
            try:
                st.session_state["shopping_pdf"] = build_shopping_pdf(
                    pd.DataFrame(shopping_data)
                )
            except Exception:
                st.session_state["shopping_pdf"] = None
        else:
            st.session_state["shopping_pdf"] = None

        st.session_state["travel_pdf"] = (
            build_pdf(st.session_state["travel"]) if st.session_state.get("travel") else None
        )

        st.session_state["ready"] = True


# ---------------------------------------------------------
# RESULTS – TABS
# ---------------------------------------------------------
if st.session_state.get("ready"):
    st.markdown(
        """
        <div class="lp-card">
            <div class="lp-section-title">📊 Planner Output</div>
            <div class="lp-section-caption">
                Switch between Meal Plan, Shopping List, Travel Itinerary, and raw JSON logs.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(
        [
            "🍽 Meal Plan",
            "🛒 Shopping List",
            "✈ Travel Itinerary",
            "📜 Logs",
        ]
    )

    # -------- Meal Tab --------
    with tabs[0]:
        st.markdown("#### 🍽 Meal Plan")
        meal = st.session_state.get("meal")
        if meal:
            st.markdown(f"```text\n{meal}\n```")
            if st.session_state.get("meal_pdf"):
                st.download_button(
                    "⬇️ Download Meal Plan PDF",
                    st.session_state["meal_pdf"],
                    "meal_plan.pdf",
                    "application/pdf",
                )
        else:
            st.info("No meal plan generated for this query.")

    # -------- Shopping Tab --------
    with tabs[1]:
        st.markdown("#### 🛒 Shopping List")
        shopping = st.session_state.get("shopping")
        if shopping:
            if isinstance(shopping, list):
                try:
                    st.dataframe(pd.DataFrame(shopping), use_container_width=True)
                except Exception:
                    st.write(shopping)

            if st.session_state.get("shopping_pdf"):
                st.download_button(
                    "⬇️ Download Shopping List PDF",
                    st.session_state["shopping_pdf"],
                    "shopping_list.pdf",
                    "application/pdf",
                )
        else:
            st.info("No shopping list generated.")

    # -------- Travel Tab --------
    with tabs[2]:
        st.markdown("#### ✈ Travel Itinerary")
        travel = st.session_state.get("travel")
        if travel:
            st.markdown(f"```text\n{travel}\n```")
            if st.session_state.get("travel_pdf"):
                st.download_button(
                    "⬇️ Download Travel Itinerary PDF",
                    st.session_state["travel_pdf"],
                    "travel_itinerary.pdf",
                    "application/pdf",
                )
        else:
            st.info("No travel itinerary generated.")

    # -------- Logs Tab --------
    with tabs[3]:
        st.markdown("#### 📜 Raw JSON Logs")
        st.json(st.session_state.get("logs"))


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
footer_html = f"""
<div class="lp-footer">
    {"<img src='data:image/png;base64," + logo_b64 + "' />" if logo_b64 else ""}
    <div><strong>✨ LifePilot — Intelligent Planner</strong></div>
    <div style="margin-top:4px;">
        Designed &amp; Developed by <b>Saranya Ganesan</b>
    </div>
    <div style="margin-top:4px;">
        <a href="https://www.linkedin.com/in/saranya-ganesan-texas" target="_blank">LinkedIn</a>
        <span class="lp-dot">•</span>
        <a href="https://github.com/saranyaganesandeveloper/LifePilot-Capstone-Project" target="_blank">GitHub</a>
    </div>
    <div style="margin-top:6px; font-size:11px; opacity:0.85;">
        © 2025 Saranya. All Rights Reserved.
    </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
