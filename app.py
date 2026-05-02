import streamlit as st
import requests
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time

# --- 1. CONFIGURATION ---
DRAFT_ID = "1308917460388294656"
MY_USER_ID = "1123419086659723264"
MY_USERNAME = "TizBos"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1oi03c9o5-KKYYDhamPR7WggPHHsTfwl9RYUlV2hqy_Q/edit?usp=sharing"

st.set_page_config(page_title="TizBos War Room", layout="wide")

# --- 2. ADP DATA (Based on your provided May 2026 Startup list) ---
STARTUP_ADP = {
    "Christian Watson": 101.2, "Chris Godwin": 145.1, "Mark Andrews": 146.6,
    "Kenneth Gainwell": 148.9, "Michael Penix Jr.": 149.4, "Jacoby Brissett": 152.1,
    "Shedeur Sanders": 152.2, "Elijah Sarratt": 152.4, "Tony Pollard": 153.3,
    "Tua Tagovailoa": 154.6, "Emmett Johnson": 154.8, "Chigoziem Okonkwo": 155.4,
    "Travis Kelce": 155.6, "Germie Bernard": 156.4, "Woody Marks": 156.6,
    "Juwan Johnson": 156.9, "Khalil Shakir": 157.4, "Gunnar Helm": 157.6,
    "T.J. Hockenson": 157.8, "Dallas Goedert": 157.9, "Jalen McMillan": 158.0,
    "Jordan Mason": 158.6, "Rachaad White": 161.8, "Mason Taylor": 162.2,
    "Zachariah Branch": 163.0, "Chris Brazzell": 163.0, "J.J. McCarthy": 166.2,
    "Geno Smith": 169.2, "Tre Harris": 170.9, "Antonio Williams": 171.2,
    "Brandon Aiyuk": 171.8
}

# --- 3. DATA PERSISTENCE ---
@st.cache_data(ttl=86400)
def fetch_master_players():
    return requests.get("https://api.sleeper.app/v1/players/nfl").json()

def fetch_draft_picks():
    try:
        return requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks").json()
    except:
        return []

conn = st.connection("gsheets", type=GSheetsConnection)

def get_voting_data():
    try:
        return conn.read(spreadsheet=SHEET_URL, ttl="1s")
    except:
        return pd.DataFrame(columns=["Player", "Votes", "Timestamp"])

player_db = fetch_master_players()

# --- 4. CORE INTERFACE ---
def run_app():
    picks = fetch_draft_picks()
    votes = get_voting_data()
    current_pick = len(picks) + 1
    
    # Blacklist drafted players using IDs for absolute accuracy
    drafted_ids = {str(p.get('player_id')) for p in picks}

    st.title(f"🚀 TizBos War Room | Pick {current_pick}")
    
    col_board, col_intel = st.columns([2, 1])

    with col_board:
        st.subheader("📊 Draft Progress")
        if picks:
            board = []
            for p in picks:
                is_you = str(p.get('picked_by')) == MY_USER_ID
                board.append({
                    "Pick": p['pick_no'],
                    "Player": f"{p['metadata'].get('first_name')} {p['metadata'].get('last_name')}",
                    "Pos": p['metadata'].get('position'),
                    "Status": "✅ MINE" if is_you else "❌ GONE",
                    "is_me": is_you
                })
            df = pd.DataFrame(board).iloc[::-1]
            
            def row_color(row):
                style = 'background-color: #1b5e20' if row.is_me else 'background-color: #424242'
                return [f'{style}; color: white'] * len(row)
            
            st.table(df.style.apply(row_color, axis=1).hide(axis="index").hide(subset=["is_me"], axis="columns"))
        else:
            st.info("The board is waiting for the 1.01.")

    with col_intel:
        # --- REVISED SMASH ALERTS (Threshold: +2) ---
        st.subheader("🔥 Smash Alerts")
        smashes = []
        
        for name, adp in STARTUP_ADP.items():
            pid = next((k for k, v in player_db.items() 
                        if f"{v.get('first_name', '')} {v.get('last_name', '')}".lower() == name.lower()), None)
            
            if pid and pid not in drafted_ids:
                # UPDATED CRITERIA: Trigger alert if current pick is 2+ spots past ADP
                if current_pick >= (adp + 2): 
                    smashes.append({
                        "Player": name, 
                        "ADP": adp, 
                        "Value": f"+{round(current_pick - adp, 1)} spots"
                    })

        if smashes:
            st.success(f"VALUE DETECTED AT PICK {current_pick}!")
            st.dataframe(pd.DataFrame(smashes), hide_index=True, use_container_width=True)
        else:
            st.info("No major values falling past ADP yet.")

        # --- VOTING ---
        st.divider()
        st.subheader("🗳️ Vote Next Pick")
        
        # Pull 300 available players for the dropdown
        avail_players = []
        for p_id, info in player_db.items():
            if p_id not in drafted_ids and info.get('active'):
                avail_players.append({
                    "name": f"{info.get('first_name')} {info.get('last_name')} ({info.get('position')})",
                    "rank": info.get('search_rank') or 999
                })
        
        top_300 = sorted(avail_players, key=lambda x: x['rank'])[:300]
        options = [p['name'] for p in top_300]
        
        vote_on = st.selectbox("Select Player:", ["-- Search --"] + options)
        if st.button("Submit Vote"):
            if vote_on != "-- Search --":
                new_v = pd.DataFrame([{"Player": vote_on, "Votes": 1, "Timestamp": time.time()}])
                conn.update(spreadsheet=SHEET_URL, data=pd.concat([votes, new_v]))
                st.toast("Vote Recorded.")
                time.sleep(1)
                st.rerun()

# Run the UI and refresh every 20 seconds
run_app()
time.sleep(20)
st.rerun()
