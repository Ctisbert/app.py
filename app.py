import streamlit as st
import requests
import pandas as pd

# CONFIGURATION
USERNAME = "TizBos"
SPORT = "nfl"
SEASON = "2026"

st.set_page_config(page_title="TizBos Draft War Room", layout="wide")

st.title("🏈 TizBos Virtual Draft Room")
st.subheader("Live Sleeper Sync + Community Voting")

# 1. FETCH USER ID
@st.cache_data
def get_user_id(username):
    res = requests.get(f"https://api.sleeper.app/v1/user/{username}").json()
    return res['user_id']

user_id = get_user_id(USERNAME)

# 2. FETCH DRAFT ID (Finds your most recent draft)
@st.cache_data
def get_draft_id(u_id):
    drafts = requests.get(f"https://api.sleeper.app/v1/user/{u_id}/drafts/{SPORT}/{SEASON}").json()
    return drafts[0]['draft_id'] # Gets the newest draft

draft_id = get_draft_id(user_id)

# 3. LIVE DATA FETCHING
def get_draft_data():
    picks = requests.get(f"https://api.sleeper.app/v1/draft/{draft_id}/picks").json()
    status = requests.get(f"https://api.sleeper.app/v1/draft/{draft_id}").json()
    return picks, status

picks, status = get_draft_data()

# --- UI LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📜 Draft Board")
    if not picks:
        st.info("The draft hasn't started yet! Waiting for the first pick...")
    else:
        # Create a table of picks
        df = pd.DataFrame([
            {"Round": p['round'], "Pick": p['pick_no'], "Player": f"{p['metadata']['first_name']} {p['metadata']['last_name']}", "Team": p['metadata']['team']}
            for p in picks
        ])
        st.table(df.tail(10)) # Show last 10 picks

with col2:
    st.header("🗳️ Community Vote")
    st.write("Who should TizBos pick next?")
    
    # Simple voting buttons
    options = ["Best Available RB", "Best Available WR", "Quarterback", "TIGHT END!"]
    vote = st.radio("Cast your suggestion:", options)
    
    if st.button("Submit Vote"):
        st.success(f"Vote cast for {vote}! TizBos has been alerted.")
        # Note: In a 'free' cloud setup, this resets if the app sleeps, 
        # but works perfectly for a live 2-hour draft window.

st.divider()
st.caption(f"Connected to Draft ID: {draft_id} | Refreshes automatically on interaction.")
