# ════════════════════════════════════════════════════════════════════════
# APP.PY — CareerBridge AI Pro
# Complete rewrite fixing all bugs + improved UI + novel features
# Every line explained for beginners
# ════════════════════════════════════════════════════════════════════════

# ─── IMPORTS ────────────────────────────────────────────────────────────
# Think of imports like plugging in appliances before using them.
# Without importing, Python doesn't know what streamlit or groq IS.

import streamlit as st        # The web framework — builds the entire UI
import json                   # Converts text ↔ Python dictionaries (like a translator)
import pdfplumber             # Reads PDF files and pulls out the text
from groq import Groq         # The AI brain — sends prompts, gets responses

# ─── PAGE CONFIG ────────────────────────────────────────────────────────
# This is like setting up a room before guests arrive.
# MUST be the very first Streamlit command — nothing can come before it.

st.set_page_config(
    page_title="CareerBridge AI",   # Browser tab title
    layout="wide",                   # Use full screen width
    page_icon="🎓",                  # Icon in the browser tab
    initial_sidebar_state="expanded"  # Start open so nav is visible
)

# ─── SESSION STATE SETUP ────────────────────────────────────────────────
# Session state is like a notepad that Streamlit keeps between button clicks.
# Without it, every click resets everything (like a goldfish memory).
# We check "is X already written on the notepad?" before writing again.

if "theme" not in st.session_state:
    # First time the app loads — set default theme to Dark
    st.session_state.theme = "Dark"

if "nav_expanded" not in st.session_state:
    # Controls whether the nav rail is slim (icons, 76px)
    # or expanded (icons + labels, 230px). The ☰/‹ button flips this.
    st.session_state.nav_expanded = False

if "page" not in st.session_state:
    # Remembers which section the user is on, so toggling the rail
    # width does NOT reset them back to the first page.
    st.session_state.page = "📋 Resume Auditor"

if "audit_data" not in st.session_state:
    # No analysis run yet — set to None as a placeholder
    st.session_state.audit_data = None

# ─── THEME CSS ──────────────────────────────────────────────────────────
# CSS is like a style rulebook for the webpage.
# We define two rulebooks (dark/light) and apply whichever the user picked.
# The 'if/else' checks the notepad (session_state) to pick the right one.

if st.session_state.theme == "Dark":
    # ── "Terminal-tech" dark palette — deep navy with electric cyan ──
    # WHY these colours: cyan-on-navy is the classic look of developer
    # tools (VS Code, GitHub dark, terminal UIs) — instantly "techy".
    BG         = "#05080f"   # Near-black navy — the deepest layer
    SURFACE    = "#0b111e"   # Panel cards — one step lighter than BG
    BORDER     = "#1c2940"   # Steel-blue borders — visible but subtle
    TEXT       = "#e6edf7"   # Blue-tinted white — crisp on navy
    MUTED      = "#8b9bb4"   # FIX: was #5a5a7a (too dark/unreadable).
                              # Brightened so captions are legible.
    ACCENT     = "#38bdf8"   # Electric cyan — buttons, highlights, links
    ACCENT_2   = "#818cf8"   # Violet — second gradient stop for buttons
    ACCENT_DIM = "rgba(56,189,248,0.12)"   # Transparent cyan wash
    GREEN      = "#34d399"   # Status colours unchanged — universal signals
    AMBER      = "#fbbf24"
    RED        = "#f87171"
    CARD_BG    = "#0a1322"   # Score card — between BG and SURFACE
    GLOW       = "0 0 18px rgba(56,189,248,0.25)"  # Cyan glow for buttons
else:
    # ── Clean "lab-white" light palette with indigo accent ──
    BG         = "#f6f8fc"   # Soft cool white — easier on eyes than pure white
    SURFACE    = "#ffffff"   # Cards pop against the soft background
    BORDER     = "#dfe6f0"   # Light steel borders
    TEXT       = "#0b1220"   # Near-black navy text — maximum contrast
    MUTED      = "#5b6b84"   # Readable slate for captions
    ACCENT     = "#4f46e5"   # Indigo — professional, techy, not orange
    ACCENT_2   = "#0ea5e9"   # Sky — second gradient stop
    ACCENT_DIM = "rgba(79,70,229,0.10)"
    GREEN      = "#059669"
    AMBER      = "#d97706"
    RED        = "#dc2626"
    CARD_BG    = "#eef2fa"
    GLOW       = "0 4px 14px rgba(79,70,229,0.25)"

# Build the CSS string using the colour variables above.
# The f"..." means Python will slot in the variable values automatically.
# ── Rail width driven by the toggle state ─────────────────────────────
# Python decides the width; the CSS below just consumes the value.
# 76px  = icons only   |   230px = icons + labels
SIDEBAR_W = "230px" if st.session_state.nav_expanded else "76px"

