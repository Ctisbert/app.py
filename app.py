import streamlit as st
import requests
import pandas as pd

# --- CONFIG ---
DRAFT_ID = "1308917460388294656"
SPORT = "nfl"

st.set_page_config(page_title="TizBos Elite War Room", layout="wide")

# --- 1. THE PLAYER TRANSLATOR (Maps IDs to Names) ---
@st.cache_data(ttl=86400) # Only downloads once per day
def get_player_map():
    # Fetching the master list to convert ID numbers to Names
    players = requests.get(f"https://api.sleeper.app/v1/players/{SPORT}").json()
    return players

player_map = get_player_map()

def get_name(p_id):
    p = player_map.get(str(p_id), {})
    if not p:
        return f"Unknown ({p_id})"
    return f"{p.get('first_name', '')} {p.get('last_name', '')} - {p.get('position', '')} ({p.get('team', 'FA')})"

# --- 2. DATA FETCHING ---
def get_data():
    # Pull picks already made
    picks = requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks").json()
    # Pull draft configuration/status
    status = requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}").json()
    # Pull currently trending players
    trending = requests.get(f"https://api.sleeper.app/v1/players/{SPORT}/trending/add").json()
    return picks, status, trending

picks, status, trending = get_data()

# --- 3. THE UI LAYOUT ---
st.title("🏈 TizBos Virtual Draft War Room")
st.write(f"**Draft Status:** `{status.get('status', 'PRE_DRAFT').upper()}`")

# Split screen into Tabs for better organization
tab1, tab2 = st.tabs(["📊 Live Draft Board", "💬 Chat & Community Vote"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📜 Recent Picks")
        if picks:
            # Table showing names instead of IDs
            pick_list = []
            for p in picks:
                name = f"{p['metadata']['first_name']} {p['metadata']['last_name']}"
                pick_list.append({
                    "Pick": p['pick_no'], 
                    "Player": name, 
                    "Pos": p['metadata']['position'],
                    "NFL Team": p['metadata']['team']
                })
            # Displaying newest picks at the top
            st.table(pd.DataFrame(pick_list).iloc[::-1])
        else:
            st.info("The draft hasn't started yet. Waiting for the first pick!")

    with col2:
        st.header("🌟 Best Available")
        st.write("Top trending players currently being added:")
        for p in trending[:12]: # Show top 12
            st.write(f"✅ **{get_name(p['player_id'])}**")

with tab2:
    # CHAT SECTION
    st.header("🗣️ Room Chat")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show messages
    for msg in st.session_state.messages:
        st.write(f"**{msg['user']}**: {msg['text']}")

    # Form to send new messages
    with st.form("chat_form", clear_on_submit=True):
        u_name = st.text_input("Your Nickname", value="DraftWatcher")
        u_msg = st.text_input("Message...")
        if st.form_submit_button("Send"):
            if u_msg:
                st.session_state.messages.append({"user": u_name, "text": u_msg})
                st.rerun()

    st.divider()
    
    # VOTING SECTION
    st.header("🗳️ Help TizBos Pick")
    # Use trending player names as the options
    vote_names = [get_name(p['player_id']) for p in trending[:5]]
    selection = st.radio("Who should be the next pick?", ["Select a player..."] + vote_names)
    
    if st.button("Submit Vote"):
        if selection != "Select a player...":
            st.success(f"Vote for {selection} submitted to TizBos!")
        else:
            st.warning("Please pick a player from the list to vote.")
