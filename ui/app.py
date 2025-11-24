# ui/app.py

import io
import os
import base64
import json
from typing import Any

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
    layout="wide",
)


# ---------------------------------------------------------
# SESSION-STATE INITIALIZATION
# ---------------------------------------------------------
if "orc" not in st.session_state:
    st.session_state["orc"] = Orchestrator()

if "ready" not in st.session_state:
    st.session_state["ready"] = False

if "theme" not in st.session_state:
    st.session_state["theme"] = "light"  # "light" or "dark"

if "show_settings" not in st.session_state:
    st.session_state["show_settings"] = False

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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "..", "docs", "lifepilot_logo.png")
logo_b64 = load_image_base64(LOGO_PATH)


# ---------------------------------------------------------
# THEME COLORS
# ---------------------------------------------------------
def get_theme_colors(theme: str) -> dict[str, str]:
    if theme == "dark":
        return {
            "bg": "#060814",
            "card": "#111827",
            "card_soft": "#0b1020",
            "accent": "#4b6fff",
            "accent_soft": "#4b6fff22",
            "text": "#f9fafb",
            "muted": "#9ca3af",
            "border": "#1f2937",
            "danger": "#ef4444",
        }
    else:
        # light
        return {
            "bg": "#f5f6fb",
            "card": "#ffffff",
            "card_soft": "#eef1ff",
            "accent": "#4b6fff",
            "accent_soft": "#4b6fff18",
            "text": "#111827",
            "muted": "#6b7280",
            "border": "#e5e7eb",
            "danger": "#dc2626",
        }


colors = get_theme_colors(st.session_state["theme"])


# ---------------------------------------------------------
# GLOBAL CSS (layout + theme)
# ---------------------------------------------------------
global_css = f"""
<style>

/* Base background */
.stApp {{
    background: {colors["bg"]};
    color: {colors["text"]};
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "SF Pro Text",
                 "Segoe UI", sans-serif;
}}

/* Remove default Streamlit padding */
.block-container {{
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1100px;
}}

/* Header card */
.lp-header {{
    width: 100%;
    padding: 18px 24px;
    border-radius: 18px;
    background: linear-gradient(90deg, #4b6fff, #7b9dff);
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.35);
    display: flex;
    align-items: center;
    gap: 18px;
    color: #ffffff;
    margin-bottom: 1.5rem;
}}

.lp-header-logo {{
    width: 64px;
    height: 64px;
    border-radius: 20px;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.75);
    overflow: hidden;
    flex-shrink: 0;
}}

.lp-header-logo img {{
    width: 64px;
    height: 64px;
}}

.lp-header-text-main {{
    font-size: 28px;
    font-weight: 750;
    letter-spacing: 0.02em;
    margin-bottom: 2px;
}}

.lp-header-text-sub {{
    font-size: 13px;
    opacity: 0.95;
}}

/* Small pill labels, buttons etc */
.lp-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.2);
    background: rgba(15,23,42,0.25);
    font-size: 11px;
    backdrop-filter: blur(8px);
}}

/* Theme toggle alignment */
.lp-header-right {{
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
    font-size: 12px;
}}

/* Generic card */
.lp-card {{
    background: {colors["card"]};
    border-radius: 18px;
    padding: 18px 18px 14px 18px;
    border: 1px solid {colors["border"]};
    box-shadow: 0 16px 35px rgba(15, 23, 42, 0.15);
    margin-bottom: 16px;
}}

/* Softer card */
.lp-card-soft {{
    background: {colors["card_soft"]};
    border-radius: 14px;
    padding: 10px 12px;
    border: 1px dashed {colors["border"]};
    margin-top: 8px;
}}

/* Section title */
.lp-section-title {{
    font-weight: 600;
    font-size: 15px;
    margin-bottom: 4px;
}}

/* Little caption under sections */
.lp-section-caption {{
    font-size: 12px;
    color: {colors["muted"]};
    margin-bottom: 6px;
}}

/* Text area label */
.lp-input-label {{
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 4px;
}}

/* Tabs styling – soften background */
div[data-baseweb="tab"] > button {{
    border-radius: 999px !important;
}}

/* Footer */
.lp-footer {{
    text-align: center;
    padding: 28px 0 10px 0;
    color: {colors["muted"]};
    font-size: 12px;
}}

.lp-footer img {{
    width: 70px;
    margin-bottom: 6px;
}}

/* System control buttons container */
.lp-system-buttons button[kind="secondary"] {{
    border-radius: 999px !important;
}}

/* Small dot separator */
.lp-dot {{
    margin: 0 6px;
    opacity: 0.5;
}}
</style>
"""
st.markdown(global_css, unsafe_allow_html=True)


