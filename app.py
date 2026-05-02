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

# --- 1. STARTUP ADP DATA (May 2026 Consensus) ---
# Note: Ensure these names match Sleeper exactly (e.g. "Devon Achane" vs "De'Von Achane")
startup_adp = {
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

# --- 2. DATA HELPERS ---
@st.cache_data(ttl=86400)
def get_player_map():
    return requests.get(f"https://api.sleeper.app/v1/players/{SPORT}").json()

def get_live_picks():
    try:
        return requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks").json()
    except:
        return []

conn = st.connection("gsheets", type=GSheetsConnection)

def get_sheet_data():
    try:
        return conn.read(spreadsheet=SHEET_URL, ttl="1s")
    except:
        return pd.DataFrame(columns=["Player", "Votes", "Session_ID", "Last_Seen"])

player_map = get_player_map()

# --- 3. LIVE REFRESH LOGIC ---
with st.sidebar:
    st.title("Settings")
    live_mode = st.toggle("🛰️ Live Refresh Mode", value=False)
    st.divider()
    st.header(f"🛡️ Team {MY_USERNAME}")

st.title("🏈 TizBos Draft War Room")
main_container = st.empty()

def render_content():
    picks = get_live_picks()
    all_data = get_sheet_data()
    current_pick_no = len(picks) + 1
    
    # 1. CLEAN DRAFTED NAMES FOR BETTER MATCHING
    drafted_names = [
        f"{p['metadata'].get('first_name', '')} {p['metadata'].get('last_name', '')}".strip().lower() 
        for p in picks
    ]
    
    with main_container.container():
        m1, m2 = st.columns(2)
        m1.metric("🟢 Current Pick", f"Pick {current_pick_no}")
        m2.metric("🗳️ Total Votes", len(all_data[all_data["Votes"] == 1]) if "Votes" in all_data.columns else 0)

        col_board, col_vote = st.columns([2, 1])

        with col_board:
            st.subheader("📜 Live Draft Board")
            if picks:
                board_list = []
                for p in picks:
                    is_me = str(p.get('picked_by')) == "1123419086659723264"
                    board_list.append({
                        "Pick": p['pick_no'],
                        "Player": f"{p['metadata'].get('first_name', '')} {p['metadata'].get('last_name', '')}",
                        "Pos": p['metadata'].get('position', 'N/A'),
                        "Team": p['metadata'].get('team', 'N/A'),
                        "is_me": is_me
                    })
                df = pd.DataFrame(board_list).iloc[::-1]
                st.table(df.style.hide(axis="index").hide(subset=["is_me"], axis="columns"))
            else:
                st.info("Draft starting soon...")

        with col_vote:
            st.subheader("🔥 Startup Smash Alert")
            smashes = []
            
            # 2. UPDATED MATCHING: Compare normalized names to exclude drafted players
            for name, adp in startup_adp.items():
                if name.strip().lower() not in drafted_names:
                    if current_pick_no > (adp + 4):
                        smashes.append({"Player": name, "ADP": adp, "Value": f"+{round(current_pick_no - adp, 1)}"})
            
            if smashes:
                st.success(f"⚠️ VALUE DETECTED!")
                st.table(pd.DataFrame(smashes))
            else:
                st.info("No major values falling yet.")

# Initial run
render_content()

# Auto-Refresh if enabled
if live_mode:
    time.sleep(30)
    st.rerun()
