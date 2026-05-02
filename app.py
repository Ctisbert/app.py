import streamlit as st
import requests
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import time

# --- 1. CONFIGURATION & IDENTITY ---
DRAFT_ID = "1308917460388294656"
MY_USER_ID = "1123419086659723264"
MY_USERNAME = "TizBos"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1oi03c9o5-KKYYDhamPR7WggPHHsTfwl9RYUlV2hqy_Q/edit?usp=sharing"

st.set_page_config(page_title="TizBos War Room", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DATA ENGINES (Caching for Speed) ---
@st.cache_data(ttl=86400)
def fetch_master_player_data():
    """Download the full NFL player database once per day."""
    return requests.get("https://api.sleeper.app/v1/players/nfl").json()

def get_live_state():
    """Get real-time draft status and picks."""
    try:
        return requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks").json()
    except:
        return []

# Connect to the Voting Ledger
conn = st.connection("gsheets", type=GSheetsConnection)

def get_votes():
    try:
        return conn.read(spreadsheet=SHEET_URL, ttl="1s")
    except:
        return pd.DataFrame(columns=["Player", "Votes", "Timestamp"])

# --- 3. THE "SMASH" LOGIC (Market Value vs. Live Draft) ---
# Sourced from Dynasty Data Lab May 2026 Startup ADP
STARTUP_ADP = {
    "Bijan Robinson": 1.01, "Josh Allen": 1.02, "Jahmyr Gibbs": 1.03, "Drake Maye": 1.04,
    "Ja'Marr Chase": 1.05, "Jaxon Smith-Njigba": 1.06, "Puka Nacua": 1.07, "Brock Bowers": 1.08,
    "Trey McBride": 1.10, "Jeremiyah Love": 1.09, "Ashton Jeanty": 1.11, "Amon-Ra St. Brown": 1.13,
    "Caleb Williams": 1.14, "Malik Nabers": 1.15, "Lamar Jackson": 1.16, "Joe Burrow": 1.17,
    "Justin Jefferson": 1.18, "Devon Achane": 1.19, "CeeDee Lamb": 1.20, "Omarion Hampton": 1.21,
    "Colston Loveland": 1.22, "Drake London": 1.23, "Jaxson Dart": 1.24, "Justin Herbert": 1.25,
    "Tetairoa McMillan": 1.26, "Patrick Mahomes": 1.27, "Jonathan Taylor": 1.28, "James Cook": 1.29,
    "Tyler Warren": 1.30, "Trevor Lawrence": 1.31, "Jalen Hurts": 1.32, "Bo Nix": 1.33,
    "George Pickens": 1.34, "Emeka Egbuka": 1.35, "Chris Olave": 1.36, "Harold Fannin": 1.37,
    "Brock Purdy": 1.38, "Kenneth Walker III": 1.39, "Nico Collins": 1.40
}

# --- 4. EXECUTION ENGINE ---
player_db = fetch_master_player_data()

def run_war_room():
    picks = get_live_state()
    votes_df = get_votes()
    current_pick = len(picks) + 1
    
    # BLACKLIST: Every player already taken (ID-based for 100% accuracy)
    drafted_ids = {str(p.get('player_id')) for p in picks}

    # UI HEADER
    st.title(f"🛡️ {MY_USERNAME} War Room: Pick {current_pick} On the Clock")
    
    col_board, col_intel = st.columns([2, 1])

    with col_board:
        st.subheader("📊 Live Draft Board")
        if picks:
            # Construct board from newest to oldest
            board_data = []
            for p in picks:
                is_tizbos = str(p.get('picked_by')) == MY_USER_ID
                board_data.append({
                    "Pick": p['pick_no'],
                    "Player": f"{p['metadata'].get('first_name')} {p['metadata'].get('last_name')}",
                    "Pos": p['metadata'].get('position'),
                    "Owner": "✅ TIZBOS" if is_tizbos else "❌ OPPONENT",
                    "is_me": is_tizbos
                })
            df = pd.DataFrame(board_data).iloc[::-1]
            
            # Highlight TizBos picks in Green, Opponents in Dark Red
            def style_rows(row):
                bg = 'background-color: #06402B' if row.is_me else 'background-color: #3D0C02'
                return [f'{bg}; color: white'] * len(row)
            
            st.table(df.style.apply(style_rows, axis=1).hide(axis="index").hide(subset=["is_me"], axis="columns"))
        else:
            st.info("The board is clear. Waiting for the first pick.")

    with col_intel:
        # --- THE SMASH ENGINE ---
        st.subheader("🔥 Market Value Smashes")
        smashes = []
        
        # Cross-reference ADP dictionary with Sleeper IDs to ensure accuracy
        for name, adp_val in STARTUP_ADP.items():
            # Find the ID for the name in our list
            p_id = next((k for k, v in player_db.items() 
                        if f"{v.get('first_name')} {v.get('last_name')}".lower() == name.lower()), None)
            
            # If the ID exists and isn't in the blacklist, it's available
            if p_id and p_id not in drafted_ids:
                # If they've fallen 3+ spots past their ADP, flag it
                if current_pick > (adp_val + 3):
                    diff = current_pick - adp_val
                    smashes.append({"Player": name, "Value": f"+{round(diff, 1)} Spots"})
        
        if smashes:
            st.success("WE HAVE VALUE ON THE BOARD")
            st.dataframe(pd.DataFrame(smashes), hide_index=True, use_container_width=True)
        else:
            st.info("Market is efficient. No major smashes available.")

        # --- VOTING SYSTEM ---
        st.divider()
        st.subheader("🗳️ Next Pick Tally")
        
        # Dynamic search for top 300 available
        avail = []
        for p_id, info in player_db.items():
            if p_id not in drafted_ids and info.get('active'):
                avail.append({
                    "display": f"{info.get('first_name')} {info.get('last_name')} ({info.get('position')})",
                    "rank": info.get('search_rank') or 999
                })
        
        top_300 = sorted(avail, key=lambda x: x['rank'])[:300]
        options = [p['display'] for p in top_300]
        
        selection = st.selectbox("Search Draftable Players:", ["-- Select --"] + options)
        if st.button("Submit Vote"):
            if selection != "-- Select --":
                new_v = pd.DataFrame([{"Player": selection, "Votes": 1, "Timestamp": time.time()}])
                conn.update(spreadsheet=SHEET_URL, data=pd.concat([votes_df, new_v]))
                st.toast(f"Vote cast for {selection}!")
                time.sleep(1)
                st.rerun()

# --- 5. THE LIVE HEARTBEAT ---
# This forces the app to update even if no one clicks anything
run_war_room()

# Auto-refresh every 20 seconds to keep the board live
time.sleep(20)
st.rerun()
