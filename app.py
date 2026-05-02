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

# --- 2. DYNASTY DATA LAB ADP (May 1, 2026 Refresh) ---
# Format: "Name": Startup_ADP
STARTUP_ADP = {
    "Bijan Robinson": 1.01, "Josh Allen": 1.02, "Jahmyr Gibbs": 1.03,
    "Drake Maye": 1.04, "Ja'Marr Chase": 1.05, "Jaxon Smith-Njigba": 1.06,
    "Puka Nacua": 1.07, "Brock Bowers": 1.08, "Jeremiyah Love": 1.09,
    "Trey McBride": 1.10, "Jayden Daniels": 11.0, "Caleb Williams": 12.0,
    "Ashton Jeanty": 13.0, "Lamar Jackson": 14.0, "Amon-Ra St. Brown": 15.0,
    "Malik Nabers": 16.0, "Joe Burrow": 17.0, "Justin Jefferson": 18.0,
    "Devon Achane": 19.0, "CeeDee Lamb": 20.0, "Omarion Hampton": 21.0,
    "Colston Loveland": 22.0, "Drake London": 23.0
}

# --- 3. THE ENGINE ---
@st.cache_data(ttl=86400)
def fetch_master_data():
    """Global Sleeper database for ID mapping."""
    return requests.get("https://api.sleeper.app/v1/players/nfl").json()

def fetch_live_draft():
    """Live API check for current picks."""
    try:
        return requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks").json()
    except: return []

conn = st.connection("gsheets", type=GSheetsConnection)
player_db = fetch_master_data()

# --- 4. RENDER WAR ROOM ---
def run_war_room():
    picks = fetch_live_draft()
    current_pick = len(picks) + 1
    
    # BLACKLIST: Track drafted IDs instead of names
    drafted_ids = {str(p.get('player_id')) for p in picks}

    st.title(f"🚀 TizBos War Room | Pick {current_pick}")
    
    col_board, col_intel = st.columns([2, 1])

    with col_board:
        st.subheader("📊 Draft Progress")
        if picks:
            board = []
            for p in picks:
                is_you = str(p.get('picked_by')) == MY_USER_ID
                board_data = {
                    "Pick": p['pick_no'],
                    "Player": f"{p['metadata'].get('first_name')} {p['metadata'].get('last_name')}",
                    "Pos": p['metadata'].get('position'),
                    "Status": "✅ MINE" if is_you else "❌ GONE"
                }
                board.append(board_data)
            st.table(pd.DataFrame(board).iloc[::-1])
        else:
            st.info("The board is clear. Awaiting 1.01.")

    with col_intel:
        # --- THE SMASH ENGINE (ID-BASED) ---
        st.subheader("🔥 Smash Alerts (+2 Target)")
        smashes = []
        
        for name, adp in STARTUP_ADP.items():
            # Find the unique ID for the player on your list
            p_id = next((k for k, v in player_db.items() 
                        if f"{v.get('first_name', '')} {v.get('last_name', '')}".lower() == name.lower()), None)
            
            # Cross-reference against the drafted blacklist
            if p_id and p_id not in drafted_ids:
                if current_pick >= (adp + 2):
                    smashes.append({"Player": name, "ADP": adp, "Value": f"+{round(current_pick - adp, 1)}"})

        if smashes:
            st.success("WE HAVE VALUE DETECTED!")
            st.dataframe(pd.DataFrame(smashes), hide_index=True)
        else:
            st.info("Market is efficient. No smashes available.")

# Initial Run and Background Refresh
run_war_room()
time.sleep(20)
st.rerun()
