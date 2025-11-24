# ui/app.py

import io
import os
import base64
import json
import streamlit as st
import pandas as pd
from orchestrator import Orchestrator
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# PDF generator
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

PDF_COPYRIGHT = "© 2025 Saranya. All Rights Reserved. No part of this document may be reproduced or distributed without permission."
# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="LifePilot",
    page_icon="✨",
    layout="wide"
)

# ---------------------------------------------------------
# GLOBAL CSS (make sure fixed elements are visible)
# ---------------------------------------------------------
global_css = """
<style>
[data-testid="stAppViewContainer"] {
    overflow: visible !important;
}
</style>
"""
st.html(global_css)


# ---------------------------------------------------------
# LOAD LOGO (PROJECT-SAFE PATH)
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
# PREMIUM HEADER
# ---------------------------------------------------------
premium_header = f"""
<style>
#lp_header {{
    width: 100%;
    padding: 20px 35px;
    background: linear-gradient(90deg, #4b6fff, #7b9dff);
    border-radius: 0 0 12px 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.18);
    display: flex;
    align-items: center;
    gap: 20px;
    color: white;
    margin-bottom: 25px;
}}
#lp_header img {{
    width: 70px;
    border-radius: 12px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.4);
}}
#lp_title {{
    font-size: 32px;
    font-weight: 800;
    margin: 0;
}}
#lp_subtitle {{
    font-size: 16px;
    opacity: 0.9;
    margin-top: 4px;
}}
</style>

<div id="lp_header">
    {"<img src='data:image/png;base64," + logo_b64 + "' />" if logo_b64 else ""}
    <div>
        <div id="lp_title">✨ LifePilot</div>
        <div id="lp_subtitle">Your Intelligent Planner · by Saranya Ganesan</div>
    </div>
</div>
"""
st.html(premium_header)
page_watermark = """
<style>
body::after {
    content: "LifePilot  © 2025 Saranya";
    position: fixed;
    bottom: 10px;
    left: 10px;
    font-size: 10px;
    color: rgba(0,0,0,0.35);
    pointer-events: none;
}
</style>
"""
st.html(page_watermark)


# ---------------------------------------------------------
# INITIALIZE ORCHESTRATOR
# ---------------------------------------------------------
if "orc" not in st.session_state:
    st.session_state["orc"] = Orchestrator()

orc: Orchestrator = st.session_state["orc"]


