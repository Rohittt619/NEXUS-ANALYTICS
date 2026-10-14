"""
NEXUS-ANALYTICS Glassmorphism Theme Injector.

Injects custom CSS rules into Streamlit to produce a sleek, dark
enterprise executive decision cockpit with glowing neon accents.
"""
import streamlit as st

GLASS_THEME_CSS = """
<style>
/* Modern Cyberpunk / Enterprise Executive Palette */
:root {
    --bg-dark: #080D1A;
    --card-bg: rgba(14, 23, 42, 0.75);
    --border-glow: rgba(0, 240, 255, 0.25);
    --accent-cyan: #00F0FF;
    --accent-green: #00FF66;
    --accent-gold: #FFB800;
    --accent-magenta: #FF007A;
    --text-primary: #F8FAFC;
    --text-muted: #94A3B8;
}

/* Global Container Dark Background */
.stApp {
    background-color: var(--bg-dark);
    background-image: 
        radial-gradient(circle at 10% 10%, rgba(0, 240, 255, 0.10) 0px, transparent 40%),
        radial-gradient(circle at 90% 90%, rgba(0, 255, 102, 0.08) 0px, transparent 40%),
        radial-gradient(circle at 50% 50%, rgba(255, 0, 122, 0.05) 0px, transparent 60%);
    color: var(--text-primary);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Glassmorphism Cards */
.glass-card {
    background: var(--card-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--border-glow);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.5);
    transition: all 0.3s ease-in-out;
}

.glass-card:hover {
    border-color: var(--accent-cyan);
    box-shadow: 0 10px 40px 0 rgba(0, 240, 255, 0.25);
}

/* Title Styling */
.nexus-title {
    font-size: 2.8rem;
    font-weight: 900;
    background: linear-gradient(90deg, #00F0FF, #00FF66, #FFB800);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
    letter-spacing: -1px;
}

/* Metric Display Boxes */
.metric-box {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(0, 240, 255, 0.2);
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.metric-val {
    font-size: 2.0rem;
    font-weight: 800;
    color: var(--accent-cyan);
    text-shadow: 0 0 12px rgba(0, 240, 255, 0.4);
}

.metric-val-green {
    font-size: 2.0rem;
    font-weight: 800;
    color: var(--accent-green);
    text-shadow: 0 0 12px rgba(0, 255, 102, 0.4);
}

.metric-val-gold {
    font-size: 2.0rem;
    font-weight: 800;
    color: var(--accent-gold);
    text-shadow: 0 0 12px rgba(255, 184, 0, 0.4);
}

.metric-lbl {
    font-size: 0.85rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-top: 6px;
}

/* Status Badges */
.badge-champion {
    background: rgba(0, 255, 102, 0.2);
    color: #00FF66;
    border: 1px solid #00FF66;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 700;
}

.badge-risk {
    background: rgba(255, 0, 122, 0.2);
    color: #FF007A;
    border: 1px solid #FF007A;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 700;
}

.badge-gold {
    background: rgba(255, 184, 0, 0.2);
    color: #FFB800;
    border: 1px solid #FFB800;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 700;
}
</style>
"""


def inject_glass_theme() -> None:
    """Inject custom CSS rules into Streamlit head."""
    st.markdown(GLASS_THEME_CSS, unsafe_allow_html=True)
