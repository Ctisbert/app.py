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

# --- 2. UPDATED ADP DATA (Drafted from your provided list) ---
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
    """Fetch the full NFL player database to map IDs."""
    return requests.get("https://api.sleeper.app/v1/players/nfl").json()

def fetch_draft_picks():
    """Fetch live draft picks."""
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
    
    # BLACKLIST: Ensure drafted players are 100% gone from value lists
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
            df = pd.DataFrame(board).iloc[::-1] # Newest picks on top
            
            def row_color(row):
                style = 'background-color: #1b5e20' if row.is_me else 'background-color: #424242'
                return [f'{style}; color: white'] * len(row)
            
            st.table(df.style.apply(row_color, axis=1).hide(axis="index").hide(subset=["is_me"], axis="columns"))
        else:
            st.info("The board is waiting for the 1.01.")

    with col_intel:
        # --- ID-BASED VALUE ENGINE ---
        st.subheader("🔥 Smash Alerts")
        smashes = []
        
        for name, adp in STARTUP_ADP.items():
            # Find ID by name
            pid = next((k for k, v in player_db.items() 
                        if f"{v.get('first_name', '')} {v.get('last_name', '')}".lower() == name.lower()), None)
            
            # Use the blacklist to ensure we don't show drafted players
            if pid and pid not in drafted_ids:
                if current_pick > (adp + 4): # If falling 4+ spots past ADP
                    smashes.append({"Player": name, "ADP": adp, "Value": f"+{round(current_pick - adp, 1)}"})

        if smashes:
            st.success(f"VALUE DETECTED AT PICK {current_pick}!")
            st.dataframe(pd.DataFrame(smashes), hide_index=True)
        else:
            st.info("No extreme values detected currently.")

        # --- VOTING ---
        st.divider()
        st.subheader("🗳️ Vote Next Pick")
        
        avail_names = [f"{v.get('first_name')} {v.get('last_name')} ({v.get('position')})" 
                       for k, v in player_db.items() 
                       if k not in drafted_ids and v.get('active')]
        
        vote_on = st.selectbox("Select Player:", ["-- Search --"] + sorted(avail_names))
        if st.button("Submit Vote"):
            if vote_on != "-- Search --":
                new_v = pd.DataFrame([{"Player": vote_on, "Votes": 1, "Timestamp": time.time()}])
                conn.update(spreadsheet=SHEET_URL, data=pd.concat([votes, new_v]))
                st.toast("Vote Recorded.")
                time.sleep(1)
                st.rerun()

# Run and auto-refresh heartbeat
run_app()
time.sleep(20)
st.rerun()