# ---------------------------------------------------------
# PDF BUILDERS
# ---------------------------------------------------------
def build_pdf(text: str) -> bytes:
    """Create a simple text PDF with a copyright footer."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    story = []
    # main content
    story.append(Paragraph(text.replace("\n", "<br/>"), styles["Normal"]))
    story.append(Spacer(1, 24))
    # copyright footer
    story.append(Paragraph(f"<font size=8 color='#888888'>{PDF_COPYRIGHT}</font>", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


def build_shopping_pdf(df: pd.DataFrame) -> bytes:
    """Create a PDF from a shopping list dataframe with a copyright footer."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    lines: list[str] = []
    for _, row in df.iterrows():
        line = f"{row.get('category', '')}: {row.get('item', '')} — {row.get('quantity', '')} {row.get('notes', '')}"
        lines.append(line)

    text = "<br/>".join(lines) if lines else "No items."

    story = []
    story.append(Paragraph(text, styles["Normal"]))
    story.append(Spacer(1, 24))
    story.append(Paragraph(f"<font size=8 color='#888888'>{PDF_COPYRIGHT}</font>", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

# ---------------------------------------------------------
# PREFERENCE DEBUG
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

    results, logs = orc.handle(query, return_logs=True)

    st.session_state["meal"] = results.get("meal")
    st.session_state["shopping"] = results.get("shopping")
    st.session_state["travel"] = results.get("travel")
    st.session_state["logs"] = logs

    st.session_state["meal_pdf"] = build_pdf(results["meal"]) if results["meal"] else None

    if isinstance(results["shopping"], list):
        try:
            df = pd.DataFrame(results["shopping"])
            st.session_state["shopping_pdf"] = build_shopping_pdf(df)
        except Exception:
            st.session_state["shopping_pdf"] = None
    else:
        st.session_state["shopping_pdf"] = None

    st.session_state["travel_pdf"] = build_pdf(results["travel"]) if results["travel"] else None

    st.session_state["ready"] = True


# ---------------------------------------------------------
# DISPLAY RESULTS
# ---------------------------------------------------------
if st.session_state.get("ready"):

    tabs = st.tabs(["🍽 Meal Plan", "🛒 Shopping List", "✈ Travel Itinerary", "📜 Logs"])

    # Meal
    with tabs[0]:
        st.subheader("🍽 Meal Plan")
        meal = st.session_state.get("meal")
        if meal:
            st.markdown(f"```text\n{meal}\n```")
            if st.session_state["meal_pdf"]:
                st.download_button(
                    "⬇️ Download Meal Plan PDF",
                    st.session_state["meal_pdf"],
                    "meal_plan.pdf",
                    "application/pdf",
                )
        else:
            st.info("No meal plan generated for this query.")

    # Shopping
    with tabs[1]:
        st.subheader("🛒 Shopping List")
        shopping = st.session_state.get("shopping")
        if shopping:
            if isinstance(shopping, list):
                try:
                    df = pd.DataFrame(shopping)
                    st.dataframe(df, width="stretch")
                except Exception:
                    st.write(shopping)
            if st.session_state["shopping_pdf"]:
                st.download_button(
                    "⬇️ Download Shopping List PDF",
                    st.session_state["shopping_pdf"],
                    "shopping_list.pdf",
                    "application/pdf",
                )
        else:
            st.info("No shopping list generated.")

    # Travel
    with tabs[2]:
        st.subheader("✈ Travel Itinerary")
        travel = st.session_state.get("travel")
        if travel:
            st.markdown(f"```text\n{travel}\n```")
            if st.session_state["travel_pdf"]:
                st.download_button(
                    "⬇️ Download Travel Itinerary PDF",
                    st.session_state["travel_pdf"],
                    "travel_itinerary.pdf",
                    "application/pdf",
                )
        else:
            st.info("No travel itinerary generated.")

    # Logs
    with tabs[3]:
        st.subheader("📜 Raw JSON Logs")
        st.json(st.session_state.get("logs"))


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
# ---------------------------------------------------------
# FOOTER (with links + copyright)
# ---------------------------------------------------------
footer_html = f"""
<style>
#lp_footer_wrap {{
    text-align:center;
    padding: 30px 10px 10px 10px;
    margin-top: 50px;
    color: #555;
    font-size: 14px;
}}
#lp_footer_logo {{
    width: 80px;
    margin-bottom: 10px;
    border-radius: 12px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.12);
}}
#lp_footer_title {{
    margin: 0;
    font-weight: 600;
    font-size: 20px;
}}
#lp_footer_links a {{
    text-decoration: none;
    color: #1a0dab;
    font-weight: 600;
    margin: 0 6px;
}}
#lp_footer_copy {{
    margin-top: 8px;
    font-size: 12px;
    color: #777;
}}
</style>

<div id="lp_footer_wrap">
    {f"<img id='lp_footer_logo' src='data:image/png;base64,{logo_b64}' />" if logo_b64 else ""}
    <h3 id="lp_footer_title">✨ LifePilot — Intelligent Planner</h3>
    <p>Designed & Developed with ❤️ by <b>Saranya Ganesan</b></p>
    <div id="lp_footer_links">
        <a href="https://www.linkedin.com/in/saranya-ganesan-texas" target="_blank">🔗 LinkedIn</a> |
        <a href="https://github.com/saranyaganesandeveloper/LifePilot-Capstone-Project" target="_blank">🔗 GitHub</a>
    </div>
    <div id="lp_footer_copy">
        © 2025 Saranya. All Rights Reserved.<br/>
        No part of this application or its outputs may be reproduced or distributed without permission.
    </div>
</div>
"""

st.html(footer_html)



# ---------------------------------------------------------
# ANIMATED LOGO FLOATING BUBBLE
# ---------------------------------------------------------
animated_bubble = f"""
<style>
#lp_bubble {{
    position: fixed;
    bottom: 25px;
    right: 25px;
    width: 65px;
    height: 65px;
    border-radius: 50%;
    background: white;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.25);
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    z-index: 999999999;
    animation: pulseGlow 1.8s infinite ease-in-out;
    transition: transform 0.2s ease;
}}
#lp_bubble:hover {{
    transform: scale(1.12);
}}
#lp_bubble img {{
    width: 42px;
    height: 42px;
    border-radius: 50%;
}}
@keyframes pulseGlow {{
    0%  {{ box-shadow: 0 0 0px rgba(75,111,255,0.6); transform: scale(1.0); }}
    50% {{ box-shadow: 0 0 18px rgba(75,111,255,0.75); transform: scale(1.08); }}
    100%{{ box-shadow: 0 0 0px rgba(75,111,255,0.6); transform: scale(1.0); }}
}}

#lp_popup {{
    position: fixed;
    bottom: 100px;
    right: 25px;
    width: 260px;
    background: white;
    border-radius: 14px;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.25);
    padding: 16px;
    font-size: 14px;
    z-index: 999999999;
    display: none;
}}
#lp_popup a {{
    text-decoration: none;
    color: #1a0dab;
    font-weight: 600;
    display: block;
    margin-top: 6px;
}}
</style>

<div id="lp_bubble">
    {"<img src='data:image/png;base64," + logo_b64 + "' />" if logo_b64 else "✨"}
</div>

<div id="lp_popup">
    <strong>✨ Made by Saranya</strong><br>
    Creator of LifePilot — Multi-Agent AI Planner.<br><br>
    <a href="https://www.linkedin.com/in/saranya-ganesan-texas" target="_blank">🔗 LinkedIn</a>
    <a href="https://github.com/saranyaganesandeveloper/LifePilot-Capstone-Project" target="_blank">🔗 GitHub</a>
</div>

<script>
const bubble = document.getElementById("lp_bubble");
const popup = document.getElementById("lp_popup");
if (bubble && popup) {{
    bubble.onclick = () => {{
        popup.style.display = (popup.style.display === "none" || popup.style.display === "") ? "block" : "none";
    }};
}}
</script>
"""

st.html(animated_bubble)