css = f"""
<style>
/* Google Fonts — FIX: correct URL (old code had wrong domain) */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

/* Global reset — applies to every element on the page */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {TEXT};
}}

/* Main app background */
.stApp {{ background: {BG}; }}

/* ── Hide only what we don't need — leave the header structure intact ──
   We target specific CHILDREN of the header, never the header itself.
   Hiding the header element would also hide its children including
   the sidebar toggle button — exactly the bug we had before. ── */

/* Hide hamburger menu (top-left Streamlit icon) */
#MainMenu {{ display: none !important; }}

/* Hide "Made with Streamlit" footer text */
footer {{ display: none !important; }}

/* Hide the coloured decorative bar at the very top */
[data-testid="stDecoration"] {{ display: none !important; }}

/* Hide the deploy/share toolbar buttons (top-right) */
[data-testid="stToolbar"] {{ display: none !important; }}

/* Make the header bar transparent so it blends in.
   We use background:transparent NOT visibility:hidden.
   Why? visibility:hidden hides the element AND its children.
   background:transparent makes it see-through but children remain visible.
   The sidebar toggle is a child of this header — we need it to survive. */
header[data-testid="stHeader"] {{
    background: transparent !important;
    border-bottom: none !important;
}}

/* ── Sidebar styling ── */
[data-testid="stSidebar"] {{
    background: {SURFACE};
    border-right: 1px solid {BORDER};
}}

/* ── Panel card (used for input sections) ── */
.panel {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1rem;
}}
.panel-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: {TEXT};
    margin-bottom: 0.5rem;
}}

/* ── Score card (the big circular number) ── */
.score-card {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}}
/* The orange circle — uses a CSS trick: border-radius 50% makes any square a circle */
.score-circle {{
    min-width: 90px;
    height: 90px;
    border-radius: 50%;
    border: 6px solid {ACCENT};
    background: {ACCENT_DIM};
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: {ACCENT};
}}
.score-label {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: {TEXT};
    margin-bottom: 0.2rem;
}}
.score-verdict {{
    font-size: 0.85rem;
    color: {MUTED};
}}

/* ── Badge row (Critical / Warnings / Good counts) ── */
.badge-row {{
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}}
.badge {{
    flex: 1;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 600;
    text-align: center;
}}
.badge-red    {{ background: rgba(220,38,38,0.1);  border: 1px solid {RED};   color: {RED}; }}
.badge-amber  {{ background: rgba(217,119,6,0.1);  border: 1px solid {AMBER}; color: {AMBER}; }}
.badge-green  {{ background: rgba(5,150,105,0.1);  border: 1px solid {GREEN}; color: {GREEN}; }}

/* ── Highlighted resume paragraph ── */
.highlight-box {{
    background: {SURFACE};
    border-left: 4px solid {ACCENT};
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    font-size: 0.88rem;
    line-height: 1.7;
    color: {TEXT};
}}

/* ── ATS keyword chip (green for found, red for missing) ── */
.kw-found   {{ display:inline-block; background:rgba(5,150,105,0.12); border:1px solid {GREEN}; 
               color:{GREEN}; font-size:0.75rem; padding:3px 10px; border-radius:20px; margin:2px; }}
.kw-missing {{ display:inline-block; background:rgba(220,38,38,0.10); border:1px solid {RED};   
               color:{RED};   font-size:0.75rem; padding:3px 10px; border-radius:20px; margin:2px; }}

/* ── Info callout box ── */
.callout {{
    background: {ACCENT_DIM};
    border: 1px solid {ACCENT};
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    font-size: 0.85rem;
    color: {ACCENT};
    margin-bottom: 1rem;
}}

/* ── Streamlit widget overrides ── */
.stTextArea textarea, .stTextInput input {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT} !important;
    font-size: 0.875rem !important;
}}
.stTextArea textarea:focus, .stTextInput input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 2px {ACCENT_DIM} !important;
}}
/* Primary button gets the orange accent */
.stButton button[kind="primary"] {{
    background: {ACCENT} !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    color: #fff !important;
    transition: opacity 0.2s ease !important;
}}
.stButton button[kind="primary"]:hover {{ opacity: 0.88 !important; }}

/* Expander panels */
div[data-testid="stExpander"] {{
    background: {SURFACE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 12px !important;
}}

/* ═══════════════════════════════════════════════════════════════════
   NAV RAIL — always visible, width toggles 76px ⇄ 230px
   ═══════════════════════════════════════════════════════════════════
   THE DISAPPEARING-SIDEBAR FIX (root cause of your screenshot):
   When Streamlit "collapses" a sidebar it does NOT delete it — it
   slides it off-screen with `transform: translateX(-100%)` and sets
   aria-expanded="false". Our old CSS locked the WIDTH but never
   cancelled the TRANSFORM, so one stray collapse click slid the whole
   rail off the left edge — with the reopen arrow hidden, it was gone.
   Fix: force transform:none + margin-left:0 in BOTH aria states.
   Analogy: we had bolted the door open but forgot the window — this
   nails every escape route shut. The rail physically cannot leave. */

section[data-testid="stSidebar"],
section[data-testid="stSidebar"][aria-expanded="true"],
section[data-testid="stSidebar"][aria-expanded="false"] {{
    min-width: {SIDEBAR_W} !important;   /* Python-injected: 76px or 230px */
    max-width: {SIDEBAR_W} !important;
    width:     {SIDEBAR_W} !important;
    transform: none !important;          /* cancel the slide-away animation */
    margin-left: 0 !important;           /* cancel off-screen margin trick  */
    visibility: visible !important;
    display: block !important;
    background: {SURFACE} !important;
    border-right: 1px solid {BORDER} !important;
    transition: min-width 0.2s ease, max-width 0.2s ease !important;
}}

[data-testid="stSidebar"] > div:first-child {{
    padding: 0.75rem 0.5rem !important;
    width: {SIDEBAR_W} !important;
}}

/* Streamlit's own collapse arrows stay dead — OUR ☰/‹ button replaces them */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebar"] button[kind="header"] {{
    display: none !important;
}}

/* ── Kill the radio widget's own "Navigate" label ────────────────────
   label_visibility="collapsed" hides it, but our blanket `label`
   styling below was resurrecting it — where it wrapped vertically
   ("N av ig at e") inside the 76px rail. This nukes it for good. */
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] .stRadio > label:first-child {{
    display: none !important;
    height: 0 !important;
    visibility: hidden !important;
}}

/* ── Nav radio → vertical tile stack ── */
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
    flex-direction: column !important;
    display: flex !important;
    gap: 0.45rem !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
    display: flex !important;
    align-items: center !important;
    /* icons centred in rail mode, left-aligned when labels are showing */
    justify-content: {("flex-start" if st.session_state.nav_expanded else "center")} !important;
    width: 92% !important;
    height: 48px !important;
    margin: 0 auto !important;
    padding: 0 0.6rem !important;
    border-radius: 10px !important;
    border: 1px solid transparent !important;
    cursor: pointer !important;
    font-size: {("0.95rem" if st.session_state.nav_expanded else "1.4rem")} !important;
    color: {TEXT} !important;
    transition: background 0.15s ease !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label > div:first-child {{
    display: none !important;   /* hide the radio circles */
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
    background: {ACCENT_DIM} !important;
}}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {{
    background: {ACCENT_DIM} !important;
    border: 1px solid {ACCENT} !important;
    box-shadow: {GLOW} !important;       /* techy glow on the active tab */
}}

/* ── Sidebar buttons (☰/‹ toggle + theme) as square tiles ── */
[data-testid="stSidebar"] .stButton button {{
    width: 92% !important;
    height: 44px !important;
    margin: 0 auto !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    background: transparent !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    font-size: 1.15rem !important;
    color: {ACCENT} !important;
    padding: 0 !important;
}}
[data-testid="stSidebar"] .stButton button:hover {{
    background: {ACCENT_DIM} !important;
    border-color: {ACCENT} !important;
}}

/* ═══ TECHY POLISH ═══════════════════════════════════════════════════ */

/* Faint blueprint grid over the page background — the "engineering
   paper" effect. Two overlapping 1px gradients drawn every 42px. */
.stApp {{
    background:
        linear-gradient({BORDER}22 1px, transparent 1px),
        linear-gradient(90deg, {BORDER}22 1px, transparent 1px),
        {BG} !important;
    background-size: 42px 42px, 42px 42px, auto !important;
}}

/* Primary buttons: cyan→violet gradient + glow, instead of flat orange */
.stButton button[kind="primary"] {{
    background: linear-gradient(135deg, {ACCENT}, {ACCENT_2}) !important;
    box-shadow: {GLOW} !important;
    border: none !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border-radius: 10px !important;
}}
.stButton button[kind="primary"]:hover {{
    filter: brightness(1.12) !important;
}}

/* Inputs glow cyan when focused — terminal vibe */
.stTextArea textarea:focus, .stTextInput input:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 2px {ACCENT_DIM}, {GLOW} !important;
}}

/* Readability fixes for dark mode — every text element inherits TEXT */
p, span, label, div, li {{ color: {TEXT}; }}
.stCaption, [data-testid="stCaptionContainer"], small {{ color: {MUTED} !important; }}
h1,h2,h3,h4 {{ color: {TEXT} !important; letter-spacing: -0.01em; }}

/* ── Full annotated CV document ──────────────────────────────────────
   .cv-doc  = scrollable "paper" holding the ENTIRE extracted CV
   .hl-good = green wash under phrases the AI judged strong
   .hl-bad  = red wash + underline under weak/passive phrases        */
.cv-doc {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    max-height: 460px;          /* taller than viewport → scrolls   */
    overflow-y: auto;            /* the scrollbar                    */
    font-size: 0.86rem;
    line-height: 1.85;
    color: {TEXT};
    white-space: pre-wrap;       /* keep the CV's own line breaks    */
}}
.hl-good {{
    background: rgba(52,211,153,0.16);
    border-bottom: 2px solid {GREEN};
    border-radius: 3px;
    padding: 0 2px;
}}
.hl-bad {{
    background: rgba(248,113,113,0.14);
    border-bottom: 2px dashed {RED};
    border-radius: 3px;
    padding: 0 2px;
}}
/* legend chips above the document */
.legend-chip {{
    display: inline-block;
    font-size: 0.75rem;
    padding: 2px 10px;
    border-radius: 12px;
    margin-right: 8px;
}}

/* ── Skill Coverage progress bars ── */
.cov-row  {{ margin-bottom: 0.65rem; }}
.cov-head {{ display:flex; justify-content:space-between; margin-bottom:3px;
             font-size:0.85rem; }}
.cov-name {{ font-weight:600; color:{TEXT}; }}
.cov-pct  {{ color:{MUTED}; }}
.cov-track{{ background:{BORDER}; border-radius:6px; height:8px; overflow:hidden; }}
.cov-fill {{ height:8px; border-radius:6px; }}

</style>
"""

