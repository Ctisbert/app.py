import streamlit as st
import requests
import pandas as pd

# --- CONFIGURATION ---
DRAFT_ID = "1308917460388294656"
SPORT = "nfl"

st.set_page_config(page_title="TizBos War Room", layout="wide")

# --- DATA FETCHING ---
def get_draft_data():
    # Gets the actual picks made
    picks = requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks").json()
    # Gets the draft status (who is on the clock)
    status = requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}").json()
    return picks, status

def get_trending_players():
    # Pulls the top 10 players being added right now on Sleeper
    return requests.get(f"https://api.sleeper.app/v1/players/{SPORT}/trending/add?lookback_hours=24&limit=10").json()

picks, status = get_draft_data()
trending = get_trending_players()

# --- SIDEBAR: LIVE VOTE ---
with st.sidebar:
    st.header("🗳️ Cast Your Vote")
    st.write("Help TizBos decide the next pick!")
    
    # We use Sleeper's trending players as the voting options
    vote_options = [f"Player ID: {p['player_id']} ({p['count']} adds)" for p in trending]
    selection = st.radio("Who is the best pick here?", ["Wait for suggestions..."] + vote_options)
    
    if st.button("Submit Vote"):
        if selection != "Wait for suggestions...":
            st.success(f"Vote recorded for {selection}!")
            # We store this in "session state" so it stays while the app is open
            if 'votes' not in st.session_state:
                st.session_state.votes = {}
            st.session_state.votes[selection] = st.session_state.votes.get(selection, 0) + 1
        else:
            st.warning("Please select a player first.")

    if 'votes' in st.session_state:
        st.write("---")
        st.write("**Current Tally:**")
        st.write(st.session_state.votes)

# --- MAIN SCREEN ---
st.title("🏈 TizBos Draft War Room")
st.write(f"**Draft Status:** {status.get('status', 'Unknown').upper()}")

col1, col2 = st.columns([2, 1])

with col1:
    st.header("📜 Recent Picks")
    if picks:
        # Create a clean table of the last 15 picks
        df = pd.DataFrame([
            {
                "Pick": p['pick_no'],
                "Player": f"{p['metadata']['first_name']} {p['metadata']['last_name']}",
                "Pos": p['metadata']['position'],
                "Team": p['metadata']['team']
            } for p in picks
        ])
        st.table(df.tail(15).iloc[::-1]) # Shows newest at the top
    else:
        st.info("No picks made yet. The board is fresh!")

with col2:
    st.header("🔥 Trending Now")
    st.write("These players are being added globally on Sleeper:")
    for p in trending:
        st.write(f"📍 Player ID: **{p['player_id']}**")
