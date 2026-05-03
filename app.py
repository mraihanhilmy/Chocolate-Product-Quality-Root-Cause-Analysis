import streamlit as st
import pandas as pd

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Root Cause Analyzer – Chocolate QA",
    page_icon="🍫",
    layout="wide",
)

# ─── Acronym Glossary ───────────────────────────────────────────────────────
ACRONYMS = {
    "RM": "Raw Materials",
    "REMU": "Raw Material type Emulsifier",
    "QC": "Quality Control",
    "PQ": "Process Quality / In-Line Quality Control",
    "R&D": "Research and Development",
    "ST": "Storage Tank (post-refining/conching transit storage)",
    "SVT": "Service Tank (stores chocolate from ST to feed the depositor)",
}

# ─── Load & Parse Data ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_excel(
        "Possible_Causes_for_Physical___Chemical_Problems_in_Finished_Goods_M_Raihan_Hilmy.xlsx",
        header=None,
    )
    # Drop header row
    df = df.iloc[1:].reset_index(drop=True)
    df.columns = ["product_type", "quality_issue", "why1", "why2", "why3", "why4", "why5", "why6", "notes"]

    # Forward-fill empty cells (NaN or same as previous)
    for col in ["product_type", "quality_issue", "why1", "why2", "why3", "why4", "why5"]:
        df[col] = df[col].ffill()

    # Normalize whitespace
    for col in ["product_type", "quality_issue", "why1", "why2", "why3", "why4", "why5", "why6"]:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace("nan", None)
        df[col] = df[col].replace("", None)

    return df

df = load_data()

# ─── Helpers ────────────────────────────────────────────────────────────────
WHY_COLS = ["why1", "why2", "why3", "why4", "why5", "why6"]
WHY_LABELS = ["Why 1", "Why 2", "Why 3", "Why 4", "Why 5", "Why 6"]