# Inject the CSS into the page — unsafe_allow_html=True lets Streamlit render raw HTML
# FIX: old code had "unsafe_allowed_with_html" (typo) — correct param is unsafe_allow_html
st.markdown(css, unsafe_allow_html=True)

# ─── SIDEBAR ────────────────────────────────────────────────────────────
# Everything inside 'with st.sidebar:' appears in the left panel.
# Think of it as a control panel on the side of the app.

# ── NAVIGATION RAIL with ‹ ⇄ ☰ toggle ─────────────────────────────────────
# Two states, both ALWAYS visible (the rail can never fully disappear):
#   ☰  rail mode     → 76px  wide, icons only
#   ‹  expanded mode → 230px wide, icons + labels
# The width is injected into the CSS from Python, so flipping
# st.session_state.nav_expanded re-renders the whole layout.

NAV_FULL = ["📋 Resume Auditor", "🛠 Project Architect",
            "💬 Interview Coach", "📚 Learning Path"]

with st.sidebar:

    # ── The toggle button ────────────────────────────────────────────────
    # Icon signals the CURRENT state and what clicking will do:
    #   ☰ shown while slim   → "there is more, click to expand"
    #   ‹ shown while wide   → "click to tuck the labels away"
    # This is OUR button in session_state — Streamlit reruns cannot
    # break it because the state lives in Python, not in fragile DOM CSS.
    toggle_icon = "‹" if st.session_state.nav_expanded else "☰"
    if st.button(toggle_icon, key="nav_toggle", help="Expand / collapse navigation",
                 use_container_width=True):
        # Flip the notepad value, then redraw the app with the new width
        st.session_state.nav_expanded = not st.session_state.nav_expanded
        st.rerun()

    st.markdown(f"<hr style='margin:0.4rem 0;border-color:{BORDER}'>",
                unsafe_allow_html=True)

    # ── Build the option labels for the CURRENT mode ─────────────────────
    # Expanded → full labels ("📋 Resume Auditor")
    # Slim     → first character only ("📋")
    if st.session_state.nav_expanded:
        display_opts = NAV_FULL
    else:
        display_opts = [o.split()[0] for o in NAV_FULL]   # icons only

    # Keep the user on the SAME page when the rail width flips.
    # Without index=cur_idx, toggling would reset them to page 1.
    cur_idx = NAV_FULL.index(st.session_state.page)

    # key changes with the mode so Streamlit rebuilds the radio cleanly
    # when the option labels change shape (icons ↔ full text).
    nav_choice = st.radio(
        "Navigate", display_opts, index=cur_idx,
        label_visibility="collapsed",
        key=f"nav_{st.session_state.nav_expanded}",
    )

    # Map whichever label style was clicked back to the FULL page name,
    # so the router below (if app_mode == "📋 Resume Auditor":) is untouched.
    st.session_state.page = NAV_FULL[display_opts.index(nav_choice)]
    app_mode = st.session_state.page

    st.markdown(f"<hr style='margin:0.4rem 0;border-color:{BORDER}'>",
                unsafe_allow_html=True)

    # ── Theme toggle icon ────────────────────────────────────────────────
    theme_icon = "☀️" if st.session_state.theme == "Dark" else "🌙"
    if st.button(theme_icon, key="theme_toggle", help="Switch theme",
                 use_container_width=True):
        st.session_state.theme = ("Light" if st.session_state.theme == "Dark"
                                  else "Dark")
        st.rerun()

