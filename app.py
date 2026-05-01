import streamlit as st
import requests
import pandas as pd

# --- CONFIG ---
DRAFT_ID = "1308917460388294656"
SPORT = "nfl"
MY_USERNAME = "TizBos"

st.set_page_config(page_title="TizBos Elite War Room", layout="wide")

# --- 1. DATA TRANSLATORS ---
@st.cache_data(ttl=86400) 
def get_player_map():
    # Fetching master list for ADP and Names
    return requests.get(f"https://api.sleeper.app/v1/players/{SPORT}").json()

@st.cache_data
def get_user_id(username):
    # Fetching your specific user_id to identify your picks
    res = requests.get(f"https://api.sleeper.app/v1/user/{username}").json()
    return res['user_id']

player_map = get_player_map()
my_user_id = get_user_id(MY_USERNAME)

# --- 2. LIVE DATA FETCHING ---
def get_live_data():
    picks = requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks").json() #
    status = requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}").json() #
    return picks, status

picks, status = get_live_data()

# --- 3. LOGIC FOR TABLES ---
def get_best_available(picks_made):
    drafted_ids = {str(p['player_id']) for p in picks_made}
    available = []
    for p_id, info in player_map.items():
        if p_id not in drafted_ids and info.get('active'):
            # Using search_rank as the proxy for ADP
            adp = info.get('search_rank') or 999 
            available.append({"name": f"{info.get('first_name')} {info.get('last_name')}", "pos": info.get('position'), "adp": adp})
    return sorted(available, key=lambda x: x['adp'])[:50]

# --- 4. THE UI LAYOUT ---
st.title("🏈 TizBos Elite Draft War Room")

# Sidebar for YOUR Team
with st.sidebar:
    st.header(f"🛡️ Team {MY_USERNAME}")
    my_picks = [f"{p['metadata']['first_name']} {p['metadata']['last_name']} ({p['metadata']['position']})" 
                for p in picks if str(p.get('picked_by')) == str(my_user_id)]
    if my_picks:
        for mp in my_picks:
            st.success(mp)
    else:
        st.write("No players drafted yet.")

tab1, tab2 = st.tabs(["📊 Live Board", "💬 Chat & Vote"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📜 Full Draft Board")
        if picks:
            # Create a dataframe to apply coloring
            df_picks = pd.DataFrame([
                {
                    "Pick": p['pick_no'],
                    "Player": f"{p['metadata']['first_name']} {p['metadata']['last_name']}",
                    "Team": p['metadata']['team'],
                    "Is_Me": str(p.get('picked_by')) == str(my_user_id)
                } for p in picks
            ])
            
            # Apply Red highlighting for everyone else, Green for TizBos
            def highlight_picks(row):
                color = 'background-color: #2e7d32' if row.Is_Me else 'background-color: #c62828'
                return [color] * len(row)

            st.table(df_picks.style.apply(highlight_picks, axis=1))
        else:
            st.info("Waiting for the first pick...")

    with col2:
        st.header("🌟 Top 50 Available")
        best_available = get_best_available(picks)
        for p in best_available:
            st.write(f"📍 **{p['name']}** ({p['pos']})")

with tab2:
    # CHAT & VOTING (Same as previous version)
    st.header("🗣️ Room Chat")
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages: st.write(f"**{msg['user']}**: {msg['text']}")
    
    with st.form("chat", clear_on_submit=True):
        n, m = st.text_input("Name"), st.text_input("Message")
        if st.form_submit_button("Send") and m:
            st.session_state.messages.append({"user": n, "text": m})
            st.rerun()