def get_options(df, filters: dict, col: str):
    """Return unique non-null values for `col` after applying `filters`."""
    mask = pd.Series([True] * len(df))
    for k, v in filters.items():
        mask &= df[k] == v
    vals = df.loc[mask, col].dropna().unique().tolist()
    return sorted(set(v for v in vals if v))

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #1a0a00; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #2c1502; }

    /* Cards */
    .why-card {
        background: linear-gradient(135deg, #3d1f00 0%, #2c1502 100%);
        border: 1px solid #6b3a00;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .why-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #c8860a;
        margin-bottom: 4px;
    }
    .why-text {
        font-size: 0.97rem;
        color: #f5e6d0;
        line-height: 1.5;
    }

    /* Root cause highlight */
    .root-card {
        background: linear-gradient(135deg, #5a2d00 0%, #3d1500 100%);
        border: 2px solid #e8960a;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 12px;
    }
    .root-label {
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #e8960a;
        margin-bottom: 6px;
    }
    .root-text {
        font-size: 1.05rem;
        font-weight: 600;
        color: #ffe8b0;
        line-height: 1.5;
    }

    /* Breadcrumb */
    .breadcrumb {
        font-size: 0.8rem;
        color: #a0714a;
        margin-bottom: 20px;
        padding: 8px 14px;
        background: #2c1502;
        border-radius: 8px;
        border-left: 3px solid #6b3a00;
    }

    /* Section headers */
    .section-header {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #c8860a;
        margin-top: 6px;
        margin-bottom: 4px;
    }

    /* Selectbox labels */
    label { color: #f5e6d0 !important; }

    /* Divider */
    hr { border-color: #4a2500; }

    /* Acronym table */
    .acro-row { display: flex; gap: 12px; margin-bottom: 6px; }
    .acro-key {
        background: #4a2500;
        color: #f5c842;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.82rem;
        min-width: 52px;
        text-align: center;
    }
    .acro-val { color: #d4b896; font-size: 0.82rem; line-height: 1.4; }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar: Glossary ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🍫 Chocolate QA")
    st.markdown("### Root Cause Analyzer")
    st.markdown("---")
    st.markdown("#### 📖 Acronym Glossary")
    for abbr, meaning in ACRONYMS.items():
        st.markdown(
            f'<div class="acro-row">'
            f'<div class="acro-key">{abbr}</div>'
            f'<div class="acro-val">{meaning}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown("---")
    st.markdown(
        '<div style="color:#a0714a;font-size:0.75rem;">Select a product and problem type '
        'in the main area to begin drilling into root causes.</div>',
        unsafe_allow_html=True,
    )

# ─── Main Content ────────────────────────────────────────────────────────────
st.markdown("## 🍫 Quality Problem Root Cause Analyzer")
st.markdown(
    "Navigate through each level by selecting an option. "
    "The tool will guide you from the first symptom down to the deepest root cause."
)
st.markdown("---")

# Initialize session state
for key in ["product", "issue", *WHY_COLS]:
    if key not in st.session_state:
        st.session_state[key] = None

def reset_from(level: int):
    """Reset all selections at and after `level` (0=product, 1=issue, 2=why1, ...)."""
    if level <= 0:
        st.session_state["product"] = None
    if level <= 1:
        st.session_state["issue"] = None
    for i, col in enumerate(WHY_COLS):
        if level <= i + 2:
            st.session_state[col] = None

# ── Row 1: Product & Issue ───────────────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<div class="section-header">1 · Product Type</div>', unsafe_allow_html=True)
    product_opts = sorted(df["product_type"].dropna().unique().tolist())
    sel_product = st.selectbox(
        "Select product type",
        options=["— select —"] + product_opts,
        index=0 if st.session_state["product"] is None
              else (["— select —"] + product_opts).index(st.session_state["product"]),
        label_visibility="collapsed",
        key="_sel_product",
    )
    if sel_product != "— select —" and sel_product != st.session_state["product"]:
        reset_from(0)
        st.session_state["product"] = sel_product
        st.rerun()
    elif sel_product == "— select —" and st.session_state["product"] is not None:
        reset_from(0)
        st.rerun()

with col_b:
    if st.session_state["product"]:
        st.markdown('<div class="section-header">2 · Quality Issue</div>', unsafe_allow_html=True)
        issue_opts = get_options(df, {"product_type": st.session_state["product"]}, "quality_issue")
        sel_issue = st.selectbox(
            "Select quality issue",
            options=["— select —"] + issue_opts,
            index=0 if st.session_state["issue"] is None
                  else (["— select —"] + issue_opts).index(st.session_state["issue"])
                       if st.session_state["issue"] in issue_opts else 0,
            label_visibility="collapsed",
            key="_sel_issue",
        )
        if sel_issue != "— select —" and sel_issue != st.session_state["issue"]:
            reset_from(1)
            st.session_state["product"] = sel_product
            st.session_state["issue"] = sel_issue
            st.rerun()
        elif sel_issue == "— select —" and st.session_state["issue"] is not None:
            reset_from(1)
            st.rerun()

# ── Why Cascade ──────────────────────────────────────────────────────────────
if st.session_state["product"] and st.session_state["issue"]:
    st.markdown("---")

    # Build breadcrumb
    breadcrumb_parts = [st.session_state["product"], st.session_state["issue"]]
    for col in WHY_COLS:
        if st.session_state[col]:
            breadcrumb_parts.append(st.session_state[col])
        else:
            break
    st.markdown(
        f'<div class="breadcrumb">📍 ' + " &rsaquo; ".join(breadcrumb_parts) + "</div>",
        unsafe_allow_html=True,
    )

    # Display confirmed selections as cards and prompt next why
    confirmed_whys = []
    for col in WHY_COLS:
        if st.session_state[col]:
            confirmed_whys.append((col, st.session_state[col]))

    # Show confirmed why cards
    for i, (col, val) in enumerate(confirmed_whys):
        label = WHY_LABELS[i]
        st.markdown(
            f'<div class="why-card">'
            f'<div class="why-label">{label}</div>'
            f'<div class="why-text">{val}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Determine next why to show
    next_idx = len(confirmed_whys)
    if next_idx < len(WHY_COLS):
        next_col = WHY_COLS[next_idx]
        next_label = WHY_LABELS[next_idx]

        # Build filter dict for this level
        filters = {
            "product_type": st.session_state["product"],
            "quality_issue": st.session_state["issue"],
        }
        for col, val in confirmed_whys:
            filters[col] = val

        next_opts = get_options(df, filters, next_col)

        if next_opts:
            st.markdown(
                f'<div class="section-header">{next_idx + 3} · {next_label}</div>',
                unsafe_allow_html=True,
            )
            sel_next = st.selectbox(
                f"Select {next_label}",
                options=["— select —"] + next_opts,
                index=0,
                label_visibility="collapsed",
                key=f"_sel_{next_col}",
            )
            if sel_next != "— select —":
                st.session_state[next_col] = sel_next
                st.rerun()
        else:
            # No deeper why → last confirmed is the root cause
            if confirmed_whys:
                last_col, last_val = confirmed_whys[-1]
                last_label = WHY_LABELS[len(confirmed_whys) - 1]
                # Re-render last card as root cause
                # (already shown above, just add root cause banner)
                st.markdown(
                    f'<div class="root-card">'
                    f'<div class="root-label">🎯 Root Cause Identified ({last_label})</div>'
                    f'<div class="root-text">{last_val}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
    else:
        # All 6 whys selected — deepest level
        if confirmed_whys:
            last_col, last_val = confirmed_whys[-1]
            last_label = WHY_LABELS[len(confirmed_whys) - 1]
            st.markdown(
                f'<div class="root-card">'
                f'<div class="root-label">🎯 Root Cause Identified ({last_label})</div>'
                f'<div class="root-text">{last_val}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )



    # ── Reset Button ──────────────────────────────────────────────────────────
    st.markdown("")
    if st.button("🔄 Start Over", type="secondary"):
        reset_from(0)
        st.rerun()