# ---------------------------------------------------------
# SYSTEM CONTROL CALLBACKS
# ---------------------------------------------------------
def clear_memory() -> None:
    """Clear vector memory but keep current UI layout."""
    try:
        orc.memory.vectors = []
        orc.memory.texts = []
    except Exception:
        pass
    st.session_state["ready"] = False


def clear_preferences_only() -> None:
    """Alias for now – clears memory, preserves logs."""
    clear_memory()


def reset_everything() -> None:
    """Hard reset of the session orchestrator + results."""
    st.session_state.clear()
    st.session_state["orc"] = Orchestrator()
    st.session_state["theme"] = "light"
    st.session_state["show_settings"] = False


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
header_html = f"""
<div class="lp-header">
  <div class="lp-header-logo">
    {"<img src='data:image/png;base64," + logo_b64 + "' />" if logo_b64 else ""}
  </div>
  <div style="flex:1; display:flex; flex-direction:column;">
    <div class="lp-header-text-main">✨ LifePilot</div>
    <div class="lp-header-text-sub">
      Your Intelligent Planner · Meals · Shopping · Travel
    </div>
    <div style="margin-top:8px;">
      <span class="lp-pill">Multi-Agent · Gemini · Vector Memory</span>
    </div>
  </div>
</div>
"""

# Lay out header + right-side controls using columns
header_col_left, header_col_right = st.columns([4, 2])
with header_col_left:
    st.markdown(header_html, unsafe_allow_html=True)

with header_col_right:
    with st.container():
        st.markdown(
            "<div class='lp-header-right'>Theme & Settings</div>",
            unsafe_allow_html=True,
        )
        col_theme, col_settings = st.columns(2)
        with col_theme:
            dark_mode = st.toggle(
                "Dark Mode",
                value=(st.session_state["theme"] == "dark"),
                key="theme_toggle",
            )
            st.session_state["theme"] = "dark" if dark_mode else "light"
        with col_settings:
            if st.button("⚙️ Settings", use_container_width=True):
                st.session_state["show_settings"] = not st.session_state.get(
                    "show_settings", False
                )


# ---------------------------------------------------------
# SETTINGS / CONFIG SIDEBAR "MODAL"
# (does not change backend behavior, only UI)
# ---------------------------------------------------------
if st.session_state.get("show_settings", False):
    with st.sidebar:
        st.markdown("### ⚙️ LifePilot Configuration")
        st.caption(
            "These controls are for experimentation / UI only. "
            "Core behavior is still driven by environment variables & backend code."
        )
        st.text_input("Display Name", value="Saranya", help="For future personalization.")
        st.slider(
            "LLM Creativity (temperature – cosmetic only)",
            0.0,
            1.0,
            0.4,
            0.1,
            help="UI-only slider. Actual temperature is controlled in backend.",
        )
        st.text_input(
            "Primary Model (display only)",
            value="gemini-2.5-flash",
        )
        st.text_input(
            "Deployment URL (read-only)",
            value="https://lifepilot-service-254077494572.us-central1.run.app",
            disabled=True
        )
        st.button("Close Settings", on_click=lambda: st.session_state.update({"show_settings": False}))


