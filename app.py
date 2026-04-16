import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.set_page_config(page_title="Busy Bees - AI Churn Risk Demo", page_icon="🐝", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #F5F0E8; }
h1, h2, h3 { color: #5C3317; }
.risk-HIGH { background-color:#5C3317;color:white;padding:20px;border-radius:10px;text-align:center;font-size:22px;font-weight:bold;margin:10px 0; }
.risk-MEDIUM { background-color:#7B4A2D;color:white;padding:20px;border-radius:10px;text-align:center;font-size:22px;font-weight:bold;margin:10px 0; }
.risk-LOW { background-color:#E8D5B7;color:#5C3317;padding:20px;border-radius:10px;text-align:center;font-size:22px;font-weight:bold;margin:10px 0; }
.driver-box { background-color:#E8D5B7;border-left:4px solid #5C3317;padding:10px 15px;margin:5px 0;border-radius:4px;color:#5C3317; }
.rec-box { background-color:#5C3317;color:white;padding:15px;border-radius:8px;margin:5px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown("# Busy Bees - AI Churn Risk Detector")
st.markdown("**ASU Capstone 2026** | Froude, Theodore, Tummala, Traore")
st.markdown("---")
st.markdown("Type a message a sitter might send to support and see the AI predict their churn risk in real time.")

EXPLICIT_CHURN = [
    "stop taking jobs","leave the platform","quit","done with this",
    "not worth my time","different way to make money","i'm done",
    "not coming back","figure something else out","not working out",
    "take a break","thinking about stopping","want to stop","considering leaving","might leave"
]
FRUSTRATION = [
    "frustrated","frustrating","ridiculous","unacceptable","terrible","awful",
    "horrible","disappointed","disgusting","useless","nothing has happened",
    "no one has responded","still waiting","fed up","sick of","not okay",
    "overwhelmed","exhausted","stressed","burnt out"
]
FINANCIAL = [
    "need that money","can't afford","hurting my income","not making enough",
    "not making much","already not making","missed jobs","losing money","need the income","not paid"
]
WORKLOAD = ["overwhelmed","too much","schedule","workload","busy","can't keep up","exhausted","burnout","no time"]
POSITIVE = ["love","great","amazing","thank you","helpful","excited","happy","appreciate","wonderful","glad","enjoy"]

vader = SentimentIntensityAnalyzer()

def score_message(text):
    t = text.lower()
    sentiment = vader.polarity_scores(text)["compound"]
    explicit   = any(p in t for p in EXPLICIT_CHURN)
    frust_count = sum(1 for p in FRUSTRATION if p in t)
    financial  = any(p in t for p in FINANCIAL)
    workload   = any(p in t for p in WORKLOAD)
    positive   = any(p in t for p in POSITIVE)
    short_msg  = len(text.split()) < 8

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
        drivers.append("Financial distress language")
        recs.append("Offer earnings boost or guaranteed booking incentive")
    if workload:
        score += 0.15
        drivers.append("Workload / scheduling stress signals")
        recs.append("Offer flexible scheduling options")
    if short_msg and not positive:
        score += 0.08
        drivers.append("Disengaged message style (very brief)")
    if positive and sentiment > 0.3:
        score = max(0, score - 0.25)
    score = min(score, 1.0)

    if score >= 0.55:
        risk = "HIGH"
        if not recs: recs.append("Priority: account manager check-in call")
    elif score >= 0.28:
        risk = "MEDIUM"
        if not recs: recs.append("Standard: automated engagement nudge")
    else:
        risk = "LOW"
        if not recs: recs.append("Monitor: no immediate action required")

    if not drivers:
        drivers = ["No significant churn signals detected", "Positive or neutral engagement"]

    return {"risk": risk, "score": score, "sentiment": sentiment, "drivers": drivers, "recs": recs}

examples = {
    "Select an example...": "",
    "HIGH risk - workload stress": "I'm overwhelmed with my schedule and thinking about stopping. It's just not worth it anymore.",
    "HIGH risk - payment dispute": "I need that money. I've been waiting 3 weeks and nobody has responded. I'm done waiting.",
    "MEDIUM risk - low engagement": "I haven't been getting many jobs lately. Not sure how much longer I can keep trying.",
    "LOW risk - happy sitter": "Hi! Just wanted to check on my payment. You guys are always so helpful. I have two more jobs booked!",
    "LOW risk - safety resolved": "I'm better today, thank you for asking. It makes me feel better about continuing to use the platform.",
}

selected = st.selectbox("Try an example or type your own:", list(examples.keys()))
prefill = examples[selected] if selected != "Select an example..." else ""
user_input = st.text_area("Sitter message:", value=prefill, height=120, placeholder="Type what a sitter might say to support...")

if st.button("Analyze churn risk", type="primary", use_container_width=True):
    if user_input.strip():
        r = score_message(user_input)
        st.markdown("---")
        st.markdown("## Results")
        st.markdown(
            '<div class="risk-' + r["risk"] + '">Risk Level: ' + r["risk"] + ' &nbsp;|&nbsp; Churn Probability: ' + str(round(r["score"]*100)) + '%</div>',
            unsafe_allow_html=True)
        sent_label = "Negative" if r["sentiment"] < -0.1 else "Positive" if r["sentiment"] > 0.1 else "Neutral"
        st.markdown("**Sentiment:** " + sent_label + " (" + str(round(r["sentiment"],3)) + ")")
        st.markdown("**Churn drivers detected:**")
        for d in r["drivers"]:
            st.markdown('<div class="driver-box">' + d + '</div>', unsafe_allow_html=True)
        st.markdown("**Recommended actions:**")
        for rec in r["recs"]:
            st.markdown('<div class="rec-box">' + rec + '</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.caption("Powered by VADER sentiment analysis + churn signal detection | ASU Capstone 2026")
    else:
        st.warning("Please enter a message to analyze.")

with st.sidebar:
    st.markdown("## About this demo")
    st.markdown("""
This shows a simplified version of the **Busy Bees AI Churn Prediction System**.

**Full system includes:**
- XGBoost model on 4,139 sitters
- 22 NLP features from Chatwoot
- SHAP explainability per sitter
- 30/60/90-day churn windows
- Three-agent CrewAI workflow

**Team:** Froude, Theodore, Tummala, Traore
**Arizona State University 2026**
    """)
    st.markdown("---")
    st.markdown("**Risk tiers:**")
    st.markdown("🔴 HIGH - over 55% signal score")
    st.markdown("🟡 MEDIUM - 28 to 55%")
    st.markdown("🟢 LOW - under 28%")
