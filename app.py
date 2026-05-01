import streamlit as st
import requests
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time

# --- CONFIG ---
DRAFT_ID = "1308917460388294656"
SPORT = "nfl"
MY_USERNAME = "TizBos"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1oi03c9o5-KKYYDhamPR7WggPHHsTfwl9RYUlV2hqy_Q/edit?usp=sharing"

st.set_page_config(page_title="TizBos Draft War Room", layout="wide")

# --- 1. DATA TRANSLATORS ---
@st.cache_data(ttl=86400)
def get_player_map():
    return requests.get(f"https://api.sleeper.app/v1/players/{SPORT}").json()

@st.cache_data
def get_user_id(username):
    try:
        res = requests.get(f"https://api.sleeper.app/v1/user/{username}").json()
        return res.get('user_id')
    except:
        return None

player_map = get_player_map()
my_user_id = get_user_id(MY_USERNAME)

# --- 2. LIVE DATA & CONNECTIONS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_live_picks():
    return requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks").json()

def get_sheet_data():
    try:
        return conn.read(spreadsheet=SHEET_URL, ttl="1s")
    except:
        return pd.DataFrame(columns=["Player", "Votes", "Session_ID", "Last_Seen"])

picks = get_live_picks()
all_data = get_sheet_data()

# --- 3. LIVE VISITOR COUNTER ---
if "user_session_id" not in st.session_state:
    st.session_state.user_session_id = str(time.time())

current_time = time.time()
presence_row = pd.DataFrame([{
    "Session_ID": st.session_state.user_session_id, 
    "Last_Seen": current_time
}])

# Calculate how many people are active (seen in last 30 seconds)
if "Last_Seen" in all_data.columns:
    active_users_df = all_data[all_data["Last_Seen"] > (current_time - 30)]
    active_count = active_users_df["Session_ID"].nunique()
    if active_count == 0: active_count = 1
else:
    active_count = 1

# --- 4. HEADER & METRICS ---
st.title("🏈 TizBos Draft War Room")
m1, m2 = st.columns(2)
m1.metric("🟢 Live Now", f"{active_count} Users")
m2.metric("🗳️ Total Votes Cast", len(all_data[all_data["Votes"] == 1]) if "Votes" in all_data.columns else 0)

# --- 5. SIDEBAR: TEAM TIZBOS ---
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
        st.info("Waiting for picks...")

# --- 6. MAIN INTERFACE ---
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
        df = pd.DataFrame(board_data).iloc[::-1]
        
        def color_pick_row(row):
            color = 'background-color: #1b5e20; color: white' if row.Is_Me else 'background-color: #b71c1c; color: white'
            return [color] * len(row)

        st.table(df[['Pick', 'Player', 'Pos', 'Team', 'Owner']].style.apply(color_pick_row, axis=1))
    else:
        st.info("Draft hasn't started yet. Board will populate automatically.")

with col_vote:
    st.subheader("🗳️ Community Tally")
    if not all_data.empty and "Player" in all_data.columns:
        vote_counts = all_data[all_data["Votes"] == 1].groupby("Player").size().reset_index(name='Total Votes')
        vote_counts = vote_counts.sort_values(by='Total Votes', ascending=False)
        st.dataframe(vote_counts, hide_index=True, use_container_width=True)

    st.divider()
    st.write("**Who should TizBos draft next?**")
    drafted_ids = {str(p['player_id']) for p in picks}
    
    avail = []
    for p_id, info in player_map.items():
        if p_id not in drafted_ids and info.get('active'):
            adp = info.get('search_rank') or 999
            avail.append({"name": f"{info.get('first_name')} {info.get('last_name')} ({info.get('position')})", "adp": adp})
    
    top_options = sorted(avail, key=lambda x: x['adp'])[:25]
    player_names = [p['name'] for p in top_options]
    
    vote_choice = st.selectbox("Select a player:", ["-- Choose Player --"] + player_names)
    
    if st.button("Cast Vote"):
        if vote_choice != "-- Choose Player --":
            new_vote = pd.DataFrame([{
                "Player": vote_choice, 
                "Votes": 1, 
                "Session_ID": st.session_state.user_session_id, 
                "Last_Seen": time.time()
            }])
            updated_df = pd.concat([all_data, new_vote], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.balloons()
            st.rerun()
