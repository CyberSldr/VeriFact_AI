import os
import streamlit as st
import streamlit as st
import requests
from google import genai

# --- CONFIGURATION ---
# This looks for a secret called "GOOGLE_API_KEY"
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)

# --- APP STYLING ---
st.set_page_config(page_title="VeriFact AI", page_icon="🔍", layout="centered")

st.title("🔍 VeriFact AI")
st.markdown("### Global News & Misinformation Verifier")
st.info("Paste a headline, social media post, or claim below to verify its accuracy.")

# --- HELPER FUNCTIONS ---
def get_fact_check(query):
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={GOOGLE_API_KEY}"
    res = requests.get(url).json()
    return res.get("claims", [])

# --- USER INTERFACE ---
user_input = st.text_area("What would you like to verify?", placeholder="e.g., Scientists have discovered a new planet made of diamonds...")

if st.button("Verify Claim"):
    if not user_input.strip():
        st.warning("Please enter a claim first!")
    else:
        with st.spinner("Analyzing across global databases and AI neural networks..."):
            # 1. Check Fact-Check Database
            claims = get_fact_check(user_input)
            
            if claims:
                st.success("✅ Match found in Fact-Check Database!")
                c = claims[0]
                review = c["claimReview"][0]
                
                # Display result in a nice card
                with st.expander("View Official Fact Check Report", expanded=True):
                    st.write(f"**Claim:** {c['text']}")
                    st.metric("Rating", review['textualRating'].upper())
                    st.write(f"**Source:** {review['publisher']['name']}")
                    st.link_button("Read Full Article", review['url'])
            else:
                # 2. AI Reasoning Layer
                st.info("🤖 No direct database match. Initiating AI Deep Analysis...")
                
                prompt = (
                    f"Analyze this claim: '{user_input}'. "
                    "Provide: 1. A Credibility Score (0-100), 2. Potential logical fallacies, "
                    "3. Whether it matches known misinformation patterns. Keep it structured."
                )
                
                try:
                    response = client.models.generate_content(
                        model='gemini-3-flash-preview',
                        contents=prompt
                    )
                    st.markdown("---")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"AI Analysis failed: {e}")

st.divider()
st.caption("VeriFact v2.0 | Powered by Gemini 3 Flash & Google Fact Check Tools | Created by CYBERSLDER")