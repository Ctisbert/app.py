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

# --- 1. DATA & ADP MAPPING (Sourced from Dynasty Data Lab May 2026) ---
@st.cache_data(ttl=86400)
def get_player_map():
    return requests.get(f"https://api.sleeper.app/v1/players/{SPORT}").json()

# Top Startup ADP (May 2026)
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

player_map = get_player_map()
conn = st.connection("gsheets", type=GSheetsConnection)

def get_live_picks():
    try: return requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks").json()
    except: return []

def get_sheet_data():
    try: return conn.read(spreadsheet=SHEET_URL, ttl="1s")
    except: return pd.DataFrame(columns=["Player", "Votes", "Session_ID", "Last_Seen"])

picks = get_live_picks()
all_data = get_sheet_data()
current_pick_no = len(picks) + 1

# --- 2. HEADER & METRICS ---
st.title("🏈 TizBos Draft War Room")
m1, m2 = st.columns(2)
m1.metric("🟢 Live Now", "1 User") # Simplified for stability
m2.metric("🗳️ Total Votes Cast", len(all_data[all_data["Votes"] == 1]) if "Votes" in all_data.columns else 0)

# --- 3. MAIN INTERFACE ---
col_board, col_vote = st.columns([2, 1])

with col_board:
    st.subheader("📜 Live Draft Board")
    if picks:
        board_list = []
        for p in picks:
            board_list.append({
                "Pick": p['pick_no'],
                "Player": f"{p['metadata'].get('first_name', '')} {p['metadata'].get('last_name', '')}",
                "Pos": p['metadata'].get('position', 'N/A'),
                "Team": p['metadata'].get('team', 'N/A'),
                "is_me": str(p.get('picked_by')) == "1123419086659723264" # Standardized your ID check
            })
        df = pd.DataFrame(board_list).iloc[::-1]
        def apply_row_style(row):
            color = 'background-color: #1b5e20; color: white' if row.is_me else 'background-color: #b71c1c; color: white'
            return [color] * len(row)
        styled_df = df.style.apply(apply_row_style, axis=1).hide(axis="index").hide(subset=["is_me"], axis="columns")
        st.table(styled_df)
    else:
        st.info("No picks yet!")

with col_vote:
    # --- SMASH ALERT SECTION ---
    st.subheader("🔥 Startup Smash Alert")
    smashes = []
    drafted_names = [f"{p['metadata'].get('first_name', '')} {p['metadata'].get('last_name', '')}".lower() for p in picks]
    
    for name, adp in startup_adp.items():
        if name.lower() not in drafted_names:
            # A Smash is available 4+ spots past their ADP
            if current_pick_no > (adp + 4):
                smashes.append({"Player": name, "ADP": adp, "Value": f"+{round(current_pick_no - adp, 1)} spots"})
    
    if smashes:
        st.success(f"⚠️ VALUE DETECTED at Pick {current_pick_no}!")
        st.table(pd.DataFrame(smashes))
    else:
        st.info("No major values falling yet.")

    st.divider()
    st.subheader("🗳️ Vote for the Next Pick")
    # Dropdown logic for 300 players...