# ── API key check — now lives in the MAIN area, not the rail ───────────
# WHY MOVED: a password input needs ~250px of width; the rail is 76px.
# Squeezing it into the rail would make it unusable, so if the key is
# missing we show the input front-and-centre in the main content area.
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.markdown(
        f"<div class='callout'>🔑 <b>Groq API key required.</b> "
        f"Paste it below to unlock the app. "
        f"Free key: console.groq.com/keys</div>",
        unsafe_allow_html=True
    )
    api_key = st.text_input("Groq API Key", type="password",
                            help="Get a free key at console.groq.com/keys")

# Guard clause — nothing below this line runs until a key is provided
if not api_key:
    st.stop()

# ─── GROQ CLIENT ────────────────────────────────────────────────────────
# Create the Groq "phone line" — a connection object we'll use to send prompts.
# Think of it like opening a phone app before making a call.
client = Groq(api_key=api_key)


# ════════════════════════════════════════════════════════════════════════
# SECTION 1: RESUME AUDITOR
# ════════════════════════════════════════════════════════════════════════

if app_mode == "📋 Resume Auditor":

    # Page header
    st.markdown(
        f"<h2 style='font-family:Space Grotesk;margin-bottom:0.25rem'>📋 Resume Auditor</h2>"
        f"<p style='color:{MUTED};margin-top:0;font-size:0.9rem'>"
        f"Upload your CV and a job description. Get a match score, skill gaps, "
        f"and ATS keyword analysis in seconds.</p>",
        unsafe_allow_html=True
    )
    st.divider()

    # Two input columns side-by-side
    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown('<div class="panel"><p class="panel-title">📄 Step 1 — Upload Your CV</p>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload CV (PDF only)",
            type=["pdf"],
            label_visibility="collapsed"   # Hide label — panel title explains it
        )
        if uploaded_file:
            # Show a small green confirmation so user knows it uploaded
            st.success(f"✅ {uploaded_file.name} uploaded")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="panel"><p class="panel-title">🎯 Step 2 — Target Role</p>', unsafe_allow_html=True)
        job_title = st.text_input(
            "Job title",
            placeholder="e.g. Data Analyst Intern",
            label_visibility="collapsed"
        )
        job_desc = st.text_area(
            "Job description",
            placeholder="Paste the full job description here...",
            height=130,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Submit button — centered using 3 columns trick
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        run_audit = st.button("⚡ Run Resume Audit", type="primary", use_container_width=True)

    # ── PIPELINE EXECUTION ───────────────────────────────────────────────
    # Only runs when button is clicked AND all inputs are provided

    if run_audit:

        # Validate inputs before wasting an API call
        if not uploaded_file:
            st.error("❌ Please upload your CV (PDF format)")
            st.stop()
        if not job_title or not job_desc:
            st.error("❌ Please enter both the job title and description")
            st.stop()

        with st.spinner("Analysing your CV against the role..."):

            # ── STEP 1: Extract text from PDF ────────────────────────────
            # pdfplumber opens the PDF like a book.
            # We loop through each "page" and pull the text out.
            # Analogy: like photocopying each page, then reading all copies together.

            extracted_text = ""   # Start with an empty string to collect all pages

            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    # extract_text() returns the text on that page, or None if blank/scanned
                    page_text = page.extract_text()
                    if page_text:
                        # Add this page's text to our collection, with a newline separator
                        extracted_text += page_text + "\n"

            # FIX: system_prompt was INSIDE the for loop in old code — it ran per page!
            # Now it's OUTSIDE the loop (correct) — runs once after ALL pages are read.

            if not extracted_text.strip():
                # .strip() removes whitespace — if nothing is left, the PDF had no text
                st.error("❌ Could not extract text from this PDF. Try a text-based PDF (not a scanned image).")
                st.stop()

            # ── STEP 2: Build the prompt ──────────────────────────────────
            # A prompt is the instruction we send to the AI.
            # Think of it as a very detailed memo to a very smart analyst.
            # We embed the CV text and job description inside the prompt.

            system_prompt = f"""
You are an expert graduate career advisor and ATS (Applicant Tracking System) analyst.
Analyse the student CV against the job description below.

RULES:
- Return ONLY a valid JSON object. No markdown, no backticks, no explanation.
- If the job description lacks specific technical requirements, infer standard tools for '{job_title}'.
- Be honest — match_score should reflect genuine alignment, not flattery.
- Extract 3-5 real keywords from the job description for ats_keywords_found and ats_keywords_missing.

Return this exact JSON structure:
{{
  "rubric": {{
    "technical_skills":     <0-10: hard skills vs the JD's requirements>,
    "experience_relevance": <0-10: how directly past roles map to this one>,
    "education_fit":        <0-10: qualifications vs what the JD asks>,
    "evidence_quality":     <0-10: quantified, verifiable achievements>
  }},
  "verdict": "<one of: Strong Match | Good Fit | Needs Work | Poor Fit>",
  "critical_count": <integer>,
  "warning_count": <integer>,
  "good_count": <integer>,
  "critical_issues": ["<specific issue>", "<specific issue>"],
  "warning_issues": ["<specific issue>", "<specific issue>"],
  "good_points": ["<specific strength>", "<specific strength>"],
  "ats_keywords_found": ["<keyword in both CV and JD>"],
  "ats_keywords_missing": ["<keyword in JD but not in CV>"],
  "skill_coverage": [
    {{"skill": "<core skill from the JD>", "percent": <0-100 how well the CV evidences it>}},
    {{"skill": "<core skill>", "percent": <0-100>}},
    {{"skill": "<core skill>", "percent": <0-100>}},
    {{"skill": "<core skill>", "percent": <0-100>}}
  ],
  "strong_phrases": ["<EXACT phrase copied VERBATIM from the CV that is strong — quantified impact, relevant tools>", "<up to 6 phrases>"],
  "weak_phrases": ["<EXACT verbatim CV phrase that is weak — vague, passive, unquantified>", "<up to 6 phrases>"],
  "cv_comment": "<one-sentence overall verdict on the CV's writing quality>"
}}

PHRASE RULES (critical):
- strong_phrases / weak_phrases MUST be copied character-for-character from the CV text.
- Do NOT paraphrase, trim, or fix typos — an inexact copy cannot be highlighted.
- Each phrase 3-15 words, no overlaps between the two lists.

CV Text:
{extracted_text}

Job Title: {job_title}
Job Description:
{job_desc}
"""

            # ── STEP 3: Call Groq API ─────────────────────────────────────
            # We send our prompt to Groq and get back an AI response.
            # response_format=json_object forces Groq to only output valid JSON.
            # Analogy: like faxing a questionnaire and getting back a filled form.

            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",    # Fast, capable Llama model
                    messages=[{
                        "role": "user",
                        "content": system_prompt      # Our detailed instruction
                    }],
                    temperature=0.1,                  # Low = more consistent, less random
                    response_format={"type": "json_object"}  # Force JSON output
                )

                # ── STEP 4: Extract the response text ────────────────────
                # FIX: Old code used completion.choices.message.content (WRONG)
                # choices is a LIST — you need [0] to get the first (and only) item.
                # Analogy: choices is a box of letters, [0] picks the first letter out.

                raw_output = completion.choices[0].message.content.strip()

                # ── STEP 5: Parse JSON into a Python dictionary ───────────
                # json.loads() converts a JSON string into a Python dict.
                # Analogy: converting a written list into a filing cabinet you can search.

                data = json.loads(raw_output)

                # ── SCORE COMPUTED IN PYTHON, NOT BY THE AI ────────────
                # WHY: a single LLM-invented "78" is unexplainable and
                # varies run to run. Instead the AI only judges four
                # narrow sub-questions (0-10 each); the final score is
                # OUR transparent weighted sum — reproducible arithmetic
                # we can show the user line by line.
                # Analogy: the examiner marks four exam sections; the
                # registrar (this code) adds them up with fixed weights.
                WEIGHTS = {
                    "technical_skills":     0.40,  # matters most for grad roles
                    "experience_relevance": 0.30,
                    "education_fit":        0.15,
                    "evidence_quality":     0.15,
                }
                rubric_raw = data.get("rubric", {})
                # Clamp every sub-score into 0-10 even if the AI misbehaves
                subs = {k: max(0.0, min(10.0, float(rubric_raw.get(k, 0))))
                        for k in WEIGHTS}
                # Weighted sum of 0-10 scores → 0-100 scale
                data["match_score"] = round(
                    sum(subs[k] * WEIGHTS[k] for k in WEIGHTS) * 10)
                data["rubric_clamped"] = subs      # for the breakdown UI
                data["rubric_weights"] = WEIGHTS

                # Persist the FULL CV text so the annotated document can
                # re-render after any rerun (button clicks etc.)
                st.session_state.cv_full = extracted_text
                st.session_state.audit_data = data

            except json.JSONDecodeError:
                # Groq returned something that wasn't valid JSON
                st.error("❌ AI returned invalid data. Please try again.")
                st.stop()

            except Exception as e:
                # Any other error (network, API key, etc.)
                st.error(f"❌ API Error: {e}")
                st.stop()

    # ── DISPLAY RESULTS ──────────────────────────────────────────────────
    # This runs separately from the pipeline above.
    # It checks the notepad (session_state) — if analysis data exists, show it.
    # This means results persist even after other button clicks.

    if st.session_state.audit_data:
        data = st.session_state.audit_data   # Shortcut variable

        st.divider()

        # ── Score card ──
        score   = data.get("match_score", 0)      # .get() safely retrieves value, default 0
        verdict = data.get("verdict", "")

        # Determine border colour based on score (like a traffic light)
        if score >= 70:
            circle_color = "#34d399"   # Green
        elif score >= 45:
            circle_color = ACCENT      # Mid score — theme accent (cyan/indigo)
        else:
            circle_color = "#f87171"   # Red

        st.markdown(f"""
        <div class="score-card">
            <div class="score-circle" style="border-color:{circle_color};color:{circle_color}">
                {score}
            </div>
            <div>
                <div class="score-label">Overall Match Score</div>
                <div class="score-verdict">{verdict}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Score breakdown — shows the arithmetic behind the number ──
        # Turns the score from a mystery into a receipt. Each line:
        #   sub-score/10  ×  weight  =  points contributed
        with st.expander("🧮 How this score was computed", expanded=False):
            subs    = data.get("rubric_clamped", {})
            weights = data.get("rubric_weights", {})
            if subs and weights:
                nice = {"technical_skills": "Technical skills",
                        "experience_relevance": "Experience relevance",
                        "education_fit": "Education fit",
                        "evidence_quality": "Evidence quality"}
                for k, w in weights.items():
                    pts = subs[k] * w * 10          # this component's points
                    st.markdown(
                        f"<div style='display:flex;justify-content:space-between;"
                        f"font-size:0.87rem;padding:3px 0'>"
                        f"<span>{nice.get(k, k)} — <b>{subs[k]:.0f}/10</b>"
                        f" × weight {w:.2f}</span>"
                        f"<span style='color:{ACCENT};font-weight:600'>"
                        f"+{pts:.0f} pts</span></div>",
                        unsafe_allow_html=True)
                st.markdown(
                    f"<hr style='margin:6px 0;border-color:{BORDER}'>"
                    f"<div style='display:flex;justify-content:space-between;"
                    f"font-weight:700'><span>Total</span>"
                    f"<span style='color:{ACCENT}'>{score}/100</span></div>",
                    unsafe_allow_html=True)
            st.caption("AI-estimated sub-scores, deterministic weighted sum. "
                       "Indicative, not definitive — see it as a structured "
                       "second opinion, not a verdict.")

        # ── Badge row (Critical / Warnings / Good counts) ──
        st.markdown(f"""
        <div class="badge-row">
            <div class="badge badge-red">🔴 {data.get("critical_count", 0)} Critical</div>
            <div class="badge badge-amber">🟡 {data.get("warning_count", 0)} Warnings</div>
            <div class="badge badge-green">🟢 {data.get("good_count", 0)} Strengths</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Two-column results layout ──
        res_left, res_right = st.columns(2, gap="large")

        with res_left:
            st.markdown(f"<h4 style='color:{TEXT}'>📝 Your CV — Annotated</h4>",
                        unsafe_allow_html=True)

            # ── Build the full highlighted document ────────────────────
            # 1. html.escape() the ENTIRE CV — turns <, >, & into safe
            #    text so nothing in the CV can inject markup.
            # 2. For each AI-returned phrase, escape it the SAME way,
            #    then wrap its occurrence in a coloured <span>.
            #    Both sides escaped identically → exact string match.
            # 3. white-space:pre-wrap in .cv-doc preserves line breaks.
            import html as html_lib

            cv_raw = st.session_state.get("cv_full", "")
            if cv_raw:
                doc = html_lib.escape(cv_raw)

                # Weak first, then strong — if the AI accidentally returns
                # overlapping phrases, strong (applied last) wins visually.
                for ph in data.get("weak_phrases", []):
                    ph_esc = html_lib.escape(ph)
                    if ph_esc and ph_esc in doc:
                        doc = doc.replace(
                            ph_esc,
                            f'<span class="hl-bad">{ph_esc}</span>')
                for ph in data.get("strong_phrases", []):
                    ph_esc = html_lib.escape(ph)
                    if ph_esc and ph_esc in doc:
                        doc = doc.replace(
                            ph_esc,
                            f'<span class="hl-good">{ph_esc}</span>')

                # Legend so the colours explain themselves
                st.markdown(
                    f'<span class="legend-chip" style="background:'
                    f'rgba(52,211,153,0.16);color:{GREEN};border:1px solid {GREEN}">'
                    f'■ strength</span>'
                    f'<span class="legend-chip" style="background:'
                    f'rgba(248,113,113,0.14);color:{RED};border:1px solid {RED}">'
                    f'■ needs work</span>',
                    unsafe_allow_html=True)

                # The whole CV, scrollable, with highlights baked in
                st.markdown(f'<div class="cv-doc">{doc}</div>',
                            unsafe_allow_html=True)
            else:
                st.info("Re-run the audit to load your CV text.")

            comment = data.get("cv_comment", "")
            if comment:
                st.caption(f"💡 {comment}")

            # ── ATS Keyword Scanner ──
            # Novel feature: shows which job keywords appear/are missing in the CV
            st.markdown(f"<h4 style='color:{TEXT};margin-top:1.5rem'>🔍 ATS Keyword Scanner</h4>",
                        unsafe_allow_html=True)
            st.caption("Keywords from the job description — green = found in your CV, red = missing")

            found_html   = "".join(f'<span class="kw-found">✓ {k}</span>'
                                    for k in data.get("ats_keywords_found", []))
            missing_html = "".join(f'<span class="kw-missing">✗ {k}</span>'
                                    for k in data.get("ats_keywords_missing", []))

            st.markdown(found_html + missing_html, unsafe_allow_html=True)

            # ── Skill Coverage bars ────────────────────────────────────
            # WHY IT WASN'T SHOWING: this section never existed in the
            # code — the mockup had it, the app didn't. The AI also
            # wasn't asked to return coverage data. Both fixed:
            # the schema above now requests "skill_coverage", and the
            # loop below draws one bar per skill.
            coverage = data.get("skill_coverage", [])
            if coverage:
                st.markdown(
                    f"<h4 style='color:{TEXT};margin-top:1.5rem'>📊 Skill Coverage</h4>",
                    unsafe_allow_html=True)
                st.caption("How strongly your CV evidences each core skill the role demands")

                for item in coverage:
                    skill = item.get("skill", "")
                    pct   = max(0, min(100, int(item.get("percent", 0))))  # clamp 0-100

                    # Traffic-light fill colour by strength
                    #   ≥70 green (solid) · 40-69 amber (developing) · <40 red (gap)
                    if pct >= 70:
                        fill = GREEN
                    elif pct >= 40:
                        fill = AMBER
                    else:
                        fill = RED

                    # Two-layer bar: full-width grey track + coloured fill
                    # whose width IS the percentage (width:{pct}%).
                    st.markdown(f"""
                    <div class="cov-row">
                        <div class="cov-head">
                            <span class="cov-name">{skill}</span>
                            <span class="cov-pct">{pct}%</span>
                        </div>
                        <div class="cov-track">
                            <div class="cov-fill" style="width:{pct}%;background:{fill}"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        with res_right:
            st.markdown(f"<h4 style='color:{TEXT}'>🛠 Audit Findings</h4>", unsafe_allow_html=True)

            # Three tabs for different severity levels
            tab_crit, tab_warn, tab_good = st.tabs(["🔴 Critical", "🟡 Warnings", "🟢 Strengths"])

            with tab_crit:
                issues = data.get("critical_issues", [])
                if issues:
                    for issue in issues:
                        st.markdown(f"• {issue}")
                else:
                    st.success("No critical issues found!")

            with tab_warn:
                warnings = data.get("warning_issues", [])
                if warnings:
                    for w in warnings:
                        st.markdown(f"• {w}")
                else:
                    st.success("No warnings!")

            with tab_good:
                goods = data.get("good_points", [])
                if goods:
                    for g in goods:
                        st.markdown(f"• {g}")
                else:
                    st.info("Run an audit to see your strengths.")


# ════════════════════════════════════════════════════════════════════════
# SECTION 2: PROJECT ARCHITECT
# ════════════════════════════════════════════════════════════════════════

elif app_mode == "🛠 Project Architect":

    st.markdown(
        f"<h2 style='font-family:Space Grotesk;margin-bottom:0.25rem'>🛠 Project Architect</h2>"
        f"<p style='color:{MUTED};font-size:0.9rem'>"
        f"Turns your skill gaps into a GitHub project blueprint you can build this weekend.</p>",
        unsafe_allow_html=True
    )
    st.divider()

    # Guard: must run Resume Auditor first to have gaps to fix
    if not st.session_state.audit_data:
        st.markdown(
            f"<div class='callout'>⚠️ Run a <b>Resume Audit</b> first to identify your gaps.<br>"
            f"The Project Architect turns those gaps into buildable projects.</div>",
            unsafe_allow_html=True
        )

    else:
        # Show what gaps we're building projects for
        gaps = st.session_state.audit_data.get("critical_issues", [])

        st.markdown(f"<h4 style='color:{TEXT}'>📋 Gaps being addressed:</h4>", unsafe_allow_html=True)
        for g in gaps:
            st.markdown(f"• {g}")

        st.divider()

        col_a, col_b = st.columns(2)
        with col_a:
            # Let user customise what kind of project they want
            project_type = st.selectbox(
                "Project type",
                ["Web App", "Data Analysis", "Machine Learning", "API / Backend", "Automation Script"]
            )
        with col_b:
            timeline = st.selectbox("Build timeline", ["Weekend (2 days)", "1 Week", "2 Weeks"])

        if st.button("⚡ Generate Project Blueprint", type="primary", use_container_width=True):
            with st.spinner("Engineering your project blueprint..."):

                architect_prompt = f"""
You are a senior software engineer mentoring a student.
Their CV audit identified these skill gaps: {gaps}
They want to build a '{project_type}' project in '{timeline}'.

Generate a professional GitHub README.md blueprint in raw Markdown.
Include:
1. A professional project title (framed as a BUSINESS problem, not a learning exercise)
2. The business problem it solves (1 paragraph)
3. Tech stack (as a bullet list with reasons for each choice)
4. ASCII directory tree of the repo structure
5. Step-by-step development checklist (10 steps maximum)
6. How this project closes the identified skill gaps (link each gap to a section)

Do NOT include pleasantries. Output raw Markdown only.
"""

                blueprint_resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": architect_prompt}],
                    temperature=0.3
                )

                # FIX: .choices[0].message.content (NOT .choices.message.content)
                # Old code was missing [0] — choices is a list
                blueprint_text = blueprint_resp.choices[0].message.content.strip()

            st.subheader("Your GitHub README Blueprint")
            # text_area so the user can copy the Markdown easily
            st.text_area("Copy this into your GitHub repo README.md", value=blueprint_text, height=450)
            st.success("✅ Copy the blueprint above, create a GitHub repo, and start building!")


# ════════════════════════════════════════════════════════════════════════
# SECTION 3: INTERVIEW COACH
# ════════════════════════════════════════════════════════════════════════

elif app_mode == "💬 Interview Coach":

    st.markdown(
        f"<h2 style='font-family:Space Grotesk;margin-bottom:0.25rem'>💬 Interview Coach</h2>"
        f"<p style='color:{MUTED};font-size:0.9rem'>"
        f"Practice answering role-specific interview questions and get instant AI feedback.</p>",
        unsafe_allow_html=True
    )
    st.divider()

    # Two modes: question generation OR code practice
    coach_mode = st.radio(
        "Choose practice mode",
        ["🎤 Behavioural Questions", "💻 Code Challenge"],
        horizontal=True    # Show side-by-side, not stacked
    )
    st.divider()

    if coach_mode == "🎤 Behavioural Questions":

        if not st.session_state.audit_data:
            st.markdown(
                f"<div class='callout'>Run a Resume Audit first — I'll generate questions "
                f"targeting YOUR specific gaps.</div>",
                unsafe_allow_html=True
            )
        else:
            gaps    = st.session_state.audit_data.get("critical_issues", [])
            verdict = st.session_state.audit_data.get("verdict", "")

            # Generate targeted interview questions based on the audit gaps
            if st.button("⚡ Generate Interview Questions", type="primary"):
                with st.spinner("Preparing questions targeting your gaps..."):

                    interview_prompt = f"""
You are an experienced graduate recruiter at a top firm.
The candidate's profile verdict was: '{verdict}'
Their critical gaps are: {gaps}

Generate exactly 5 interview questions that specifically probe these gaps.
For each question, include:
- The question itself
- What it is testing (the gap it probes)
- A model answer structure (2-3 sentences, STAR format guidance)

Format as a numbered list. Be direct and realistic — these should feel like real interview questions.
"""

                    q_resp = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": interview_prompt}],
                        temperature=0.4
                    )

                    # FIX: choices[0] not choices
                    questions_text = q_resp.choices[0].message.content.strip()

                st.markdown(questions_text)

    elif coach_mode == "💻 Code Challenge":

        st.markdown(
            f"<p style='color:{MUTED}'>Write Python code to solve the challenge below, "
            f"then submit for AI feedback.</p>",
            unsafe_allow_html=True
        )

        # Challenge selector
        challenge = st.selectbox("Select a challenge", [
            "Remove duplicates from a list while maintaining order",
            "Flatten a nested list",
            "Find the most common element in a list",
            "Check if a string is a palindrome",
            "Write a function to perform a binary search"
        ])

        # Code editor
        student_code = st.text_area(
            "Your Python solution",
            value=f"def solution():\n    # Solve: {challenge}\n    pass",
            height=180
        )

        if st.button("⚡ Evaluate My Code", type="primary"):
            with st.spinner("Evaluating your code..."):

                eval_prompt = f"""
You are a senior Python engineer reviewing a junior developer's code submission.
Challenge: '{challenge}'
Submitted code:
{student_code}

Provide:
1. Correctness verdict (does it solve the challenge? yes/no/partial)
2. Time complexity (Big O notation with a plain English explanation)
3. Space complexity (Big O)
4. Two specific improvements (code quality, edge cases, or efficiency)
5. An optimised solution with inline comments

Be concise and direct. Format with clear headings.
"""

                eval_resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": eval_prompt}],
                    temperature=0.1
                )

                # FIX: choices[0] not choices
                feedback = eval_resp.choices[0].message.content.strip()

            st.subheader("🏁 Code Review Feedback")
            st.markdown(feedback)


# ════════════════════════════════════════════════════════════════════════
# SECTION 4: LEARNING PATH (Novel Feature)
# ════════════════════════════════════════════════════════════════════════

elif app_mode == "📚 Learning Path":

    st.markdown(
        f"<h2 style='font-family:Space Grotesk;margin-bottom:0.25rem'>📚 Learning Path</h2>"
        f"<p style='color:{MUTED};font-size:0.9rem'>"
        f"A personalised, free-resource study plan to close your gaps in 4 weeks.</p>",
        unsafe_allow_html=True
    )
    st.divider()

    if not st.session_state.audit_data:
        st.markdown(
            f"<div class='callout'>Run a <b>Resume Audit</b> first — I'll build a "
            f"personalised learning plan from your gaps.</div>",
            unsafe_allow_html=True
        )
    else:
        gaps = st.session_state.audit_data.get("critical_issues", [])
        missing_keywords = st.session_state.audit_data.get("ats_keywords_missing", [])

        all_gaps = list(set(gaps + missing_keywords))   # Combine, remove duplicates

        col1, col2 = st.columns(2)
        with col1:
            weeks = st.slider("Study plan length (weeks)", 1, 8, 4)
        with col2:
            hours = st.slider("Hours available per week", 2, 20, 8)

        if st.button("⚡ Generate My Learning Plan", type="primary"):
            with st.spinner("Building your personalised study plan..."):

                plan_prompt = f"""
You are a career coach building a practical study plan for a graduate.
Their skill gaps are: {all_gaps}
Available time: {hours} hours per week for {weeks} weeks.

Build a week-by-week plan that:
1. Prioritises the most impactful gaps first
2. Recommends ONLY free resources (YouTube, freeCodeCamp, Kaggle, official docs, Coursera audit)
3. Includes one small hands-on project per gap to prove the skill
4. Is realistic for the time available

Format as a Markdown table with columns: Week | Focus Skill | Resource | Hours | Mini-Project
Then add a 'What success looks like' section at the end.
"""

                plan_resp = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": plan_prompt}],
                    temperature=0.3
                )

                # FIX: choices[0] not choices
                plan_text = plan_resp.choices[0].message.content.strip()

            st.markdown(plan_text)

