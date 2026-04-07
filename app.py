import streamlit as st
import requests
import time
from google import genai

# --- CONFIGURATION ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error("Missing API Key! Please add GOOGLE_API_KEY to your Streamlit secrets.")
    st.stop()

# --- APP STYLING ---
st.set_page_config(page_title="VeriFact AI", page_icon="🔍", layout="centered")

st.title("🔍 VeriFact AI")
st.markdown("### Global News & Misinformation Verifier")
st.info("Paste a headline or social media claim below to verify its accuracy.")

# --- HELPER FUNCTIONS ---
def get_fact_check(query):
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={GOOGLE_API_KEY}"
    try:
        res = requests.get(url).json()
        return res.get("claims", [])
    except Exception:
        return []

def stream_text(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)

# --- USER INTERFACE ---
user_input = st.text_area(
    "What would you like to verify?", 
    placeholder="e.g., Breaking: Government to impose a 50% tax on all internet usage starting tomorrow.",
    height=150
)

if st.button("Verify Claim", type="primary"):
    if not user_input.strip():
        st.warning("Please enter a claim first!")
    else:
        with st.status("🔍 Verifying Claim...", expanded=True) as status:
            st.write("Step 1: Searching global fact-check databases...")
            claims = get_fact_check(user_input)
            
            st.write("Step 2: Initializing AI Linguistic Analysis...")
            prompt = (
                f"Analyze this claim for misinformation potential: '{user_input}'. "
                "Structure your response with: \n"
                "1. Credibility Score (0-100%)\n"
                "2. Known logical fallacies found\n"
                "3. Comparison to common propaganda narratives.\n"
                "Keep it concise but detailed."
            )
            
            ai_text = ""
            max_retries = 3
            for i in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model='gemini-3-flash-preview',
                        contents=prompt
                    )
                    ai_text = response.text
                    status.update(label="✅ Analysis Complete!", state="complete", expanded=False)
                    break 
                except Exception as e:
                    if "503" in str(e) and i < max_retries - 1:
                        st.write(f"⚠️ Server busy, retrying in {i+2} seconds...")
                        time.sleep(i + 2)
                        continue
                    else:
                        status.update(label="❌ AI Analysis Failed", state="error")
                        st.error(f"Error: {e}")
                        st.stop()

        # --- DISPLAY RESULTS ---
        st.divider()
        if claims:
            st.success("### ✅ Database Match Found")
            c = claims[0]
            review = c["claimReview"][0]
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Official Rating", review['textualRating'].upper())
            with col2:
                st.write(f"**Verified by:** {review['publisher']['name']}")
            st.write(f"**The Claim:** {c['text']}")
            st.link_button("Read Full Fact-Check Report", review['url'])
            st.divider()

        st.subheader("🤖 AI Credibility Report")
        st.write_stream(stream_text(ai_text))

st.divider()
st.caption("VeriFact v2.0 | 2026 Edition | Powered by Gemini 3 Flash & Google Fact Check Tools | Created by CYBERSLDER")