# ---------------------------------------------------------
# SYSTEM CONTROLS CARD
# ---------------------------------------------------------
with st.container():
    st.markdown(
        f"""
        <div class="lp-card">
          <div class="lp-section-title">🧩 System Controls</div>
          <div class="lp-section-caption">
            Manage memory & debugging. These actions affect how LifePilot remembers your preferences.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sys_cols = st.columns([1.1, 1.2, 1])
    with sys_cols[0]:
        st.button("🧹 Clear Memory", on_click=clear_memory, use_container_width=True)
    with sys_cols[1]:
        st.button(
            "✨ Clear Preferences Only",
            on_click=clear_preferences_only,
            use_container_width=True,
        )
    with sys_cols[2]:
        st.button("🔥 Reset Everything", on_click=reset_everything, use_container_width=True)

    # Memory debug expander
    with st.expander("🔍 View Current Preferences (Memory Debug)", expanded=False):
        try:
            prefs = orc.build_preferences()
            st.json(prefs)
        except Exception as e:
            st.error(f"Failed to load preferences: {e}")


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
        line = (
            f"{row.get('category', '')}: {row.get('item', '')} — "
            f"{row.get('quantity', '')} {row.get('notes', '')}"
        )
        lines.append(line)

    text = "<br/>".join(lines) if lines else "No items."
    story = [Paragraph(text, styles["Normal"])]
    doc.build(story)
    buffer.seek(0)
    return buffer.read()


# ---------------------------------------------------------
# MAIN INPUT CARD
# ---------------------------------------------------------
with st.container():
    st.markdown(
        f"""
        <div class="lp-card">
          <div class="lp-section-title">💬 Ask LifePilot</div>
          <div class="lp-section-caption">
            Describe what you need. LifePilot will automatically decide whether to plan meals, shopping, travel, or all three.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Slightly below the label card, place the actual text area & run button
    col_input, col_run = st.columns([4, 1])
    with col_input:
        query = st.text_area(
            label="Ask LifePilot",
            label_visibility="collapsed",
            placeholder=(
                "Examples:\n"
                "• Plan my next week: vegetarian meals, groceries, and a 2-day trip to Dallas.\n"
                "• I love South Indian food, lactose-free. Give me a 3-day meal plan.\n"
                "• Plan a 1-day Austin trip with kid-friendly spots."
            ),
            height=120,
        )

    with col_run:
        st.write("")  # spacing
        st.write("")
        run_clicked = st.button("🚀 Run LifePilot", use_container_width=True)


# ---------------------------------------------------------
# RUN ORCHESTRATOR
# ---------------------------------------------------------
if run_clicked:
    if not (query or "").strip():
        st.warning("Please enter a request before running LifePilot.")
    else:
        with st.spinner("Running LifePilot agents…"):
            results, logs = orc.handle(query, return_logs=True)

        # Store in session_state for PDF & tab re-renders
        st.session_state["meal"] = results.get("meal")
        st.session_state["shopping"] = results.get("shopping")
        st.session_state["travel"] = results.get("travel")
        st.session_state["logs"] = logs

        # PDFs
        if st.session_state.get("meal"):
            st.session_state["meal_pdf"] = build_pdf(st.session_state["meal"])
        else:
            st.session_state["meal_pdf"] = None

        shopping_data: Any = st.session_state.get("shopping")
        if isinstance(shopping_data, list) and shopping_data:
            try:
                df_for_pdf = pd.DataFrame(shopping_data)
                st.session_state["shopping_pdf"] = build_shopping_pdf(df_for_pdf)
            except Exception:
                st.session_state["shopping_pdf"] = None
        else:
            st.session_state["shopping_pdf"] = None

        if st.session_state.get("travel"):
            st.session_state["travel_pdf"] = build_pdf(st.session_state["travel"])
        else:
            st.session_state["travel_pdf"] = None

        st.session_state["ready"] = True


# ---------------------------------------------------------
# RESULTS TABS
# ---------------------------------------------------------
if st.session_state.get("ready"):

    tabs = st.tabs(["🍽 Meal Plan", "🛒 Shopping List", "✈ Travel Itinerary", "📜 Logs"])

    # --------- Meal Tab ---------
    with tabs[0]:
        st.markdown("### 🍽 Meal Plan")
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

    # --------- Shopping Tab ---------
    with tabs[1]:
        st.markdown("### 🛒 Shopping List")
        shopping = st.session_state.get("shopping")

        if shopping:
            if isinstance(shopping, str):
                try:
                    shopping = json.loads(shopping)
                except Exception:
                    pass

            if isinstance(shopping, list):
                try:
                    df = pd.DataFrame(shopping)
                    st.dataframe(df, use_container_width=True)
                except Exception:
                    st.write(shopping)
            else:
                st.write(shopping)

            if st.session_state.get("shopping_pdf"):
                st.download_button(
                    "⬇️ Download Shopping List PDF",
                    st.session_state["shopping_pdf"],
                    "shopping_list.pdf",
                    "application/pdf",
                )
        else:
            st.info("No shopping list generated for this query.")

    # --------- Travel Tab ---------
    with tabs[2]:
        st.markdown("### ✈ Travel Itinerary")
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

    # --------- Logs Tab ---------
    with tabs[3]:
        st.markdown("### 📜 Raw JSON Logs")
        st.json(st.session_state.get("logs"))


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
footer_html = f"""
<div class="lp-footer">
    {"<img src='data:image/png;base64," + logo_b64 + "' />" if logo_b64 else ""}
    <div><strong>✨ LifePilot — Intelligent Planner</strong></div>
    <div style="margin-top:4px;">
        Designed &amp; Developed with ❤️ by <b>Saranya Ganesan</b>
    </div>
    <div style="margin-top:4px;">
        <a href="https://www.linkedin.com/in/saranya-ganesan-texas" target="_blank">LinkedIn</a>
        <span class="lp-dot">•</span>
        <a href="https://github.com/saranyaganesandeveloper/LifePilot-Capstone-Project" target="_blank">GitHub</a>
    </div>
    <div style="margin-top:6px; font-size:11px; opacity:0.8;">
        © 2025 Saranya. All Rights Reserved. No part of this application or its output may be reproduced or distributed without permission.
    </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
