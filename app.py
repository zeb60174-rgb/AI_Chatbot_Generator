import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# ── Load API key ──────────────────────────────────────────────────────────────
# Priority 1: Streamlit secrets (for Streamlit Community Cloud deployment)
# Priority 2: .env file (for local / Colab use)
load_dotenv()

def get_api_key():
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY", "")

GEMINI_API_KEY = get_api_key()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AutoBot Builder",
    page_icon="🤖",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    color: #e0e0ff;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800;
}

.hero-title {
    text-align: center;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.hero-sub {
    text-align: center;
    color: #94a3b8;
    font-size: 1rem;
    margin-bottom: 2rem;
    font-family: 'Space Mono', monospace;
}

.output-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}

.output-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #a78bfa;
    font-family: 'Space Mono', monospace;
    margin-bottom: 0.4rem;
}

.output-content {
    color: #e2e8f0;
    line-height: 1.7;
    white-space: pre-wrap;
}

.prompt-box {
    background: rgba(0,0,0,0.4);
    border: 1px solid rgba(96,165,250,0.4);
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    color: #93c5fd;
    white-space: pre-wrap;
    overflow-x: auto;
}

.stButton>button {
    background: linear-gradient(90deg, #7c3aed, #2563eb);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 2rem;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    width: 100%;
    transition: opacity 0.2s;
}
.stButton>button:hover { opacity: 0.85; }

.stTextInput>div>div>input,
.stSelectbox>div>div>div {
    background: rgba(255,255,255,0.05) !important;
    color: #e0e0ff !important;
    border: 1px solid rgba(167,139,250,0.3) !important;
    border-radius: 8px !important;
}

label { color: #cbd5e1 !important; }
.stSelectbox svg { fill: #a78bfa !important; }

.divider {
    border: none;
    border-top: 1px solid rgba(167,139,250,0.15);
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🤖 AutoBot Builder</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Generate a complete chatbot configuration in seconds</div>', unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── API Key check / input ─────────────────────────────────────────────────────
# if not GEMINI_API_KEY:
#     st.warning("⚠️ No API key found. Enter your Gemini API key below (for local use only).")
#     GEMINI_API_KEY = st.text_input("Gemini API Key", type="password", placeholder="AIza...")
#     if not GEMINI_API_KEY:
#         st.stop()
# ── API Key check (NO UI input) ───────────────────────────────────────────────
if not GEMINI_API_KEY:
    st.error(
        "❌ GEMINI_API_KEY not found.\n\n"
        "👉 For local use: create a .env file and add:\n"
        "GEMINI_API_KEY=your_key_here\n\n"
        "👉 For Streamlit Cloud: add it in Secrets."
    )
    st.stop()

# Configure Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    st.error(f"Failed to configure Gemini: {e}")
    st.stop()

# ── Input form ────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    bot_title = st.text_input(
        "🏷️ Chatbot Title",
        placeholder="e.g. Medical Assistant Bot",
        help="Give your chatbot a clear, descriptive name."
    )

with col2:
    domain = st.selectbox(
        "🌐 Domain",
        ["Education", "Medical", "Business", "Legal", "Tech Support", "Customer Service", "Custom"],
        help="The field or industry your chatbot will serve."
    )

col3, col4 = st.columns(2)

with col3:
    tone = st.selectbox(
        "🎭 Tone",
        ["Professional", "Friendly", "Funny", "Empathetic", "Concise"],
        help="How should the chatbot communicate?"
    )

with col4:
    language = st.selectbox(
        "🌍 Response Language",
        ["English", "Urdu", "Arabic", "French", "Spanish", "German"],
        help="Language the chatbot will primarily respond in."
    )

audience = st.text_input(
    "👥 Target Audience (optional)",
    placeholder="e.g. students, patients, small business owners",
)

generate_btn = st.button("⚡ Generate Chatbot Configuration")

# ── Generation ────────────────────────────────────────────────────────────────
def build_prompt(title, domain, tone, language, audience):
    audience_line = f"Target audience: {audience}." if audience else ""
    return f"""
You are an expert chatbot designer. A user wants to build a chatbot with the following specs:

- Title: {title}
- Domain: {domain}
- Tone: {tone}
- Response Language: {language}
- {audience_line}

Generate a complete chatbot configuration in the following EXACT format (use these exact section headers):

BOT NAME:
<A creative, professional name for the bot>

DESCRIPTION:
<2-3 sentences describing what this chatbot does and who it helps>

PERSONALITY:
<4-5 bullet points describing the bot's personality traits and communication style>

SAMPLE CONVERSATIONS:
<3 realistic Q&A pairs formatted as:
User: ...
Bot: ...
(blank line between pairs)>

SYSTEM PROMPT TEMPLATE:
<A ready-to-use system prompt (150-250 words) that can be pasted directly into any LLM API call to make it behave as this chatbot. Include placeholders like {{user_name}} where appropriate.>

Make everything specific, practical, and immediately usable.
""".strip()

if generate_btn:
    if not bot_title.strip():
        st.error("Please enter a chatbot title.")
        st.stop()

    with st.spinner("Generating your chatbot configuration..."):
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = build_prompt(bot_title, domain, tone, language, audience)
            response = model.generate_content(prompt)
            raw = response.text.strip()
        except Exception as e:
            st.error(f"Gemini API error: {e}")
            st.stop()

    # ── Parse sections ─────────────────────────────────────────────────────
    def extract_section(text, header, next_headers):
        start_tag = header + "\n"
        start = text.find(start_tag)
        if start == -1:
            return "N/A"
        start += len(start_tag)
        end = len(text)
        for nh in next_headers:
            idx = text.find(nh + "\n", start)
            if idx != -1 and idx < end:
                end = idx
        return text[start:end].strip()

    all_headers = [
        "BOT NAME:", "DESCRIPTION:", "PERSONALITY:",
        "SAMPLE CONVERSATIONS:", "SYSTEM PROMPT TEMPLATE:"
    ]

    def get_section(header):
        idx = all_headers.index(header)
        rest = all_headers[idx + 1:]
        return extract_section(raw, header, rest)

    bot_name    = get_section("BOT NAME:")
    description = get_section("DESCRIPTION:")
    personality = get_section("PERSONALITY:")
    sample_qa   = get_section("SAMPLE CONVERSATIONS:")
    sys_prompt  = get_section("SYSTEM PROMPT TEMPLATE:")

    # ── Display output ─────────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("## ✅ Your Chatbot Configuration")

    for label, content, is_code in [
        ("🤖 Bot Name",           bot_name,    False),
        ("📋 Description",        description, False),
        ("🎭 Personality",        personality, False),
        ("💬 Sample Conversations", sample_qa, False),
    ]:
        st.markdown(f"""
        <div class="output-card">
            <div class="output-label">{label}</div>
            <div class="output-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="output-card">
        <div class="output-label">🧠 System Prompt Template</div>
        <div class="prompt-box">{sys_prompt}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Download ───────────────────────────────────────────────────────────
    full_output = f"""AUTOBOT BUILDER — CHATBOT CONFIGURATION
Generated for: {bot_title}
Domain: {domain} | Tone: {tone} | Language: {language}
{'=' * 60}

BOT NAME:
{bot_name}

DESCRIPTION:
{description}

PERSONALITY:
{personality}

SAMPLE CONVERSATIONS:
{sample_qa}

SYSTEM PROMPT TEMPLATE:
{sys_prompt}
"""
    st.download_button(
        label="⬇️ Download Configuration (.txt)",
        data=full_output,
        file_name=f"{bot_title.replace(' ', '_')}_config.txt",
        mime="text/plain",
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center;color:#475569;font-size:0.8rem;'
    'font-family:Space Mono,monospace;">AutoBot Builder • Powered by Gemini 1.5 Flash</p>',
    unsafe_allow_html=True
)
