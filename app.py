import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(
    page_title="Busy Bees - AI Churn Risk Detector",
    page_icon="🐝",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #F5F0E8; }
.main .block-container { padding: 2rem 3rem; max-width: 1100px; }

.header-bar {
    background: linear-gradient(135deg, #5C3317 0%, #7B4A2D 100%);
    padding: 2rem 2.5rem; border-radius: 16px;
    margin-bottom: 2rem; color: white;
}
.header-bar h1 { color: white; font-size: 2rem; font-weight: 700; margin: 0 0 0.3rem 0; }
.header-bar p  { color: #E8D5B7; font-size: 0.95rem; margin: 0; }

.input-card {
    background: white; border-radius: 16px;
    padding: 2rem; margin-bottom: 1.5rem;
    border: 1px solid #E8D5B7;
    box-shadow: 0 2px 8px rgba(92,51,23,0.08);
}
.input-card h3 { color: #5C3317; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem; }

.result-card {
    background: white; border-radius: 16px;
    padding: 2rem; margin-bottom: 1rem;
    border: 1px solid #E8D5B7;
    box-shadow: 0 2px 8px rgba(92,51,23,0.08);
}

.risk-badge-HIGH {
    background: #5C3317; color: white;
    padding: 1.2rem 2rem; border-radius: 12px;
    font-size: 1.6rem; font-weight: 700;
    text-align: center; margin: 1rem 0;
    letter-spacing: 0.5px;
}
.risk-badge-MEDIUM {
    background: #7B4A2D; color: white;
    padding: 1.2rem 2rem; border-radius: 12px;
    font-size: 1.6rem; font-weight: 700;
    text-align: center; margin: 1rem 0;
}
.risk-badge-LOW {
    background: #E8D5B7; color: #5C3317;
    padding: 1.2rem 2rem; border-radius: 12px;
    font-size: 1.6rem; font-weight: 700;
    text-align: center; margin: 1rem 0;
    border: 2px solid #C49A6C;
}

.prob-bar-bg {
    background: #E8D5B7; border-radius: 8px;
    height: 18px; margin: 0.5rem 0 1rem 0; overflow: hidden;
}
.prob-bar-fill {
    height: 18px; border-radius: 8px;
    background: #5C3317; transition: width 0.6s ease;
}

.driver-item {
    background: #F5F0E8; border-left: 4px solid #5C3317;
    padding: 0.7rem 1rem; margin: 0.4rem 0;
    border-radius: 0 8px 8px 0; color: #5C3317;
    font-size: 0.95rem;
}
.rec-item {
    background: #5C3317; color: white;
    padding: 0.7rem 1rem; margin: 0.4rem 0;
    border-radius: 8px; font-size: 0.95rem;
}

.metric-box {
    background: white; border-radius: 12px;
    padding: 1rem 1.5rem; text-align: center;
    border: 1px solid #E8D5B7;
    box-shadow: 0 1px 4px rgba(92,51,23,0.06);
}
.metric-box .val { font-size: 1.8rem; font-weight: 700; color: #5C3317; }
.metric-box .lbl { font-size: 0.8rem; color: #7B4A2D; margin-top: 0.2rem; }

.example-btn {
    background: #E8D5B7; color: #5C3317; border: none;
    padding: 0.4rem 0.9rem; border-radius: 20px;
    font-size: 0.85rem; cursor: pointer; margin: 0.2rem;
    font-weight: 500;
}
.stButton > button {
    background: #5C3317 !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 600 !important; font-size: 1rem !important;
    padding: 0.7rem 2rem !important;
    transition: background 0.2s !important;
}
.stButton > button:hover { background: #7B4A2D !important; }

.sidebar-card {
    background: #5C3317; color: white;
    border-radius: 12px; padding: 1.2rem;
    margin-bottom: 1rem;
}
section[data-testid="stSidebar"] { background-color: #F5F0E8; }
section[data-testid="stSidebar"] * { color: #5C3317; }

.footer-note {
    text-align: center; color: #7B4A2D;
    font-size: 0.8rem; margin-top: 2rem;
    padding-top: 1rem; border-top: 1px solid #E8D5B7;
}
</style>
""", unsafe_allow_html=True)

EXPLICIT_CHURN = [
    "stop taking jobs","leave the platform","quit","done with this",
    "not worth my time","different way to make money","i'm done",
    "not coming back","figure something else out","not working out",
    "take a break","thinking about stopping","want to stop",
    "considering leaving","might leave","moving on","giving up"
]
FRUSTRATION = [
    "frustrated","frustrating","ridiculous","unacceptable","terrible","awful",
    "horrible","disappointed","disgusting","useless","nothing has happened",
    "no one has responded","still waiting","fed up","sick of","not okay",
    "overwhelmed","exhausted","stressed","burnt out","annoyed","angry"
]
FINANCIAL = [
    "need that money","can't afford","hurting my income","not making enough",
    "not making much","already not making","missed jobs","losing money",
    "need the income","not paid","payment issue","no payment"
]
WORKLOAD = [
    "overwhelmed","too much","schedule","workload","busy",
    "can't keep up","exhausted","burnout","no time","too many jobs"
]
POSITIVE = [
    "love","great","amazing","thank you","helpful","excited",
    "happy","appreciate","wonderful","glad","enjoy","fantastic","perfect"
]

vader = SentimentIntensityAnalyzer()

def score_message(text):
    t = text.lower()
    sentiment = vader.polarity_scores(text)["compound"]
    explicit     = any(p in t for p in EXPLICIT_CHURN)
    frust_count  = sum(1 for p in FRUSTRATION if p in t)
    financial    = any(p in t for p in FINANCIAL)
    workload     = any(p in t for p in WORKLOAD)
    positive     = any(p in t for p in POSITIVE)
    short_msg    = len(text.split()) < 8

    score = 0.0
    drivers = []
    recs = []

    if explicit:
        score += 0.50
        drivers.append("Explicit churn language detected")
        recs.append("Immediate personal outreach - retention call within 24 hours")
    if sentiment < -0.4:
        score += 0.25
        drivers.append("Strongly negative sentiment (" + str(round(sentiment,2)) + ")")
        recs.append("Empathy-first response - acknowledge frustration before solutions")
    elif sentiment < -0.1:
        score += 0.12
        drivers.append("Negative sentiment (" + str(round(sentiment,2)) + ")")
    if frust_count >= 2:
        score += 0.20
        drivers.append("Multiple frustration signals (" + str(frust_count) + " detected)")
        recs.append("Escalate to human support agent")
    elif frust_count == 1:
        score += 0.10
        drivers.append("Frustration language present")
    if financial:
        score += 0.20
        drivers.append("Financial distress language detected")
        recs.append("Offer earnings boost or guaranteed booking incentive")
    if workload:
        score += 0.15
        drivers.append("Workload or scheduling stress signals")
        recs.append("Offer flexible scheduling options")
    if short_msg and not positive:
        score += 0.08
        drivers.append("Disengaged message style (very brief response)")
    if positive and sentiment > 0.3:
        score = max(0, score - 0.25)
    score = min(score, 1.0)

    if score >= 0.55:
        risk = "HIGH"
        if not recs: recs.append("Priority: account manager check-in call")
    elif score >= 0.28:
        risk = "MEDIUM"
        if not recs: recs.append("Standard: automated engagement nudge + follow-up")
    else:
        risk = "LOW"
        if not recs: recs.append("Monitor: no immediate action required")

    if not drivers:
        drivers = ["No significant churn signals detected", "Positive or neutral engagement"]

    return {"risk": risk, "score": score, "sentiment": sentiment, "drivers": drivers, "recs": recs}

# ── HEADER ────────────────────────────────────────────────────────
st.markdown("""
<div class="header-bar">
  <h1>🐝 Busy Bees — AI Churn Risk Detector</h1>
  <p>ASU Capstone 2026 &nbsp;|&nbsp; Froude, Theodore, Tummala, Traore &nbsp;|&nbsp; Powered by VADER + Churn Signal Detection</p>
</div>
""", unsafe_allow_html=True)

# ── TOP METRICS ───────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="metric-box"><div class="val">4,139</div><div class="lbl">Active sitters scored</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-box"><div class="val">93.7%</div><div class="lbl">Annual churn rate</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-box"><div class="val">92.27%</div><div class="lbl">System eval score</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="metric-box"><div class="val">$327K</div><div class="lbl">3-year value (10% reduction)</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── MAIN LAYOUT ───────────────────────────────────────────────────
left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.markdown('<div class="input-card"><h3>Type a sitter message</h3>', unsafe_allow_html=True)
    st.markdown("Enter any message a sitter might send to support — or try one of the examples below.")

    # Example buttons as selectbox
    examples = {
        "-- choose an example or type your own --": "",
        "HIGH: overwhelmed + thinking of stopping": "I'm overwhelmed with my schedule and thinking about stopping. It's just not worth it anymore.",
        "HIGH: payment dispute, 3 weeks waiting":   "I need that money. I've been waiting 3 weeks and nobody has responded. I'm done waiting.",
        "HIGH: app crash, missing jobs":            "The app keeps crashing and I've missed at least 4 jobs because of it. I can't afford this.",
        "MEDIUM: low job volume, discouraged":      "I haven't been getting many jobs lately. Not sure how much longer I can keep trying.",
        "MEDIUM: rating dispute":                   "I got a 1-star review that is completely unfair. This is directly hurting my income.",
        "LOW: happy, payment question":             "Hi! Just wanted to check on my payment. You guys are always so helpful. I have two more jobs booked this weekend!",
        "LOW: safety concern resolved":             "I'm better today, thank you for asking. It makes me feel better about continuing to use the platform.",
    }

    selected = st.selectbox("Quick examples:", list(examples.keys()), label_visibility="collapsed")
    prefill = examples[selected] if selected != "-- choose an example or type your own --" else ""

    user_input = st.text_area(
        "Your message:",
        value=prefill,
        height=160,
        placeholder="Type anything a sitter might say... e.g. 'I'm thinking about leaving the platform' or 'Thanks so much for your help!'",
        label_visibility="collapsed"
    )

    analyze = st.button("Analyze churn risk", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # How it works
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:1.2rem 1.5rem;border:1px solid #E8D5B7;margin-top:0.5rem;">
    <p style="color:#5C3317;font-weight:600;margin-bottom:0.5rem;">How it works</p>
    <p style="color:#7B4A2D;font-size:0.88rem;margin:0;">
    The AI scans for explicit churn phrases, sentiment trajectory, frustration signals,
    financial distress language, and engagement patterns. In the full system, these signals
    combine with 18 behavioral features per sitter and an XGBoost model trained on 4,139 sitters.
    </p>
    </div>
    """, unsafe_allow_html=True)

with right:
    if analyze and user_input.strip():
        r = score_message(user_input)
        pct = int(r["score"] * 100)
        sent_label = "Negative" if r["sentiment"] < -0.1 else "Positive" if r["sentiment"] > 0.1 else "Neutral"
        sent_color = "#A32D2D" if r["sentiment"] < -0.1 else "#2E7D52" if r["sentiment"] > 0.1 else "#5C3317"

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.markdown("#### Risk Assessment")
        st.markdown(f'<div class="risk-badge-{r["risk"]}">Risk Level: {r["risk"]} &nbsp;|&nbsp; {pct}% churn signal</div>', unsafe_allow_html=True)

        # Progress bar
        bar_color = "#5C3317" if r["risk"] == "HIGH" else "#7B4A2D" if r["risk"] == "MEDIUM" else "#C49A6C"
        st.markdown(f"""
        <div style="margin:0.5rem 0 1rem 0;">
          <div style="display:flex;justify-content:space-between;font-size:0.8rem;color:#7B4A2D;margin-bottom:4px;">
            <span>0%</span><span>Churn probability</span><span>100%</span>
          </div>
          <div class="prob-bar-bg">
            <div class="prob-bar-fill" style="width:{pct}%;background:{bar_color};"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f'<p style="color:#7B4A2D;font-size:0.9rem;margin-bottom:1rem;">Sentiment: <strong style="color:{sent_color};">{sent_label}</strong> &nbsp;(score: {r["sentiment"]:.3f})</p>', unsafe_allow_html=True)

        st.markdown("**Signals detected:**")
        for d in r["drivers"]:
            st.markdown(f'<div class="driver-item">{d}</div>', unsafe_allow_html=True)

        st.markdown("<br>**Recommended actions:**", unsafe_allow_html=True)
        for rec in r["recs"]:
            st.markdown(f'<div class="rec-item">{rec}</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    elif analyze:
        st.warning("Please enter a message to analyze.")
    else:
        st.markdown("""
        <div style="background:white;border-radius:16px;padding:3rem 2rem;text-align:center;
                    border:2px dashed #E8D5B7;color:#7B4A2D;">
          <div style="font-size:3rem;margin-bottom:1rem;">🐝</div>
          <p style="font-size:1.1rem;font-weight:600;color:#5C3317;">Ready to analyze</p>
          <p style="font-size:0.9rem;">Type a sitter message on the left and click<br><strong>Analyze churn risk</strong></p>
          <br>
          <p style="font-size:0.85rem;color:#C49A6C;">Try: "I'm thinking about stopping, it's not worth it"</p>
        </div>
        """, unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## About")
    st.markdown("""
**Busy Bees AI Churn Prediction System**
Built for ASU Capstone 2026

**Full system includes:**
- XGBoost model on 4,139 sitters
- 22 NLP features from Chatwoot
- SHAP explainability per sitter
- 30/60/90-day churn windows
- Three-agent CrewAI workflow
- Chatwoot live integration

**This demo:** VADER sentiment + churn signal detection
    """)
    st.markdown("---")
    st.markdown("**Risk tiers:**")
    st.markdown("🔴 **HIGH** - churn signal >55%")
    st.markdown("🟡 **MEDIUM** - signal 28-55%")
    st.markdown("🟢 **LOW** - signal <28%")
    st.markdown("---")
    st.markdown("**Team**")
    st.markdown("Lilith Froude")
    st.markdown("Pratiksha Theodore")
    st.markdown("Sunanda Tummala")
    st.markdown("Gemima Traore")
    st.markdown("*Arizona State University 2026*")

st.markdown('<div class="footer-note">Busy Bees AI Churn Prediction System | ASU Capstone 2026 | Powered by VADER Sentiment Analysis + Lexicon-Based Churn Detection</div>', unsafe_allow_html=True)
