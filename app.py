import streamlit as st
import requests
import pandas as pd

# --- CONFIG ---
DRAFT_ID = "1308917460388294656"
SPORT = "nfl"

st.set_page_config(page_title="TizBos Elite War Room", layout="wide")

# --- 1. THE PLAYER TRANSLATOR (Maps IDs to Names & ADP) ---
@st.cache_data(ttl=86400) 
def get_player_map():
    # Fetching the master list which includes ADP data
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
    picks = requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks").json()
    status = requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}").json()
    return picks, status

picks, status = get_data()

# --- 3. FILTERING BEST AVAILABLE (TOP 50 BY ADP) ---
def get_best_available(picks_made):
    # Get IDs of players already taken
    drafted_ids = {str(p['player_id']) for p in picks_made}
    
    # Filter master list for players not yet drafted and sort by ADP
    available = []
    for p_id, info in player_map.items():
        if p_id not in drafted_ids and info.get('active'):
            adp = info.get('search_rank') or info.get('fantasy_data_id') or 999 # Sleeper ADP fallback
            available.append({
                "id": p_id,
                "name": f"{info.get('first_name')} {info.get('last_name')}",
                "pos": info.get('position'),
                "adp": adp
            })
    
    # Sort by ADP (lowest number first) and take top 50
    sorted_available = sorted(available, key=lambda x: x['adp'])
    return sorted_available[:50]

best_available = get_best_available(picks)

# --- 4. THE UI LAYOUT ---
st.title("🏈 TizBos Virtual Draft War Room")
st.write(f"**Draft Status:** `{status.get('status', 'PRE_DRAFT').upper()}`")

tab1, tab2 = st.tabs(["📊 Live Draft Board", "💬 Chat & Community Vote"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📜 Recent Picks")
        if picks:
            pick_list = [{"Pick": p['pick_no'], "Player": f"{p['metadata']['first_name']} {p['metadata']['last_name']}", "Pos": p['metadata']['position']} for p in picks]
            st.table(pd.DataFrame(pick_list).iloc[::-1])
        else:
            st.info("The draft hasn't started yet.")

    with col2:
        st.header("🌟 Top 50 Available (ADP)")
        for p in best_available:
            st.write(f"📍 **{p['name']}** ({p['pos']})")

with tab2:
    st.header("🗣️ Room Chat")
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        st.write(f"**{msg['user']}**: {msg['text']}")

    with st.form("chat_form", clear_on_submit=True):
        u_name = st.text_input("Your Nickname", value="DraftWatcher")
        u_msg = st.text_input("Message...")
        if st.form_submit_button("Send") and u_msg:
            st.session_state.messages.append({"user": u_name, "text": u_msg})
            st.rerun()

    st.divider()
    
    st.header("🗳️ Help TizBos Pick")
    # Show top 15 available players as voting options
    vote_options = [f"{p['name']} ({p['pos']})" for p in best_available[:15]]
    selection = st.radio("Who is the best pick right now?", ["Select..."] + vote_options)
    
    if st.button("Submit Vote") and selection != "Select...":
        st.success(f"Vote for {selection} recorded!")
