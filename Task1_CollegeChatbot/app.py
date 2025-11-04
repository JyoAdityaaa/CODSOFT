"""
CMR Engineering College Virtual Assistant
Developed by: Jyothiraditya R
Purpose: Internship Project Submission
Version: FINAL (Optimized + Accurate)
"""

import json
import streamlit as st
import difflib
import random
import time
import os
import re
from datetime import datetime


# ---------------------------------------------------
# Load Knowledge Base
# ---------------------------------------------------
@st.cache_data(ttl=3600)
def load_data(filepath="college_info.json"):
    """Load JSON knowledge base."""
    if not os.path.exists(filepath):
        st.error("❌ 'college_info.json' file not found.")
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------
# Intent Recognition and Response Generation
# ---------------------------------------------------
def clean_text(text):
    """Normalize text for better keyword recognition."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = text.replace(" or ", " ").replace(" and ", " ")
    return text.strip()


def format_section(section):
    """Convert dictionary or list to formatted markdown."""
    if isinstance(section, dict):
        parts = []
        if "info" in section:
            parts.append(f"**{section['info']}**")
        if "details" in section:
            if isinstance(section["details"], dict):
                details = "\n".join([f"**{k}:** {v}" for k, v in section["details"].items()])
                parts.append(details)
            else:
                parts.append(section["details"])
        if "list" in section:
            parts.append("**Highlights:**\n" + "\n".join([f"- {i}" for i in section["list"]]))
        if "note" in section:
            parts.append(f"📝 {section['note']}")
        return "\n\n".join(parts)
    return str(section)


def get_response(user_input, data):
    """Main intent-matching logic (final-safe version)."""
    if not data:
        return "⚠️ Data not loaded."

    query = clean_text(user_input)
    tokens = set(query.split())

    # ---- 1️⃣  Keyword map (expanded for plurals) ----
    keyword_map = {
        "college": ["college", "about", "cmr", "cmrec", "institution"],
        "location": ["location", "where", "address", "situated", "located", "place"],
        "departments": ["department", "departments", "branch", "branches", "program", "programs", "course", "courses", "stream", "streams"],
        "placements": ["placement", "placements", "career", "recruitment", "recruitments", "company", "companies", "job", "jobs", "hiring"],
        "fees": ["fees", "fee", "cost", "tuition", "payment", "structure", "quota"],
        "facilities": ["facility", "facilities", "lab", "labs", "library", "wifi", "sports", "hostel", "hostels", "campus"],
        "rules": ["rules", "rule", "discipline", "policy", "policies", "regulation", "attendance", "dress", "behavior", "conduct"],
        "events": ["event", "events", "fest", "fests", "function", "functions", "celebration", "activities", "annual", "cultural", "technical"],
        "contact": ["contact", "contacts", "email", "phone", "website", "principal"],
        "timing": ["timing", "timings", "schedule", "hours", "time", "class", "college timings"],
        "transport": ["transport", "bus", "buses", "route", "routes", "secunderabad"],
        "faculty": ["faculty", "faculties", "professor", "lecturer", "teacher", "teachers", "staff"]
    }

    prefix = random.choice([
        "Sure! Here's what I found 👇",
        "Got it! Here's the info:",
        "Of course 😊",
        "Here you go:",
        "Let me help you with that —"
    ])

    # ---- 2️⃣  Keyword intent detection (highest priority) ----
    matched_key = None
    for key, keywords in keyword_map.items():
        for kw in keywords:
            if kw in tokens or kw in query:
                matched_key = key
                break
        if matched_key:
            break

    if matched_key and matched_key in data:
        return prefix + "\n\n" + format_section(data[matched_key])

    # ---- 3️⃣  Fallback: token-overlap fuzzy search (safer than difflib) ----
    best_key = None
    best_score = 0
    for key in data.keys():
        overlap = len(set(key.split()) & tokens)
        if overlap > best_score:
            best_score = overlap
            best_key = key
    if best_key and best_score > 0:
        return prefix + "\n\n" + format_section(data[best_key])

    # ---- 4️⃣  Ultimate fallback ----
    fallback = data.get("fallback", "🤔 I’m not sure about that.")
    suggestions = ", ".join(data.get("fallback_replies", ["Placements", "Fees", "Facilities"]))
    return f"{fallback}\nTry asking about {suggestions}."

# ---------------------------------------------------
# Streamlit Frontend
# ---------------------------------------------------
def main():
    st.set_page_config(page_title="🎓 CMREC Chatbot", page_icon="🤖", layout="centered")

    # Custom styling
    st.markdown("""
        <style>
        body { background-color: #0E1117; color: white; }
        .user-bubble {
            background-color: #25D366;
            color: #000;
            padding: 10px 15px;
            border-radius: 12px;
            margin: 8px 0;
            text-align: right;
            max-width: 80%;
            margin-left: 20%;
        }
        .bot-bubble {
            background: #2C2F36;
            color: white;
            padding: 12px 15px;
            border-radius: 12px;
            margin: 8px 0;
            text-align: left;
            max-width: 80%;
        }
        a { color: #66bfff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center;'>🎓 CMR Engineering College Virtual Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>👋 Hello! Ask me anything about CMR College — placements, fees, rules, or facilities.</p>", unsafe_allow_html=True)

    data = load_data()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    query = st.chat_input("Type your question...")

    if query:
        with st.spinner("🤖 Typing..."):
            time.sleep(random.uniform(0.5, 1.0))
        response = get_response(query, data)
        st.session_state.chat_history.append(("You", query))
        st.session_state.chat_history.append(("Bot", response))

    # Display chat
    for sender, msg in st.session_state.chat_history:
        bubble_class = "user-bubble" if sender == "You" else "bot-bubble"
        st.markdown(f"<div class='{bubble_class}'><b>{sender}:</b><br>{msg}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Feedback system
    with st.expander("💬 Feedback or Suggestions"):
        feedback = st.text_area("Your feedback:")
        if st.button("Submit Feedback"):
            if feedback.strip():
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open("feedbacks.txt", "a", encoding="utf-8") as f:
                    f.write(f"[{timestamp}] {feedback}\n")
                st.success("✅ Feedback submitted successfully!")
            else:
                st.warning("⚠️ Please type something before submitting.")

    # Export chat
    if st.button("⬇️ Download Chat Transcript"):
        if not st.session_state.chat_history:
            st.warning("No chat yet.")
        else:
            transcript = "\n".join([f"{a}: {b}" for a, b in st.session_state.chat_history])
            st.download_button("Download Chat", transcript, "CMREC_Chat_History.txt", "text/plain")

    # Quick actions
    st.markdown("### 💡 Quick Topics")
    cols = st.columns(4)
    for i, topic in enumerate([ "Fees", "Facilities", "Rules", "Location",]):
        if cols[i].button(topic):
            response = get_response(topic, data)
            st.session_state.chat_history.append(("You", topic))
            st.session_state.chat_history.append(("Bot", response))
            st.rerun()


if __name__ == "__main__":
    main()
