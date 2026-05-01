# --- VISITOR/ACTION COUNTER ---
total_votes_cast = len(tally_df)
st.metric(label="📊 Community Engagement", value=f"{total_votes_cast} Votes Cast")

import streamlit as st
import requests
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- CONFIG ---
DRAFT_ID = "1308917460388294656"
SPORT = "nfl"
MY_USERNAME = "TizBos"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1oi03c9o5-KKYYDhamPR7WggPHHsTfwl9RYUlV2hqy_Q/edit?usp=sharing"

st.set_page_config(page_title="TizBos Draft War Room", layout="wide")

# --- 1. DATA TRANSLATORS ---
@st.cache_data(ttl=86400)
def get_player_map():
    # Pulling master player data for names and ADP
    return requests.get(f"https://api.sleeper.app/v1/players/{SPORT}").json()

@st.cache_data
def get_user_id(username):
    # Identifying TizBos's Sleeper ID
    try:
        res = requests.get(f"https://api.sleeper.app/v1/user/{username}").json()
        return res.get('user_id')
    except:
        return None

player_map = get_player_map()
my_user_id = get_user_id(MY_USERNAME)

# --- 2. LIVE DATA FETCHING ---
def get_live_picks():
    return requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks").json()

# Establish Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

def get_vote_tally():
    try:
        # Pulls existing votes from your Google Sheet
        df = conn.read(spreadsheet=SHEET_URL, ttl="1s")
        return df
    except:
        return pd.DataFrame(columns=["Player", "Votes"])

picks = get_live_picks()
tally_df = get_vote_tally()

# --- 3. SIDEBAR: TEAM TIZBOS ---
with st.sidebar:
    st.header(f"🛡️ Team {MY_USERNAME}")
    my_picks = [
        f"{p['metadata']['first_name']} {p['metadata']['last_name']} ({p['metadata']['position']})" 
        for p in picks if str(p.get('picked_by')) == str(my_user_id)
    ]
    if my_picks:
        for mp in my_picks:
            st.success(f"DRAFTED: {mp}")
    else:
        st.info("Waiting to make your first selection.")
    
    st.divider()
    st.write("💡 *Board updates live as picks are made.*")

# --- 4. MAIN INTERFACE ---
st.title("🏈 TizBos Draft War Room")

col_board, col_vote = st.columns([2, 1])

with col_board:
    st.subheader("📜 Live Draft Board")
    if picks:
        board_data = []
        for p in picks:
            is_me = str(p.get('picked_by')) == str(my_user_id)
            board_data.append({
                "Pick": p['pick_no'],
                "Player": f"{p['metadata']['first_name']} {p['metadata']['last_name']}",
                "Pos": p['metadata']['position'],
                "Team": p['metadata']['team'],
                "Owner": "TIZBOS" if is_me else "OPPONENT",
                "Is_Me": is_me
            })
        
        df = pd.DataFrame(board_data).iloc[::-1] # Show latest picks at top
        
        # High-contrast color coding
        def color_pick_row(row):
            # Dark Green for you, Dark Red for others
            color = 'background-color: #1b5e20; color: white' if row.Is_Me else 'background-color: #b71c1c; color: white'
            return [color] * len(row)

        st.table(df[['Pick', 'Player', 'Pos', 'Team', 'Owner']].style.apply(color_pick_row, axis=1))
    else:
        st.info("Draft hasn't started yet. Board will populate automatically.")

with col_vote:
    st.subheader("🗳️ Community Tally")
    
    # Show the current vote leaderboard
    if not tally_df.empty and "Player" in tally_df.columns:
        # Tally and sort
        vote_counts = tally_df.groupby("Player").size().reset_index(name='Total Votes')
        vote_counts = vote_counts.sort_values(by='Total Votes', ascending=False)
        st.dataframe(vote_counts, hide_index=True, use_container_width=True)
    else:
        st.write("No votes cast yet. Be the first!")

    st.divider()
    
    # Voting Logic
    st.write("**Who should TizBos draft next?**")
    drafted_ids = {str(p['player_id']) for p in picks}
    
    # Filter for top 25 available by ADP
    avail = []
    for p_id, info in player_map.items():
        if p_id not in drafted_ids and info.get('active'):
            adp = info.get('search_rank') or 999
            avail.append({
                "name": f"{info.get('first_name')} {info.get('last_name')} ({info.get('position')})",
                "adp": adp
            })
    
    top_options = sorted(avail, key=lambda x: x['adp'])[:25]
    player_names = [p['name'] for p in top_options]
    
    vote_choice = st.selectbox("Select a player:", ["-- Choose Player --"] + player_names)
    
    if st.button("Cast Vote"):
        if vote_choice != "-- Choose Player --":
            # Append new vote to the Google Sheet
            new_row = pd.DataFrame([{"Player": vote_choice, "Votes": 1}])
            updated_df = pd.concat([tally_df, new_row], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.balloons()
            st.success(f"Vote recorded for {vote_choice}!")
            st.rerun()
