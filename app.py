import streamlit as st
import requests
import pandas as pd
import time

# --- 1. CONFIGURATION ---
DRAFT_ID = "1308917460388294656"
MY_USER_ID = "1123419086659723264"

st.set_page_config(page_title="TizBos War Room", layout="wide")

# --- 2. MASTER ADP & ID MAPPING ---
# I have mapped these to Sleeper IDs to prevent naming mismatches
PLAYER_VALUATION = {
    "10236": {"name": "Bijan Robinson", "adp": 1.01},
    "4046":  {"name": "Josh Allen", "adp": 1.02},
    "9221":  {"name": "Jahmyr Gibbs", "adp": 1.03},
    "11613": {"name": "Drake Maye", "adp": 1.04},
    "7564":  {"name": "Ja'Marr Chase", "adp": 1.05},
    "9488":  {"name": "Jaxon Smith-Njigba", "adp": 1.06},
    "11559": {"name": "Puka Nacua", "adp": 1.07},
    "11566": {"name": "Brock Bowers", "adp": 1.08},
    "13100": {"name": "Jeremiyah Love", "adp": 1.09},
    "11589": {"name": "Trey McBride", "adp": 1.10},
    "11607": {"name": "Jayden Daniels", "adp": 11.0},
    "11603": {"name": "Caleb Williams", "adp": 12.0},
    "13101": {"name": "Ashton Jeanty", "adp": 13.0},
    "4881":  {"name": "Lamar Jackson", "adp": 14.0},
    "7547":  {"name": "Amon-Ra St. Brown", "adp": 15.0},
    "11612": {"name": "Malik Nabers", "adp": 16.0},
    "6770":  {"name": "Joe Burrow", "adp": 17.0},
    "6794":  {"name": "Justin Jefferson", "adp": 18.0},
    "11560": {"name": "Devon Achane", "adp": 19.0}
}

# --- 3. FETCH DATA ---
def fetch_picks():
    try:
        return requests.get(f"https://api.sleeper.app/v1/draft/{DRAFT_ID}/picks").json()
    except: return []

# --- 4. RENDER WAR ROOM ---
def run_app():
    picks = fetch_picks()
    current_pick = len(picks) + 1
    
    # CRITICAL FIX: Create a set of IDs that are already gone
    drafted_ids = {str(p.get('player_id')) for p in picks}

    st.title(f"🚀 TizBos War Room | Pick {current_pick}")
    
    col_board, col_smash = st.columns([2, 1])

    with col_board:
        st.subheader("📊 Recent Picks")
        if picks:
            history = []
            for p in picks:
                history.append({
                    "Pick": p['pick_no'],
                    "Player": f"{p['metadata'].get('first_name')} {p['metadata'].get('last_name')}",
                    "Status": "✅ MINE" if str(p.get('picked_by')) == MY_USER_ID else "❌ GONE"
                })
            st.table(pd.DataFrame(history).iloc[::-1].head(10))

    with col_smash:
        st.subheader("🔥 Smash Alerts (+2 Threshold)")
        smashes = []
        
        for pid, data in PLAYER_VALUATION.items():
            # Only show if the ID is NOT in the drafted list
            if pid not in drafted_ids:
                if current_pick >= (data['adp'] + 2):
                    smashes.append({
                        "Player": data['name'],
                        "ADP": data['adp'],
                        "Value": f"+{round(current_pick - data['adp'], 1)}"
                    })

        if smashes:
            st.success("VALUES FOUND!")
            st.dataframe(pd.DataFrame(smashes), hide_index=True)
        else:
            st.info("Market is efficient.")

run_app()
time.sleep(20)
st.rerun()
