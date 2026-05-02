import streamlit as st
import requests
import pandas as pd
import time

# --- 1. CONFIGURATION ---
DRAFT_ID = "1308917460388294656"
MY_USER_ID = "1123419086659723264"

st.set_page_config(page_title="TizBos War Room", layout="wide")

# --- 2. MASTER RANKINGS (Mapping RK to IDs) ---
# Hardcoded to ensure zero naming mismatches
RANKINGS = {
    "4046": {"name": "Josh Allen", "rk": 1},
    "10236": {"name": "Bijan Robinson", "rk": 2},
    "11613": {"name": "Drake Maye", "rk": 3},
    "9221": {"name": "Jahmyr Gibbs", "rk": 4},
    "7564": {"name": "Ja'Marr Chase", "rk": 5},
    "9488": {"name": "Jaxon Smith-Njigba", "rk": 6},
    "11559": {"name": "Puka Nacua", "rk": 7},
    "11607": {"name": "Jayden Daniels", "rk": 8},
    "7547": {"name": "Amon-Ra St. Brown", "rk": 9},
    "4881": {"name": "Lamar Jackson", "rk": 10},
    "11603": {"name": "Caleb Williams", "rk": 11},
    "11612": {"name": "Malik Nabers", "rk": 12},
    "11566": {"name": "Brock Bowers", "rk": 13},
    "13101": {"name": "Ashton Jeanty", "rk": 14},
    "11589": {"name": "Trey McBride", "rk": 15},
    "6770": {"name": "Joe Burrow", "rk": 16},
    "6794": {"name": "Justin Jefferson", "rk": 17},
    "13100": {"name": "Jeremiyah Love", "rk": 18},
    "6783": {"name": "CeeDee Lamb", "rk": 19},
    "11560": {"name": "Devon Achane", "rk": 20},
    "13102": {"name": "Omarion Hampton", "rk": 21},
    "11624": {"name": "Jaxson Dart", "rk": 22},
    "6801": {"name": "Jalen Hurts", "rk": 23},
    "6797": {"name": "Justin Herbert", "rk": 24},
    "8151": {"name": "Drake London", "rk": 25}
    # Add more as needed based on your RK list
}

# --- 3. DYNAMIC DATA FETCHING ---
@st.cache_data(ttl=10) # 10-second "freshness" window
def get_live_picks():
    try:
        # Pulls live data from Sleeper's draft picks endpoint
        response = requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks")
        return response.json()
    except Exception as e:
        st.error(f"Sync Error: {e}")
        return []

# --- 4. RENDER ENGINE ---
def render_live_war_room():
    live_picks = get_live_picks()
    current_pick_number = len(live_picks) + 1
    
    # CRITICAL: Strip the list of ALL drafted player IDs from the live feed
    drafted_ids = {str(p.get('player_id')) for p in live_picks}

    st.title(f"🚀 Live War Room | Current Pick: {current_pick_number}")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("🔥 Smash Alerts (+2 Value)")
        available_smash = []
        for pid, data in RANKINGS.items():
            # Only process players who are NOT in the drafted_ids set
            if pid not in drafted_ids:
                if current_pick_number >= (data['rk'] + 2):
                    available_smash.append({
                        "Player": data['name'],
                        "RK": data['rk'],
                        "Value": f"+{current_pick_number - data['rk']}"
                    })
        
        if available_smash:
            st.success("TARGET FOUND")
            st.dataframe(pd.DataFrame(available_smash), hide_index=True)
        else:
            st.info("Searching for values...")

    with col2:
        st.subheader("📜 Recent Pick History")
        if live_picks:
            history = []
            for p in live_picks:
                history.append({
                    "No": p['pick_no'],
                    "Player": f"{p['metadata'].get('first_name')} {p['metadata'].get('last_name')}",
                    "Team": "✅ TizBos" if str(p.get('picked_by')) == MY_USER_ID else "❌ Opponent"
                })
            # Show last 10 picks, most recent first
            st.table(pd.DataFrame(history).iloc[::-1].head(10))

render_live_war_room()

# Auto-rerun loop: Forces the app to check for new picks every 15 seconds
time.sleep(15)
st.rerun()
